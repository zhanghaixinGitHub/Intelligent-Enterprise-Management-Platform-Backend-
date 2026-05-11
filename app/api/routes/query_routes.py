from uuid import uuid4
from fastapi import APIRouter, Depends

from app.ai.nl2query.query_executor import QueryExecutor
from app.api.dependencies.security import CurrentUserContext, get_current_user
from app.api.schemas.common import DataQueryRequest


router = APIRouter(prefix="/api/v1/query", tags=["query"])
query_executor = QueryExecutor()


@router.post("/ask")
def ask_data(payload: DataQueryRequest, current_user: CurrentUserContext = Depends(get_current_user)):
    result = query_executor.run(payload.question)
    return {
        "queryId": str(uuid4()),
        "status": result["status"],
        "summary": result["summary"],
        "data": result["data"],
        "employeeId": current_user.employeeId,
    }
