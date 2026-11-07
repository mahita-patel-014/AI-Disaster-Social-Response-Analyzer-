const API = `http://${window.location.hostname || "127.0.0.1"}:8000`;

// ============================================================
// ELEMENTS
// ============================================================

const fileInput =
    document.getElementById("newsImage");

const dropZone =
    document.getElementById("dropZone");

const chooseImage =
    document.getElementById("chooseImage");

const preview =
    document.getElementById("preview");

const uploadContent =
    document.getElementById("uploadContent");

const analyzeBtn =
    document.getElementById("analyzeBtn");

const loading =
    document.getElementById("loading");

const message =
    document.getElementById("message");

const result =
    document.getElementById("result");

const emptyResult =
    document.getElementById("emptyResult");

const headline =
    document.getElementById("headline");

const incidentLocation =
    document.getElementById("incidentLocation");

// ============================================================
// RESPONSE GENERATION ELEMENTS
// ============================================================

const generateResponseBox =
    document.getElementById("generateResponseBox");

const generateResponseBtn =
    document.getElementById("generateResponseBtn");

// ============================================================
// SELECTED IMAGE
// ============================================================

let selectedFile = null;

// ============================================================
// CHECK REQUIRED ELEMENTS
// ============================================================

if (!fileInput) {
    console.error("newsImage element not found.");
}

if (!dropZone) {
    console.error("dropZone element not found.");
}

if (!chooseImage) {
    console.error("chooseImage element not found.");
}

if (!analyzeBtn) {
    console.error("analyzeBtn element not found.");
}

// ============================================================
// CHOOSE IMAGE
// ============================================================

if (chooseImage && fileInput) {

    chooseImage.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            fileInput.click();

        }
    );

}

// ============================================================
// FILE INPUT
// ============================================================

if (fileInput) {

    fileInput.addEventListener(
        "change",
        function () {

            if (
                this.files &&
                this.files.length > 0
            ) {

                setImage(
                    this.files[0]
                );

            }

        }
    );

}

// ============================================================
// DRAG OVER
// ============================================================

if (dropZone) {

    dropZone.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            dropZone.classList.add(
                "drag-over"
            );

        }
    );

}

// ============================================================
// DRAG LEAVE
// ============================================================

if (dropZone) {

    dropZone.addEventListener(
        "dragleave",
        function () {

            dropZone.classList.remove(
                "drag-over"
            );

        }
    );

}

// ============================================================
// DROP IMAGE
// ============================================================

if (dropZone) {

    dropZone.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            dropZone.classList.remove(
                "drag-over"
            );

            const files =
                event.dataTransfer.files;

            if (
                files &&
                files.length > 0
            ) {

                setImage(
                    files[0]
                );

            }

        }
    );

}

// ============================================================
// SET IMAGE
// ============================================================

function setImage(file) {

    // --------------------------------------------------------
    // Validate file
    // --------------------------------------------------------

    if (!file) {

        showMessage(
            "Please select an image.",
            "error"
        );

        return;

    }

    // --------------------------------------------------------
    // Validate MIME type
    // --------------------------------------------------------

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/bmp"
    ];

    if (
        file.type &&
        !allowedTypes.includes(
            file.type
        )
    ) {

        showMessage(
            "Please upload JPG, JPEG, PNG, WEBP, GIF or BMP.",
            "error"
        );

        return;

    }

    // --------------------------------------------------------
    // Validate size
    // --------------------------------------------------------

    if (
        file.size >
        10 * 1024 * 1024
    ) {

        showMessage(
            "Image size must be less than 10 MB.",
            "error"
        );

        return;

    }

    // --------------------------------------------------------
    // Store selected file
    // --------------------------------------------------------

    selectedFile = file;

    // --------------------------------------------------------
    // Hide old response button
    // --------------------------------------------------------

    if (generateResponseBox) {

        generateResponseBox.classList.add(
            "hidden"
        );

    }

    if (result) {
        result.classList.add("hidden");
    }

    if (emptyResult) {
        emptyResult.classList.remove("hidden");
    }

    localStorage.removeItem("ai_cp_real_news");

    // --------------------------------------------------------
    // Preview
    // --------------------------------------------------------

    if (preview) {

        const objectURL =
            URL.createObjectURL(
                file
            );

        preview.src =
            objectURL;

        preview.classList.remove(
            "hidden"
        );

    }

    // --------------------------------------------------------
    // Hide upload instructions
    // --------------------------------------------------------

    if (uploadContent) {

        uploadContent.classList.add(
            "hidden"
        );

    }

    // --------------------------------------------------------
    // Show message
    // --------------------------------------------------------

    showMessage(
        "Image selected successfully.",
        "success"
    );

}

