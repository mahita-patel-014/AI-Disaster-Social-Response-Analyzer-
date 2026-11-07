from datetime import datetime


def create_analysis_document(
    email,
    headline,
    disaster_type,
    location,
    verification
):

    return {

        "email":
            email,

        "headline":
            headline,

        "disaster_type":
            disaster_type,

        "location":
            location,

        "status":
            verification[
                "status"
            ],

        "confidence":
            verification[
                "confidence"
            ],

        "reason":
            verification[
                "reason"
            ],

        "evidence":
            verification[
                "results"
            ],

        "created_at":
            datetime.utcnow()

    }