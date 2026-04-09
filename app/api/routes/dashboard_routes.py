from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infra.db.session import get_db
from app.domain.services.dashboard_service import DashboardService


router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
dashboard_service = DashboardService()


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return dashboard_service.overview(db)
