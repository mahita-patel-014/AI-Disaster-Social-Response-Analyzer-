import re


# ============================================================
# OPTIONAL NER
# ============================================================

try:

    from transformers import pipeline

    location_ner = pipeline(
        "token-classification",
        model="dslim/bert-base-NER",
        aggregation_strategy="simple"
    )

except Exception as error:

    print(
        "Location NER unavailable:",
        error
    )

    location_ner = None


# ============================================================
# COMMON LOCATIONS
# ============================================================

KNOWN_LOCATIONS = [

    # Countries
    "India",
    "Nepal",
    "Pakistan",
    "Bangladesh",
    "Sri Lanka",
    "China",
    "Japan",
    "Indonesia",
    "Philippines",
    "Australia",
    "United States",
    "USA",
    "United Kingdom",
    "UK",
    "Canada",
    "Brazil",
    "Turkey",
    "Afghanistan",
    "Myanmar",
    "Thailand",

    # Indian states/cities
    "Gujarat",
    "Maharashtra",
    "Rajasthan",
    "Punjab",
    "Haryana",
    "Assam",
    "Bihar",
    "Kerala",
    "Odisha",
    "West Bengal",
    "Uttar Pradesh",
    "Madhya Pradesh",
    "Tamil Nadu",
    "Karnataka",
    "Delhi",
    "Mumbai",
    "Ahmedabad",
    "Surat",
    "Vadodara",
    "Chennai",
    "Kolkata",
    "Bengaluru",
    "Hyderabad",
    "Pune",
    "Jaipur",
    "Patna",
    "Guwahati",

    # Nepal
    "Kathmandu",
    "Pokhara",
    "Lalitpur",
    "Bhaktapur",

    # Other major locations
    "New York",
    "California",
    "Texas",
    "London",
    "Paris",
    "Tokyo",
    "Beijing",
    "Sydney",
    "Jakarta",
    "Manila"
]


# ============================================================
# LOCATION EXTRACTION
# ============================================================

def extract_location(
    headline: str
):

    if not headline:

        return "Not detected"

    text = headline.strip()

    if not text:

        return "Not detected"


    locations = []


    # ========================================================
    # 1. KNOWN LOCATION MATCH
    # ========================================================

    lower_text = text.lower()

    for location in KNOWN_LOCATIONS:

        pattern = (
            r"\b"
            + re.escape(
                location.lower()
            )
            + r"\b"
        )

        if re.search(
            pattern,
            lower_text
        ):

            locations.append(
                location
            )


    # ========================================================
    # 2. NER
    # ========================================================

    if location_ner is not None:

        try:

            entities = location_ner(
                text
            )

            for entity in entities:

                group = str(
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
                    group in {
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
                error
            )


    # ========================================================
    # 3. REMOVE DUPLICATES
    # ========================================================

    cleaned = []

    seen = set()

    for location in locations:

        normalized = (
            location
            .strip()
            .lower()
        )

        if (
            normalized
            and normalized not in seen
        ):

            seen.add(
                normalized
            )

            cleaned.append(
                location.strip()
            )


    if cleaned:

        return ", ".join(
            cleaned
        )


    return "Not detected"