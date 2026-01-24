#!/usr/bin/env python3
"""
Test all backend module imports and basic functionality.
"""
import sys
sys.path.insert(0, '/mnt/Data/Techsprint/Retro-fit/backend')

print("\n" + "="*60)
print("TESTING ALL MODULE IMPORTS")
print("="*60)

tests_passed = 0
tests_failed = 0

# Test 1: app.main
try:
    from app.main import app
    print("✓ app.main imports successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.main FAILED: {e}")
    tests_failed += 1

# Test 2: modernization router
try:
    from app.routers.modernization import router
    print("✓ app.routers.modernization imports successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.routers.modernization FAILED: {e}")
    tests_failed += 1

# Test 3: auditor
try:
    from app.services.auditor import CodeAuditor
    auditor = CodeAuditor()
    print("✓ app.services.auditor imports and instantiates successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.services.auditor FAILED: {e}")
    tests_failed += 1

# Test 4: refactor
try:
    from app.services.refactor import CodeRefactorer
    refactorer = CodeRefactorer()
    print("✓ app.services.refactor imports and instantiates successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.services.refactor FAILED: {e}")
    tests_failed += 1

# Test 5: cloudbuild
try:
    from app.services.cloudbuild import CloudBuildService, get_cloud_build_service
    build_service = get_cloud_build_service(use_simulate=True)
    print("✓ app.services.cloudbuild imports and instantiates successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.services.cloudbuild FAILED: {e}")
    tests_failed += 1

# Test 6: json_parser
try:
    from app.utils.json_parser import JSONParser
    parser = JSONParser()
    print("✓ app.utils.json_parser imports and instantiates successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.utils.json_parser FAILED: {e}")
    tests_failed += 1

# Test 7: sanitizer
try:
    from app.utils.sanitizer import sanitizer_service
    print("✓ app.utils.sanitizer imports and instantiates successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.utils.sanitizer FAILED: {e}")
    tests_failed += 1

# Test 8: storage
try:
    from app.services.storage import StorageService
    print("✓ app.services.storage imports successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.services.storage FAILED: {e}")
    tests_failed += 1

# Test 9: config
try:
    from app.core.config import settings
    print(f"✓ app.core.config imports successfully (Project: {settings.GCP_PROJECT_ID})")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.core.config FAILED: {e}")
    tests_failed += 1

# Test 10: schemas
try:
    from app.models.schemas import ProcessingStateResponse, ProcessingStatus
    print("✓ app.models.schemas imports successfully")
    tests_passed += 1
except Exception as e:
    print(f"✗ app.models.schemas FAILED: {e}")
    tests_failed += 1

print("\n" + "="*60)
print(f"TEST RESULTS: {tests_passed} passed, {tests_failed} failed")
print("="*60 + "\n")

if tests_failed == 0:
    print("✓ ALL TESTS PASSED - BACKEND READY FOR DEPLOYMENT")
    sys.exit(0)
else:
    print(f"✗ {tests_failed} TESTS FAILED")
    sys.exit(1)
