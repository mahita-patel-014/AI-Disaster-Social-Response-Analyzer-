import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from datetime import datetime, timezone


# ============================================================
# GOOGLE NEWS
# ============================================================

GOOGLE_NEWS_URL = (
    "https://news.google.com/rss/search?"
    "q={query}&"
    "hl=en-IN&"
    "gl=IN&"
    "ceid=IN:en"
)


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(value):

    if not value:
        return ""

    value = re.sub(
        r"\s+",
        " ",
        str(value)
    )

    return value.strip()


# ============================================================
# NORMALIZE
# ============================================================

def normalize_text(value):

    value = clean_text(
        value
    ).lower()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# HEADLINE KEYWORDS
# ============================================================

STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "has",
    "have",
    "had",
    "this",
    "that",
    "of",
    "to",
    "in",
    "on",
    "for",
    "and",
    "or",
    "with",
    "from",
    "by",
    "after",
    "before",
    "news",
    "latest",
    "breaking"
}


def keywords(text):

    words = normalize_text(
        text
    ).split()

    return [
        word
        for word in words
        if (
            len(word) >= 3
            and word not in STOP_WORDS
        )
    ]


# ============================================================
# XML TEXT
# ============================================================

def xml_text(
    parent,
    tag
):

    element = parent.find(
        tag
    )

    if element is None:

        return ""

    return clean_text(
        element.text
    )


# ============================================================
# GOOGLE NEWS SEARCH
# ============================================================

def search_google_news(
    headline,
    disaster_type=None,
    location=None,
    limit=10
):

    headline = clean_text(
        headline
    )

    if not headline:

        return []


    # --------------------------------------------------------
    # Build search query
    # --------------------------------------------------------

    search_parts = []

    # Important headline keywords
    headline_words = keywords(
        headline
    )

    if headline_words:

        search_parts.extend(
            headline_words[:8]
        )


    if disaster_type:

        disaster_word = clean_text(
            disaster_type
        )

        if disaster_word:

            search_parts.append(
                disaster_word
            )


    if location:

        location_text = clean_text(
            location
        )

        if (
            location_text
            and
            location_text.lower()
            != "not detected"
        ):

            search_parts.append(
                location_text
            )


    # Remove duplicates
    query_words = []

    for word in search_parts:

        if word.lower() not in [
            x.lower()
            for x in query_words
        ]:

            query_words.append(
                word
            )


    query = " ".join(
        query_words
    )


    if not query:

        query = headline


    # --------------------------------------------------------
    # Google News RSS
    # --------------------------------------------------------

    encoded_query = urllib.parse.quote_plus(
        query
    )

    url = GOOGLE_NEWS_URL.format(
        query=encoded_query
    )


    try:

        request = urllib.request.Request(

            url,

            headers={
                "User-Agent":
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
            }

        )


        with urllib.request.urlopen(
            request,
            timeout=8
        ) as response:

            xml_data = response.read()


    except Exception as error:

        print(
            "Google News search error:",
            repr(error)
        )

        return []


    # --------------------------------------------------------
    # Parse XML
    # --------------------------------------------------------

    try:

        root = ET.fromstring(
            xml_data
        )

    except Exception as error:

        print(
            "Google News XML error:",
            repr(error)
        )

        return []


    results = []


    for item in root.findall(
        ".//item"
    )[:limit]:

        title = xml_text(
            item,
            "title"
        )

        link = xml_text(
            item,
            "link"
        )

        published = xml_text(
            item,
            "pubDate"
        )

        source_element = item.find(
            "source"
        )

        source = ""

        if source_element is not None:

            source = clean_text(
                source_element.text
            )


        if not title:

            continue


        # ----------------------------------------------------
        # Similarity
        # ----------------------------------------------------

        similarity = calculate_similarity(
            headline,
            title
        )


        results.append({

            "title":
                title,

            "source":
                source or "Google News",

            "url":
                link,

            "published":
                published,

            "similarity":
                round(
                    similarity,
                    2
                )

        })


    return results


# ============================================================
# TEXT SIMILARITY
# ============================================================

def calculate_similarity(
    submitted,
    source_title
):

    submitted_words = set(
        keywords(
            submitted
        )
    )

    source_words = set(
        keywords(
            source_title
        )
    )


    if not submitted_words:

        return 0.0


    if not source_words:

        return 0.0


    intersection = (
        submitted_words
        &
        source_words
    )


    # Jaccard-like score
    union = (
        submitted_words
        |
        source_words
    )


    if not union:

        return 0.0


    score = (
        len(intersection)
        /
        len(union)
    ) * 100


    return score


# ============================================================
# VERIFY NEWS
# ============================================================

def verify_news(
    headline,
    disaster_type,
    location
):

    evidence = search_google_news(

        headline=headline,

        disaster_type=disaster_type,

        location=location,

        limit=10
    )


    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    if not evidence:

        return {

            "status":
                "UNVERIFIED",

            "verification_confidence":
                0,

            "reason":
                "No matching current Google News "
                "sources were found.",

            "evidence":
                []

        }


    # --------------------------------------------------------
    # Sort strongest matches first
    # --------------------------------------------------------

    evidence.sort(

        key=lambda item:
            item.get(
                "similarity",
                0
            ),

        reverse=True
    )


    # --------------------------------------------------------
    # Strong evidence
    # --------------------------------------------------------

    strong_matches = [

        item
        for item in evidence
        if item.get(
            "similarity",
            0
        ) >= 30

    ]


    # --------------------------------------------------------
    # Calculate verification confidence
    # --------------------------------------------------------

    if len(strong_matches) >= 3:

        status = "REAL"

        verification_confidence = 90


    elif len(strong_matches) == 2:

        status = "REAL"

        verification_confidence = 82


    elif len(strong_matches) == 1:

        status = "UNVERIFIED"

        verification_confidence = 65


    else:

        status = "UNVERIFIED"

        verification_confidence = 35


    # --------------------------------------------------------
    # Reason
    # --------------------------------------------------------

    if status == "REAL":

        reason = (
            "Multiple current Google News sources "
            "corroborate the submitted headline."
        )

    else:

        reason = (
            "Some related news was found, but there "
            "is not enough matching evidence to "
            "confirm the submitted headline."
        )


    # --------------------------------------------------------
    # Keep top 4 evidence
    # --------------------------------------------------------

    evidence = evidence[:4]


    return {

        "status":
            status,

        "verification_confidence":
            verification_confidence,

        "reason":
            reason,

        "evidence":
            evidence

    }