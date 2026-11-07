from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.db import resource_requests_collection


router = APIRouter(
    prefix="/api/resources",
    tags=["Resource Requests"]
)


class ResourceRequest(BaseModel):
    disaster_type: str = Field(min_length=1, max_length=80)
    location: str = Field(min_length=1, max_length=200)
    requester_name: str = Field(min_length=1, max_length=100)
    resource_name: str = Field(min_length=1, max_length=120)
    resource_details: str = Field(min_length=1, max_length=500)
    resource_type: str = Field(min_length=1, max_length=40)
    quantity: str = Field(min_length=1, max_length=80)


@router.post("/requests")
async def create_resource_request(request: ResourceRequest):
    created_at = datetime.now(timezone.utc)
    document = request.dict()
    text_fields = (
        "disaster_type",
        "location",
        "requester_name",
        "resource_name",
        "resource_details",
        "resource_type",
        "quantity",
    )
    for field in text_fields:
        document[field] = document[field].strip()
        if not document[field]:
            raise HTTPException(
                status_code=422,
                detail=f"{field.replace('_', ' ').capitalize()} is required."
            )

    document.update({
        "status": "requested",
        "created_at": created_at,
    })

    result = await resource_requests_collection.insert_one(document)

    return {
        "success": True,
        "message": "Resource request saved.",
        "request": {
            "id": str(result.inserted_id),
            **{field: document[field] for field in text_fields},
            "status": "requested",
            "created_at": created_at.isoformat(),
        }
    }


def public_resource_request(document: dict) -> dict:
    created_at = document.get("created_at", "")
    return {
        "id": str(document["_id"]),
        "disaster_type": document.get("disaster_type", ""),
        "location": document.get("location", ""),
        "requester_name": document.get("requester_name", ""),
        "resource_name": document.get("resource_name", ""),
        "resource_details": document.get("resource_details", ""),
        "resource_type": document.get("resource_type", ""),
        "quantity": document.get("quantity", ""),
        "status": document.get("status", "requested"),
        "created_at": (
            created_at.isoformat()
            if hasattr(created_at, "isoformat")
            else str(created_at)
        )
    }
