# Invisible Work Analyzer

A FastAPI-based backend application for analyzing and tracking invisible work activities in professional settings. This tool helps identify, categorize, and quantify work that often goes unrecognized in traditional performance metrics.

## Features

- **File Upload Support**: Upload text files, CSV files, PDFs, and DOCX documents
- **Text Extraction**: Automatically extract text content from various file formats
- **Activity Classification**: Classify activities into 8 categories:
  - Mentoring
  - Knowledge Sharing
  - Documentation
  - Incident Support
  - Meetings
  - Cross-Team Collaboration
  - Process Improvement
  - Administrative Work
- **Analysis & Scoring**: Generate invisible work scores (0.0 to 1.0) based on activity patterns
- **Recognition Gap Score**: Calculate a score (0-100) estimating how much work is invisible in traditional metrics
- **Performance Summaries**: Automatically generate performance review summaries
- **Recognition Gap Analysis**: Detailed explanation and recommendations for highlighting invisible contributions
- **Data Persistence**: Store all analysis results in SQLite database
- **RESTful API**: Full CRUD operations for managing analyses

## Project Structure

```
invisible-work-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Application configuration
│   ├── database.py             # Database setup and session management
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── routers/
│   │   ├── __init__.py
│   │   └── analysis.py         # Analysis endpoints
│   └── utils/
│       ├── __init__.py
│       ├── file_processor.py   # File upload and text extraction
│       └── analyzer.py         # Activity classification and scoring
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**:
   ```bash
   cd invisible-work-analyzer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env file with your preferred settings
   ```

## Running the Application

### Development Server

Start the FastAPI development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

### Production Server

For production deployment:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Root Endpoints

- **GET /** - Welcome message and API information
- **GET /health** - Health check endpoint

### Analysis Endpoints

#### Upload and Analyze File

```http
POST /api/analysis/upload
Content-Type: multipart/form-data

Parameters:
- file: File to upload (txt, csv, pdf, docx)

