# HiddenImpact™ Error Fix Guide

## Diagnosis Complete ✅

The diagnostic script revealed:
- ✅ Database schema is correct (all 30 columns present)
- ✅ File structure is complete
- ⚠️ Dependencies missing in system Python (but server is running, so likely using venv)

## Current Errors

### 1. POST `/api/analysis/upload` → 500 Internal Server Error
### 2. GET `/api/validation/confidence` → 404 Not Found

## Root Cause Analysis

Since the server is running (as shown in your logs), the issue is likely:

1. **For 500 Error**: Runtime exception during file upload processing
2. **For 404 Error**: Possible route caching or server needs restart

## Solution: Complete Server Restart

### Step 1: Stop Current Server

```bash
# In the terminal where uvicorn is running, press:
Ctrl+C

# Or if running in background:
pkill -f "uvicorn app.main:app"
```

### Step 2: Activate Virtual Environment (if using one)

```bash
cd invisible-work-analyzer

# If you have a venv:
source venv/bin/activate  # On macOS/Linux
# OR
.\venv\Scripts\activate   # On Windows
```

### Step 3: Verify/Install Dependencies

```bash
# Check if requirements.txt exists
cat requirements.txt

# Install/update all dependencies
pip install --upgrade fastapi sqlalchemy pydantic aiosqlite python-multipart uvicorn
```

### Step 4: Clear Python Cache

```bash
# Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

### Step 5: Restart Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Verify Endpoints

Open browser and check:

1. **API Documentation**: http://localhost:8000/docs
   - Should show ALL endpoints including `/api/validation/confidence`

2. **Test validation endpoint**:
   ```bash
   curl http://localhost:8000/api/validation/confidence
   ```
   Expected response:
   ```json
   {
     "confidence_score": 0.0,
     "total_validations": 0,
     "approved_count": 0,
     "rejected_count": 0,
     "pending_count": 0
   }
   ```

3. **Test upload endpoint**:
   ```bash
   echo "Mentored junior developer on React" > test.txt
   curl -X POST http://localhost:8000/api/analysis/upload \
     -F "file=@test.txt"
   ```
   Expected: 201 Created with JSON analysis result

## Alternative: Fresh Start

If errors persist, do a complete fresh start:

```bash
# 1. Stop server
pkill -f uvicorn

# 2. Backup database (optional)
cp invisible_work.db invisible_work.db.backup

# 3. Delete database to recreate fresh
rm invisible_work.db

# 4. Clear cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 5. Restart server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will automatically recreate the database with the correct schema on startup.

## Debugging: Enable Detailed Logging

If you still see errors, enable detailed logging to see the exact error:

### Option 1: Add to main.py

```python
# At the top of app/main.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Option 2: Run with --log-level debug

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## Expected Behavior After Fix

### Upload Endpoint
```
POST /api/analysis/upload
Status: 201 Created
Response: {
  "id": 1,
  "filename": "test.txt",
  "invisible_work_score": 85.5,
  "hidden_hero_score": 72.3,
  ...
}
```

### Validation Confidence Endpoint
```
GET /api/validation/confidence
Status: 200 OK
Response: {
  "confidence_score": 0.0,
  "total_validations": 0,
  "approved_count": 0,
  "rejected_count": 0,
  "pending_count": 0
}
```

## Frontend Connection

After backend is fixed, test frontend:

1. **Start frontend** (in separate terminal):
   ```bash
   cd invisible-work-frontend
   npm start
   ```

2. **Open browser**: http://localhost:3000

3. **Test upload**: Try uploading a file through the UI

## Still Having Issues?

### Check Server Logs

Look for Python tracebacks in the terminal where uvicorn is running. The error will show:
- Which line is failing
- What exception occurred
- Missing fields or validation errors

### Common Error Patterns

**If you see "KeyError: 'performance_summary'"**:
- Database schema is outdated
- Solution: Delete database and restart

**If you see "ValidationError"**:
- Pydantic schema mismatch
- Solution: Check schemas.py matches models.py

**If you see "No module named..."**:
- Dependencies not installed in active environment
- Solution: Activate correct venv and install requirements

## Quick Health Check

Run this command to verify everything:

```bash
cd invisible-work-analyzer
python3 diagnose.py
```

Should show:
```
✅ PASS - Dependencies
✅ PASS - File Structure  
✅ PASS - Imports
✅ PASS - Database
✅ PASS - Analyzer

Result: 5/5 checks passed
```

---

**HiddenImpact™** - Workforce Intelligence Platform  
Created by Rajan Singh | Powered by IBM BOB