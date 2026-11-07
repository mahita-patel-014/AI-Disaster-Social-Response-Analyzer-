import math
import requests


# ============================================================
# DISASTER TYPE NORMALIZATION
# ============================================================

def normalize_disaster_type(disaster_type: str) -> str:

    if not disaster_type:
        return "general"

    value = str(disaster_type).strip().lower()

    if "flood" in value:
        return "flood"

    if "earthquake" in value:
        return "earthquake"

    if "fire" in value:
        return "fire"

    if (
        "cyclone" in value
        or "hurricane" in value
        or "storm" in value
    ):
        return "cyclone"

    if "drought" in value:
        return "drought"

    return "general"


# ============================================================
# DISASTER MAP CONFIGURATION
# ============================================================

DISASTER_MAP_CONFIG = {

    "flood": {
        "radius_km": 5,
        "color": "#0066ff",
        "fill_color": "#0066ff",
        "priority_color": "#00bfff",
        "label": "Flood Affected Region"
    },

    "earthquake": {
        "radius_km": 5,
        "color": "#ff0000",
        "fill_color": "#ff3b30",
        "priority_color": "#ff8c00",
        "label": "Earthquake Affected Region"
    },

    "fire": {
        "radius_km": 3,
        "color": "#ff0000",
        "fill_color": "#ff4500",
        "priority_color": "#ff8c00",
        "label": "Fire Affected Region"
    },

    "cyclone": {
        "radius_km": 15,
        "color": "#a020f0",
        "fill_color": "#c000ff",
        "priority_color": "#ff00aa",
        "label": "Cyclone Affected Region"
    },

    "drought": {
        "radius_km": 10,
        "color": "#b8860b",
        "fill_color": "#daa520",
        "priority_color": "#ffd700",
        "label": "Drought Affected Region"
    },

    "general": {
        "radius_km": 5,
        "color": "#ff0000",
        "fill_color": "#ff3b30",
        "priority_color": "#ff8c00",
        "label": "Disaster Affected Region"
    }
}


# ============================================================
# GET MAP CONFIG
# ============================================================

def get_map_config(disaster_type: str):

    normalized = normalize_disaster_type(
        disaster_type
    )

    return DISASTER_MAP_CONFIG.get(
        normalized,
        DISASTER_MAP_CONFIG["general"]
    )


# ============================================================
# GEOCODE LOCATION
# ============================================================

