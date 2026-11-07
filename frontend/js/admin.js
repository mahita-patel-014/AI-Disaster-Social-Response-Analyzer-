const API =
    "http://127.0.0.1:8000";

// ============================================================
// CURRENT ADMIN
// ============================================================

let current = null;
let resourceRequestData = [];

try {

    current = JSON.parse(
        localStorage.getItem(
            "ai_cp_user"
        ) || "null"
    );

} catch (error) {

    console.error(
        "Invalid localStorage user:",
        error
    );

    current = null;

}


// ============================================================
// ADMIN SECURITY
// ============================================================

if (
    !current ||
    String(current.role || "").toLowerCase() !== "admin"
) {

    window.location.href =
        "register.html";

}


// ============================================================
// WELCOME
// ============================================================

const welcomeElement =
    document.getElementById(
        "welcome"
    );

if (welcomeElement) {

    welcomeElement.textContent =
        `Welcome, ${current?.username || "Admin"}`;

}


// ============================================================
// LOGOUT
// ============================================================

const logoutButton =
    document.getElementById(
        "logout"
    );

if (logoutButton) {

    logoutButton.onclick = () => {

        localStorage.removeItem(
            "ai_cp_user"
        );

        window.location.href =
            "register.html";

    };

}


// ============================================================
// LOAD USERS
// ============================================================

async function loadUsers() {

    const userRows =
        document.getElementById(
            "userRows"
        );

    try {

        const response =
            await fetch(
                `${API}/api/admin/users`,
                {
                    method: "GET"
                }
            );


        if (!response.ok) {

            let errorMessage =
                "Unable to load users.";

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.detail ||
                    errorMessage;

            } catch (error) {

                console.warn(
                    "Could not read user error response.",
                    error
                );

            }

            throw new Error(
                errorMessage
            );

        }


        const data =
            await response.json();


        // ====================================================
        // ALWAYS MAKE SURE USERS IS AN ARRAY
        // ====================================================

        const users =
            Array.isArray(data?.users)
                ? data.users
                : [];


        console.log(
            "ADMIN USERS:",
            users
        );


        // ====================================================
        // TOTAL USERS
        // ====================================================

        const totalUsers =
            document.getElementById(
                "totalUsers"
            );

        if (totalUsers) {

            totalUsers.textContent =
                users.length;

        }


        // ====================================================
        // NORMAL USERS
        // ====================================================

        const normalUsers =
            document.getElementById(
                "normalUsers"
            );

        if (normalUsers) {

            normalUsers.textContent =
                users.filter(
                    user =>
                        String(
                            user?.role || ""
                        ).toLowerCase()
                        === "user"
                ).length;

        }


        // ====================================================
        // ADMIN USERS
        // ====================================================

        const adminUsers =
            document.getElementById(
                "adminUsers"
            );

        if (adminUsers) {

            adminUsers.textContent =
                users.filter(
                    user =>
                        String(
                            user?.role || ""
                        ).toLowerCase()
                        === "admin"
                ).length;

        }


        // ====================================================
        // USER TABLE
        // ====================================================

        if (!userRows) {

            console.warn(
                "userRows element not found."
            );

            return;

        }


        if (users.length === 0) {

            userRows.innerHTML = `

                <tr>

                    <td
                        colspan="5"
                        style="text-align:center;"
                    >
                        No registered users found.
                    </td>

                </tr>

            `;

            return;

        }


        userRows.innerHTML =

            users.map(
                user => {

                    const id =
                        String(
                            user?.id || ""
                        );


                    const username =
                        esc(
                            user?.username || "-"
                        );


                    const email =
                        esc(
                            user?.email || "-"
                        );


                    const role =
                        esc(
                            capitalize(
                                user?.role || "user"
                            )
                        );


                    const created =
                        formatDate(
                            user?.created_at
                        );


                    const emailForCheck =
                        String(
                            user?.email || ""
                        ).toLowerCase();


                    let deleteButton =
                        "";


                    // ------------------------------------------------
                    // KEEP ADMIN ACCOUNT PROTECTED
                    // ------------------------------------------------

                    if (
                        emailForCheck !==
                        "mahip1234@gmail.com"
                    ) {

                        deleteButton = `

                            <button
                                class="delete"
                                onclick="deleteUser('${escAttribute(id)}')"
                            >
                                Delete
                            </button>

                        `;

                    }


                    return `

<tr>

<td>
    ${username}
</td>

<td>
    ${email}
</td>

<td>
    ${role}
</td>

<td>
    ${created}
</td>

<td>

    <button
        class="edit"
        onclick='openEdit(${JSON.stringify(user).replace(/'/g, "&#39;")})'
    >
        Edit
    </button>

    ${deleteButton}

</td>

</tr>

                    `;

                }
            )
            .join("");


    } catch (error) {

        console.error(
            "Load users error:",
            error
        );


        if (userRows) {

            userRows.innerHTML = `

                <tr>

                    <td
                        colspan="5"
                        style="
                            text-align:center;
                            color:#d33;
                            padding:20px;
                        "
                    >

                        ${esc(
                            error.message ||
                            "Unable to load users."
                        )}

                    </td>

                </tr>

            `;

        }

    }

}


