from typing import Optional
from urllib.parse import quote_plus

from fastapi import (
    APIRouter,
    HTTPException
)

from pydantic import BaseModel

from backend.services.response_service import (
    generate_emergency_response
)


router = APIRouter(
    prefix="/api/response",
    tags=["Emergency Response"]
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ResponseRequest(BaseModel):

    status: str

    disaster_type: Optional[str] = ""

    location: Optional[str] = ""


# ============================================================
# GOOGLE MAPS URL
# ============================================================

def generate_google_maps_url(
    location: str
):

    if not location:
        return None

    location = str(
        location
    ).strip()

    if not location:
        return None

    invalid_locations = [
        "not detected",
        "unknown",
        "none",
        "--",
        "n/a",
        "null",
        "undefined",
        "affected area"
    ]

    if location.lower() in invalid_locations:
        return None

    encoded_location = quote_plus(
        location
    )

    return (
        "https://www.google.com/maps/search/"
        "?api=1"
        f"&query={encoded_location}"
    )


# ============================================================
# GENERATE RESPONSE
# ============================================================

@router.post("/generate")
async def generate_response(
    request: ResponseRequest
):

    # --------------------------------------------------------
    # ONLY REAL NEWS
    # --------------------------------------------------------

    status = (
        request.status
        or ""
    ).strip().upper()

    if status != "REAL":

        raise HTTPException(
            status_code=400,
            detail=(
                "Emergency response can only "
                "be generated for REAL news."
            )
        )


    # --------------------------------------------------------
    # DISASTER TYPE
    # --------------------------------------------------------

    disaster_type = (
        request.disaster_type
        or ""
    ).strip()

    if not disaster_type:

        raise HTTPException(
            status_code=400,
            detail="Disaster type is required."
        )


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    location = (
        request.location
        or ""
    ).strip()


    # --------------------------------------------------------
    # GOOGLE MAPS
    # --------------------------------------------------------

    google_maps_url = (
        generate_google_maps_url(
            location
        )
    )


    # --------------------------------------------------------
    # GENERATE EMERGENCY RESPONSE
    # --------------------------------------------------------

    try:

        result = generate_emergency_response(
            disaster_type=disaster_type,
            location=location
        )

    except Exception as error:

        print(
            "Response generation error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Emergency response generation failed."
            )
        )


    # --------------------------------------------------------
    # SAFETY FALLBACK
    # --------------------------------------------------------

    if not isinstance(
        result,
        dict
    ):

        result = {
            "success": True,
            "response": result
        }


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    result["location"] = location

    result[
        "google_maps_url"
    ] = google_maps_url


    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    disaster_map = result.get(
        "map"
    )


    # --------------------------------------------------------
    # LOCATION STATUS
    # --------------------------------------------------------

    if (
        isinstance(
            disaster_map,
            dict
        )
        and disaster_map.get(
            "enabled"
        ) is True
    ):

        result[
            "location_status"
        ] = (
            "Location successfully "
            "detected and mapped."
        )

    elif google_maps_url:

        result[
            "location_status"
        ] = (
            "Location detected, but exact "
            "map coordinates could not be resolved."
        )

    else:

        result[
            "location_status"
        ] = (
            "No specific location "
            "was detected."
        )


    # --------------------------------------------------------
    # PRESERVE SERVICE MAP
    # --------------------------------------------------------

    if isinstance(
        disaster_map,
        dict
    ):

        disaster_map[
            "google_maps_url"
        ] = google_maps_url

        result[
            "map"
        ] = disaster_map


    # --------------------------------------------------------
    # MAP NOTICE
    # --------------------------------------------------------

    result[
        "map_notice"
    ] = (
        "The highlighted affected zone "
        "is an AI estimated planning area "
        "based on the detected disaster type "
        "and location. It is not an exact "
        "real-time disaster boundary."
    )


    # --------------------------------------------------------
    # NO DATABASE SAVING
    # --------------------------------------------------------

    result[
        "saved_to_database"
    ] = False

    result[
        "response_id"
    ] = None


    return result