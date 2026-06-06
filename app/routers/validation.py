from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_db
from app.models import ContributionValidation, ValidationStatus, Analysis
from app.schemas import (
    ContributionValidationCreate,
    ContributionValidationUpdate,
    ContributionValidationResponse,
    ValidationConfidenceScore
)

router = APIRouter(prefix="/api/validation", tags=["validation"])


@router.post("/", response_model=ContributionValidationResponse, status_code=status.HTTP_201_CREATED)
async def create_validation(
    validation: ContributionValidationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new contribution validation request"""
    
    # Check if analysis exists
    result = await db.execute(select(Analysis).where(Analysis.id == validation.analysis_id))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with id {validation.analysis_id} not found"
        )
    
    # Create validation
    db_validation = ContributionValidation(
        analysis_id=validation.analysis_id,
        contribution_text=validation.contribution_text,
        validator_name=validation.validator_name,
        notes=validation.notes,
        status=ValidationStatus.PENDING
    )
    
    db.add(db_validation)
    await db.commit()
    await db.refresh(db_validation)
    
    return ContributionValidationResponse(
        id=db_validation.id,
        analysis_id=db_validation.analysis_id,
        contribution_text=db_validation.contribution_text,
        validator_name=db_validation.validator_name,
        status=db_validation.status.value,
        notes=db_validation.notes,
        created_at=db_validation.created_at,
        updated_at=db_validation.updated_at
    )


@router.get("/", response_model=List[ContributionValidationResponse])
async def list_validations(
    status_filter: str = None,
    analysis_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """List all contribution validations with optional filters"""
    
    query = select(ContributionValidation)
    
    if status_filter:
        try:
            status_enum = ValidationStatus(status_filter.lower())
            query = query.where(ContributionValidation.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}. Must be one of: pending, approved, rejected"
            )
    
    if analysis_id:
        query = query.where(ContributionValidation.analysis_id == analysis_id)
    
    query = query.order_by(ContributionValidation.created_at.desc())
    
    result = await db.execute(query)
    validations = result.scalars().all()
    
    return [
        ContributionValidationResponse(
            id=v.id,
            analysis_id=v.analysis_id,
            contribution_text=v.contribution_text,
            validator_name=v.validator_name,
            status=v.status.value,
            notes=v.notes,
            created_at=v.created_at,
            updated_at=v.updated_at
        )
        for v in validations
    ]


@router.get("/confidence", response_model=ValidationConfidenceScore)
async def get_validation_confidence(db: AsyncSession = Depends(get_db)):
    """Calculate and return validation confidence score"""
    
    # Get all validations and count them in Python
    result = await db.execute(select(ContributionValidation))
    validations = result.scalars().all()
    
    total = len(validations)
    approved = sum(1 for v in validations if v.status == ValidationStatus.APPROVED)
    rejected = sum(1 for v in validations if v.status == ValidationStatus.REJECTED)
    pending = sum(1 for v in validations if v.status == ValidationStatus.PENDING)
    
    # Calculate confidence score
    # Formula: (approved / (approved + rejected)) * 100
    # If no validations completed, confidence is 0
    completed = approved + rejected
    if completed == 0:
        confidence_score = 0.0
    else:
        confidence_score = (approved / completed) * 100
    
    return ValidationConfidenceScore(
        confidence_score=round(confidence_score, 2),
        total_validations=total,
        approved_count=approved,
        rejected_count=rejected,
        pending_count=pending
    )


@router.get("/{validation_id}", response_model=ContributionValidationResponse)
async def get_validation(
    validation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific contribution validation by ID"""
    
    result = await db.execute(
        select(ContributionValidation).where(ContributionValidation.id == validation_id)
    )
    validation = result.scalar_one_or_none()
    
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation with id {validation_id} not found"
        )
    
    return ContributionValidationResponse(
        id=validation.id,
        analysis_id=validation.analysis_id,
        contribution_text=validation.contribution_text,
        validator_name=validation.validator_name,
        status=validation.status.value,
        notes=validation.notes,
        created_at=validation.created_at,
        updated_at=validation.updated_at
    )


@router.put("/{validation_id}", response_model=ContributionValidationResponse)
async def update_validation(
    validation_id: int,
    update_data: ContributionValidationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a contribution validation status"""
    
    result = await db.execute(
        select(ContributionValidation).where(ContributionValidation.id == validation_id)
    )
    validation = result.scalar_one_or_none()
    
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation with id {validation_id} not found"
        )
    
    # Validate status
    try:
        status_enum = ValidationStatus(update_data.status.lower())
        validation.status = status_enum
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {update_data.status}. Must be one of: pending, approved, rejected"
        )
    
    if update_data.notes is not None:
        validation.notes = update_data.notes
    
    await db.commit()
    await db.refresh(validation)
    
    return ContributionValidationResponse(
        id=validation.id,
        analysis_id=validation.analysis_id,
        contribution_text=validation.contribution_text,
        validator_name=validation.validator_name,
        status=validation.status.value,
        notes=validation.notes,
        created_at=validation.created_at,
        updated_at=validation.updated_at
    )


@router.delete("/{validation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_validation(
    validation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a contribution validation"""
    
    result = await db.execute(
        select(ContributionValidation).where(ContributionValidation.id == validation_id)
    )
    validation = result.scalar_one_or_none()
    
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation with id {validation_id} not found"
        )
    
    await db.delete(validation)
    await db.commit()
    
    return None

# Made with Bob
