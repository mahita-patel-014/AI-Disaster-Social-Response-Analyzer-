import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from starlette.concurrency import run_in_threadpool
from backend.database.db import email_requests_collection

router = APIRouter(prefix="/api/email", tags=["Resource Email"])


class ResourceEmail(BaseModel):
    recipient_email: EmailStr
    disaster_type: str = Field(min_length=1, max_length=80)
    disaster_location: str = Field(min_length=1, max_length=200)
    resource_type: str = Field(min_length=1, max_length=40)
    resource_name: str = Field(min_length=1, max_length=120)
    quantity: str = Field(min_length=1, max_length=80)
    contact_name: str = Field(min_length=1, max_length=100)


def _send_email(data: ResourceEmail) -> None:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("SMTP_FROM_EMAIL", "").strip() or username
    if not username:
        raise RuntimeError(
            "Email sending is not set up yet. Add the sender account's SMTP_USERNAME to the project-root .env, then restart the backend."
        )
    if not password:
        raise RuntimeError(
            "SMTP_PASSWORD is missing from the project-root .env. For Gmail, add an app password for the configured sender account, then restart the backend."
        )
    message = EmailMessage()
    message["Subject"] = f"Emergency resource request: {data.resource_type} needed"
    message["From"] = sender
    message["To"] = str(data.recipient_email)
    message.set_content(
        "EMERGENCY RESOURCE REQUEST\n\n"
        f"Disaster: {data.disaster_type}\n"
        f"Location: {data.disaster_location}\n"
        f"Contact name: {data.contact_name}\n"
        f"Resource: {data.resource_name}\n"
        f"Resource type: {data.resource_type}\n"
        f"Quantity needed: {data.quantity}\n"
    )

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(message)


def _email_body(data: ResourceEmail) -> str:
    return (
        "EMERGENCY RESOURCE REQUEST\n\n"
        f"Disaster: {data.disaster_type}\n"
        f"Location: {data.disaster_location}\n"
        f"Contact name: {data.contact_name}\n"
        f"Resource: {data.resource_name}\n"
        f"Resource type: {data.resource_type}\n"
        f"Quantity needed: {data.quantity}\n"
    )


@router.post("/resource-request")
async def send_resource_email(data: ResourceEmail):
    mode = os.getenv("EMAIL_DELIVERY_MODE", "demo").strip().lower()
    subject = f"Emergency resource request: {data.resource_type} needed"
    if mode == "demo":
        await email_requests_collection.insert_one({
            "recipient_email": str(data.recipient_email),
            "subject": subject,
            "body": _email_body(data),
            "request": data.model_dump() if hasattr(data, "model_dump") else data.dict(),
            "delivery_mode": "demo",
            "status": "simulated",
            "created_at": datetime.now(timezone.utc),
        })
        return {
            "success": True,
            "recipient": str(data.recipient_email),
            "delivery_mode": "demo",
            "message": "Demo email recorded; no external email was sent.",
        }
    if mode != "smtp":
        raise HTTPException(status_code=500, detail="EMAIL_DELIVERY_MODE must be set to 'demo' or 'smtp'.")
    try:
        await run_in_threadpool(_send_email, data)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (smtplib.SMTPException, OSError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"Email could not be sent. Check SMTP settings: {exc}") from exc
    return {"success": True, "recipient": str(data.recipient_email), "delivery_mode": "smtp"}
