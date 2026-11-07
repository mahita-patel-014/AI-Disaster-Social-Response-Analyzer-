from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Form,
    HTTPException
)

from backend.models.disaster_model import (
    predict_disaster
)

from backend.database.db import (
    analysis_history_collection
)

from transformers import pipeline

import requests
import xml.etree.ElementTree as ET

from difflib import SequenceMatcher

from datetime import datetime, timezone

import re

from urllib.parse import quote_plus


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/analyze",
    tags=["AI Analysis"]
)


# ============================================================
# GOOGLE NEWS SETTINGS
# ============================================================

GOOGLE_NEWS_URL = (
    "https://news.google.com/rss/search"
)


# ============================================================
# LOCATION NER
# ============================================================

try:

    location_ner = pipeline(
        "token-classification",
        model="dslim/bert-base-NER",
        aggregation_strategy="simple"
    )

    print(
        "Location NER model loaded successfully."
    )

except Exception as error:

    print(
        "Location NER model loading failed:",
        error
    )

    location_ner = None


# ============================================================
# DISASTER KEYWORDS
# ============================================================

DISASTER_KEYWORDS = {

    "earthquake": [
        "earthquake",
        "earthquakes",
        "quake",
        "tremor",
        "seismic"
    ],

    "flood": [
        "flood",
        "flooding",
        "flash flood",
        "floods",
        "inundation"
    ],

    "fire": [
        "fire",
        "wildfire",
        "forest fire",
        "blaze",
        "burning"
    ],

    "cyclone": [
        "cyclone",
        "hurricane",
        "typhoon",
        "storm"
    ],

    "landslide": [
        "landslide",
        "landslides",
        "mudslide",
        "mudslides",
        "rockslide",
        "rockslides"
    ],

    "drought": [
        "drought",
        "water shortage",
        "dry spell"
    ]

}


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(headline: str):

    if not headline:
        return "Not detected"

    headline = headline.strip()

    if not headline:
        return "Not detected"

    locations = []


    # ========================================================
    # METHOD 1
    # BERT NER
    # ========================================================

    if location_ner is not None:

        try:

            entities = location_ner(
                headline
            )

            for entity in entities:

                entity_group = str(
                    entity.get(
                        "entity_group",
                        ""
                    )
                ).upper()

                word = str(
                    entity.get(
                        "word",
                        ""
                    )
                ).strip()

                if (
                    entity_group in {
                        "LOC",
                        "GPE"
                    }
                    and word
                ):

                    locations.append(
                        word
                    )

        except Exception as error:

            print(
                "NER location error:",
                repr(error)
            )


    # ========================================================
    # METHOD 2
    # COMMON NEWS PHRASES
    # ========================================================

    patterns = [
        r"\b(?:in|at|near|from|of)\s+"
        r"([A-Z][A-Za-z'-]*(?:\s+[A-Z][A-Za-z'-]*){0,3})",
        r"\b([A-Z][a-z'-]+(?:\s+[A-Z][a-z'-]+){1,3})\b"
    ]


    for pattern in patterns:

        matches = re.findall(
            pattern,
            headline
        )

        for match in matches:

            cleaned = (
                match
                .strip()
                .rstrip(".,:;!?")
            )

            cleaned = re.split(
                r"\s+(?:on|at|during|before|after|today|yesterday|"
                r"amid|following|once again|as|hit|struck|claiming|leaving)\b",
                cleaned,
                maxsplit=1,
                flags=re.IGNORECASE
            )[0].strip()

            if (
                len(cleaned) >= 3
                and cleaned not in locations
            ):

                locations.append(
                    cleaned
                )


    # ========================================================
    # CLEAN LOCATIONS
    # ========================================================

    cleaned_locations = []

    for location in locations:

        location = (
            location
            .strip()
            .replace("##", "")
        )

        location = re.split(
            r"\s+(?:on|at|during|before|after|today|yesterday|"
            r"amid|following|once again|as|hit|struck|claiming|leaving)\b",
            location,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0].strip()

        if not location:
            continue

        exists = False

        for existing in cleaned_locations:

            if (
                existing.lower()
                == location.lower()
            ):

                exists = True
                break

        if not exists:

            cleaned_locations.append(
                location
            )


    if cleaned_locations:

        cleaned_locations.sort(
            key=lambda location: headline.lower().find(location.lower())
        )

        return ", ".join(
            cleaned_locations[:3]
        )

    return "Not detected"