def geocode_location(location: str):

    if not location:
        return None

    location = str(location).strip()

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

    try:

        url = (
            "https://nominatim.openstreetmap.org/search"
        )

        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }

        headers = {
            "User-Agent":
                "AI-CP-Disaster-Response-System/1.0"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return None

        return {
            "latitude": float(
                data[0]["lat"]
            ),
            "longitude": float(
                data[0]["lon"]
            ),
            "display_name": data[0].get(
                "display_name",
                location
            )
        }

    except Exception as error:

        print(
            "Geocoding error:",
            repr(error)
        )

        return None


# ============================================================
# CREATE IRREGULAR AFFECTED REGION
# ============================================================

def create_affected_region(
    latitude: float,
    longitude: float,
    radius_km: float
):

    points = []

    total_points = 32

    latitude_km = 111.0

    longitude_km = (
        111.0
        * max(
            math.cos(
                math.radians(latitude)
            ),
            0.15
        )
    )

    multipliers = [
        0.82, 0.96, 1.05, 0.91,
        1.12, 0.98, 0.87, 1.08,
        0.94, 1.14, 0.89, 1.02,
        1.09, 0.93, 1.16, 0.88,
        1.04, 0.97, 1.11, 0.86,
        1.07, 1.13, 0.92, 1.00,
        1.15, 0.90, 1.06, 0.95,
        1.10, 0.84, 1.03, 0.99
    ]

    for index in range(total_points):

        angle = (
            2 * math.pi * index
            / total_points
        )

        distance = (
            radius_km
            * multipliers[index]
        )

        lat_offset = (
            distance
            * math.sin(angle)
            / latitude_km
        )

        lon_offset = (
            distance
            * math.cos(angle)
            / longitude_km
        )

        points.append({
            "latitude":
                latitude + lat_offset,

            "longitude":
                longitude + lon_offset
        })

    if points:

        points.append(
            points[0].copy()
        )

    return points


# ============================================================
# CREATE PRIORITY REGION
# ============================================================

def create_priority_region(
    latitude: float,
    longitude: float,
    radius_km: float
):

    priority_radius = (
        radius_km * 0.45
    )

    points = []

    total_points = 24

    latitude_km = 111.0

    longitude_km = (
        111.0
        * max(
            math.cos(
                math.radians(latitude)
            ),
            0.15
        )
    )

    for index in range(total_points):

        angle = (
            2 * math.pi * index
            / total_points
        )

        variation = (
            0.90
            + (
                (index % 5)
                * 0.035
            )
        )

        distance = (
            priority_radius
            * variation
        )

        lat_offset = (
            distance
            * math.sin(angle)
            / latitude_km
        )

        lon_offset = (
            distance
            * math.cos(angle)
            / longitude_km
        )

        points.append({
            "latitude":
                latitude + lat_offset,

            "longitude":
                longitude + lon_offset
        })

    if points:

        points.append(
            points[0].copy()
        )

    return points


# ============================================================
# GENERATE DISASTER MAP
# ============================================================

def generate_disaster_map(
    disaster_type: str,
    location: str
):

    normalized = normalize_disaster_type(
        disaster_type
    )

    config = get_map_config(
        disaster_type
    )

    coordinates = geocode_location(
        location
    )

    if not coordinates:

        return {
            "enabled": False,

            "disaster_type":
                disaster_type,

            "normalized_disaster":
                normalized,

            "location":
                location,

            "mapped_location":
                None,

            "latitude":
                None,

            "longitude":
                None,

            "radius_km":
                config["radius_km"],

            "radius_meters":
                config["radius_km"] * 1000,

            "affected_region":
                [],

            "priority_region":
                [],

            "color":
                config["color"],

            "fill_color":
                config["fill_color"],

            "priority_color":
                config["priority_color"],

            "label":
                config["label"],

            "zone_type":
                "Location unavailable",

            "priority_zone":
                "Unavailable",

            "description":
                "The location could not be mapped.",

            "warning":
                (
                    "The affected region cannot be "
                    "displayed without coordinates."
                )
        }

    latitude = coordinates[
        "latitude"
    ]

    longitude = coordinates[
        "longitude"
    ]

    radius_km = config[
        "radius_km"
    ]

    affected_region = (
        create_affected_region(
            latitude,
            longitude,
            radius_km
        )
    )

    priority_region = (
        create_priority_region(
            latitude,
            longitude,
            radius_km
        )
    )

    return {

        "enabled": True,

        "disaster_type":
            disaster_type,

        "normalized_disaster":
            normalized,

        "location":
            location,

        "mapped_location":
            coordinates.get(
                "display_name",
                location
            ),

        "latitude":
            latitude,

        "longitude":
            longitude,

        "radius_km":
            radius_km,

        "radius_meters":
            radius_km * 1000,

        "affected_region":
            affected_region,

        "priority_region":
            priority_region,

        "color":
            config["color"],

        "fill_color":
            config["fill_color"],

        "priority_color":
            config["priority_color"],

        "label":
            config["label"],

        "zone_type":
            "AI Estimated Affected Zone",

        "priority_zone":
            "High Priority Emergency Zone",

        "description":
            (
                "Estimated disaster impact area "
                "for emergency response planning."
            ),

        "warning":
            (
                "This is an AI estimated planning "
                "region and not an exact real-time "
                "official disaster boundary."
            )
    }


# ============================================================
# EMERGENCY RESPONSE
# ============================================================

def generate_emergency_response(
    disaster_type: str,
    location: str
):

    normalized = normalize_disaster_type(
        disaster_type
    )

    # --------------------------------------------------------
    # FLOOD
    # --------------------------------------------------------

    if normalized == "flood":

        result = {

            "success": True,

            "disaster_type":
                disaster_type,

            "normalized_disaster":
                "flood",

            "location":
                location,

            "summary":
                (
                    f"Flood emergency response "
                    f"activated for {location}."
                ),

            "response": {

                "medical": [
                    "Doctors",
                    "Medical teams",
                    "First-aid teams",
                    "Emergency medicines"
                ],

                "rescue": [
                    "Rescue teams",
                    "Boat rescue teams",
                    "Soldiers",
                    "Emergency divers"
                ],

                "food": [
                    "Ready-to-eat food",
                    "Food distribution teams"
                ],

                "shelter": [
                    "Temporary shelters",
                    "Relief camps"
                ],

                "water": [
                    "Drinking water",
                    "Water purification units"
                ],

                "transport": [
                    "Rescue boats",
                    "Emergency vehicles",
                    "Ambulances"
                ],

                "security": [
                    "Police",
                    "Disaster response security"
                ]
            },

            "situation": {

                "road_condition":
                    "Several roads may be waterlogged or blocked.",

                "water_level":
                    "Water level requires continuous monitoring.",

                "electricity":
                    "Electricity supply may require emergency inspection.",

                "food_requirement":
                    "Emergency food distribution required.",

                "shelter_requirement":
                    "Temporary shelter required for displaced people.",

                "medical_requirement":
                    "Medical teams and emergency medicines required."
            },

            "resources": [
                "Drinking Water",
                "Food",
                "Doctors / Medical Team",
                "Rescue Team",
                "Shelter",
                "Emergency Transport",
                "Security Team"
            ],

            "notice":
                (
                    "Prioritize evacuation from "
                    "low-lying and flooded areas."
                )
        }

    # --------------------------------------------------------
    # EARTHQUAKE
    # --------------------------------------------------------

    elif normalized == "earthquake":

        result = {

            "success": True,

            "disaster_type":
                disaster_type,

            "normalized_disaster":
                "earthquake",

            "location":
                location,

            "summary":
                (
                    f"Earthquake emergency response "
                    f"activated for {location}."
                ),

            "response": {

                "medical": [
                    "Doctors",
                    "Trauma teams",
                    "First-aid teams",
                    "Emergency medicines"
                ],

                "rescue": [
                    "Search and rescue teams",
                    "Soldiers",
                    "Fire and rescue teams",
                    "Structural rescue specialists"
                ],

                "food": [
                    "Emergency food packets",
                    "Community kitchens"
                ],

                "shelter": [
                    "Temporary shelters",
                    "Emergency camps"
                ],

                "water": [
                    "Drinking water",
                    "Water tanks"
                ],

                "transport": [
                    "Ambulances",
                    "Rescue vehicles",
                    "Heavy rescue equipment"
                ],

                "security": [
                    "Police",
                    "Crowd control teams"
                ]
            },

            "situation": {

                "road_condition":
                    "Roads may be blocked by debris or structural damage.",

                "water_level":
                    "Normal monitoring unless secondary flooding occurs.",

                "electricity":
                    "Electrical infrastructure requires safety inspection.",

                "food_requirement":
                    "Emergency food supplies required.",

                "shelter_requirement":
                    "Temporary shelter required for affected residents.",

                "medical_requirement":
                    "Trauma and emergency medical teams required."
            },

            "resources": [
                "Doctors / Trauma Team",
                "Rescue Team",
                "Soldiers",
                "Food",
                "Drinking Water",
                "Temporary Shelter",
                "Ambulance",
                "Security Team"
            ],

            "notice":
                (
                    "Keep people away from "
                    "damaged structures."
                )
        }

    # --------------------------------------------------------
    # FIRE
    # --------------------------------------------------------

    elif normalized == "fire":

        result = {

            "success": True,

            "disaster_type":
                disaster_type,

            "normalized_disaster":
                "fire",

            "location":
                location,

            "summary":
                (
                    f"Fire emergency response "
                    f"activated for {location}."
                ),

            "response": {

                "medical": [
                    "Doctors",
                    "Burn treatment teams",
                    "First-aid teams",
                    "Emergency medicines"
                ],

                "rescue": [
                    "Firefighters",
                    "Rescue teams",
                    "Emergency evacuation teams"
                ],

                "food": [
                    "Emergency food packets",
                    "Food distribution teams"
                ],

                "shelter": [
                    "Temporary shelters",
                    "Evacuation centers"
                ],

                "water": [
                    "Drinking water",
                    "Firefighting water supply"
                ],

                "transport": [
                    "Fire engines",
                    "Ambulances",
                    "Emergency vehicles"
                ],

                "security": [
                    "Police",
                    "Crowd control teams"
                ]
            },

            "situation": {

                "road_condition":
                    "Access roads may be restricted for emergency vehicles.",

                "water_level":
                    "Water supply should be monitored for firefighting operations.",

                "electricity":
                    "Power may need to be isolated in affected areas.",

                "food_requirement":
                    "Emergency food support required for evacuated residents.",

                "shelter_requirement":
                    "Evacuation shelters required.",

                "medical_requirement":
                    "Burn and smoke-inhalation treatment required."
            },

            "resources": [
                "Firefighters",
                "Doctors",
                "Ambulance",
                "Drinking Water",
                "Food",
                "Emergency Shelter",
                "Security Team"
            ],

            "notice":
                (
                    "Keep civilians away from "
                    "the active fire zone."
                )
        }

    # --------------------------------------------------------
    # CYCLONE
    # --------------------------------------------------------

    elif normalized == "cyclone":

        result = {

            "success": True,

            "disaster_type":
                disaster_type,

            "normalized_disaster":
                "cyclone",

            "location":
                location,

            "summary":
                (
                    f"Cyclone emergency response "
                    f"activated for {location}."
                ),

            "response": {

                "medical": [
                    "Doctors",
                    "Emergency medical teams",
                    "First-aid teams",
                    "Emergency medicines"
                ],

                "rescue": [
                    "Rescue teams",
                    "Soldiers",
                    "Evacuation teams"
                ],

                "food": [
                    "Emergency food packets",
                    "Food distribution teams"
                ],

                "shelter": [
                    "Cyclone shelters",
                    "Temporary relief camps"
                ],

                "water": [
                    "Drinking water",
                    "Water tanks"
                ],

                "transport": [
                    "Emergency vehicles",
                    "Ambulances",
                    "Rescue vehicles"
                ],

                "security": [
                    "Police",
                    "Security teams"
                ]
            },

            "situation": {

                "road_condition":
                    "Roads may be blocked by fallen trees or debris.",

                "water_level":
                    "Flooding and water levels should be continuously monitored.",

                "electricity":
                    "Power interruptions are possible.",

                "food_requirement":
                    "Emergency food stock required.",

                "shelter_requirement":
                    "Cyclone shelters required.",

                "medical_requirement":
                    "Emergency medical teams required."
            },

            "resources": [
                "Doctors",
                "Rescue Team",
                "Soldiers",
                "Food",
                "Drinking Water",
                "Cyclone Shelter",
                "Emergency Transport",
                "Security"
            ],

            "notice":
                (
                    "Move vulnerable people to "
                    "safe shelters before severe conditions."
                )
        }

    # --------------------------------------------------------
    # DROUGHT
    # --------------------------------------------------------

    elif normalized == "drought":

        result = {

            "success": True,

            "disaster_type":
                disaster_type,

            "normalized_disaster":
                "drought",

            "location":
                location,

            "summary":
                (
                    f"Drought emergency response "
                    f"activated for {location}."
                ),

            "response": {

                "medical": [
                    "Doctors",
                    "Medical teams",
                    "Health monitoring teams"
                ],

                "rescue": [
                    "Relief teams",
                    "Emergency support teams"
                ],

                "food": [
                    "Food supplies",
                    "Food distribution teams"
                ],

                "shelter": [
                    "Relief shelters",
                    "Temporary camps"
                ],

                "water": [
                    "Drinking water",
                    "Water tankers",
                    "Water purification units"
                ],

                "transport": [
                    "Water tankers",
                    "Emergency vehicles"
                ],

                "security": [
                    "Police",
                    "Relief distribution security"
                ]
            },

            "situation": {

                "road_condition":
                    "Roads generally remain usable but water supply routes require monitoring.",

                "water_level":
                    "Water availability is critically important and requires monitoring.",

                "electricity":
                    "Power infrastructure should be monitored.",

                "food_requirement":
                    "Food assistance may be required.",

                "shelter_requirement":
                    "Relief centers may be required.",

                "medical_requirement":
                    "Medical monitoring for dehydration and heat-related illness required."
            },

            "resources": [
                "Drinking Water",
                "Water Tankers",
                "Food",
                "Doctors",
                "Medical Team",
                "Relief Shelter",
                "Transport",
                "Security"
            ],

            "notice":
                (
                    "Prioritize drinking water "
                    "distribution and vulnerable populations."
                )
        }

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    else:

        result = {

            "success": True,

            "disaster_type":
                disaster_type,

            "normalized_disaster":
                "general",

            "location":
                location,

            "summary":
                (
                    f"Emergency response "
                    f"activated for {location}."
                ),

            "response": {

                "medical": [
                    "Doctors",
                    "Medical teams",
                    "First-aid teams"
                ],

                "rescue": [
                    "Emergency rescue teams",
                    "Disaster response teams"
                ],

                "food": [
                    "Emergency food"
                ],

                "shelter": [
                    "Temporary shelter"
                ],

                "water": [
                    "Drinking water"
                ],

                "transport": [
                    "Emergency vehicles",
                    "Ambulances"
                ],

                "security": [
                    "Police",
                    "Security teams"
                ]
            },

            "situation": {

                "road_condition":
                    "Emergency road assessment required.",

                "water_level":
                    "Water conditions should be monitored.",

                "electricity":
                    "Electricity infrastructure should be checked.",

                "food_requirement":
                    "Emergency food assessment required.",

                "shelter_requirement":
                    "Temporary shelter assessment required.",

                "medical_requirement":
                    "Emergency medical assessment required."
            },

            "resources": [
                "Doctors",
                "Medical Team",
                "Rescue Team",
                "Food",
                "Drinking Water",
                "Shelter",
                "Transport",
                "Security"
            ],

            "notice":
                (
                    "Verify the emergency situation "
                    "before deployment."
                )
        }


    # ========================================================
    # MAP
    # ========================================================

    result["map"] = generate_disaster_map(
        disaster_type=disaster_type,
        location=location
    )


    # ========================================================
    # IMPORTANT:
    # NO DATABASE SAVING
    # ========================================================

    result["saved_to_database"] = False

    result["response_id"] = None


    return result