// ============================================================
// LOAD REGISTRATION LOGS
// ============================================================
//
// Your current admin_dashboard.html does NOT contain
// a Registration Logs section.
//
// Therefore this function does not make an unnecessary
// request when logRows and totalLogs are absent.
//
// ============================================================

async function loadLogs() {

    const logRows =
        document.getElementById(
            "logRows"
        );


    const totalLogs =
        document.getElementById(
            "totalLogs"
        );


    // --------------------------------------------------------
    // No logs section in current HTML
    // --------------------------------------------------------

    if (
        !logRows &&
        !totalLogs
    ) {

        console.log(
            "Registration Logs section not present. Skipping."
        );

        return;

    }


    try {

        const response =
            await fetch(
                `${API}/api/admin/logs`,
                {
                    method: "GET"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Registration logs endpoint unavailable."
            );

        }


        const data =
            await response.json();


        const logs =
            Array.isArray(
                data?.logs
            )
                ? data.logs
                : [];


        if (totalLogs) {

            totalLogs.textContent =
                logs.length;

        }


        if (!logRows) {

            return;

        }


        if (logs.length === 0) {

            logRows.innerHTML = `

                <tr>

                    <td
                        colspan="6"
                        style="text-align:center;"
                    >
                        No registration logs found.
                    </td>

                </tr>

            `;

            return;

        }


        logRows.innerHTML =

            logs.map(
                log => `

<tr>

<td>
    ${esc(
        log?.action || "-"
    )}
</td>

<td>
    ${esc(
        log?.username || "-"
    )}
</td>

<td>
    ${esc(
        log?.email || "-"
    )}
</td>

<td>
    ${esc(
        log?.role || "-"
    )}
</td>

<td>
    ${
        log?.success
            ? "Success"
            : "Failed"
    }
</td>

<td>
    ${formatDate(
        log?.created_at
    )}
</td>

</tr>

                `
            )
            .join("");


    } catch (error) {

        console.warn(
            "Registration logs unavailable:",
            error
        );


        if (totalLogs) {

            totalLogs.textContent =
                "0";

        }


        if (logRows) {

            logRows.innerHTML = `

                <tr>

                    <td
                        colspan="6"
                        style="text-align:center;"
                    >
                        Registration logs unavailable.
                    </td>

                </tr>

            `;

        }

    }

}


// ============================================================
// RESOURCE REQUESTS
// ============================================================

