"use strict";

/* ============================================================
   AI CP DISASTER - RESOURCE REQUEST
   PHASE 1 - UI ONLY

   PURPOSE:
   - Open resource request popup
   - Show disaster information
   - Show selected resource information
   - Collect person name
   - Collect mobile number
   - Validate details

   NOT INCLUDED:
   - Backend SMS sending
   - Backend API
   - MongoDB
   - ACCEPT
   - REJECT
   - MutationObserver
   - Automatic button scanning
   ============================================================ */


/* ============================================================
   CURRENT DISASTER INFORMATION
   ============================================================ */

let currentDisaster = {
    disaster_type: "Unknown Disaster",
    disaster_location: "Location not available"
};


/* ============================================================
   SET DISASTER INFORMATION
   ============================================================ */

function setResourceDisasterInfo(disasterType, location) {

    currentDisaster = {
        disaster_type:
            disasterType || "Unknown Disaster",

        disaster_location:
            location || "Location not available"
    };

    console.log(
        "RESOURCE DISASTER INFO:",
        currentDisaster
    );
}


/* ============================================================
   LOAD DISASTER INFORMATION
   ============================================================ */

function loadDisasterInformation() {

    const keys = [
        "analysisResult",
        "analysis_result",
        "analysisData",
        "analysis_data",
        "disasterAnalysis",
        "disaster_analysis",
        "responseData",
        "response_data"
    ];


    for (const key of keys) {

        /* ====================================================
           SESSION STORAGE
           ==================================================== */

        try {

            const sessionValue =
                sessionStorage.getItem(key);

            if (sessionValue) {

                const data =
                    JSON.parse(sessionValue);

                if (data) {

                    currentDisaster.disaster_type =
                        data.disaster_type ||
                        data.disasterType ||
                        data.prediction ||
                        data.predicted_disaster ||
                        currentDisaster.disaster_type;


                    currentDisaster.disaster_location =
                        data.disaster_location ||
                        data.disasterLocation ||
                        data.location ||
                        currentDisaster.disaster_location;


                    console.log(
                        "RESOURCE DISASTER FROM SESSION:",
                        currentDisaster
                    );

                    return;
                }
            }

        } catch (error) {

            console.warn(
                "Session storage read error:",
                error
            );
        }


        /* ====================================================
           LOCAL STORAGE
           ==================================================== */

        try {

            const localValue =
                localStorage.getItem(key);

            if (localValue) {

                const data =
                    JSON.parse(localValue);

                if (data) {

                    currentDisaster.disaster_type =
                        data.disaster_type ||
                        data.disasterType ||
                        data.prediction ||
                        data.predicted_disaster ||
                        currentDisaster.disaster_type;


                    currentDisaster.disaster_location =
                        data.disaster_location ||
                        data.disasterLocation ||
                        data.location ||
                        currentDisaster.disaster_location;


                    console.log(
                        "RESOURCE DISASTER FROM LOCAL:",
                        currentDisaster
                    );

                    return;
                }
            }

        } catch (error) {

            console.warn(
                "Local storage read error:",
                error
            );
        }
    }


    console.log(
        "RESOURCE DISASTER:",
        currentDisaster
    );
}


/* ============================================================
   OPEN RESOURCE REQUEST POPUP
   ============================================================ */

