# HiddenImpact™ Troubleshooting Guide

## Current Errors Analysis

Based on the server logs, there are two main issues:

### 1. 500 Internal Server Error on `/api/analysis/upload`

**Error:** `POST /api/analysis/upload HTTP/1.1" 500 Internal Server Error`

**Possible Causes:**
- Missing database fields
- File processing error
- Analyzer error
- Missing dependencies

**Solution Steps:**

1. **Check if all database migrations are applied:**
```bash
cd invisible-work-analyzer
# Delete existing database to recreate with latest schema
rm -f invisible_work.db
# Restart server to recreate database
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Verify all required fields exist in Analysis model:**
The model should have these fields:
- `filename`, `filenames`, `number_of_files`
- `file_type`, `content`, `category_breakdown`
- `total_activities`, `invisible_work_score`
- `recognition_gap_score`, `recognition_gap_explanation`, `recognition_gap_recommendations`
- `impact_score`, `impact_explanation`, `top_impact_drivers`
- `ai_insights`, `performance_summary`
- `hidden_hero_score`, `hidden_hero_classification`, `hidden_hero_analysis`

3. **Check server logs for detailed error:**
```bash
# Look for Python traceback in terminal where uvicorn is running
# The error will show which field or operation is failing
```

### 2. 404 Not Found on `/api/validation/confidence`

**Error:** `GET /api/validation/confidence HTTP/1.1" 404 Not Found`

**Possible Causes:**
- Router not properly registered
- Endpoint path mismatch
- Server needs restart

**Solution Steps:**

1. **Verify router is registered in main.py:**
```python
# Should have both routers included:
app.include_router(analysis.router)
app.include_router(validation.router)
```

2. **Restart the server:**
```bash
# Stop current server (Ctrl+C)
# Start again
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Test endpoint directly:**
```bash
curl http://localhost:8000/api/validation/confidence
```

4. **Check FastAPI docs:**
```
Open: http://localhost:8000/docs
Look for: GET /api/validation/confidence
If it's not there, the router isn't registered properly
```

## Quick Fix: Complete Reset

If errors persist, perform a complete reset:

```bash
# 1. Stop the server (Ctrl+C)

# 2. Delete database
cd invisible-work-analyzer
rm -f invisible_work.db

# 3. Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# 4. Reinstall dependencies (if needed)
pip install -r requirements.txt

# 5. Restart server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Verification Steps

After applying fixes, verify everything works:

### 1. Check API Documentation
```
Open: http://localhost:8000/docs
Verify all endpoints are listed:
- POST /api/analysis/upload
- POST /api/analysis/upload-multiple
- POST /api/analysis/compare
- GET /api/analysis/
- GET /api/analysis/{id}
- POST /api/validation/
- GET /api/validation/
- GET /api/validation/confidence ← Should be here
- GET /api/validation/{id}
- PUT /api/validation/{id}
```

### 2. Test Upload Endpoint
```bash
# Create a test file
echo "Mentored junior developer on React best practices" > test.txt

# Upload it
curl -X POST http://localhost:8000/api/analysis/upload \
  -F "file=@test.txt" \
  -v
```

Expected: 201 Created with JSON response

### 3. Test Validation Confidence
```bash
curl http://localhost:8000/api/validation/confidence
```

Expected: 200 OK with JSON:
```json
{
  "confidence_score": 0.0,
  "total_validations": 0,
  "approved_count": 0,
  "rejected_count": 0,
  "pending_count": 0
}
```

## Common Issues

### Issue: "No module named 'pydantic'"
**Solution:**
```bash
pip install pydantic fastapi sqlalchemy aiosqlite python-multipart
```

### Issue: "Database is locked"
**Solution:**
```bash
# Stop all running instances
pkill -f uvicorn
# Delete database
rm invisible_work.db
# Restart
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue: "CORS error in browser"
**Solution:** Already configured in main.py with `allow_origins=["*"]`

### Issue: Frontend can't connect
**Solution:**
1. Check backend is running on correct port (8000)
2. Verify frontend API_BASE_URL matches backend
3. Check network connectivity

## Debug Mode

Enable detailed logging:

```python
# In app/main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Database Schema Check

Verify database schema:

```bash
cd invisible-work-analyzer
sqlite3 invisible_work.db ".schema analyses"
sqlite3 invisible_work.db ".schema contribution_validations"
```

Should show all columns including:
- `hidden_hero_score`
- `hidden_hero_classification`
- `hidden_hero_analysis`
- `performance_summary`
- `filenames`
- `number_of_files`

## Contact

If issues persist after following this guide:
1. Check server terminal for Python tracebacks
2. Check browser console for frontend errors
3. Verify all files match the latest version
4. Consider complete reinstall

---

**HiddenImpact™** - Workforce Intelligence Platform
Created by Rajan Singh | Powered by IBM BOB