// ============================================================
// ANALYZE NEWS
// ============================================================

if (analyzeBtn) {

    analyzeBtn.addEventListener(
        "click",
        analyzeNews
    );

}

// ============================================================
// ANALYZE NEWS FUNCTION
// ============================================================

async function analyzeNews() {

    // --------------------------------------------------------
    // IMAGE REQUIRED
    // --------------------------------------------------------

    if (!selectedFile) {

        showMessage(
            "Please drag and drop a disaster image first.",
            "error"
        );

        return;

    }

    // --------------------------------------------------------
    // HEADLINE REQUIRED
    // --------------------------------------------------------

    const headlineText =
        headline
            ? headline.value.trim()
            : "";

    if (!headlineText) {

        showMessage(
            "Please enter the news headline.",
            "error"
        );

        if (headline) {

            headline.focus();

        }

        return;

    }

    // --------------------------------------------------------
    // LOADING
    // --------------------------------------------------------

    if (loading) {

        loading.classList.remove(
            "hidden"
        );

    }

    analyzeBtn.disabled =
        true;

    showMessage(
        "",
        ""
    );

    // --------------------------------------------------------
    // HIDE PREVIOUS RESPONSE BUTTON
    // --------------------------------------------------------

    if (generateResponseBox) {

        generateResponseBox.classList.add(
            "hidden"
        );

    }

    // --------------------------------------------------------
    // CREATE FORM DATA
    // --------------------------------------------------------

    const formData =
        new FormData();

    formData.append(
        "image",
        selectedFile
    );

    formData.append(
        "headline",
        headlineText
    );

    formData.append(
        "location",
        incidentLocation?.value.trim() || ""
    );

    try {

        // ----------------------------------------------------
        // SEND TO FASTAPI
        // ----------------------------------------------------

        const response =
            await fetch(
                `${API}/api/analyze/news`,
                {
                    method: "POST",
                    body: formData
                }
            );

        // ----------------------------------------------------
        // RESPONSE CONTENT TYPE
        // ----------------------------------------------------

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";

        let data;

        if (
            contentType.includes(
                "application/json"
            )
        ) {

            data =
                await response.json();

        } else {

            const text =
                await response.text();

            throw new Error(
                text ||
                "FastAPI returned an invalid response."
            );

        }

        // ----------------------------------------------------
        // API ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "News analysis failed."
            );

        }

        // ----------------------------------------------------
        // DEBUG
        // ----------------------------------------------------

        console.log(
            "========================================"
        );

        console.log(
            "FULL AI ANALYSIS RESPONSE"
        );

        console.log(
            data
        );

        console.log(
            "========================================"
        );

        // ----------------------------------------------------
        // DISPLAY RESULT
        // ----------------------------------------------------

        displayResult(
            data
        );

        // ----------------------------------------------------
        // GET RESPONSE INFORMATION
        // ----------------------------------------------------

        const disaster =
            data.disaster || {};

        const disasterType =
            disaster.disaster_type ||
            data.disaster_type ||
            "Unknown";

        const location =
            data.location ||
            data.disaster_location ||
            "Not detected";

        let status =
            data.status ||
            data.news_status ||
            "NEEDS_REVIEW";

        status =
            String(
                status
            )
            .trim()
            .toUpperCase();

        // ----------------------------------------------------
        // RESPONSE FLOW
        //
        // REAL:
        // Save news + show Generate Response button
        //
        // FAKE:
        // No response
        //
        // NEEDS REVIEW:
        // No response
        // ----------------------------------------------------

        if (status === "REAL") {

            await saveRealNews(
                data,
                headlineText,
                disasterType,
                location
            );

            if (generateResponseBox) {

                generateResponseBox.classList.remove(
                    "hidden"
                );

            }

        } else {

            if (generateResponseBox) {

                generateResponseBox.classList.add(
                    "hidden"
                );

            }

            // Remove old REAL news
            localStorage.removeItem(
                "ai_cp_real_news"
            );

        }

        // ----------------------------------------------------
        // SUCCESS MESSAGE
        // ----------------------------------------------------

        showMessage(
            "News analysis completed successfully.",
            "success"
        );

    } catch (error) {

        console.error(
            "ANALYSIS ERROR:",
            error
        );

        showMessage(
            error.message ||
            "Unable to connect to the FastAPI server.",
            "error"
        );

    } finally {

        // ----------------------------------------------------
        // STOP LOADING
        // ----------------------------------------------------

        if (loading) {

            loading.classList.add(
                "hidden"
            );

        }

        analyzeBtn.disabled =
            false;

    }

}

