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
    """Create a new organization"""
    try:
        org = Organization(
            id=uuid.uuid4(),
            name=org_data.name,
            industry=org_data.industry,
            size_estimate=org_data.size_estimate,
            mission_statement=org_data.mission_statement,
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)
        logger.info(f"✅ Organization created: {org.name} ({org.id})")
        return org
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to create organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create organization")


@router.get("", response_model=list[OrgResponse])
async def list_organizations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all organizations"""
    try:
        result = await db.execute(select(Organization).order_by(Organization.created_at.desc()))
        orgs = result.scalars().all()
        logger.info(f"📋 Fetched {len(orgs)} organizations")
        return orgs
    except Exception as e:
        logger.error(f"❌ Failed to list organizations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch organizations")


@router.get("/{org_id}", response_model=OrgResponse)
async def get_organization(org_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a specific organization by ID"""
    try:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        logger.info(f"🔍 Fetched organization: {org.name}")
        return org
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch organization")


@router.put("/{org_id}", response_model=OrgResponse)
async def update_organization(org_id: uuid.UUID, org_data: OrgCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update an organization"""
    try:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Update fields
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
        logger.error(f"❌ Failed to update organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update organization")


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(org_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete an organization"""
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
        
        logger.info(f"🗑️  Organization deleted: {org.name}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to delete organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete organization")