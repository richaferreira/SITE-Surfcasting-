from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.integrations.openweather import OpenWeatherClient  # noqa: E402
from app.integrations.stormglass import StormglassClient  # noqa: E402
from app.services.fishing_score import FishingScoreService  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calcula o Score de Pesca para uma coordenada.")
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument(
        "--sea-bearing",
        type=float,
        required=True,
        help="Direção em graus da faixa de areia para o mar.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not -90 <= args.latitude <= 90:
        raise SystemExit("Latitude deve estar entre -90 e 90.")
    if not -180 <= args.longitude <= 180:
        raise SystemExit("Longitude deve estar entre -180 e 180.")
    if not 0 <= args.sea_bearing < 360:
        raise SystemExit("Sea bearing deve estar entre 0 e menos de 360 graus.")

    settings = get_settings()
    service = FishingScoreService(
        openweather=OpenWeatherClient(
            api_key=settings.openweather_api_key,
            timeout_seconds=settings.request_timeout_seconds,
        ),
        stormglass=StormglassClient(
            api_key=settings.stormglass_api_key,
            timeout_seconds=settings.request_timeout_seconds,
        ),
    )
    result = service.calculate(
        latitude=args.latitude,
        longitude=args.longitude,
        sea_bearing_deg=args.sea_bearing,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