// ============================================================
// SAVE REAL NEWS
// ============================================================

async function saveRealNews(
    data,
    headlineText,
    disasterType,
    location
) {

    try {

        const disaster =
            data.disaster || {};

        let imageData =
            "";

        // ----------------------------------------------------
        // Convert uploaded image to Data URL
        // ----------------------------------------------------

        if (selectedFile) {

            imageData =
                await imageToDataURL(
                    selectedFile
                );

        }

        // ----------------------------------------------------
        // Extract status
        // ----------------------------------------------------

        let status =
            data.status ||
            data.news_status ||
            "NEEDS_REVIEW";

        status =
            String(
                status
            )
            .trim()
            .toUpperCase();

        // ----------------------------------------------------
        // Only save REAL news
        // ----------------------------------------------------

        if (
            status !== "REAL"
        ) {

            return;

        }

        // ----------------------------------------------------
        // Create REAL news object
        // ----------------------------------------------------

        const realNews = {

            status:
                "REAL",

            analysis_id:
                data.analysis_id || "",

            headline:
                headlineText,

            disaster_type:
                disasterType,

            location:
                location,

            confidence:
                Number(
                    disaster.confidence ??
                    data.confidence ??
                    data.image_confidence ??
                    0
                ),

            verification_confidence:
                Number(
                    data.verification_confidence ??
                    data.verification_score ??
                    0
                ),

            headline_match_score:
                Number(
                    data.headline_match_score ??
                    data.verification_confidence ??
                    0
                ),

            verification_score:
                Number(
                    data.verification_score ??
                    data.verification_confidence ??
                    0
                ),

            evidence:
                Array.isArray(
                    data.evidence
                )
                    ? data.evidence
                    : [],

            reason:
                data.reason ||
                "",

            image:
                imageData,

            created_at:
                new Date().toISOString()

        };

        // ----------------------------------------------------
        // Save for response screen
        // ----------------------------------------------------

        localStorage.setItem(
            "ai_cp_real_news",
            JSON.stringify(
                realNews
            )
        );

        console.log(
            "REAL NEWS SAVED:",
            realNews
        );

    } catch (error) {

        console.error(
            "Unable to save REAL news:",
            error
        );

        throw new Error(
            "The verification is REAL, but this browser could not save it for the response workflow."
        );

    }

}

// ============================================================
// IMAGE TO DATA URL
// ============================================================

function imageToDataURL(file) {

    return new Promise(
        function (resolve, reject) {

            const reader =
                new FileReader();

            reader.onload =
                function () {

                    resolve(
                        reader.result
                    );

                };

            reader.onerror =
                function () {

                    reject(
                        new Error(
                            "Unable to read uploaded image."
                        )
                    );

                };

            reader.readAsDataURL(
                file
            );

        }
    );

}

// ============================================================
// GENERATE RESPONSE BUTTON
// ============================================================

