const API = "http://127.0.0.1:8000";

const STORAGE_KEY = "ai_cp_real_news";


const noNews = document.getElementById("noNews");
const newsSection = document.getElementById("newsSection");

const newsImage = document.getElementById("newsImage");
const headline = document.getElementById("headline");

const statusBadge = document.getElementById("statusBadge");
const newsStatus = document.getElementById("newsStatus");

const disasterType = document.getElementById("disasterType");
const locationElement = document.getElementById("location");

const confidence = document.getElementById("confidence");
const verificationConfidence =
    document.getElementById("verificationConfidence");

const evidenceCount =
    document.getElementById("evidenceCount");

const verificationReason =
    document.getElementById("verificationReason");

const createdAt =
    document.getElementById("createdAt");

const generateResponseBtn =
    document.getElementById("generateResponseBtn");

const responseLoading =
    document.getElementById("responseLoading");

const responseSection =
    document.getElementById("responseSection");

const responseSummary =
    document.getElementById("responseSummary");

const responseMessage =
    document.getElementById("responseMessage");


// ============================================================
// SHOW
// ============================================================

function show(element) {

    if (element) {
        element.classList.remove("hidden");
    }
}


// ============================================================
// HIDE
// ============================================================

function hide(element) {

    if (element) {
        element.classList.add("hidden");
    }
}


// ============================================================
// SAFE TEXT
// ============================================================

function safeText(value, fallback = "--") {

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {
        return fallback;
    }

    return String(value);
}


// ============================================================
// FORMAT CONFIDENCE
// ============================================================

function formatConfidence(value) {

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {
        return "--";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
        return String(value);
    }

    if (number <= 1) {
        return `${(number * 100).toFixed(2)}%`;
    }

    return `${number.toFixed(2)}%`;
}


// ============================================================
// GET STORED NEWS
// ============================================================

function getStoredNews() {

    try {

        const raw =
            localStorage.getItem(STORAGE_KEY);

        if (!raw) {
            return null;
        }

        return JSON.parse(raw);

    } catch (error) {

        console.error(
            "Unable to read saved news:",
            error
        );

        return null;
    }
}


// ============================================================
// SHOW NO NEWS
// ============================================================

function showNoNews() {

    show(noNews);

    hide(newsSection);

    hide(responseLoading);

    hide(responseSection);
}


// ============================================================
// LOAD NEWS
// ============================================================

function loadNews() {

    const data = getStoredNews();


    if (!data) {

        showNoNews();

        return;
    }


    const status =
        safeText(
            data.status ||
            data.news_status
        ).toUpperCase();


    if (status !== "REAL") {

        showNoNews();

        return;
    }

    window.setResourceDisasterInfo?.(
        data.disaster_type || data.disaster || "Unspecified",
        data.location || "Location not provided"
    );


    hide(noNews);

    show(newsSection);


    // ========================================================
    // STATUS
    // ========================================================

    statusBadge.textContent =
        "REAL";

    newsStatus.textContent =
        "REAL";


    // ========================================================
    // IMAGE
    // ========================================================

    if (data.image) {

        newsImage.src =
            data.image;


        newsImage.onerror =
            function () {

                this.style.display =
                    "none";

            };

    } else {

        newsImage.style.display =
            "none";
    }


    // ========================================================
    // HEADLINE
    // ========================================================

    headline.textContent =
        safeText(
            data.headline
        );


    // ========================================================
    // DISASTER TYPE
    // ========================================================

    disasterType.textContent =
        safeText(
            data.disaster_type ||
            data.disaster
        );


    // ========================================================
    // LOCATION
    // ========================================================

    locationElement.textContent =
        safeText(
            data.location
        );


    // ========================================================
    // CONFIDENCE
    // ========================================================

    confidence.textContent =
        formatConfidence(
            data.confidence
        );


    // ========================================================
    // VERIFICATION CONFIDENCE
    // ========================================================

    verificationConfidence.textContent =
        formatConfidence(
            data.verification_confidence
        );


    // ========================================================
    // EVIDENCE
    // ========================================================

    let evidence =
        data.evidence;


    if (!Array.isArray(evidence)) {

        evidence = [];
    }


    evidenceCount.textContent =
        String(
            evidence.length
        );


    // ========================================================
    // REASON
    // ========================================================

    verificationReason.textContent =
        safeText(

            data.reason,

            "The news was classified as REAL by the verification process."

        );


    // ========================================================
    // DATE
    // ========================================================

    if (data.created_at) {

        try {

            const date =
                new Date(
                    data.created_at
                );


            createdAt.textContent =
                date.toLocaleString();


        } catch {

            createdAt.textContent =
                "";
        }
    }
}


// ============================================================
// SET LIST
// ============================================================

