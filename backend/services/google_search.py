import html
import re
from urllib.parse import quote_plus
from xml.etree import ElementTree

import requests


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
)


def clean_text(value):

    if not value:
        return ""

    value = html.unescape(
        value
    )

    value = re.sub(
        r"<[^>]+>",
        "",
        value
    )

    return value.strip()


def search_google_news(
    query,
    limit=10
):

    url = (
        GOOGLE_NEWS_RSS
        + "?q="
        + quote_plus(query)
        + "&hl=en-IN"
        + "&gl=IN"
        + "&ceid=IN:en"
    )

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        root = ElementTree.fromstring(
            response.content
        )

    except Exception as error:

        print(
            "Google News search error:",
            error
        )

        return []


    results = []

    for item in root.findall(
        ".//item"
    ):

        title = clean_text(
            item.findtext(
                "title",
                ""
            )
        )

        link = clean_text(
            item.findtext(
                "link",
                ""
            )
        )

        published = clean_text(
            item.findtext(
                "pubDate",
                ""
            )
        )

        source_element = item.find(
            "source"
        )

        source = ""

        if source_element is not None:

            source = clean_text(
                source_element.text
                or ""
            )

        if not title or not link:
            continue

        results.append({

            "title": title,

            "url": link,

            "source": source,

            "published": published

        })

        if len(results) >= limit:
            break


    return results