if (generateResponseBtn) {

    generateResponseBtn.addEventListener(
        "click",
        function () {

            const savedNews =
                localStorage.getItem(
                    "ai_cp_real_news"
                );

            if (!savedNews) {

                showMessage(
                    "No REAL disaster news is available for response generation.",
                    "error"
                );

                return;

            }

            try {

                const realNews =
                    JSON.parse(
                        savedNews
                    );

                const status =
                    String(
                        realNews.status ||
                        ""
                    )
                    .trim()
                    .toUpperCase();

                if (
                    status !== "REAL"
                ) {

                    showMessage(
                        "Emergency response is available only for REAL news.",
                        "error"
                    );

                    return;

                }

                window.location.href =
                    "news_verification.html";

            } catch (error) {

                console.error(
                    "Saved news parsing error:",
                    error
                );

                showMessage(
                    "Saved disaster news data is invalid.",
                    "error"
                );

            }

        }
    );

}

// ============================================================
// DISPLAY RESULT
// ============================================================

function displayResult(data) {

    // --------------------------------------------------------
    // GET DISASTER RESULT
    // --------------------------------------------------------

    const disaster =
        data.disaster && typeof data.disaster === "object"
            ? data.disaster
            : {};

    const disasterType =
        disaster.disaster_type ||
        data.disaster_type ||
        (typeof data.disaster === "string" ? data.disaster : "") ||
        "Unknown";
    const imageConfidence = Number(
        disaster.confidence ??
        data.image_confidence ??
        data.confidence ??
        0
    );

    // --------------------------------------------------------
    // SHOW RESULT
    // --------------------------------------------------------

    if (emptyResult) {

        emptyResult.classList.add(
            "hidden"
        );

    }

    if (result) {

        result.classList.remove(
            "hidden"
        );

    }

    // --------------------------------------------------------
    // DISASTER TYPE
    // --------------------------------------------------------

    const resolvedTypeElement =
        document.getElementById("disasterType");

    if (resolvedTypeElement) {
        resolvedTypeElement.textContent =
            capitalize(disasterType);
    }

    const confidenceElement =
        document.getElementById("confidence");
    const confidenceBar =
        document.getElementById("confidenceBar");
    const validConfidence =
        Number.isFinite(imageConfidence)
            ? Math.min(100, Math.max(0, imageConfidence))
            : 0;

    if (confidenceElement) {
        confidenceElement.textContent =
            `${validConfidence.toFixed(2)}%`;
    }

    if (confidenceBar) {
        confidenceBar.style.width =
            `${validConfidence}%`;
    }

    const disasterTypeNote =
        document.getElementById("disasterTypeNote");

    if (disasterTypeNote) {
        disasterTypeNote.textContent =
            data.disaster_type_note ||
            disaster.disaster_type_note ||
            "";
    }

    // --------------------------------------------------------
    // LOCATION
    // --------------------------------------------------------

    const locationElement =
        document.getElementById(
            "location"
        );

    const location =
        data.location ||
        data.disaster_location ||
        "Not detected";

    if (locationElement) {

        locationElement.textContent =
            location;

    }

    // --------------------------------------------------------
    // NEWS STATUS
    // --------------------------------------------------------

    let status =
        data.status ||
        data.news_status ||
        "NEEDS_REVIEW";

    status =
        String(
            status
        )
        .trim()
        .toUpperCase();

    // --------------------------------------------------------
    // NEWS STATUS ELEMENTS
    // --------------------------------------------------------

    const newsStatus =
        document.getElementById(
            "newsStatus"
        );

    const newsStatusValue =
        document.getElementById(
            "newsStatusValue"
        );

    const newsStatusBadge =
        document.getElementById(
            "newsStatusBadge"
        );

    if (newsStatus) {

        newsStatus.textContent =
            status.replaceAll("_", " ");

    }

    if (newsStatusValue) {

        newsStatusValue.textContent =
            status.replaceAll("_", " ");

    }

    if (newsStatusBadge) {

        newsStatusBadge.textContent =
            status.replaceAll("_", " ");

        newsStatusBadge.className =
            "status-badge";

        newsStatusBadge.classList.add(
            status.toLowerCase()
        );

    }

    // --------------------------------------------------------
    // EVIDENCE
    // --------------------------------------------------------

    const evidence =
        Array.isArray(
            data.evidence
        )
            ? data.evidence
            : [];

    const sourceCount =
        document.getElementById("sourceCount");

    if (sourceCount) {
        sourceCount.textContent =
            String(evidence.length);
    }

    // --------------------------------------------------------
    // REASON
    // --------------------------------------------------------

    const verificationReason =
        document.getElementById(
            "verificationReason"
        );

    if (verificationReason) {

        const explanation =
            data.reason ||
            "No verification explanation available.";
        const imageAssessment =
            data.image_assessment ||
            disaster.disaster_type_note ||
            "";

        verificationReason.textContent =
            imageAssessment
                ? `${explanation} ${imageAssessment}`
                : explanation;

    }

    // --------------------------------------------------------
    // DISPLAY EVIDENCE
    // --------------------------------------------------------

    displayEvidence(
        evidence
    );

}

