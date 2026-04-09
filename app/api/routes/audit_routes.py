from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.infra.db.session import get_db
from app.domain.models.audit_log import AuditLog


router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/logs")
def get_logs(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "path": log.path,
            "method": log.method,
            "statusCode": log.status_code,
            "operatorId": log.operator_id,
            "message": log.message,
        }
        for log in logs
    ]