# ============================================================
# DETECT DISASTER FROM HEADLINE
# ============================================================

def detect_headline_disaster(
    headline: str
):

    text = headline.lower()

    scores = {}

    for disaster, keywords in (
        DISASTER_KEYWORDS.items()
    ):

        score = 0

        for keyword in keywords:

            score += len(
                re.findall(
                    rf"(?<!\w){re.escape(keyword)}(?!\w)",
                    text
                )
            )

        scores[disaster] = score


    if not scores:

        return None


    best_disaster = max(
        scores,
        key=scores.get
    )


    if scores[best_disaster] == 0:

        return None


    return best_disaster


# ============================================================
# TOKENIZE
# ============================================================

def tokenize(text: str):

    return set(
        re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )
    )


# ============================================================
# TEXT SIMILARITY
# ============================================================

def calculate_similarity(
    headline: str,
    article_title: str
):

    headline_clean = (
        headline
        .lower()
        .strip()
    )

    article_clean = (
        article_title
        .lower()
        .strip()
    )


    sequence_score = (
        SequenceMatcher(
            None,
            headline_clean,
            article_clean
        ).ratio()
        * 100
    )


    headline_words = tokenize(
        headline_clean
    )

    article_words = tokenize(
        article_clean
    )


    if headline_words:

        overlap_score = (
            len(
                headline_words
                & article_words
            )
            /
            len(headline_words)
        ) * 100

    else:

        overlap_score = 0


    final_score = (
        sequence_score * 0.45
        +
        overlap_score * 0.55
    )


    return round(
        final_score,
        2
    )


# ============================================================
# GOOGLE NEWS SEARCH
# ============================================================

def search_google_news(
    headline: str,
    disaster_type: str = None,
    location: str = None
):

    query_parts = []

    if disaster_type:

        query_parts.append(
            disaster_type
        )


    if (
        location
        and location != "Not detected"
    ):

        query_parts.append(
            location
        )

    if not query_parts and headline:

        query_parts.append(
            headline
        )


    query = " ".join(
        query_parts
    )


    encoded_query = quote_plus(
        query
    )


    url = (
        f"{GOOGLE_NEWS_URL}"
        f"?q={encoded_query}"
        f"&hl=en-IN"
        f"&gl=IN"
        f"&ceid=IN:en"
    )


    try:

        response = requests.get(

            url,

            timeout=15,

            headers={
                "User-Agent":
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/120 Safari/537.36"
            }
        )

        response.raise_for_status()


    except Exception as error:

        print(
            "Google News request failed:",
            repr(error)
        )

        return []


    try:

        root = ET.fromstring(
            response.content
        )

    except Exception as error:

        print(
            "Google News XML error:",
            repr(error)
        )

        return []


    evidence = []


    for item in root.findall(
        ".//item"
    ):

        title_element = item.find(
            "title"
        )

        link_element = item.find(
            "link"
        )

        pub_element = item.find(
            "pubDate"
        )

        source_element = item.find(
            "source"
        )


        title = (
            title_element.text
            if title_element is not None
            else ""
        )


        link = (
            link_element.text
            if link_element is not None
            else ""
        )


        published = (
            pub_element.text
            if pub_element is not None
            else ""
        )


        source = (
            source_element.text
            if source_element is not None
            else "Google News"
        )


        if not title:

            continue


        similarity = (
            calculate_similarity(
                headline,
                title
            )
        )


        evidence.append({

            "title":
                title.strip(),

            "source":
                source.strip(),

            "published":
                published.strip(),

            "url":
                link.strip(),

            "similarity":
                similarity

        })


    evidence.sort(

        key=lambda item:
            item["similarity"],

        reverse=True

    )


    return evidence[:10]


