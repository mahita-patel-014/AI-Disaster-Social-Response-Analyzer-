import re


DISASTER_KEYWORDS = {

    "Earthquake": [
        "earthquake",
        "earthquake struck",
        "tremor",
        "seismic",
        "magnitude",
        "quake"
    ],

    "Flood": [
        "flood",
        "flooding",
        "flash flood",
        "river overflow",
        "heavy rainfall",
        "water level"
    ],

    "Fire": [
        "fire",
        "wildfire",
        "forest fire",
        "blaze",
        "burning"
    ],

    "Cyclone": [
        "cyclone",
        "hurricane",
        "typhoon",
        "tropical storm"
    ],

    "Drought": [
        "drought",
        "water shortage",
        "dry spell",
        "water crisis"
    ],

    "Landslide": [
        "landslide",
        "mudslide",
        "rockslide"
    ],

    "Tsunami": [
        "tsunami",
        "tidal wave"
    ],

    "Volcanic Eruption": [
        "volcano",
        "volcanic eruption",
        "eruption",
        "lava"
    ],

    "Storm": [
        "storm",
        "thunderstorm",
        "windstorm"
    ],

    "Heatwave": [
        "heatwave",
        "heat wave",
        "extreme heat"
    ]

}


def detect_disaster_type(
    text: str
):

    text = text.lower()


    scores = {}


    for disaster, keywords in DISASTER_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1


        scores[disaster] = score


    best = max(
        scores,
        key=scores.get
    )


    if scores[best] == 0:

        return "Other"


    return best