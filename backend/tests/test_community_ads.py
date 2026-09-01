from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.models.enums import AdPlacement, CommunityCategory
from app.schemas.ad import AdCampaignInput
from app.schemas.community import CommunityThreadCreate


def test_community_normalizes_text_and_accepts_managed_media() -> None:
    payload = CommunityThreadCreate(
        title="  Relato da maré enchendo  ",
        content="  A vala produziu durante a primeira hora da enchente.  ",
        category=CommunityCategory.RELATO,
        media_url="/media/abc.webp",
    )

    assert payload.title == "Relato da maré enchendo"
    assert payload.content.startswith("A vala")


def test_community_rejects_insecure_external_media() -> None:
    with pytest.raises(ValidationError):
        CommunityThreadCreate(
            title="Imagem externa insegura",
            content="Conteúdo suficiente para validar a discussão.",
            category=CommunityCategory.CAPTURA,
            media_url="http://example.com/capture.jpg",
        )


def test_ad_requires_https_and_valid_period() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        AdCampaignInput(
            name="Campanha inválida",
            placement=AdPlacement.HOME_TOPO,
            title="Oferta do parceiro",
            image_url="/media/banner.webp",
            target_url="http://example.com",
            alt_text="Banner promocional do parceiro",
            starts_at=now,
            ends_at=now - timedelta(hours=1),
        )


def test_ad_accepts_managed_image_and_https_target() -> None:
    now = datetime.now(timezone.utc)
    campaign = AdCampaignInput(
        name="Parceiro local",
        placement=AdPlacement.ACADEMIA,
        title="Equipamento selecionado",
        image_url="/media/banner.webp",
        target_url="https://example.com/oferta",
        alt_text="Vara de surfcasting sobre suporte",
        starts_at=now,
        ends_at=now + timedelta(days=7),
    )

    assert campaign.is_active is True