async function loadResourceRequests() {

    const rows = document.getElementById("resourceRequestRows");
    const total = document.getElementById("resourceRequestTotal");
    if (!rows) return;

    rows.innerHTML = '<tr><td colspan="10" style="text-align:center;">Loading resource requests...</td></tr>';

    try {
        const response = await fetch(`${API}/api/admin/resource-requests?limit=1000`);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Unable to load resource requests.");
        }

        resourceRequestData = Array.isArray(data.requests) ? data.requests : [];
        if (total) {
            total.textContent = `${resourceRequestData.length} saved resource request(s)`;
        }

        if (!resourceRequestData.length) {
            rows.innerHTML = '<tr><td colspan="10" style="text-align:center;padding:20px;">No resource requests saved yet.</td></tr>';
            return;
        }

        rows.innerHTML = resourceRequestData.map(request => `
            <tr>
                <td>${esc(request.disaster_type || "-")}</td>
                <td>${esc(request.location || "-")}</td>
                <td>${esc(request.requester_name || "-")}</td>
                <td>${esc(request.resource_name || "-")}</td>
                <td class="resource-request-details">${esc(request.resource_details || "-")}</td>
                <td>${esc(request.resource_type || "-")}</td>
                <td>${esc(request.quantity || "-")}</td>
                <td>${esc(request.status || "requested")}</td>
                <td>${formatDate(request.created_at)}</td>
                <td>${esc(request.id || "-")}</td>
            </tr>
        `).join("");
    } catch (error) {
        console.error("Load resource requests error:", error);
        resourceRequestData = [];
        if (total) total.textContent = "Could not load resource requests.";
        rows.innerHTML = `<tr><td colspan="10" style="text-align:center;color:#d33;padding:20px;">${esc(error.message || "Unable to load resource requests.")}</td></tr>`;
    }
}