function openResourceRequest(resource) {

    console.log(
        "📞 CALL RESOURCE CLICKED:",
        resource
    );


    /* ========================================================
       CLOSE EXISTING POPUP
       ======================================================== */

    closeResourcePopup();


    resource =
        resource || {};


    /* ========================================================
       RESOURCE INFORMATION
       ======================================================== */

    const resourceName =
        resource.resource_name ||
        resource.resourceName ||
        resource.name ||
        "Emergency Resource";


    const resourceType =
        resource.resource_type ||
        resource.resourceType ||
        resource.type ||
        "OTHER";


    const quantity =
        resource.quantity ||
        resource.required_quantity ||
        resource.requiredQuantity ||
        "As required";


    const priority =
        resource.priority ||
        "HIGH";


    /* ========================================================
       LOAD DISASTER INFORMATION
       ======================================================== */

    loadDisasterInformation();


    /* ========================================================
       CREATE OVERLAY
       ======================================================== */

    const overlay =
        document.createElement("div");


    overlay.id =
        "resourceRequestOverlay";


    overlay.style.cssText = `

        position: fixed !important;
        inset: 0 !important;

        z-index: 9999999 !important;

        display: flex !important;

        align-items: center !important;
        justify-content: center !important;

        padding: 20px !important;

        box-sizing: border-box !important;

        background:
            rgba(0, 0, 0, 0.65) !important;

        backdrop-filter: blur(5px);

    `;


    /* ========================================================
       CREATE POPUP
       ======================================================== */

    const popup =
        document.createElement("div");


    popup.className =
        "resource-request-popup";


    popup.style.cssText = `

        width: 100% !important;

        max-width: 500px !important;

        max-height: 90vh !important;

        overflow-y: auto !important;

        box-sizing: border-box !important;

        padding: 26px !important;

        position: relative !important;

        border-radius: 18px !important;

        background: #ffffff !important;

        color: #111827 !important;

        font-family:
            Arial,
            sans-serif !important;

        box-shadow:
            0 20px 60px
            rgba(0, 0, 0, 0.35) !important;

        animation:
            resourcePopupOpen
            0.2s ease-out;

    `;


    /* ========================================================
       POPUP CONTENT
       ======================================================== */

    popup.innerHTML = `

        <!-- CLOSE BUTTON -->

        <button
            type="button"
            id="resourcePopupClose"
            style="
                position:absolute;

                top:12px;
                right:15px;

                width:34px;
                height:34px;

                border:none;

                border-radius:50%;

                background:#f1f5f9;

                color:#111827;

                font-size:22px;

                cursor:pointer;
            "
        >
            ×
        </button>


        <!-- PHONE ICON -->

        <div
            style="
                width:55px;
                height:55px;

                display:flex;

                align-items:center;
                justify-content:center;

                margin-bottom:14px;

                border-radius:14px;

                background:#dbeafe;

                font-size:27px;
            "
        >
            📞
        </div>


        <!-- TITLE -->

        <div
            style="
                font-size:23px;

                font-weight:800;

                color:#111827;

                margin-bottom:7px;

                padding-right:40px;
            "
        >
            CALL RESOURCE
        </div>


        <!-- DESCRIPTION -->

        <div
            style="
                font-size:14px;

                color:#64748b;

                line-height:1.5;

                margin-bottom:20px;
            "
        >
            Enter the person's details to
            request the required emergency resource.
        </div>


        <!-- ==================================================
             RESOURCE INFORMATION
             ================================================== -->

        <div
            style="
                background:#f8fafc;

                border-radius:12px;

                padding:15px;

                margin-bottom:22px;
            "
        >


            <!-- DISASTER -->

            <div style="margin-bottom:12px;">

                <span
                    style="
                        display:block;

                        color:#64748b;

                        font-size:12px;

                        margin-bottom:3px;
                    "
                >
                    Disaster
                </span>

                <strong
                    style="
                        display:block;

                        color:#111827;

                        font-size:14px;
                    "
                >
                    ${escapeHTML(
                        currentDisaster.disaster_type
                    )}
                </strong>

            </div>


            <!-- LOCATION -->

            <div style="margin-bottom:12px;">

                <span
                    style="
                        display:block;

                        color:#64748b;

                        font-size:12px;

                        margin-bottom:3px;
                    "
                >
                    Location
                </span>

                <strong
                    style="
                        display:block;

                        color:#111827;

                        font-size:14px;
                    "
                >
                    ${escapeHTML(
                        currentDisaster.disaster_location
                    )}
                </strong>

            </div>


            <!-- REQUIRED RESOURCE -->

            <div style="margin-bottom:12px;">

                <span
                    style="
                        display:block;

                        color:#64748b;

                        font-size:12px;

                        margin-bottom:3px;
                    "
                >
                    Required Resource
                </span>

                <strong
                    style="
                        display:block;

                        color:#111827;

                        font-size:14px;
                    "
                >
                    ${escapeHTML(resourceName)}
                </strong>

            </div>


            <!-- RESOURCE TYPE -->

            <div style="margin-bottom:12px;">

                <span
                    style="
                        display:block;

                        color:#64748b;

                        font-size:12px;

                        margin-bottom:3px;
                    "
                >
                    Resource Type
                </span>

                <strong
                    style="
                        display:block;

                        color:#111827;

                        font-size:14px;
                    "
                >
                    ${escapeHTML(resourceType)}
                </strong>

            </div>


            <!-- QUANTITY -->

            <div style="margin-bottom:12px;">

                <span
                    style="
                        display:block;

                        color:#64748b;

                        font-size:12px;

                        margin-bottom:3px;
                    "
                >
                    Quantity
                </span>

                <strong
                    style="
                        display:block;

                        color:#111827;

                        font-size:14px;
                    "
                >
                    ${escapeHTML(quantity)}
                </strong>

            </div>


            <!-- PRIORITY -->

            <div>

                <span
                    style="
                        display:block;

                        color:#64748b;

                        font-size:12px;

                        margin-bottom:3px;
                    "
                >
                    Priority
                </span>

                <strong
                    style="
                        display:block;

                        color:#dc2626;

                        font-size:14px;
                    "
                >
                    ${escapeHTML(priority)}
                </strong>

            </div>

        </div>


        <!-- ==================================================
             PERSON NAME
             ================================================== -->

        <label
            for="resourcePersonName"
            style="
                display:block;

                margin-bottom:7px;

                font-size:13px;

                font-weight:700;

                color:#111827;
            "
        >
            Person Name
        </label>


        <input
            type="text"
            id="resourcePersonName"
            placeholder="Enter person's name"
            autocomplete="name"
            style="
                width:100%;

                height:45px;

                border:1px solid #cbd5e1;

                border-radius:8px;

                padding:0 12px;

                box-sizing:border-box;

                margin-bottom:15px;

                font-size:14px;

                outline:none;
            "
        />


        <!-- ==================================================
             MOBILE NUMBER
             ================================================== -->

        <label
            for="resourcePersonPhone"
            style="
                display:block;

                margin-bottom:7px;

                font-size:13px;

                font-weight:700;

                color:#111827;
            "
        >
            Mobile Number
        </label>


        <input
            type="tel"
            id="resourcePersonPhone"
            placeholder="+919876543210"
            autocomplete="tel"
            style="
                width:100%;

                height:45px;

                border:1px solid #cbd5e1;

                border-radius:8px;

                padding:0 12px;

                box-sizing:border-box;

                margin-bottom:18px;

                font-size:14px;

                outline:none;
            "
        />


        <!-- ==================================================
             SEND RESOURCE REQUEST
             ================================================== -->

        <button
            type="button"
            id="resourceRequestSubmit"
            style="
                width:100%;

                height:47px;

                border:none;

                border-radius:9px;

                background:#2563eb;

                color:#ffffff;

                font-size:13px;

                font-weight:800;

                cursor:pointer;
            "
        >
            SEND RESOURCE REQUEST
        </button>


        <!-- MESSAGE -->

        <div
            id="resourceRequestMessage"
            style="
                margin-top:12px;

                font-size:13px;

                line-height:1.5;

                min-height:20px;
            "
        ></div>

    `;


    /* ========================================================
       ADD POPUP TO PAGE
       ======================================================== */

    overlay.appendChild(popup);

    document.body.appendChild(overlay);


    /* ========================================================
       CLOSE BUTTON
       ======================================================== */

    const closeButton =
        document.getElementById(
            "resourcePopupClose"
        );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeResourcePopup
        );
    }


    /* ========================================================
       SUBMIT BUTTON
       ======================================================== */

    const submitButton =
        document.getElementById(
            "resourceRequestSubmit"
        );


    if (submitButton) {

        submitButton.addEventListener(
            "click",
            function () {

                handlePhaseOneSubmit(
                    resourceName,
                    resourceType,
                    quantity,
                    priority
                );

            }
        );
    }


    /* ========================================================
       CLICK OUTSIDE POPUP
       ======================================================== */

    overlay.addEventListener(
        "click",
        function (event) {

            if (event.target === overlay) {

                closeResourcePopup();
            }

        }
    );


    /* ========================================================
       ESCAPE KEY
       ======================================================== */

    document.addEventListener(
        "keydown",
        handleResourceEscape
    );


    /* ========================================================
       AUTO FOCUS
       ======================================================== */

    setTimeout(
        function () {

            const nameInput =
                document.getElementById(
                    "resourcePersonName"
                );


            if (nameInput) {

                nameInput.focus();
            }

        },
        50
    );
}