// ============================================================
// DISPLAY NEWS EVIDENCE
// ============================================================

function displayEvidence(
    evidence
) {

    const evidenceList =
        document.getElementById(
            "evidenceList"
        );

    if (!evidenceList) {

        return;

    }

    evidenceList.innerHTML =
        "";

    if (
        !Array.isArray(
            evidence
        ) ||
        evidence.length === 0
    ) {

        evidenceList.innerHTML = `

            <div class="evidence-item">

                <p>
                    No matching Google News evidence found.
                </p>

            </div>

        `;

        return;

    }

    evidence.forEach(
        function (item) {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "evidence-item";

            const title =
                item.title ||
                "News Source";

            const source =
                item.source ||
                "Google News";

            const published =
                item.published ||
                "";

            const similarity =
                Number(
                    item.similarity ??
                    0
                );

            const url =
                item.url ||
                "";

            div.innerHTML = `

                <h4>
                    ${escapeHtml(
                        title
                    )}
                </h4>

                <p>

                    <strong>
                        Source:
                    </strong>

                    ${escapeHtml(
                        source
                    )}

                </p>

                ${
                    published
                    ? `

                        <p>

                            <strong>
                                Published:
                            </strong>

                            ${escapeHtml(
                                published
                            )}

                        </p>

                    `
                    : ""
                }

                <p>

                    <strong>
                        Match:
                    </strong>

                    ${formatNumber(
                        similarity
                    )}%

                </p>

                ${
                    url
                    ? `

                        <p>

                            <a
                                href="${escapeAttribute(
                                    url
                                )}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                View News Source
                            </a>

                        </p>

                    `
                    : ""
                }

            `;

            evidenceList.appendChild(
                div
            );

        }
    );

}

// ============================================================
// MESSAGE
// ============================================================

function showMessage(
    text,
    type
) {

    if (!message) {

        return;

    }

    message.textContent =
        text;

    message.className =
        "message";

    if (type) {

        message.classList.add(
            type
        );

    }

}

// ============================================================
// FORMAT NUMBER
// ============================================================

function formatNumber(
    value
) {

    const number =
        Number(
            value
        );

    if (
        !Number.isFinite(
            number
        )
    ) {

        return "0.00";

    }

    return number.toFixed(
        2
    );

}

// ============================================================
// CAPITALIZE
// ============================================================

function capitalize(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "-";

    }

    const text =
        String(
            value
        );

    return (
        text
            .charAt(0)
            .toUpperCase()
        +
        text
            .slice(1)
    );

}

// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(
    value
) {

    return String(
        value
    )

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}

// ============================================================
// ATTRIBUTE ESCAPE
// ============================================================

function escapeAttribute(
    value
) {

    return escapeHtml(
        value
    );

}

// ============================================================
// NOTE:
//
// The old generateResponse() function has intentionally been
// removed from this file.
//
// Response generation is now performed on:
//     news_verification.html
//
// That page reads:
//     localStorage["ai_cp_real_news"]
//
// and calls:
//     POST /api/response/generate
//
// This prevents response generation from happening
// automatically during news analysis.
// ============================================================