function exportResourceRequestsCsv() {
    if (!resourceRequestData.length) {
        window.alert("There are no resource requests to export.");
        return;
    }

    const columns = [
        ["Request ID", "id"],
        ["Disaster", "disaster_type"],
        ["Location", "location"],
        ["Requester", "requester_name"],
        ["Resource", "resource_name"],
        ["Resource Details", "resource_details"],
        ["Resource Type", "resource_type"],
        ["Quantity", "quantity"],
        ["Status", "status"],
        ["Created At", "created_at"]
    ];
    const csvCell = value => {
        let text = String(value ?? "");
        if (/^[\s]*[=+\-@]/.test(text)) text = `'${text}`;
        return `"${text.replace(/"/g, '""')}"`;
    };
    const csv = [
        columns.map(([label]) => csvCell(label)).join(","),
        ...resourceRequestData.map(request =>
            columns.map(([, key]) => csvCell(request[key])).join(",")
        )
    ].join("\r\n");
    const blob = new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `resource_requests_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ============================================================
// BIG-DATA BATCH ANALYTICS PROTOTYPE
// ============================================================

async function loadBigDataAnalytics() {
    const notice = document.getElementById("bigDataNotice");
    const disasterRows = document.getElementById("bigDataDisasterRows");
    const locationRows = document.getElementById("bigDataLocationRows");
    const resourceRows = document.getElementById("bigDataResourceRows");
    if (!notice || !disasterRows || !locationRows || !resourceRows) return;

    notice.textContent = "Running batch aggregation over saved MongoDB records...";
    try {
        const response = await fetch(`${API}/api/admin/big-data/summary`);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Unable to run batch analytics.");
        }

        document.getElementById("bigDataProcessed").textContent =
            String(data.processed_records ?? 0);
        document.getElementById("bigDataAnalysisCount").textContent =
            String(data.analysis_records ?? 0);
        document.getElementById("bigDataResourceCount").textContent =
            String(data.resource_requests ?? 0);

        renderAnalyticsCounts(disasterRows, data.disaster_breakdown, "No disaster reports found.");
        renderAnalyticsCounts(locationRows, data.location_breakdown, "No location data found.");

        const resources = Array.isArray(data.resource_breakdown)
            ? data.resource_breakdown
            : [];
        resourceRows.innerHTML = resources.length
            ? resources.map(item => `
                <tr>
                    <td>${esc(item.disaster_type || "Unknown")}</td>
                    <td>${esc(item.location || "Not detected")}</td>
                    <td>${esc(item.resource_type || "Other")}</td>
                    <td>${esc(item.request_count ?? 0)}</td>
                </tr>
            `).join("")
            : '<tr><td colspan="4" style="text-align:center;padding:18px;">No resource request data found.</td></tr>';

        notice.textContent =
            `${data.processing_mode || "MongoDB batch aggregation prototype"} — ${data.infrastructure_note || "This is not a Hadoop/Spark deployment."}`;
    } catch (error) {
        console.error("Big-data batch analytics error:", error);
        notice.textContent = error.message || "Unable to load batch analytics.";
        disasterRows.innerHTML = '<tr><td colspan="2" style="text-align:center;color:#d33;">Analytics unavailable.</td></tr>';
        locationRows.innerHTML = '<tr><td colspan="2" style="text-align:center;color:#d33;">Analytics unavailable.</td></tr>';
        resourceRows.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#d33;">Analytics unavailable.</td></tr>';
    }
}

function renderAnalyticsCounts(target, items, emptyMessage) {
    const rows = Array.isArray(items) ? items : [];
    target.innerHTML = rows.length
        ? rows.map(item => `
            <tr>
                <td>${esc(item.name || "Unknown")}</td>
                <td>${esc(item.count ?? 0)}</td>
            </tr>
        `).join("")
        : `<tr><td colspan="2" style="text-align:center;padding:18px;">${esc(emptyMessage)}</td></tr>`;
}


// ============================================================
// LOAD NEWS ANALYSIS
// ============================================================
//
// IMPORTANT:
//
// The HTML already contains:
//
// <section class="panel">
//     ...
//     <tbody id="analysisRows">
// </section>
//
// Therefore this function ONLY loads data.
//
// It does NOT create another News Analysis History panel.
//
// ============================================================

async function loadAnalysis() {

    const analysisRows =
        document.getElementById(
            "analysisRows"
        );


    // --------------------------------------------------------
    // Make sure HTML table exists
    // --------------------------------------------------------

    if (!analysisRows) {

        console.error(
            "analysisRows element not found in HTML."
        );

        return;

    }


    try {

        // ----------------------------------------------------
        // Loading message
        // ----------------------------------------------------

        analysisRows.innerHTML = `

            <tr>

                <td
                    colspan="9"
                    style="
                        text-align:center;
                        padding:20px;
                    "
                >
                    Loading analysis data...
                </td>

            </tr>

        `;


        // ----------------------------------------------------
        // GET ANALYSIS DATA
        // ----------------------------------------------------

        const response =
            await fetch(
                `${API}/api/admin/analysis?limit=100`,
                {
                    method: "GET"
                }
            );


        // ----------------------------------------------------
        // HANDLE API ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            let errorMessage =
                "Unable to load analysis data.";


            try {

                const errorData =
                    await response.json();


                errorMessage =
                    errorData?.detail ||
                    errorMessage;

            } catch (error) {

                console.warn(
                    "Could not parse analysis error.",
                    error
                );

            }


            throw new Error(
                errorMessage
            );

        }


        // ----------------------------------------------------
        // RESPONSE JSON
        // ----------------------------------------------------

        const data =
            await response.json();


        console.log(
            "ADMIN ANALYSIS RESPONSE:",
            data
        );


        // ----------------------------------------------------
        // ALWAYS MAKE SURE ANALYSIS IS AN ARRAY
        // ----------------------------------------------------

        const analysis =
            Array.isArray(
                data?.analysis
            )
                ? data.analysis
                : [];


        console.log(
            "ADMIN ANALYSIS RECORDS:",
            analysis
        );


        // ====================================================
        // TOTAL ANALYSIS
        // ====================================================

        const totalAnalysis =
            document.getElementById(
                "totalAnalysis"
            );


        if (totalAnalysis) {

            totalAnalysis.textContent =
                analysis.length;

        }


        // ====================================================
        // NO DATA
        // ====================================================

        if (analysis.length === 0) {

            analysisRows.innerHTML = `

                <tr>

                    <td
                        colspan="9"
                        style="
                            text-align:center;
                            padding:25px;
                        "
                    >

                        No news analysis records
                        found in MongoDB.

                    </td>

                </tr>

            `;

            return;

        }


        // ====================================================
        // DISPLAY NEWS ANALYSIS DATA
        // ====================================================

        analysisRows.innerHTML =

            analysis.map(
                item => {

                    // ----------------------------------------
                    // EMAIL
                    // ----------------------------------------

                    const email =
                        item?.email ||
                        "-";


                    // ----------------------------------------
                    // HEADLINE
                    // ----------------------------------------

                    const headline =
                        item?.headline ||
                        "-";


                    // ----------------------------------------
                    // IMAGE
                    // ----------------------------------------

                    const image =
                        item?.image_filename ||
                        item?.image ||
                        "-";


                    // ----------------------------------------
                    // DISASTER TYPE
                    // ----------------------------------------

                    const disaster =
                        item?.disaster_type ||
                        "Unknown";


                    // ----------------------------------------
                    // CONFIDENCE
                    // ----------------------------------------

                    const confidence =
                        toNumber(
                            item?.confidence
                        );


                    // ----------------------------------------
                    // LOCATION
                    // ----------------------------------------

                    const location =
                        item?.location ||
                        "Not detected";


                    // ----------------------------------------
                    // STATUS
                    // ----------------------------------------

                    const status =
                        String(
                            item?.status ||
                            "UNVERIFIED"
                        ).toUpperCase();


                    // ----------------------------------------
                    // VERIFICATION CONFIDENCE
                    // ----------------------------------------

                    const verification =
                        toNumber(
                            item?.verification_confidence
                        );


                    // ----------------------------------------
                    // CREATED DATE
                    // ----------------------------------------

                    const created =
                        formatDate(
                            item?.created_at
                        );


                    // ----------------------------------------
                    // RETURN TABLE ROW
                    // ----------------------------------------

                    return `

<tr>

<td>
    ${esc(email)}
</td>

<td
    title="${escAttribute(headline)}"
>
    ${esc(
        shorten(
            headline,
            60
        )
    )}
</td>

<td>
    ${esc(image)}
</td>

<td>

    <strong>
        ${esc(
            capitalize(
                disaster
            )
        )}
    </strong>

</td>

<td>
    ${confidence.toFixed(2)}%
</td>

<td>
    ${esc(location)}
</td>

<td>

    <span
        class="status-badge ${escAttribute(
            status.toLowerCase()
        )}"
    >

        ${esc(status)}

    </span>

