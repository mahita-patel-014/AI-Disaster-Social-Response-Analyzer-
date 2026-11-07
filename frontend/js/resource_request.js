"use strict";

const DEFAULT_RESOURCE_CONTACT = { name: "Mahita" };
const configuredApi = window.RESOURCE_API_BASE || localStorage.getItem("RESOURCE_API_BASE");
const localFrontend = location.protocol === "file:" || location.port === "5500" || location.port === "5501";
const RESOURCE_API = configuredApi || (localFrontend ? `http://${location.hostname || "127.0.0.1"}:8000` : location.origin);
let currentDisaster = { disaster_type: "Unspecified", disaster_location: "Location not provided" };
let currentResourceRequest = null;

function loadDisasterInformation() {
    const keys = ["ai_cp_real_news", "analysisResult", "analysis_result", "analysisData", "analysis_data", "disasterAnalysis", "disaster_analysis", "responseData", "response_data"];
    for (const storage of [sessionStorage, localStorage]) for (const key of keys) {
        try {
            const value = storage.getItem(key);
            if (!value) continue;
            const data = JSON.parse(value);
            currentDisaster = {
                disaster_type: data.disaster_type || data.disasterType || data.prediction || data.predicted_disaster || currentDisaster.disaster_type,
                disaster_location: data.disaster_location || data.disasterLocation || data.location || currentDisaster.disaster_location
            };
            return;
        } catch (_) { /* Ignore unrelated or outdated saved data. */ }
    }
}

function inferResourceType(text) {
    const value = String(text || "").toLowerCase();
    if (/water|drink/.test(value)) return "WATER";
    if (/food|meal|ration/.test(value)) return "FOOD";
    if (/medical|medicine|doctor|first aid/.test(value)) return "MEDICAL";
    if (/rescue|boat|evacuat/.test(value)) return "RESCUE";
    if (/shelter|tent/.test(value)) return "SHELTER";
    if (/transport|vehicle/.test(value)) return "TRANSPORT";
    return "OTHER";
}

function openResourceRequest(resource = {}) {
    closeResourcePopup();
    if (typeof resource === "string") resource = { resource_name: resource };
    const recommended = resource.resource_name || resource.resourceName || resource.name || "Emergency supply";
    const type = String(resource.resource_type || resource.resourceType || resource.type || inferResourceType(recommended)).toUpperCase();
    const quantity = resource.quantity || resource.required_quantity || resource.requiredQuantity || "";
    const overlay = document.createElement("div");
    overlay.id = "resourceRequestOverlay";
    overlay.style.cssText = "position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;padding:18px;background:rgba(5,15,35,.72);backdrop-filter:blur(5px);";
    const popup = document.createElement("section");
    popup.setAttribute("role", "dialog");
    popup.setAttribute("aria-modal", "true");
    popup.setAttribute("aria-labelledby", "resourcePopupTitle");
    popup.style.cssText = "position:relative;width:min(760px,100%);max-height:94vh;overflow:auto;padding:32px;background:white;border-radius:20px;box-shadow:0 25px 80px rgba(0,0,0,.3);font:16px/1.5 Arial,sans-serif;color:#172033;";
    popup.innerHTML = `
        <button type="button" id="resourcePopupClose" aria-label="Close" style="position:absolute;right:15px;top:12px;border:0;border-radius:50%;width:36px;height:36px;background:#eef4ff;font-size:23px;cursor:pointer">×</button>
        <div id="resourcePopupContent"></div>
    `;
    overlay.appendChild(popup);
    document.body.appendChild(overlay);
    document.getElementById("resourcePopupClose").addEventListener("click", closeResourcePopup);
    overlay.addEventListener("click", event => { if (event.target === overlay) closeResourcePopup(); });
    document.addEventListener("keydown", handleResourceEscape);
    renderResourceRequestForm({ recommended, type, quantity });
}

