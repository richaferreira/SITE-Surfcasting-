import asyncio
from io import BytesIO
from unittest.mock import Mock

import pytest
from fastapi import UploadFile
from PIL import Image
from starlette.datastructures import Headers

from app.core.config import Settings
from app.core.exceptions import UnprocessableError
from app.models.enums import MediaKind
from app.services.media import MediaService


def image_upload(filename: str = "foto.png") -> UploadFile:
    content = BytesIO()
    Image.new("RGB", (3200, 1600), color=(15, 84, 112)).save(content, format="PNG")
    content.seek(0)
    return UploadFile(
        file=content,
        filename=filename,
        headers=Headers({"content-type": "image/png"}),
    )


def test_image_upload_is_resized_converted_and_filename_is_sanitized(tmp_path) -> None:
    settings = Settings(
        media_root=tmp_path,
        media_image_max_dimension=1200,
        media_image_quality=80,
    )
    session = Mock()
    actor = Mock(id=9)

    asset = asyncio.run(
        MediaService(session, settings).save(
            image_upload("../../capa-perigosa.png"),
            actor=actor,
        )
    )

    assert asset.kind is MediaKind.IMAGE
    assert asset.original_name == "capa-perigosa.png"
    assert asset.mime_type == "image/webp"
    assert asset.width == 1200
    assert asset.height == 600
    assert asset.stored_name.endswith(".webp")
    assert (tmp_path / asset.stored_name).is_file()
    session.commit.assert_called_once()


def test_unsupported_upload_type_is_rejected(tmp_path) -> None:
    upload = UploadFile(
        file=BytesIO(b"not-an-image"),
        filename="payload.svg",
        headers=Headers({"content-type": "image/svg+xml"}),
    )
    service = MediaService(Mock(), Settings(media_root=tmp_path))

    with pytest.raises(UnprocessableError):
        asyncio.run(service.save(upload, actor=Mock(id=1)))