/* ============================================================
   PHASE 1 SUBMIT
   ============================================================ */

function handlePhaseOneSubmit(
    resourceName,
    resourceType,
    quantity,
    priority
) {

    const nameInput =
        document.getElementById(
            "resourcePersonName"
        );


    const phoneInput =
        document.getElementById(
            "resourcePersonPhone"
        );


    const message =
        document.getElementById(
            "resourceRequestMessage"
        );


    const submitButton =
        document.getElementById(
            "resourceRequestSubmit"
        );


    if (
        !nameInput ||
        !phoneInput ||
        !message ||
        !submitButton
    ) {

        console.error(
            "Resource request form elements not found."
        );

        return;
    }


    const personName =
        nameInput.value.trim();


    const phone =
        phoneInput.value.trim();


    /* ========================================================
       NAME VALIDATION
       ======================================================== */

    if (!personName) {

        message.style.color =
            "#dc2626";

        message.textContent =
            "Please enter person's name.";

        nameInput.focus();

        return;
    }


    /* ========================================================
       PHONE VALIDATION
       ======================================================== */

    if (!phone) {

        message.style.color =
            "#dc2626";

        message.textContent =
            "Please enter mobile number.";

        phoneInput.focus();

        return;
    }


    /* ========================================================
       INTERNATIONAL FORMAT
       ======================================================== */

    if (!phone.startsWith("+")) {

        message.style.color =
            "#dc2626";

        message.textContent =
            "Use international format, for example +919876543210.";

        phoneInput.focus();

        return;
    }


    /* ========================================================
       PHONE LENGTH VALIDATION
       ======================================================== */

    const phoneDigits =
        phone.replace(/\D/g, "");


    if (
        phoneDigits.length < 10 ||
        phoneDigits.length > 15
    ) {

        message.style.color =
            "#dc2626";

        message.textContent =
            "Please enter a valid mobile number.";

        phoneInput.focus();

        return;
    }


    /* ========================================================
       DETAILS READY
       ======================================================== */

    console.log(
        "✅ RESOURCE REQUEST DETAILS READY",
        {

            disaster_type:
                currentDisaster.disaster_type,

            disaster_location:
                currentDisaster.disaster_location,

            resource_name:
                resourceName,

            resource_type:
                resourceType,

            quantity:
                quantity,

            priority:
                priority,

            person_name:
                personName,

            phone:
                phone
        }
    );


    /* ========================================================
       SUCCESS MESSAGE
       ======================================================== */

    message.style.color =
        "#16a34a";


    message.textContent =
        "Resource request details are ready.";


    /* ========================================================
       UPDATE BUTTON
       ======================================================== */

    submitButton.textContent =
        "REQUEST DETAILS READY";


    submitButton.style.background =
        "#16a34a";


    submitButton.style.cursor =
        "default";


    submitButton.disabled =
        true;
}