</td>

<td>
    ${verification.toFixed(2)}%
</td>

<td>
    ${created}
</td>

</tr>

                    `;

                }
            )
            .join("");


    } catch (error) {

        console.error(
            "Analysis loading error:",
            error
        );


        const totalAnalysis =
            document.getElementById(
                "totalAnalysis"
            );


        if (totalAnalysis) {

            totalAnalysis.textContent =
                "0";

        }


        analysisRows.innerHTML = `

            <tr>

                <td
                    colspan="9"
                    style="
                        text-align:center;
                        color:#d33;
                        padding:25px;
                    "
                >

                    ${esc(
                        error.message ||
                        "Unable to load analysis data."
                    )}

                </td>

            </tr>

        `;

    }

}


// ============================================================
// OPEN EDIT MODAL
// ============================================================

function openEdit(user) {

    if (!user) {

        return;

    }


    const editId =
        document.getElementById(
            "editId"
        );


    const editUsername =
        document.getElementById(
            "editUsername"
        );


    const editEmail =
        document.getElementById(
            "editEmail"
        );


    const editRole =
        document.getElementById(
            "editRole"
        );


    const editPassword =
        document.getElementById(
            "editPassword"
        );


    const editModal =
        document.getElementById(
            "editModal"
        );


    if (editId) {

        editId.value =
            user.id || "";

    }


    if (editUsername) {

        editUsername.value =
            user.username || "";

    }


    if (editEmail) {

        editEmail.value =
            user.email || "";

    }


    if (editRole) {

        editRole.value =
            user.role || "user";

    }


    if (editPassword) {

        editPassword.value =
            "";

    }


    if (editModal) {

        editModal.classList.remove(
            "hidden"
        );

    }

}


// ============================================================
// CLOSE MODAL
// ============================================================

function closeModal() {

    const editModal =
        document.getElementById(
            "editModal"
        );


    if (editModal) {

        editModal.classList.add(
            "hidden"
        );

    }

}


// ============================================================
// SAVE EDIT
// ============================================================

async function saveEdit() {

    const id =
        document
            .getElementById(
                "editId"
            )
            ?.value
            ?.trim();


    if (!id) {

        alert(
            "User ID is missing."
        );

        return;

    }


    const username =
        document
            .getElementById(
                "editUsername"
            )
            ?.value
            ?.trim();


    const email =
        document
            .getElementById(
                "editEmail"
            )
            ?.value
            ?.trim();


    const role =
        document
            .getElementById(
                "editRole"
            )
            ?.value;


    const password =
        document
            .getElementById(
                "editPassword"
            )
            ?.value
            ?.trim();


    if (
        !username ||
        !email
    ) {

        alert(
            "Username and email are required."
        );

        return;

    }


    const body = {

        username:
            username,

        email:
            email,

        role:
            role || "user",

        password:
            password || null

    };


    try {

        const response =
            await fetch(

                `${API}/api/admin/users/${encodeURIComponent(id)}`,

                {

                    method:
                        "PUT",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            body
                        )

                }

            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data?.detail ||
                "Update failed."
            );

            return;

        }


        alert(
            "User updated successfully."
        );


        closeModal();


        await loadUsers();


    } catch (error) {

        console.error(
            "Update user error:",
            error
        );


        alert(
            error.message ||
            "Could not update user."
        );

    }

}


// ============================================================
// DELETE USER
// ============================================================

async function deleteUser(id) {

    if (!id) {

        alert(
            "User ID is missing."
        );

        return;

    }


    if (
        !confirm(
            "Delete this user permanently?"
        )
    ) {

        return;

    }


    try {

        const response =
            await fetch(

                `${API}/api/admin/users/${encodeURIComponent(id)}`,

                {

                    method:
                        "DELETE"

                }

            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data?.detail ||
                "Delete failed."
            );

            return;

        }


        alert(
            "User deleted successfully."
        );


        await loadUsers();


    } catch (error) {

        console.error(
            "Delete user error:",
            error
        );


        alert(
            error.message ||
            "Could not delete user."
        );

    }

}


// ============================================================
// DATE FORMAT
// ============================================================

function formatDate(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "-";

    }


    const date =
        new Date(
            value
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return esc(
            String(value)
        );

    }


    return date.toLocaleString();

}


// ============================================================
// NUMBER CONVERSION
// ============================================================

function toNumber(value) {

    const number =
        Number(
            value
        );


    if (
        Number.isFinite(
            number
        )
    ) {

        return number;

    }


    return 0;

}


// ============================================================
// SHORTEN TEXT
// ============================================================

function shorten(
    value,
    maxLength
) {

    const text =
        String(
            value ?? ""
        );


    if (
        text.length <=
        maxLength
    ) {

        return text;

    }


    return (
        text.substring(
            0,
            maxLength
        )
        + "..."
    );

}


// ============================================================
// CAPITALIZE
// ============================================================

function capitalize(value) {

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {

        return "-";

    }


    const text =
        String(
            value
        );


    return (
        text.charAt(0).toUpperCase()
        +
        text.slice(1)
    );

}


// ============================================================
// HTML ESCAPE
// ============================================================

function esc(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,
        character => ({

            "&":
                "&amp;",

            "<":
                "&lt;",

            ">":
                "&gt;",

            '"':
                "&quot;",

            "'":
                "&#039;"

        })[character]
    );

}


// ============================================================
// ATTRIBUTE ESCAPE
// ============================================================

function escAttribute(value) {

    return esc(
        value
    );

}


// ============================================================
// LOAD EVERYTHING
// ============================================================

async function loadAll() {

    console.log(
        "Loading admin dashboard..."
    );


    // --------------------------------------------------------
    // USERS
    // --------------------------------------------------------

    await loadUsers();


    // --------------------------------------------------------
    // REGISTRATION LOGS
    // --------------------------------------------------------

    await loadLogs();


    // --------------------------------------------------------
    // NEWS ANALYSIS
    // --------------------------------------------------------

    await loadAnalysis();

    // --------------------------------------------------------
    // RESOURCE REQUESTS
    // --------------------------------------------------------

    await loadResourceRequests();

    // --------------------------------------------------------
    // BIG-DATA BATCH ANALYTICS
    // --------------------------------------------------------

    await loadBigDataAnalytics();

    console.log(
        "Admin dashboard loaded."
    );

}


// ============================================================
// START
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadAll();

    }
);
