import pytest
from pydantic import ValidationError

from app.models.enums import BeachProfile
from app.schemas.beach import BeachCreate, BeachUpdate
from app.utils.slug import slugify


def test_slugify_preserves_clean_seo_slug() -> None:
    assert slugify("Praia de Itaúna — Saquarema") == "praia-de-itauna-saquarema"


def test_beach_create_normalizes_state() -> None:
    payload = BeachCreate(
        name="Praia de Itaúna",
        city="Saquarema",
        state="rj",
        latitude=-22.93,
        longitude=-42.49,
        sea_bearing_deg=160,
        beach_profile=BeachProfile.TOMBO,
    )

    assert payload.state == "RJ"
    assert payload.is_published is False


def test_invalid_coordinates_and_bearing_are_rejected() -> None:
    with pytest.raises(ValidationError):
        BeachCreate(
            name="Praia inválida",
            city="Saquarema",
            latitude=-100,
            longitude=-42.49,
            sea_bearing_deg=360,
            beach_profile=BeachProfile.TOMBO,
        )


def test_empty_beach_update_is_rejected() -> None:
    with pytest.raises(ValidationError):
        BeachUpdate()


def test_non_nullable_update_field_rejects_explicit_null() -> None:
    with pytest.raises(ValidationError):
        BeachUpdate(name=None)
