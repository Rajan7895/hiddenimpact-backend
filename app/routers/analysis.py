from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import shutil
from pathlib import Path
import json
import uuid

from app.database import get_db
from app.models import Analysis
from app.schemas import (
    AnalysisResponse,
    AnalysisListResponse,
    ErrorResponse,
    TeamComparisonResponse,
    EmployeeComparison,
    TeamSummary,
    Leaderboards
)
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
            filenames=[file.filename],  # Single file as array
            number_of_files=1,
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
            ai_insights=analysis_result.ai_insights.model_dump(),
            hidden_hero_score=analysis_result.hidden_hero_score,
            hidden_hero_classification=analysis_result.hidden_hero_classification,
            hidden_hero_analysis=analysis_result.hidden_hero_analysis
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
            hidden_hero_score=db_analysis.hidden_hero_score,
            hidden_hero_classification=db_analysis.hidden_hero_classification,
            hidden_hero_analysis=db_analysis.hidden_hero_analysis,
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


@router.post(
    "/upload-multiple",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def upload_and_analyze_multiple(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple files (txt, csv, pdf, docx) and analyze them together as a single combined analysis.
    
    Returns:
    - Combined analysis results from all files
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    combined_text = []
    filenames = []
    file_types = set()
    temp_files = []
    
    try:
        # Process each file
        for file in files:
            # Validate file extension
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in settings.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_extension} not supported in {file.filename}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
            
            # Save uploaded file temporarily
            temp_file_path = upload_dir / file.filename
            temp_files.append(temp_file_path)
            
            try:
                with temp_file_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error saving file {file.filename}: {str(e)}"
                )
            
            # Extract text from file
            file_processor = FileProcessor()
            text_content, file_type = file_processor.extract_text(str(temp_file_path))
            
            if text_content.strip():
                combined_text.append(f"=== {file.filename} ===\n{text_content}\n")
                filenames.append(file.filename)
                file_types.add(file_type)
        
        if not combined_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content found in any of the files"
            )
        
        # Combine all text content
        full_text = "\n\n".join(combined_text)
        
        # Analyze the combined content
        analyzer = InvisibleWorkAnalyzer()
        analysis_result = analyzer.analyze(full_text)
        
        # Determine primary file type
        primary_file_type = list(file_types)[0] if len(file_types) == 1 else "mixed"
        
        # Create combined filename
        if len(filenames) == 1:
            combined_filename = filenames[0]
        else:
            combined_filename = f"Combined Analysis ({len(filenames)} files)"
        
        # Store in database
        db_analysis = Analysis(
            filename=combined_filename,
            filenames=filenames,
            number_of_files=len(filenames),
            file_type=primary_file_type,
            content=full_text,
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
            ai_insights=analysis_result.ai_insights.model_dump(),
            hidden_hero_score=analysis_result.hidden_hero_score,
            hidden_hero_classification=analysis_result.hidden_hero_classification,
            hidden_hero_analysis=analysis_result.hidden_hero_analysis
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
            hidden_hero_score=db_analysis.hidden_hero_score,
            hidden_hero_classification=db_analysis.hidden_hero_classification,
            hidden_hero_analysis=db_analysis.hidden_hero_analysis,
            number_of_files=db_analysis.number_of_files,
            filenames=db_analysis.filenames,
            created_at=db_analysis.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing files: {str(e)}"
        )
    finally:
        # Clean up temporary files
        for temp_file_path in temp_files:
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
                    hidden_hero_score=analysis.hidden_hero_score,
                    hidden_hero_classification=analysis.hidden_hero_classification,
                    hidden_hero_analysis=analysis.hidden_hero_analysis,
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
            hidden_hero_score=analysis.hidden_hero_score,
            hidden_hero_classification=analysis.hidden_hero_classification,
            hidden_hero_analysis=analysis.hidden_hero_analysis,
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


@router.post(
    "/compare",
    response_model=TeamComparisonResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def compare_team(
    files: List[UploadFile] = File(...)
):
    """
    Compare multiple employees by analyzing each file independently.
    
    Each file represents a different employee. Returns individual results
    plus team-level summary and leaderboards.
    
    Does not store results in database - returns ephemeral comparison data.
    """
    if len(files) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team comparison requires at least 2 files"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    temp_files = []
    employees = []
    
    try:
        analyzer = InvisibleWorkAnalyzer()
        
        # Process each file independently
        for file in files:
            # Validate file extension
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in settings.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_extension} not supported in {file.filename}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
            
            # Save uploaded file temporarily
            temp_file_path = upload_dir / file.filename
            temp_files.append(temp_file_path)
            
            try:
                with temp_file_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error saving file {file.filename}: {str(e)}"
                )
            
            # Extract text from file
            file_processor = FileProcessor()
            text_content, _ = file_processor.extract_text(str(temp_file_path))
            
            if not text_content.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No text content found in {file.filename}"
                )
            
            # Analyze this employee
            employee_data = analyzer.analyze_for_comparison(text_content, file.filename)
            employees.append(employee_data)
        
        # Generate team summary
        team_summary_data = analyzer.calculate_team_summary(employees)
        
        # Generate leaderboards
        leaderboards_data = analyzer.generate_leaderboards(employees)
        
        # Create response
        comparison_id = str(uuid.uuid4())
        
        return TeamComparisonResponse(
            comparison_id=comparison_id,
            employees=[EmployeeComparison(**emp) for emp in employees],
            team_summary=TeamSummary(**team_summary_data),
            leaderboards=Leaderboards(**leaderboards_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing team comparison: {str(e)}"
        )
    finally:
        # Clean up temporary files
        for temp_file_path in temp_files:
            if temp_file_path.exists():
                temp_file_path.unlink()

# Made with Bob