/* ============================================================
   CLOSE RESOURCE POPUP
   ============================================================ */

function closeResourcePopup() {

    const overlay =
        document.getElementById(
            "resourceRequestOverlay"
        );


    if (overlay) {

        overlay.remove();
    }


    document.removeEventListener(
        "keydown",
        handleResourceEscape
    );
}


/* ============================================================
   ESCAPE KEY
   ============================================================ */

function handleResourceEscape(event) {

    if (event.key === "Escape") {

        closeResourcePopup();
    }
}


/* ============================================================
   ESCAPE HTML
   ============================================================ */

function escapeHTML(value) {

    return String(value ?? "")

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");
}


/* ============================================================
   GLOBAL FUNCTIONS
   ============================================================ */

window.openResourceRequest =
    openResourceRequest;


window.closeResourcePopup =
    closeResourcePopup;


window.setResourceDisasterInfo =
    setResourceDisasterInfo;


/* ============================================================
   POPUP ANIMATION
   ============================================================ */

const resourcePopupStyle =
    document.createElement("style");


resourcePopupStyle.textContent = `

    @keyframes resourcePopupOpen {

        from {

            opacity: 0;

            transform:
                scale(0.95)
                translateY(10px);
        }

        to {

            opacity: 1;

            transform:
                scale(1)
                translateY(0);
        }

    }

`;


document.head.appendChild(
    resourcePopupStyle
);


/* ============================================================
   INITIALIZATION
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "✅ resource_request.js loaded successfully"
        );

        loadDisasterInformation();

    }
);