function renderResourceRequestForm({ recommended, type, quantity }) {
    const content = document.getElementById("resourcePopupContent");
    content.innerHTML = `
        <h2 id="resourcePopupTitle" style="margin:0 48px 8px 0;color:#123d78;font-size:28px;line-height:1.2">Request a Resource</h2>
        <p style="margin:0 0 20px;color:#64748b;line-height:1.6">Enter the requester and resource details. Select Done to save the request and review its message.</p>
        <div style="padding:16px 18px;margin-bottom:20px;border-radius:12px;background:#f5f8fd;line-height:1.8;font-size:16px">
            <div><b>Disaster:</b> ${escapeHTML(currentDisaster.disaster_type)}</div>
            <div><b>Location:</b> ${escapeHTML(currentDisaster.disaster_location)}</div>
            <div><b>Recommended:</b> ${escapeHTML(recommended)}</div>
        </div>
        <label for="resourcePersonName" style="display:block;margin:14px 0 7px;font-weight:700">Requester name</label>
        <input id="resourcePersonName" type="text" autocomplete="name" maxlength="100" required value="${escapeAttribute(DEFAULT_RESOURCE_CONTACT.name)}" placeholder="Enter contact name" style="width:100%;box-sizing:border-box;padding:14px;border:1px solid #cbd5e1;border-radius:10px;font:inherit">
        <label for="resourceName" style="display:block;margin:14px 0 7px;font-weight:700">Resource needed</label>
        <input id="resourceName" type="text" maxlength="120" required value="${escapeAttribute(recommended)}" placeholder="e.g. bottled drinking water" style="width:100%;box-sizing:border-box;padding:14px;border:1px solid #cbd5e1;border-radius:10px;font:inherit">
        <label for="resourceDetails" style="display:block;margin:14px 0 7px;font-weight:700">Resource details</label>
        <textarea id="resourceDetails" maxlength="500" required rows="3" placeholder="Describe specifications, delivery needs, or other important details" style="width:100%;box-sizing:border-box;padding:14px;border:1px solid #cbd5e1;border-radius:10px;font:inherit;resize:vertical"></textarea>
        <label for="resourceType" style="display:block;margin:14px 0 7px;font-weight:700">Resource type</label>
        <select id="resourceType" style="width:100%;box-sizing:border-box;padding:14px;border:1px solid #cbd5e1;border-radius:10px;font:inherit">
            ${["WATER", "FOOD", "MEDICAL", "RESCUE", "SHELTER", "TRANSPORT", "SECURITY", "OTHER"].map(option => `<option value="${option}" ${type === option || (option === "WATER" && type === "DRINKING WATER") ? "selected" : ""}>${option === "WATER" ? "Water" : option.charAt(0) + option.slice(1).toLowerCase()}</option>`).join("")}
        </select>
        <label for="resourceQuantity" style="display:block;margin:14px 0 7px;font-weight:700">Quantity needed</label>
        <input id="resourceQuantity" type="text" maxlength="80" required ${quantity ? `value="${escapeAttribute(quantity)}"` : ""} placeholder="e.g. 20 water bottles" style="width:100%;box-sizing:border-box;padding:14px;border:1px solid #cbd5e1;border-radius:10px;font:inherit">
        <div id="resourceRequestMessage" role="status" aria-live="polite" style="min-height:22px;margin:12px 0;color:#b42318;line-height:1.5"></div>
        <button type="button" id="resourceRequestSubmit" style="width:100%;padding:16px;border:0;border-radius:10px;background:#2563eb;color:white;font:inherit;font-weight:800;cursor:pointer">Done</button>
    `;
    document.getElementById("resourceRequestSubmit").addEventListener("click", handleResourceRequestSubmit);
    document.getElementById("resourcePersonName").focus();
}

function buildResourceMessage(request) {
    return [
        "EMERGENCY RESOURCE REQUEST",
        "",
        `Disaster: ${currentDisaster.disaster_type}`,
        `Location: ${currentDisaster.disaster_location}`,
        `Requester: ${request.name}`,
        `Resource needed: ${request.resource}`,
        `Resource details: ${request.details}`,
        `Resource type: ${request.type}`,
        `Quantity needed: ${request.quantity}`
    ].join("\n");
}

async function handleResourceRequestSubmit() {
    const name = document.getElementById("resourcePersonName");
    const resourceName = document.getElementById("resourceName");
    const resourceDetails = document.getElementById("resourceDetails");
    const quantity = document.getElementById("resourceQuantity");
    const message = document.getElementById("resourceRequestMessage");
    if (![name, resourceName, resourceDetails, quantity].every(input => input.value.trim())) {
        message.style.color = "#b42318";
        message.textContent = "Complete all requester and resource details.";
        return;
    }

    const button = document.getElementById("resourceRequestSubmit");
    button.disabled = true;
    button.textContent = "Saving request...";
    currentResourceRequest = {
        name: name.value.trim(),
        resource: resourceName.value.trim(),
        details: resourceDetails.value.trim(),
        type: document.getElementById("resourceType").value,
        quantity: quantity.value.trim()
    };

    try {
        const response = await fetch(`${RESOURCE_API}/api/resources/requests`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                disaster_type: currentDisaster.disaster_type,
                location: currentDisaster.disaster_location,
                requester_name: currentResourceRequest.name,
                resource_name: currentResourceRequest.resource,
                resource_details: currentResourceRequest.details,
                resource_type: currentResourceRequest.type,
                quantity: currentResourceRequest.quantity
            })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Could not save this resource request.");
        }
        currentResourceRequest.id = data.request?.id || "";
        currentResourceRequest.createdAt = data.request?.created_at || new Date().toISOString();
        renderResourceRequestMessage();
    } catch (error) {
        message.style.color = "#b42318";
        message.textContent = error.message || "Could not save this resource request.";
        button.disabled = false;
        button.textContent = "Retry Save";
        console.error("Could not save resource request:", error);
    }
}

