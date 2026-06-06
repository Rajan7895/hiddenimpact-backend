from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import shutil
from pathlib import Path

from app.database import get_db
from app.models import Analysis
from app.schemas import AnalysisResponse, AnalysisListResponse, ErrorResponse
from app.utils.file_processor import FileProcessor
from app.utils.analyzer import InvisibleWorkAnalyzer
from app.config import settings

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post(
    "/upload",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def upload_and_analyze(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file (txt, csv, pdf, docx) and analyze it for invisible work activities.
    
    Returns:
    - Analysis results including category breakdown, score, and performance summary
    """
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Save uploaded file temporarily
    temp_file_path = upload_dir / file.filename
    try:
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    try:
        # Extract text from file
        file_processor = FileProcessor()
        text_content, file_type = file_processor.extract_text(str(temp_file_path))
        
        if not text_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content found in the file"
            )
        
        # Analyze the content
        analyzer = InvisibleWorkAnalyzer()
        analysis_result = analyzer.analyze(text_content)
        
        # Store in database
        db_analysis = Analysis(
            filename=file.filename,
            file_type=file_type,
            content=text_content,
            category_breakdown=analysis_result.category_breakdown.model_dump(),
            total_activities=analysis_result.total_activities,
            invisible_work_score=analysis_result.invisible_work_score,
            recognition_gap_score=analysis_result.recognition_gap_analysis.score,
            impact_score=analysis_result.impact_analysis.score,
            performance_summary=analysis_result.performance_summary,
            recognition_gap_explanation=analysis_result.recognition_gap_analysis.explanation,
            recognition_gap_recommendations=analysis_result.recognition_gap_analysis.recommendations,
            impact_explanation=analysis_result.impact_analysis.explanation,
            top_impact_drivers=analysis_result.impact_analysis.top_drivers,
            ai_insights=analysis_result.ai_insights.model_dump()
        )
        
        db.add(db_analysis)
        await db.commit()
        await db.refresh(db_analysis)
        
        return AnalysisResponse(
            id=db_analysis.id,
            filename=db_analysis.filename,
            file_type=db_analysis.file_type,
            category_breakdown=db_analysis.category_breakdown,
            invisible_work_score=db_analysis.invisible_work_score,
            recognition_gap_score=db_analysis.recognition_gap_score,
            recognition_gap_explanation=db_analysis.recognition_gap_explanation,
            recognition_gap_recommendations=db_analysis.recognition_gap_recommendations,
            impact_score=db_analysis.impact_score,
            impact_explanation=db_analysis.impact_explanation,
            top_impact_drivers=db_analysis.top_impact_drivers,
            ai_insights=db_analysis.ai_insights,
            performance_summary=db_analysis.performance_summary,
            created_at=db_analysis.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()


@router.get(
    "/",
    response_model=AnalysisListResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_all_analyses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all analysis records with pagination.
    
    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)
    """
    try:
        # Get total count
        count_query = select(Analysis)
        result = await db.execute(count_query)
        total = len(result.scalars().all())
        
        # Get paginated results
        query = select(Analysis).offset(skip).limit(limit).order_by(Analysis.created_at.desc())
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        return AnalysisListResponse(
            total=total,
            analyses=[
                AnalysisResponse(
                    id=analysis.id,
                    filename=analysis.filename,
                    file_type=analysis.file_type,
                    category_breakdown=analysis.category_breakdown,
                    invisible_work_score=analysis.invisible_work_score,
                    recognition_gap_score=analysis.recognition_gap_score,
                    recognition_gap_explanation=analysis.recognition_gap_explanation,
                    recognition_gap_recommendations=analysis.recognition_gap_recommendations,
                    impact_score=analysis.impact_score,
                    impact_explanation=analysis.impact_explanation,
                    top_impact_drivers=analysis.top_impact_drivers,
                    ai_insights=analysis.ai_insights,
                    performance_summary=analysis.performance_summary,
                    created_at=analysis.created_at
                )
                for analysis in analyses
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analyses: {str(e)}"
        )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific analysis by ID.
    """
    try:
        query = select(Analysis).where(Analysis.id == analysis_id)
        result = await db.execute(query)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID {analysis_id} not found"
            )
        
        return AnalysisResponse(
            id=analysis.id,
            filename=analysis.filename,
            file_type=analysis.file_type,
            category_breakdown=analysis.category_breakdown,
            invisible_work_score=analysis.invisible_work_score,
            recognition_gap_score=analysis.recognition_gap_score,
            recognition_gap_explanation=analysis.recognition_gap_explanation,
            recognition_gap_recommendations=analysis.recognition_gap_recommendations,
            impact_score=analysis.impact_score,
            impact_explanation=analysis.impact_explanation,
            top_impact_drivers=analysis.top_impact_drivers,
            ai_insights=analysis.ai_insights,
            performance_summary=analysis.performance_summary,
            created_at=analysis.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis: {str(e)}"
        )


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def delete_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific analysis by ID.
    """
    try:
        query = select(Analysis).where(Analysis.id == analysis_id)
        result = await db.execute(query)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID {analysis_id} not found"
            )
        
        await db.delete(analysis)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting analysis: {str(e)}"
        )

# Made with Bob
