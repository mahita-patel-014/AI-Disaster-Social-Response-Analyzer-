from motor.motor_asyncio import AsyncIOMotorClient

from backend.config import (
    MONGO_URI,
    MONGO_DB_NAME
)


# ============================================================
# MONGODB CONNECTION
# ============================================================

client = AsyncIOMotorClient(
    MONGO_URI
)

db = client[
    MONGO_DB_NAME
]


# ============================================================
# COLLECTIONS
# ============================================================

register_collection = db[
    "register"
]

analysis_history_collection = db[
    "analysis_history"
]

email_requests_collection = db[
    "email_requests"
]

resource_requests_collection = db[
    "resource_requests"
]


# IMPORTANT:
# Registration and login activity logs
register_logs_collection = db[
    "register_logs"
]



# ============================================================
# INDEXES
# ============================================================

async def ensure_indexes():

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    await register_collection.create_index(
        "email",
        unique=True
    )

    await register_collection.create_index(
        "username"
    )

    await register_collection.create_index(
        "role"
    )


    # --------------------------------------------------------
    # NEWS ANALYSIS
    # --------------------------------------------------------

    await analysis_history_collection.create_index(
        "email"
    )

    await analysis_history_collection.create_index(
        "created_at"
    )

    await analysis_history_collection.create_index(
        "disaster_type"
    )

    await analysis_history_collection.create_index(
        "location"
    )

    await email_requests_collection.create_index(
        "created_at"
    )

    await resource_requests_collection.create_index(
        "created_at"
    )


    # --------------------------------------------------------
    # REGISTRATION / LOGIN LOGS
    # --------------------------------------------------------

    await register_logs_collection.create_index(
        "email"
    )

    await register_logs_collection.create_index(
        "action"
    )

    await register_logs_collection.create_index(
        "created_at"
    )

    await register_logs_collection.create_index(
        "success"
    )

# ============================================================
# CLOSE DATABASE
# ============================================================

async def close_db():

    client.close()
