from bson import ObjectId

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    HTTPException,
    Query
)

from passlib.context import CryptContext

from backend.database.db import (
    register_collection,
    analysis_history_collection,
    resource_requests_collection
)

from backend.models.register_model import (
    UpdateUserRequest
)


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# PUBLIC USER
# ============================================================

def public_user(doc):

    return {

        "id":
            str(
                doc["_id"]
            ),

        "username":
            doc.get(
                "username",
                ""
            ),

        "email":
            doc.get(
                "email",
                ""
            ),

        "role":
            doc.get(
                "role",
                "user"
            ),

        "created_at":
            (
                doc["created_at"].isoformat()
                if hasattr(
                    doc.get(
                        "created_at"
                    ),
                    "isoformat"
                )
                else str(
                    doc.get(
                        "created_at",
                        ""
                    )
                )
            )
    }


# ============================================================
# OBJECT ID
# ============================================================

def oid(value):

    try:

        return ObjectId(
            value
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid user id."
        )


# ============================================================
# USERS
# ============================================================

@router.get("/users")
async def users():

    result = []


    async for doc in (

        register_collection

        .find(
            {},
            {
                "password_hash": 0
            }
        )

        .sort(
            "created_at",
            -1
        )

    ):

        result.append(
            public_user(
                doc
            )
        )


    return {

        "success":
            True,

        "users":
            result,

        "total":
            len(result)
    }


# ============================================================
# ANALYSIS
# ============================================================

@router.get("/analysis")
async def analysis(

    limit: int = Query(
        default=100,
        ge=1,
        le=200
    )

):

    result = []


    # IMPORTANT:
    #
    # image_data is explicitly excluded.
    #
    # This prevents MongoDB binary image data from being
    # converted into a massive JSON response.
    #

    projection = {

        "image_data":
            0
    }


    cursor = (

        analysis_history_collection

        .find(
            {},
            projection
        )

        .sort(
            "created_at",
            -1
        )

        .limit(
            limit
        )

    )


    async for doc in cursor:

        result.append({

            "id":
                str(
                    doc["_id"]
                ),

            "email":
                doc.get(
                    "email",
                    ""
                ),

            "headline":
                doc.get(
                    "headline",
                    ""
                ),

            "image":
                doc.get(
                    "image_filename",
                    ""
                ),

            "image_url":
                (
                    "/api/analyze/image/"
                    + str(
                        doc["_id"]
                    )
                ),

            "disaster_type":
                doc.get(
                    "disaster_type",
                    "Unknown"
                ),

            "confidence":
                doc.get(
                    "confidence",
                    0
                ),

            "image_confidence":
                doc.get(
                    "image_confidence",
                    0
                ),

            "location":
                doc.get(
                    "location",
                    "Not detected"
                ),

            "status":
                doc.get(
                    "status",
                    "UNVERIFIED"
                ),

            "verification_confidence":
                doc.get(
                    "verification_confidence",
                    0
                ),

            "reason":
                doc.get(
                    "reason",
                    ""
                ),

            "evidence":
                doc.get(
                    "evidence",
                    []
                ),

            "created_at":
                (
                    doc["created_at"].isoformat()
                    if hasattr(
                        doc.get(
                            "created_at"
                        ),
                        "isoformat"
                    )
                    else str(
                        doc.get(
                            "created_at",
                            ""
                        )
                    )
                )
        })


    return {

        "success":
            True,

        "analysis":
            result,

        "total":
            len(result)
    }


# ============================================================
# RESOURCE REQUESTS
# ============================================================

@router.get("/resource-requests")
async def resource_requests(
    limit: int = Query(
        default=500,
        ge=1,
        le=1000
    )
):
    from backend.routes.resource_routes import public_resource_request

    cursor = (
        resource_requests_collection
        .find({})
        .sort("created_at", -1)
        .limit(limit)
    )
    result = [
        public_resource_request(document)
        async for document in cursor
    ]

    return {
        "success": True,
        "requests": result,
        "total": len(result)
    }


# ============================================================
# LOCAL BIG-DATA BATCH ANALYTICS PROTOTYPE
# ============================================================

async def collect_aggregation(collection, pipeline):
    return [
        row
        async for row in collection.aggregate(pipeline)
    ]