Response: 201 Created
{
  "id": 1,
  "filename": "activities.txt",
  "file_type": "txt",
  "category_breakdown": {
    "mentoring": 5,
    "knowledge_sharing": 3,
    "documentation": 7,
    "incident_support": 2,
    "meetings": 4,
    "cross_team_collaboration": 3,
    "process_improvement": 2,
    "administrative_work": 1
  },
  "invisible_work_score": 0.72,
  "recognition_gap_score": 78,
  "recognition_gap_explanation": "Recognition Gap Score: 78/100 (High)...",
  "recognition_gap_recommendations": "Recommendations for Performance Reviews:...",
  "performance_summary": "This team member demonstrates exceptional commitment...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get All Analyses

```http
GET /api/analysis/?skip=0&limit=100

Response: 200 OK
{
  "total": 10,
  "analyses": [...]
}
```

#### Get Specific Analysis

```http
GET /api/analysis/{analysis_id}

Response: 200 OK
{
  "id": 1,
  "filename": "activities.txt",
  ...
}
```

#### Delete Analysis

```http
DELETE /api/analysis/{analysis_id}

Response: 204 No Content
```

## Usage Examples

### Using cURL

**Upload a file for analysis**:
```bash
curl -X POST "http://localhost:8000/api/analysis/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@activities.txt"
```

**Get all analyses**:
```bash
curl -X GET "http://localhost:8000/api/analysis/" \
  -H "accept: application/json"
```

### Using Python

```python
import requests

# Upload and analyze a file
with open('activities.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/analysis/upload', files=files)
    result = response.json()
    print(f"Invisible Work Score: {result['invisible_work_score']}")
    print(f"Performance Summary: {result['performance_summary']}")

# Get all analyses
response = requests.get('http://localhost:8000/api/analysis/')
analyses = response.json()
print(f"Total analyses: {analyses['total']}")
```

## Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and modify as needed:

```env
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./invisible_work.db

# API Configuration
API_TITLE=Invisible Work Analyzer API
API_VERSION=1.0.0
API_DESCRIPTION=API for analyzing and tracking invisible work activities

# File Upload Configuration
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
ALLOWED_EXTENSIONS=.txt,.csv,.pdf,.docx

# Analysis Configuration
INVISIBLE_WORK_THRESHOLD=0.6
```

## Activity Categories

The analyzer classifies activities into the following categories:

1. **Mentoring**: Coaching, training, onboarding, helping team members
2. **Knowledge Sharing**: Presentations, demos, tech talks, sharing best practices
3. **Documentation**: Writing docs, READMEs, guides, API documentation
4. **Incident Support**: Bug fixes, troubleshooting, on-call duties, incident response
5. **Meetings**: Standups, planning sessions, reviews, one-on-ones
6. **Cross-Team Collaboration**: Coordinating with other teams, stakeholder management
7. **Process Improvement**: Optimizing workflows, automation, tooling improvements
8. **Administrative Work**: Reports, timesheets, approvals, tracking

## Invisible Work Score

The invisible work score (0.0 to 1.0) is calculated based on:
- Number of activities in each category
- Weighted importance of each category
- Overall proportion of invisible work

**Score Interpretation**:
- **0.7 - 1.0**: Exceptional commitment to invisible work
- **0.5 - 0.7**: Solid engagement in invisible work
- **0.0 - 0.5**: Some invisible work contributions

## Recognition Gap Score

The Recognition Gap Score (0-100) estimates how much of a person's contribution is likely to be invisible in traditional performance metrics.

**Calculation Factors**:
The score focuses on five high-impact invisible work categories:
- **Mentoring** (weight: 1.0) - Often untracked but critical for team growth
- **Knowledge Sharing** (weight: 0.95) - Rarely measured but essential for team capability
- **Cross-Team Collaboration** (weight: 0.9) - Frequently overlooked despite organizational impact
- **Incident Support** (weight: 0.85) - Often seen as 'just doing the job'
- **Documentation** (weight: 0.8) - Undervalued despite long-term benefits

**Score Interpretation**:
- **80-100 (Very High)**: Significant majority of contributions are invisible in traditional metrics
- **60-79 (High)**: Substantial portion may not be fully captured in standard reviews
- **40-59 (Moderate)**: Moderate amount of work may go unrecognized
- **20-39 (Low)**: Most work is likely visible with some invisible contributions
- **0-19 (Very Low)**: Majority of work is captured in traditional metrics

**Recognition Gap Analysis Includes**:
1. **Explanation**: Detailed breakdown of why the score was assigned, including specific category contributions
2. **Recommendations**: Actionable advice for highlighting invisible work in performance reviews, including:
   - How to document and quantify impact
   - Specific metrics to track for each category
   - Best practices for maintaining a "brag document"
   - Strategies for ensuring visibility with managers

## Database Schema

The application uses SQLite with the following schema:

**analyses** table:
- `id`: Integer (Primary Key)
- `filename`: String (255)
- `file_type`: String (50)
- `content`: Text
- `category_breakdown`: JSON
- `invisible_work_score`: Float
- `recognition_gap_score`: Integer
- `performance_summary`: Text
- `recognition_gap_explanation`: Text
- `recognition_gap_recommendations`: Text
- `created_at`: DateTime
- `updated_at`: DateTime

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style

The project follows PEP 8 style guidelines. Format code using:

```bash
pip install black
black app/
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the virtual environment and all dependencies are installed
2. **Database errors**: Delete `invisible_work.db` and restart the application to recreate the database
3. **File upload errors**: Check file size limits and ensure the file format is supported
4. **Port already in use**: Change the port number in the uvicorn command

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational and professional use.

## Support

For issues, questions, or suggestions, please create an issue in the project repository.

## Acknowledgments

This tool was designed to help organizations recognize and value the often-invisible work that contributes to team success and organizational health.