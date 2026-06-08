#!/usr/bin/env python3
"""
HiddenImpact™ Diagnostic Script
Checks for common issues and provides solutions
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    required = [
        'fastapi',
        'sqlalchemy',
        'pydantic',
        'aiosqlite',
        'python-multipart'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    return True

def check_database():
    """Check database file and schema"""
    print("\n🔍 Checking database...")
    db_path = Path("invisible_work.db")
    
    if not db_path.exists():
        print("  ⚠️  Database file not found - will be created on first run")
        return True
    
    print(f"  ✅ Database exists ({db_path.stat().st_size} bytes)")
    
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check analyses table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analyses'")
        if cursor.fetchone():
            print("  ✅ analyses table exists")
            
            # Check for required columns
            cursor.execute("PRAGMA table_info(analyses)")
            columns = {row[1] for row in cursor.fetchall()}
            required_columns = {
                'id', 'filename', 'filenames', 'number_of_files', 'file_type',
                'hidden_hero_score', 'hidden_hero_classification', 'hidden_hero_analysis',
                'performance_summary'
            }
            
            missing_cols = required_columns - columns
            if missing_cols:
                print(f"  ⚠️  Missing columns: {', '.join(missing_cols)}")
                print("     Solution: Delete database and restart server")
                return False
            else:
                print(f"  ✅ All required columns present ({len(columns)} total)")
        else:
            print("  ⚠️  analyses table not found")
        
        # Check contribution_validations table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contribution_validations'")
        if cursor.fetchone():
            print("  ✅ contribution_validations table exists")
        else:
            print("  ⚠️  contribution_validations table not found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\n🔍 Checking file structure...")
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/database.py',
        'app/models.py',
        'app/schemas.py',
        'app/config.py',
        'app/routers/analysis.py',
        'app/routers/validation.py',
        'app/utils/analyzer.py',
        'app/utils/file_processor.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_imports():
    """Test if app modules can be imported"""
    print("\n🔍 Checking imports...")
    
    try:
        from app.models import Analysis, ContributionValidation
        print("  ✅ Models import successfully")
    except Exception as e:
        print(f"  ❌ Models import failed: {e}")
        return False
    
    try:
        from app.schemas import AnalysisResponse, ContributionValidationResponse
        print("  ✅ Schemas import successfully")
    except Exception as e:
        print(f"  ❌ Schemas import failed: {e}")
        return False
    
    try:
        from app.utils.analyzer import InvisibleWorkAnalyzer
        print("  ✅ Analyzer imports successfully")
    except Exception as e:
        print(f"  ❌ Analyzer import failed: {e}")
        return False
    
    return True

def test_analyzer():
    """Test if analyzer works"""
    print("\n🔍 Testing analyzer...")
    
    try:
        from app.utils.analyzer import InvisibleWorkAnalyzer
        analyzer = InvisibleWorkAnalyzer()
        result = analyzer.analyze("Mentored junior developer on React best practices")
        
        print(f"  ✅ Analyzer works")
        print(f"     Score: {result.invisible_work_score}")
        print(f"     Activities: {result.total_activities}")
        return True
    except Exception as e:
        print(f"  ❌ Analyzer test failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("=" * 60)
    print("HiddenImpact™ Diagnostic Tool")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Imports", check_imports),
        ("Database", check_database),
        ("Analyzer", test_analyzer)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Server should work correctly.")
        print("\nStart server with:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n⚠️  Some checks failed. Review errors above.")
        print("\nQuick fixes:")
        print("  1. Install missing dependencies: pip install -r requirements.txt")
        print("  2. Delete database: rm invisible_work.db")
        print("  3. Restart server")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