@router.get("/big-data/summary")
async def big_data_summary():
    analysis_total = await analysis_history_collection.count_documents({})
    resource_total = await resource_requests_collection.count_documents({})

    disaster_breakdown = await collect_aggregation(
        analysis_history_collection,
        [
            {
                "$group": {
                    "_id": {
                        "$ifNull": ["$disaster_type", "Unknown"]
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1, "_id": 1}},
            {"$limit": 20}
        ]
    )

    location_breakdown = await collect_aggregation(
        analysis_history_collection,
        [
            {
                "$group": {
                    "_id": {
                        "$ifNull": ["$location", "Not detected"]
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1, "_id": 1}},
            {"$limit": 20}
        ]
    )

    resource_breakdown = await collect_aggregation(
        resource_requests_collection,
        [
            {
                "$group": {
                    "_id": {
                        "disaster": {
                            "$ifNull": ["$disaster_type", "Unknown"]
                        },
                        "location": {
                            "$ifNull": ["$location", "Not detected"]
                        },
                        "resource_type": {
                            "$ifNull": ["$resource_type", "Other"]
                        }
                    },
                    "request_count": {"$sum": 1}
                }
            },
            {"$sort": {"request_count": -1, "_id.disaster": 1}},
            {"$limit": 50}
        ]
    )

    return {
        "success": True,
        "processing_mode": "MongoDB batch aggregation prototype",
        "infrastructure_note": (
            "Processes records currently stored in MongoDB. "
            "Hadoop, HDFS, and Spark are not configured."
        ),
        "processed_records": analysis_total + resource_total,
        "analysis_records": analysis_total,
        "resource_requests": resource_total,
        "disaster_breakdown": [
            {"name": row["_id"], "count": row["count"]}
            for row in disaster_breakdown
        ],
        "location_breakdown": [
            {"name": row["_id"], "count": row["count"]}
            for row in location_breakdown
        ],
        "resource_breakdown": [
            {
                "disaster_type": row["_id"]["disaster"],
                "location": row["_id"]["location"],
                "resource_type": row["_id"]["resource_type"],
                "request_count": row["request_count"]
            }
            for row in resource_breakdown
        ]
    }


# ============================================================
# UPDATE USER
# ============================================================

@router.put("/users/{user_id}")
async def update_user(

    user_id: str,

    payload: UpdateUserRequest

):

    user_oid = oid(
        user_id
    )


    current = await register_collection.find_one({

        "_id":
            user_oid

    })


    if not current:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )


    duplicate = await register_collection.find_one({

        "$or": [

            {
                "email":
                    str(
                        payload.email
                    ).lower()
            },

            {
                "username":
                    payload.username
            }

        ],

        "_id": {
            "$ne":
                user_oid
        }

    })


    if duplicate:

        raise HTTPException(
            status_code=409,
            detail=(
                "Another user already has "
                "that username or email."
            )
        )


    update = {

        "username":
            payload.username,

        "email":
            str(
                payload.email
            ).lower(),

        "role":
            payload.role,

        "updated_at":
            datetime.now(
                timezone.utc
            )
    }


    if payload.password:

        update[
            "password_hash"
        ] = pwd_context.hash(
            payload.password
        )


    await register_collection.update_one(

        {
            "_id":
                user_oid
        },

        {
            "$set":
                update
        }
    )


    updated = await register_collection.find_one(

        {
            "_id":
                user_oid
        },

        {
            "password_hash":
                0
        }
    )


    return {

        "success":
            True,

        "message":
            "User updated.",

        "user":
            public_user(
                updated
            )
    }


# ============================================================
# DELETE USER
# ============================================================

@router.delete("/users/{user_id}")
async def delete_user(

    user_id: str

):

    user_oid = oid(
        user_id
    )


    current = await register_collection.find_one({

        "_id":
            user_oid

    })


    if not current:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )


    if (
        current.get(
            "email",
            ""
        ).lower()
        == "mahip1234@gmail.com"
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "The configured admin "
                "account cannot be deleted."
            )
        )


    await register_collection.delete_one({

        "_id":
            user_oid

    })


    return {

        "success":
            True,

        "message":
            "User deleted."
    }