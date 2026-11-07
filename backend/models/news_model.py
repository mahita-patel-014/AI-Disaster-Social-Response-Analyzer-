from backend.services.disaster_classifier import (
    detect_disaster_type
)


def analyze_headline(headline):

    disaster_type = detect_disaster_type(
        headline
    )

    return {
        "disaster_type": disaster_type
    }