function setList(id, items) {

    const element =
        document.getElementById(id);


    if (!element) {

        return;
    }


    element.innerHTML =
        "";


    if (
        !Array.isArray(items) ||
        items.length === 0
    ) {

        const li =
            document.createElement(
                "li"
            );


        li.textContent =
            "No specific recommendation available.";


        element.appendChild(
            li
        );


        return;
    }


    items.forEach(item => {

        const li =
            document.createElement(
                "li"
            );


        li.textContent =
            safeText(
                item
            );


        element.appendChild(
            li
        );

    });
}


// ============================================================
// SET SITUATION
// ============================================================

function setSituation(id, value) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            safeText(
                value
            );
    }
}


// ============================================================
// GOOGLE MAPS URL
// ============================================================

function createGoogleMapsUrl(location) {

    if (
        location === undefined ||
        location === null
    ) {

        return null;
    }


    location =
        String(location).trim();


    if (
        location === "" ||
        location.toLowerCase() === "not detected" ||
        location === "--"
    ) {

        return null;
    }


    const encodedLocation =
        encodeURIComponent(
            location
        );


    return (
        "https://www.google.com/maps/search/?api=1&query=" +
        encodedLocation
    );
}


// ============================================================
// DISPLAY GOOGLE MAPS LOCATION
// ============================================================

function displayGoogleMapsLocation(data) {

    const mapContainer =
        document.getElementById(
            "googleMapsLocation"
        );


    if (!mapContainer) {

        console.warn(
            "googleMapsLocation element not found in HTML."
        );

        return;
    }


    mapContainer.innerHTML =
        "";


    // First use backend URL if it exists

    let mapsUrl =
        data.google_maps_url;


    // If backend did not return URL,
    // create it from the location

    if (!mapsUrl) {

        mapsUrl =
            createGoogleMapsUrl(
                data.location
            );
    }


    // ========================================================
    // MAP LINK AVAILABLE
    // ========================================================

    if (mapsUrl) {

        const mapLink =
            document.createElement(
                "a"
            );


        mapLink.href =
            mapsUrl;


        mapLink.target =
            "_blank";


        mapLink.rel =
            "noopener noreferrer";


        mapLink.className =
            "map-location-btn";


        mapLink.textContent =
            "🗺️ Open Location on Google Maps";


        mapContainer.appendChild(
            mapLink
        );


    } else {

        // ====================================================
        // LOCATION NOT AVAILABLE
        // ====================================================

        const message =
            document.createElement(
                "span"
            );


        message.textContent =
            "📍 Location not detected";


        mapContainer.appendChild(
            message
        );
    }
}


// ============================================================
// DISPLAY RESPONSE
// ============================================================

function displayResponse(data) {

    if (!data) {

        return;
    }


    // ========================================================
    // GOOGLE MAPS
    // ========================================================

    displayGoogleMapsLocation(
        data
    );


    // ========================================================
    // SUMMARY
    // ========================================================

    responseSummary.textContent =
        safeText(

            data.summary,

            "Emergency response plan generated."

        );


    // ========================================================
    // SITUATION
    // ========================================================

    const situation =
        data.situation ||
        {};


    setSituation(

        "roadCondition",

        situation.road_condition

    );


    setSituation(

        "waterLevel",

        situation.water_level

    );


    setSituation(

        "electricity",

        situation.electricity

    );


    setSituation(

        "foodRequirement",

        situation.food_requirement

    );


    setSituation(

        "shelterRequirement",

        situation.shelter_requirement

    );


    setSituation(

        "medicalRequirement",

        situation.medical_requirement

    );


    // ========================================================
    // RESPONSE
    // ========================================================

    const response =
        data.response ||
        {};


    setList(

        "medicalList",

        response.medical

    );


    setList(

        "rescueList",

        response.rescue

    );


    setList(

        "foodList",

        response.food

    );


    setList(

        "shelterList",

        response.shelter

    );


    setList(

        "waterList",

        response.water

    );


    setList(

        "transportList",

        response.transport

    );


    setList(

        "securityList",

        response.security

    );


    // ========================================================
    // RESOURCES
    // ========================================================

    const resourceList =
        document.getElementById(
            "resourceList"
        );


    if (resourceList) {

        resourceList.innerHTML =
            "";


        const resources =
            Array.isArray(
                data.resources
            )
                ? data.resources
                : [];

        const recommendedResources = [];


        resources.forEach(resource => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "resource-item";


            const resourceName = typeof resource === "string"
                ? resource
                : (resource?.resource_name || resource?.name || resource?.resource || "Emergency supply");
            const resourceType = typeof resource === "object" && resource
                ? (resource.resource_type || resource.type || "")
                : "";

            recommendedResources.push({
                resource_name: resourceName,
                resource_type: resourceType,
                quantity: typeof resource === "object" && resource
                    ? (resource.quantity || resource.required_quantity || "")
                    : ""
            });

            const label = document.createElement("span");
            label.textContent = safeText(resourceName);
            item.appendChild(label);

            resourceList.appendChild(
                item
            );

        });

        const requestButton = document.getElementById("requestAllResourcesButton");
        if (requestButton) {
            requestButton.hidden = recommendedResources.length === 0;
            requestButton.textContent = "Send Resource Phone Notification";
            requestButton.onclick = () => {
                const names = recommendedResources.map(item => item.resource_name).filter(Boolean);
                const types = [...new Set(recommendedResources.map(item => item.resource_type).filter(Boolean))];
                const quantities = [...new Set(recommendedResources.map(item => item.quantity).filter(Boolean))];
                window.openResourceRequest?.({
                    resource_name: names.join(", "),
                    resource_type: types.length === 1 ? types[0] : "OTHER",
                    quantity: quantities.length === 1 ? quantities[0] : ""
                });
            };
        }
    }


    // ========================================================
    // NOTICE
    // ========================================================

    const notice =
        document.getElementById(
            "responseNotice"
        );


    if (notice) {

        notice.textContent =
            safeText(

                data.notice,

                "Confirm emergency conditions with local authorities before deployment."

            );
    }


    // ========================================================
    // SHOW RESPONSE
    // ========================================================

    show(
        responseSection
    );
}


