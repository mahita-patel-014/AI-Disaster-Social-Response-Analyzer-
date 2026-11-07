from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from passlib.context import CryptContext

from backend.config import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    ADMIN_USERNAME
)

from backend.database.db import (
    register_collection,
    register_logs_collection
)

from backend.models.register_model import (
    RegisterRequest,
    LoginRequest
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# ============================================================
# PASSWORD
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# TIME
# ============================================================

def now():

    return datetime.now(
        timezone.utc
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
            doc["username"],

        "email":
            doc["email"],

        "role":
            doc["role"],

        "created_at":
            (
                doc["created_at"].isoformat()
                if hasattr(
                    doc["created_at"],
                    "isoformat"
                )
                else str(
                    doc["created_at"]
                )
            )
    }


# ============================================================
# WRITE REGISTRATION / LOGIN LOG
# ============================================================

async def write_log(
    action,
    username,
    email,
    role,
    success,
    message
):

    await register_logs_collection.insert_one({

        "action":
            action,

        "username":
            username,

        "email":
            email,

        "role":
            role,

        "success":
            success,

        "message":
            message,

        "created_at":
            now()
    })


# ============================================================
# SEED ADMIN
# ============================================================

async def seed_admin():

    if not all((ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)):
        raise RuntimeError(
            "Set ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD in the project-root .env."
        )

    existing = await register_collection.find_one({

        "email":
            ADMIN_EMAIL
    })


    if not existing:

        await register_collection.insert_one({

            "username":
                ADMIN_USERNAME,

            "email":
                ADMIN_EMAIL,

            "password_hash":
                pwd_context.hash(
                    ADMIN_PASSWORD
                ),

            "role":
                "admin",

            "created_at":
                now(),

            "updated_at":
                now()
        })

        print(
            "Default admin account created."
        )


# ============================================================
# REGISTER
# ============================================================

@router.post("/register")
async def register(
    payload: RegisterRequest
):

    # --------------------------------------------------------
    # PASSWORD CONFIRMATION
    # --------------------------------------------------------

    if (
        payload.password
        != payload.confirm_password
    ):

        await write_log(

            "register",

            payload.username,

            str(
                payload.email
            ),

            payload.role,

            False,

            "Passwords do not match"
        )


        raise HTTPException(

            status_code=400,

            detail="Passwords do not match."
        )


    # --------------------------------------------------------
    # ADMIN VALIDATION
    # --------------------------------------------------------

    if payload.role == "admin":

        if (

            payload.username
            != ADMIN_USERNAME

            or

            str(
                payload.email
            ).lower()
            != ADMIN_EMAIL.lower()

            or

            payload.password
            != ADMIN_PASSWORD

        ):

            await write_log(

                "register",

                payload.username,

                str(
                    payload.email
                ),

                "admin",

                False,

                "Invalid admin credentials"
            )


            raise HTTPException(

                status_code=403,

                detail=(
                    "Invalid admin credentials. "
                    "Use the configured admin "
                    "username, email and password."
                )
            )


    # --------------------------------------------------------
    # CHECK EXISTING USER
    # --------------------------------------------------------

    existing = await register_collection.find_one({

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

        ]

    })


    # --------------------------------------------------------
    # EXISTING USER
    # --------------------------------------------------------

    if existing:

        # ----------------------------------------------------
        # EXISTING ADMIN
        # ----------------------------------------------------

        if (

            payload.role == "admin"

            and

            existing.get(
                "email",
                ""
            ).lower()
            == ADMIN_EMAIL.lower()

            and

            existing.get(
                "username"
            )
            == ADMIN_USERNAME

        ):

            await write_log(

                "register",

                payload.username,

                str(
                    payload.email
                ),

                "admin",

                True,

                "Admin account reused"
            )


            return {

                "success":
                    True,

                "message":
                    "Admin verified.",

                "user":
                    public_user(
                        existing
                    ),

                "redirect":
                    "admin_dashboard.html"
            }


        # ----------------------------------------------------
        # DUPLICATE USER
        # ----------------------------------------------------

        await write_log(

            "register",

            payload.username,

            str(
                payload.email
            ),

            payload.role,

            False,

            "Username or email already exists"
        )


        raise HTTPException(

            status_code=409,

            detail=(
                "Username or email already exists."
            )
        )


    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    doc = {

        "username":
            payload.username,

        "email":
            str(
                payload.email
            ).lower(),

        "password_hash":
            pwd_context.hash(
                payload.password
            ),

        "role":
            payload.role,

        "created_at":
            now(),

        "updated_at":
            now()
    }


    # --------------------------------------------------------
    # SAVE USER
    # --------------------------------------------------------

    result = await register_collection.insert_one(
        doc
    )


    doc["_id"] = result.inserted_id


    # --------------------------------------------------------
    # SAVE REGISTER LOG
    # --------------------------------------------------------

    await write_log(

        "register",

        payload.username,

        str(
            payload.email
        ).lower(),

        payload.role,

        True,

        "Registration successful"
    )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "success":
            True,

        "message":
            "Registration successful.",

        "user":
            public_user(
                doc
            ),

        "redirect":
            (
                "admin_dashboard.html"

                if payload.role == "admin"

                else "user_dashboard.html"
            )
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
async def login(
    payload: LoginRequest
):

    doc = await register_collection.find_one({

        "email":
            str(
                payload.email
            ).lower()

    })


    # --------------------------------------------------------
    # INVALID LOGIN
    # --------------------------------------------------------

    if (

        not doc

        or

        not pwd_context.verify(

            payload.password,

            doc[
                "password_hash"
            ]
        )

    ):

        await write_log(

            "login",

            "",

            str(
                payload.email
            ).lower(),

            "",

            False,

            "Invalid email or password"
        )


        raise HTTPException(

            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Invalid email or password."
        )


    # --------------------------------------------------------
    # SUCCESSFUL LOGIN
    # --------------------------------------------------------

    await write_log(

        "login",

        doc["username"],

        doc["email"],

        doc["role"],

        True,

        "Login successful"
    )


    return {

        "success":
            True,

        "message":
            "Login successful.",

        "user":
            public_user(
                doc
            )
    }


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
async def health():

    await register_collection.find_one(

        {},

        {
            "_id": 1
        }
    )


    return {

        "status":
            "ok",

        "database":
            "ai_final_disaster"
    }