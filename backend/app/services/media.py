from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import warnings
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.config import Settings
from app.core.exceptions import (
    DependencyUnavailableError,
    PayloadTooLargeError,
    UnprocessableError,
)
from app.models.enums import MediaKind
from app.models.media import MediaAsset
from app.models.user import User
from app.repositories.media import MediaRepository


Image.MAX_IMAGE_PIXELS = 40_000_000


class MediaService:
    IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings
        self.repository = MediaRepository(session)

    async def save(self, upload: UploadFile, actor: User) -> MediaAsset:
        declared_type = (upload.content_type or "").lower()
        if declared_type in self.IMAGE_TYPES:
            kind = MediaKind.IMAGE
        elif declared_type in self.VIDEO_TYPES:
            kind = MediaKind.VIDEO
        else:
            raise UnprocessableError(
                "Formato não suportado. Envie JPG, PNG, WebP, MP4, MOV ou WebM."
            )

        root = self.settings.media_root.resolve()
        temporary_root = Path(tempfile.gettempdir()) / "surfcasting-media"
        temporary_root.mkdir(parents=True, exist_ok=True)
        root.mkdir(parents=True, exist_ok=True)
        token = uuid4().hex
        temporary_path = temporary_root / token
        original_size = await self._stream_upload(upload, temporary_path)

        output_path: Path | None = None
        try:
            if kind is MediaKind.IMAGE:
                output_path, metadata = await run_in_threadpool(
                    self._compress_image,
                    temporary_path,
                    root,
                    token,
                )
                output_mime = "image/webp"
            else:
                output_path, metadata = await run_in_threadpool(
                    self._compress_video,
                    temporary_path,
                    root,
                    token,
                )
                output_mime = "video/mp4"

            original_name = (upload.filename or "upload").replace("\\", "/").split("/")[-1][:255]
            asset = MediaAsset(
                uploaded_by_id=actor.id,
                kind=kind,
                original_name=original_name,
                stored_name=output_path.name,
                mime_type=output_mime,
                url=f"{self.settings.media_url_prefix.rstrip('/')}/{output_path.name}",
                original_size_bytes=original_size,
                size_bytes=output_path.stat().st_size,
                width=metadata.get("width"),
                height=metadata.get("height"),
                duration_seconds=metadata.get("duration_seconds"),
            )
            self.repository.add(asset)
            self.session.commit()
            return asset
        except Exception:
            self.session.rollback()
            if output_path is not None:
                output_path.unlink(missing_ok=True)
            raise
        finally:
            temporary_path.unlink(missing_ok=True)

    async def _stream_upload(self, upload: UploadFile, destination: Path) -> int:
        maximum = self.settings.media_max_upload_mb * 1024 * 1024
        written = 0
        try:
            with destination.open("wb") as target:
                while chunk := await upload.read(self.CHUNK_SIZE):
                    written += len(chunk)
                    if written > maximum:
                        raise PayloadTooLargeError(
                            f"O arquivo excede o limite de {self.settings.media_max_upload_mb} MB."
                        )
                    target.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        if written == 0:
            destination.unlink(missing_ok=True)
            raise UnprocessableError("O arquivo enviado está vazio.")
        return written

    def _compress_image(
        self,
        source: Path,
        root: Path,
        token: str,
    ) -> tuple[Path, dict[str, int | None]]:
        destination = root / f"{token}.webp"
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(source) as raw_image:
                    image = ImageOps.exif_transpose(raw_image)
                    image.load()
                    image.thumbnail(
                        (
                            self.settings.media_image_max_dimension,
                            self.settings.media_image_max_dimension,
                        ),
                        Image.Resampling.LANCZOS,
                    )
                    if image.mode not in {"RGB", "RGBA"}:
                        image = image.convert(
                            "RGBA" if "transparency" in image.info else "RGB"
                        )
                    image.save(
                        destination,
                        format="WEBP",
                        quality=self.settings.media_image_quality,
                        method=6,
                    )
                    return destination, {
                        "width": image.width,
                        "height": image.height,
                        "duration_seconds": None,
                    }
        except (
            UnidentifiedImageError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            OSError,
        ) as exc:
            destination.unlink(missing_ok=True)
            raise UnprocessableError(
                "A imagem enviada é inválida ou excede os limites seguros."
            ) from exc

    def _compress_video(
        self,
        source: Path,
        root: Path,
        token: str,
    ) -> tuple[Path, dict[str, int | None]]:
        if shutil.which(self.settings.ffmpeg_binary) is None:
            raise DependencyUnavailableError(
                "O compressor de vídeo não está disponível no servidor."
            )
        destination = root / f"{token}.mp4"
        command = [
            self.settings.ffmpeg_binary,
            "-nostdin",
            "-y",
            "-i",
            str(source),
            "-map_metadata",
            "-1",
            "-vf",
            "scale=1920:-2:force_original_aspect_ratio=decrease",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "24",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(destination),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, timeout=600)
            metadata = self._probe_video(destination)
            return destination, metadata
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            destination.unlink(missing_ok=True)
            raise UnprocessableError(
                "Não foi possível validar ou comprimir o vídeo enviado."
            ) from exc

    def _probe_video(self, video: Path) -> dict[str, int | None]:
        if shutil.which(self.settings.ffprobe_binary) is None:
            return {"width": None, "height": None, "duration_seconds": None}
        command = [
            self.settings.ffprobe_binary,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height:format=duration",
            "-of",
            "json",
            str(video),
        ]
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(result.stdout)
            stream = (payload.get("streams") or [{}])[0]
            duration = float((payload.get("format") or {}).get("duration", 0) or 0)
            return {
                "width": int(stream["width"]) if stream.get("width") else None,
                "height": int(stream["height"]) if stream.get("height") else None,
                "duration_seconds": round(duration) if duration else None,
            }
        except (subprocess.SubprocessError, OSError, ValueError, TypeError, KeyError):
            return {"width": None, "height": None, "duration_seconds": None}
