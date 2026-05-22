from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import json
from loguru import logger
from fastapi.responses import RedirectResponse
from app.config import settings
from pydantic import BaseModel, EmailStr, Field
from app.database import get_db
from app.models.auth import User, OrgMembership
from app.models import Organization
from app.schemas.organization import OrgResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import (
    hash_password, verify_password, create_access_token, get_current_user
)
import uuid
router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=uuid.uuid4(),
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.commit()
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=str(user.id), email=user.email)

@router.post("/token", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=str(user.id), email=user.email)

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email, "full_name": current_user.full_name}


@router.get("/slack/authorize")
async def slack_authorize(org_id: str):
    """
    Redirect user to Slack OAuth authorization.
    Returns the authorization URL.
    """
    slack_auth_url = (
        f"https://slack.com/oauth/v2/authorize?"
        f"client_id={settings.slack_client_id}&"
        f"scope=channels:read,groups:read,im:read,mpim:read,users:read,team:info:read&"
        f"redirect_uri={settings.slack_redirect_uri}&"
        f"state={org_id}"
    )
    return {"url": slack_auth_url}


@router.get("/slack/callback")
async def slack_callback(code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Slack OAuth callback. Exchange code for access token and save to org.
    """
    if not code or not state:
        # Redirect to upload page with error
        return RedirectResponse(
            url=f"{settings.frontend_url}/org/{state}/upload?error=slack_auth_failed",
            status_code=302
        )

    try:
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": settings.slack_client_id,
                    "client_secret": settings.slack_client_secret,
                    "code": code,
                    "redirect_uri": settings.slack_redirect_uri,
                },
            )
            data = response.json()

        if not data.get("ok"):
            logger.error(f"Slack OAuth failed: {data.get('error')}")
            return RedirectResponse(
                url=f"{settings.frontend_url}/org/{state}/upload?error={data.get('error')}",
                status_code=302
            )

        access_token = data.get("access_token")
        org_id = state

        # Save token to organization
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()

        if not org:
            return RedirectResponse(
                url=f"{settings.frontend_url}/org/{org_id}/upload?error=org_not_found",
                status_code=302
            )

        org.slack_access_token = access_token
        org.slack_connected = True
        await db.commit()

        logger.info(f"✅ Slack connected for org: {org.name}")

        # ✅ Redirect back to upload page with success
        return RedirectResponse(
            url=f"{settings.frontend_url}/org/{org_id}/upload?success=slack_connected",
            status_code=302
        )

    except Exception as e:
        logger.error(f"Slack callback error: {str(e)}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/org/{state}/upload?error=callback_error",
            status_code=302
        )


@router.get("/gmail/authorize")
async def gmail_authorize(org_id: str):
    """
    Redirect user to Google OAuth authorization for Gmail.
    Returns the authorization URL.
    """
    gmail_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"scope=https://www.googleapis.com/auth/gmail.readonly&"
        f"redirect_uri={settings.google_redirect_uri}&"
        f"response_type=code&"
        f"state={org_id}&"
        f"access_type=offline"
    )
    return {"url": gmail_auth_url}


@router.get("/gmail/callback")
async def gmail_callback(code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Google OAuth callback. Exchange code for access token and save to org.
    """
    if not code or not state:
        return RedirectResponse(
            url=f"{settings.frontend_url}/org/{state}/upload?error=gmail_auth_failed",
            status_code=302
        )

    try:
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri,
                },
            )
            data = response.json()

        if "error" in data:
            logger.error(f"Google OAuth failed: {data.get('error')}")
            return RedirectResponse(
                url=f"{settings.frontend_url}/org/{state}/upload?error={data.get('error')}",
                status_code=302
            )

        access_token = data.get("access_token")
        org_id = state

        # Save token to organization
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()

        if not org:
            return RedirectResponse(
                url=f"{settings.frontend_url}/org/{org_id}/upload?error=org_not_found",
                status_code=302
            )

        org.gmail_access_token = access_token
        org.gmail_connected = True
        await db.commit()

        logger.info(f"✅ Gmail connected for org: {org.name}")

        # ✅ Redirect back to upload page with success
        return RedirectResponse(
            url=f"{settings.frontend_url}/org/{org_id}/upload?success=gmail_connected",
            status_code=302
        )

    except Exception as e:
        logger.error(f"Gmail callback error: {str(e)}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/org/{state}/upload?error=callback_error",
            status_code=302
        )


@router.post("/disconnect/slack/{org_id}")
async def disconnect_slack(org_id: str, db: AsyncSession = Depends(get_db)):
    """Disconnect Slack from organization"""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.slack_access_token = None
    org.slack_connected = False
    await db.commit()

    logger.info(f"✅ Slack disconnected for org: {org.name}")
    return {"status": "success", "message": "Slack disconnected"}


@router.post("/disconnect/gmail/{org_id}")
async def disconnect_gmail(org_id: str, db: AsyncSession = Depends(get_db)):
    """Disconnect Gmail from organization"""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.gmail_access_token = None
    org.gmail_connected = False
    await db.commit()

    logger.info(f"✅ Gmail disconnected for org: {org.name}")
    return {"status": "success", "message": "Gmail disconnected"}