function renderResourceRequestMessage() {
    const content = document.getElementById("resourcePopupContent");
    const request = currentResourceRequest;
    const message = buildResourceMessage(request);
    content.innerHTML = `
        <h2 id="resourcePopupTitle" style="margin:0 48px 8px 0;color:#123d78;font-size:30px;line-height:1.2">Resource Request Saved</h2>
        <p style="margin:0 0 20px;color:#64748b;line-height:1.6">This request is saved in the system and will appear on the admin dashboard for CSV export.</p>
        <div style="padding:22px;margin-bottom:18px;border:1px solid #dbe5f1;border-radius:14px;background:#f5f8fd;line-height:1.9;font-size:18px">
            <div><b>Disaster type:</b> ${escapeHTML(currentDisaster.disaster_type)}</div>
            <div><b>Location:</b> ${escapeHTML(currentDisaster.disaster_location)}</div>
            <div><b>Requester:</b> ${escapeHTML(request.name)}</div>
            <div><b>Resource needed:</b> ${escapeHTML(request.resource)}</div>
            <div><b>Resource details:</b> ${escapeHTML(request.details)}</div>
            <div><b>Resource type:</b> ${escapeHTML(request.type)}</div>
            <div><b>Quantity:</b> ${escapeHTML(request.quantity)}</div>
            <div><b>Request ID:</b> ${escapeHTML(request.id)}</div>
        </div>
        <label for="resourceMessagePreview" style="display:block;margin:12px 0 7px;font-weight:700;font-size:17px">Complete request message</label>
        <textarea id="resourceMessagePreview" readonly rows="10" style="width:100%;box-sizing:border-box;padding:18px;border:1px solid #cbd5e1;border-radius:10px;background:#f8fafc;line-height:1.7;font:16px/1.7 Consolas,monospace">${escapeHTML(message)}</textarea>
        <div id="resourceRequestMessage" role="status" aria-live="polite" style="min-height:22px;margin:12px 0;color:#15803d;line-height:1.5">Saved to MongoDB. Nothing was emailed.</div>
        <div style="display:flex;gap:12px">
            <button type="button" id="resourceRequestCopy" style="flex:1;padding:15px;border:0;border-radius:10px;background:#2563eb;color:white;font:inherit;font-weight:800;cursor:pointer">Copy Message</button>
            <button type="button" id="resourceRequestClose" style="flex:1;padding:15px;border:1px solid #cbd5e1;border-radius:10px;background:white;color:#123d78;font:inherit;font-weight:800;cursor:pointer">Close</button>
        </div>
    `;
    document.getElementById("resourceRequestCopy").addEventListener("click", copyResourceMessage);
    document.getElementById("resourceRequestClose").addEventListener("click", closeResourcePopup);
    document.querySelector("#resourceRequestOverlay section").scrollTop = 0;
}

async function copyResourceMessage() {
    const message = document.getElementById("resourceMessagePreview").value;
    const status = document.getElementById("resourceRequestMessage");
    try {
        await navigator.clipboard.writeText(message);
        status.style.color = "#15803d";
        status.textContent = "Message copied. It was not sent.";
    } catch (error) {
        status.style.color = "#b42318";
        status.textContent = "Clipboard access is unavailable. Select and copy the message above.";
        console.error("Could not copy resource message:", error);
    }
}

function closeResourcePopup() {
    document.getElementById("resourceRequestOverlay")?.remove();
    document.removeEventListener("keydown", handleResourceEscape);
}

function handleResourceEscape(event) { if (event.key === "Escape") closeResourcePopup(); }
function escapeHTML(value) { return String(value ?? "").replace(/[&<>"']/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[character]); }
function escapeAttribute(value) { return escapeHTML(value).replace(/`/g, "&#096;"); }

window.openResourceRequest = openResourceRequest;
window.closeResourcePopup = closeResourcePopup;
window.setResourceDisasterInfo = (disasterType, location) => {
    currentDisaster = { disaster_type: disasterType || "Unspecified", disaster_location: location || "Location not provided" };
};

document.addEventListener("DOMContentLoaded", () => {
    loadDisasterInformation();
    document.querySelectorAll("#callResourceButton").forEach(button => button.addEventListener("click", () => openResourceRequest()));
});