# ============================================================
# VERIFY NEWS
# ============================================================

def verify_news(
    headline: str,
    disaster_type: str,
    location: str
):

    evidence = search_google_news(

        headline=headline,

        disaster_type=disaster_type,

        location=location

    )


    if not evidence:

        return {

            "status":
                "UNVERIFIED",

            "verification_confidence":
                0,

            "reason":
                "No matching current news evidence was found.",

            "evidence":
                []

        }


    best_match = evidence[0]

    best_similarity = float(
        best_match["similarity"]
    )


    if best_similarity >= 70:

        status = "REAL"

        verification_confidence = min(
            98,
            round(
                best_similarity,
                2
            )
        )

        reason = (
            "Strong matching news evidence "
            "was found in Google News."
        )


    elif best_similarity >= 45:

        status = "UNVERIFIED"

        verification_confidence = round(
            best_similarity,
            2
        )

        reason = (
            "Related news was found, but the "
            "available evidence is not strong "
            "enough to confirm the headline."
        )


    else:

        status = "UNVERIFIED"

        verification_confidence = round(
            best_similarity,
            2
        )

        reason = (
            "Search results were found, but "
            "they do not strongly match the "
            "submitted headline."
        )


    return {

        "status":
            status,

        "verification_confidence":
            verification_confidence,

        "headline_match_score":
            verification_confidence,

        "verification_score_type":
            "headline_match_score",

        "reason":
            reason,

        "evidence":
            evidence

    }


# ============================================================
# SAVE ANALYSIS TO MONGODB
# ============================================================

async def save_analysis_to_mongodb(

    filename: str,
    headline: str,
    prediction: dict,
    location: str,
    verification: dict,
    email: str = ""

):

    disaster_type = prediction.get(
        "disaster_type",
        "Unknown"
    )


    confidence = float(
        prediction.get(
            "confidence",
            0
        )
    )


    verification_confidence = float(
        verification.get(
            "verification_confidence",
            0
        )
    )


    document = {

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        "email":
            email,

        # ----------------------------------------------------
        # NEWS
        # ----------------------------------------------------

        "headline":
            headline,

        "image_filename":
            filename,

        # ----------------------------------------------------
        # AI DISASTER RESULT
        # ----------------------------------------------------

        "disaster_type":
            disaster_type,

        "confidence":
            confidence,

        "image_confidence":
            confidence,

        "predictions":
            prediction.get(
                "predictions",
                []
            ),

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        "location":
            location,

        # ----------------------------------------------------
        # VERIFICATION
        # ----------------------------------------------------

        "status":
            verification.get(
                "status",
                "UNVERIFIED"
            ),

        "verification_confidence":
            verification_confidence,

        "reason":
            verification.get(
                "reason",
                ""
            ),

        # ----------------------------------------------------
        # GOOGLE NEWS EVIDENCE
        # ----------------------------------------------------

        "evidence":
            verification.get(
                "evidence",
                []
            ),

        "evidence_count":
            len(
                verification.get(
                    "evidence",
                    []
                )
            ),

                    # ----------------------------------------------------
        # EMERGENCY RESPONSE
        # ----------------------------------------------------

        "situation_assessment": [],

        "emergency_response": [],

        "response_generated": False,

        "response_generated_at": None,

        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        "created_at":
            datetime.now(
                timezone.utc
            )

    }


    try:

        result = await (
            analysis_history_collection.insert_one(
                document
            )
        )


        print(
            "\n========================================"
        )

        print(
            "ANALYSIS SAVED TO MONGODB"
        )

        print(
            "MongoDB ID:",
            result.inserted_id
        )

        print(
            "Disaster:",
            disaster_type
        )

        print(
            "Location:",
            location
        )

        print(
            "Status:",
            verification.get(
                "status"
            )
        )

        print(
            "========================================\n"
        )


        return str(
            result.inserted_id
        )


    except Exception as error:

        print(
            "MONGODB SAVE ERROR:",
            repr(error)
        )

        # Do NOT fail the complete analysis
        # if database saving has a temporary error.

        return None


# ============================================================
# ANALYZE NEWS
# ============================================================

@router.post("/news")
async def analyze_news(

    image: UploadFile = File(...),

    headline: str = Form(""),

    email: str = Form("")

):

    # ========================================================
    # VALIDATE IMAGE
    # ========================================================

    if not image.filename:

        raise HTTPException(
            status_code=400,
            detail="Please select an image."
        )


    allowed_types = {

        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/bmp"

    }


    if (
        image.content_type
        and image.content_type
        not in allowed_types
    ):

        raise HTTPException(
            status_code=400,
            detail="Unsupported image format."
        )


    # ========================================================
    # READ IMAGE
    # ========================================================

    image_bytes = await image.read()


    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )


    # ========================================================
    # IMAGE SIZE
    # ========================================================

    if len(image_bytes) > 10 * 1024 * 1024:

        raise HTTPException(
            status_code=400,
            detail="Image must be below 10 MB."
        )


    # ========================================================
    # DISASTER MODEL
    # ========================================================

    try:

        prediction = predict_disaster(
            image_bytes
        )


    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    except RuntimeError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    except Exception as error:

        print(
            "DISASTER MODEL ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Disaster model failed."
        )


    # ========================================================
    # DISASTER RESULT
    # ========================================================

    disaster_type = (
        prediction
        .get(
            "disaster_type",
            "Unknown"
        )
    )


    disaster_confidence = float(
        prediction
        .get(
            "confidence",
            0
        )
    )


    # ========================================================
    # HEADLINE
    # ========================================================

    clean_headline = (
        headline
        .strip()
    )


    # ========================================================
    # LOCATION
    # ========================================================

    location = extract_location(
        clean_headline
    )


    # ========================================================
    # HEADLINE DISASTER
    # ========================================================

    headline_disaster = (
        detect_headline_disaster(
            clean_headline
        )
    )

    image_disaster_type = disaster_type

    if headline_disaster:
        prediction["disaster_type"] = headline_disaster
        prediction["image_model_disaster_type"] = image_disaster_type

        if image_disaster_type.lower() != headline_disaster:
            prediction["disaster_type_note"] = (
                f"Disaster type was identified from the headline. "
                f"The image model predicted {image_disaster_type} "
                f"with {disaster_confidence:.1f}% confidence."
            )

        disaster_type = headline_disaster


    # ========================================================
    # GOOGLE NEWS VERIFICATION
    # ========================================================

    verification = verify_news(

        headline=clean_headline,

        disaster_type=(
            headline_disaster
            or disaster_type
        ),

        location=location

    )


    # ========================================================
    # SAVE TO MONGODB
    # ========================================================

    analysis_id = (
        await save_analysis_to_mongodb(

            filename=image.filename,

            headline=clean_headline,

            prediction=prediction,

            location=location,

            verification=verification,

            email=email

        )
    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "success":
            True,

        "analysis_id":
            analysis_id,

        "filename":
            image.filename,

        "headline":
            clean_headline,

        "disaster_type":
            disaster_type,

        "confidence":
            prediction.get("confidence", 0),

        "image_confidence":
            prediction.get("confidence", 0),

        "location":
            location,

        "disaster":
            prediction,

        "status":
            verification[
                "status"
            ],

        "verification_confidence":
            verification[
                "verification_confidence"
            ],

        "headline_match_score":
            verification[
                "verification_confidence"
            ],

        "verification_score_type":
            verification.get(
                "verification_score_type",
                "headline_match_score",
            ),

        "reason":
            verification[
                "reason"
            ],

        "evidence":
            verification[
                "evidence"
            ],

        "evidence_count":
            len(verification["evidence"]),

        "saved_to_database":
            analysis_id is not None

    }