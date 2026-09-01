from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import require_roles
from app.models.enums import RoleCode
from app.models.user import User
from app.monitoring import monitoring_registry
from app.schemas.monitoring import MonitoringSummaryResponse


router = APIRouter(prefix="/admin/monitoring", tags=["Backoffice - Monitoramento"])
admin_dependency = require_roles(RoleCode.ADMIN)


@router.get("", response_model=MonitoringSummaryResponse)
def get_monitoring_summary(
    admin: Annotated[User, Depends(admin_dependency)],
) -> MonitoringSummaryResponse:
    del admin
    return MonitoringSummaryResponse.model_validate(monitoring_registry.snapshot())