// ============================================================
// GENERATE RESPONSE
// ============================================================

async function generateResponse() {

    const data =
        getStoredNews();


    if (!data) {

        showError(
            "No verified news data was found."
        );

        return;
    }


    // ========================================================
    // STATUS
    // ========================================================

    const status =
        safeText(

            data.status ||
            data.news_status

        ).toUpperCase();


    // ========================================================
    // ONLY REAL NEWS
    // ========================================================

    if (status !== "REAL") {

        showError(
            "Emergency response is available only for REAL news."
        );

        return;
    }


    // ========================================================
    // REQUEST BODY
    // ========================================================

    const requestBody = {

        status:
            "REAL",

        disaster_type:
            data.disaster_type ||
            data.disaster ||
            "",

        location:
            data.location ||
            ""
    };


    // ========================================================
    // LOADING
    // ========================================================

    hide(
        responseSection
    );


    hide(
        responseMessage
    );


    show(
        responseLoading
    );


    generateResponseBtn.disabled =
        true;


    generateResponseBtn.textContent =
        "Generating...";


    try {

        // ====================================================
        // API REQUEST
        // ====================================================

        const response =
            await fetch(

                `${API}/api/response/generate`,

                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            requestBody
                        )

                }
            );


        // ====================================================
        // READ JSON
        // ====================================================

        const result =
            await response.json();


        // ====================================================
        // ERROR
        // ====================================================

        if (!response.ok) {

            throw new Error(

                result.detail ||

                "Response generation failed."

            );
        }


        // ====================================================
        // ADD LOCATION TO RESULT
        // ====================================================

        /*
         * If backend does not return google_maps_url,
         * generate it here using the location already
         * returned by the news analysis.
         */

        if (!result.google_maps_url) {

            result.google_maps_url =
                createGoogleMapsUrl(
                    data.location
                );
        }


        /*
         * Make sure the response uses the original
         * detected news location.
         */

        if (
            !result.location &&
            data.location
        ) {

            result.location =
                data.location;
        }


        // ====================================================
        // DISPLAY
        // ====================================================

        displayResponse(
            result
        );

        window.setResourceDisasterInfo?.(
            requestBody.disaster_type,
            result.location || requestBody.location
        );


        // ====================================================
        // SCROLL TO RESPONSE
        // ====================================================

        responseSection.scrollIntoView({

            behavior:
                "smooth",

            block:
                "start"

        });


    } catch (error) {

        console.error(

            "Response generation error:",

            error

        );


        showError(

            error.message ||

            "Unable to generate emergency response."

        );


    } finally {

        // ====================================================
        // STOP LOADING
        // ====================================================

        hide(
            responseLoading
        );


        generateResponseBtn.disabled =
            false;


        generateResponseBtn.textContent =
            "🚨 Generate AI Response";

    }
}


// ============================================================
// ERROR
// ============================================================

function showError(message) {

    responseMessage.textContent =
        safeText(
            message
        );


    show(
        responseMessage
    );
}


// ============================================================
// BUTTON EVENT
// ============================================================

if (generateResponseBtn) {

    generateResponseBtn.addEventListener(

        "click",

        generateResponse

    );
}


// ============================================================
// INITIAL LOAD
// ============================================================

loadNews();
