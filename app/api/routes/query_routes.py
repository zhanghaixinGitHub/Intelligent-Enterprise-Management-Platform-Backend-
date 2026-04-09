from uuid import uuid4
from fastapi import APIRouter

from app.ai.nl2query.query_executor import QueryExecutor
from app.api.schemas.common import DataQueryRequest


router = APIRouter(prefix="/api/v1/query", tags=["query"])
query_executor = QueryExecutor()


@router.post("/ask")
def ask_data(payload: DataQueryRequest):
    result = query_executor.run(payload.question)
    return {
        "queryId": str(uuid4()),
        "status": result["status"],
        "summary": result["summary"],
        "data": result["data"],
    }
