from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.config import (
    FRONTEND_ORIGINS
)

from backend.database.db import (
    ensure_indexes,
    close_db
)

from backend.routes.auth_routes import (
    router as auth_router,
    seed_admin
)

from backend.routes.admin_routes import (
    router as admin_router
)

from backend.routes.analyze_routes import (
    router as analyze_router
)

from backend.routes.response_routes import router as response_router
from backend.routes.email_routes import router as email_router
from backend.routes.resource_routes import router as resource_router


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    await ensure_indexes()

    await seed_admin()

    yield

    await close_db()


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(

    title="AI CP Disaster",

    description=(
        "Disaster image analysis, news verification, and emergency response."
    ),

    version="1.0.0",

    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================
app.add_middleware(

    CORSMiddleware,

    allow_origins=FRONTEND_ORIGINS,
    allow_origin_regex=r"http://(192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}):550[01]",

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)

# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    auth_router
)

app.include_router(
    admin_router
)

app.include_router(
    analyze_router
)

app.include_router(response_router)
app.include_router(email_router)
app.include_router(resource_router)

# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {

        "project":
            "ai_cp_disaster",

        "database":
            "ai_final_disaster",

        "message":
            "API is running"
    }
