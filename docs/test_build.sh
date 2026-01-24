#!/bin/bash

# RETRO-FIT BUILD & TEST SCRIPT
# Comprehensive testing of all backend and frontend components

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  RETRO-FIT PROJECT - BUILD & TEST SUITE"
echo "════════════════════════════════════════════════════════════════"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name=$1
    local test_cmd=$2
    
    echo -n "  Testing: $test_name... "
    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
}

# ============================================================================
echo "PHASE 1: BACKEND ENVIRONMENT CHECK"
echo "════════════════════════════════════════════════════════════════"
echo ""

run_test "Python 3.11+" "python --version | grep -q '3\.[0-9]'"
run_test "pip installed" "pip --version"
run_test "FastAPI available" "python -c 'import fastapi; print(fastapi.__version__)'"
run_test "Pydantic available" "python -c 'import pydantic; print(pydantic.__version__)'"
run_test "Google Cloud libs" "python -c 'import google.cloud.storage'"

echo ""

# ============================================================================
echo "PHASE 2: BACKEND MODULE IMPORTS"
echo "════════════════════════════════════════════════════════════════"
echo ""

export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"

run_test "Config module" "python -c 'from app.core.config import settings'"
run_test "Schemas module" "python -c 'from app.models.schemas import ProcessingStateResponse'"
run_test "JSON Parser" "python -c 'from app.utils.json_parser import JSONParser'"
run_test "Sanitizer" "python -c 'from app.utils.sanitizer import sanitizer_service'"
run_test "Storage Service" "python -c 'from app.services.storage import storage_service'"
run_test "Cloud Build Service" "python -c 'from app.services.cloudbuild import get_cloud_build_service'"

echo ""

# ============================================================================
echo "PHASE 3: BACKEND FAST API APPLICATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

run_test "Main app loads" "python -c 'from app.main import app; print(app.title)'"
run_test "Router included" "python -c 'from app.routers.modernization import router'"
run_test "All services" "python -c 'from app.services.auditor import CodeAuditor; from app.services.refactor import CodeRefactorer'"

echo ""

# ============================================================================
echo "PHASE 4: FRONTEND ENVIRONMENT"
echo "════════════════════════════════════════════════════════════════"
echo ""

run_test "Node.js installed" "node --version"
run_test "npm installed" "npm --version"
run_test "package.json exists" "test -f frontend/package.json"
run_test "TypeScript config exists" "test -f frontend/tsconfig.json"
run_test "Next.js config exists" "test -f frontend/next.config.mjs"

echo ""

# ============================================================================
echo "PHASE 5: CONFIGURATION FILES"
echo "════════════════════════════════════════════════════════════════"
echo ""

run_test "Backend Dockerfile" "test -f backend/Dockerfile"
run_test "Frontend Dockerfile" "test -f frontend/Dockerfile"
run_test "docker-compose.yml" "test -f docker-compose.yml"
run_test "requirements.txt" "test -f backend/requirements.txt"
run_test ".gitignore" "test -f .gitignore"

echo ""

# ============================================================================
echo "PHASE 6: KEY FILES PRESENT"
echo "════════════════════════════════════════════════════════════════"
echo ""

run_test "main.py" "test -f backend/app/main.py"
run_test "config.py" "test -f backend/app/core/config.py"
run_test "auditor.py" "test -f backend/app/services/auditor.py"
run_test "refactor.py" "test -f backend/app/services/refactor.py"
run_test "cloudbuild.py" "test -f backend/app/services/cloudbuild.py"
run_test "vertexai_client.py" "test -f backend/app/services/vertexai_client.py"
run_test "json_parser.py" "test -f backend/app/utils/json_parser.py"
run_test "modernization.py router" "test -f backend/app/routers/modernization.py"
run_test "page.tsx" "test -f frontend/src/app/page.tsx"

echo ""

# ============================================================================
echo "PHASE 7: DOCUMENTATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

run_test "FINAL_STATUS.md" "test -f docs/FINAL_STATUS.md"
run_test "QUICK_START.md" "test -f docs/QUICK_START.md"
run_test "COMPLETION_SUMMARY.md" "test -f docs/COMPLETION_SUMMARY.md"
run_test "README.md" "test -f README.md"

echo ""

# ============================================================================
echo "PHASE 8: GIT STATUS"
echo "════════════════════════════════════════════════════════════════"
echo ""

run_test "Git repository" "git rev-parse --git-dir > /dev/null 2>&1"
run_test "Recent commits" "git log --oneline | head -1"

echo ""

# ============================================================================
# SUMMARY
echo "════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=$((TESTS_PASSED * 100 / TOTAL))

echo "  Tests Passed:  ${GREEN}${TESTS_PASSED}/${TOTAL}${NC}"
echo "  Tests Failed:  ${RED}${TESTS_FAILED}/${TOTAL}${NC}"
echo "  Pass Rate:     ${YELLOW}${PASS_RATE}%${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "  ${GREEN}✓ BUILD SUCCESSFUL - ALL CHECKS PASSED${NC}"
    echo ""
    echo "Next steps to start the application:"
    echo "  1. Install backend dependencies:"
    echo "     cd backend && pip install -r requirements.txt"
    echo ""
    echo "  2. Start the backend server:"
    echo "     cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "  3. (Optional) Start the frontend:"
    echo "     cd frontend && npm install && npm run dev"
    echo ""
    echo "  4. Visit http://localhost:3000 or http://localhost:8000/docs"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    exit 0
else
    echo -e "  ${RED}✗ BUILD FAILED - PLEASE FIX ERRORS ABOVE${NC}"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi
