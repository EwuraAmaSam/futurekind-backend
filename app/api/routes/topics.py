from fastapi import APIRouter

from app.scenarios.topics import list_scenarios

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("")
def get_topics():
    return list_scenarios()
