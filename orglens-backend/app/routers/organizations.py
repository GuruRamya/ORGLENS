from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.organization import Organization
from app.schemas.organization import OrgCreate, OrgResponse
from loguru import logger
import uuid
from app.services.auth import get_current_user, require_org_access
from app.models.auth import User, OrgMembership
router = APIRouter()


@router.post("", response_model=OrgResponse)
async def create_organization(org_data: OrgCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        org = Organization(
            id=uuid.uuid4(),
            name=org_data.name,
            industry=org_data.industry,
            size_estimate=org_data.size_estimate,
            mission_statement=org_data.mission_statement,
            is_default=org_data.is_default,
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)
        return org
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create organization")


@router.get("", response_model=list[OrgResponse])
async def list_organizations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        result = await db.execute(select(Organization).order_by(Organization.created_at.desc()))
        orgs = result.scalars().all()
        return orgs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch organizations")


@router.get("/{org_id}", response_model=OrgResponse)
async def get_organization(org_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return org
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch organization")


@router.put("/{org_id}", response_model=OrgResponse)
async def update_organization(org_id: uuid.UUID, org_data: OrgCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        
        org.name = org_data.name
        org.industry = org_data.industry
        org.size_estimate = org_data.size_estimate
        org.mission_statement = org_data.mission_statement
        
        db.add(org)
        await db.commit()
        await db.refresh(org)
        
        logger.info(f"✏️  Organization updated: {org.name}")
        return org
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update organization")


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(org_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        if org.is_default:
            raise HTTPException(
                status_code=403,
                detail="Default organization cannot be deleted"
            )
        await db.delete(org)
        await db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete organization")
