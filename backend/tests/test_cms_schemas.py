from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.core.exceptions import AuthorizationError
from app.models.enums import (
    AccessibilityLevel,
    FishingPointType,
    PostContentType,
    PostStatus,
    RoleCode,
)
from app.schemas.fishing_point import FishingPointCreate
from app.schemas.post import (
    EquipmentSpecificationInput,
    PostCreate,
    PublicPostResponse,
)
from app.services.post import PostService


def test_long_cast_equipment_specification_preserves_exact_measurements() -> None:
    payload = PostCreate(
        title="Conjunto tubular para long cast",
        content="Ficha técnica completa para pescaria de praia em alta distância.",
        content_type=PostContentType.EQUIPAMENTO,
        equipment_specification=EquipmentSpecificationInput(
            rod_length_m=4.5,
            rod_construction="tubular",
            reel_size=9000,
            main_line_material="monofilamento",
            main_line_diameter_mm=0.18,
            shock_leader_type="cônico",
            casting_weight_min_g=100,
            casting_weight_max_g=150,
        ),
    )

    assert payload.equipment_specification is not None
    assert payload.equipment_specification.rod_length_m == 4.5
    assert payload.equipment_specification.reel_size == 9000
    assert payload.equipment_specification.main_line_diameter_mm == 0.18


def test_invalid_casting_weight_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        EquipmentSpecificationInput(casting_weight_min_g=180, casting_weight_max_g=100)


def test_equipment_specification_is_restricted_to_equipment_content() -> None:
    with pytest.raises(ValidationError):
        PostCreate(
            title="Tutorial de arremesso pendular",
            content="Conteúdo técnico detalhado para executar o movimento com segurança.",
            content_type=PostContentType.TUTORIAL,
            equipment_specification=EquipmentSpecificationInput(reel_size=9000),
        )


def test_author_cannot_publish_without_admin_role() -> None:
    actor = Mock()
    actor.role.code = RoleCode.AUTHOR.value
    service = PostService(Mock())

    with pytest.raises(AuthorizationError):
        service._assert_can_publish(actor, PostStatus.PUBLICADO)


def test_fishing_point_contract_includes_access_and_risk_information() -> None:
    point = FishingPointCreate(
        name="  Canal de retorno norte  ",
        point_type=FishingPointType.CANAL_RETORNO,
        latitude=-22.93,
        longitude=-42.49,
        accessibility=AccessibilityLevel.MODERADA,
        access_notes="Acesso pela rua lateral.",
        risk_notes="Corrente forte na maré vazante.",
    )

    assert point.name == "Canal de retorno norte"
    assert point.risk_notes is not None


def test_public_post_does_not_expose_workflow_or_author_ids() -> None:
    assert "status" not in PublicPostResponse.model_fields
    assert "author_id" not in PublicPostResponse.model_fields
