#!/bin/bash
# Quick Start Script for Agentic AI Research Tool
# ==============================================
# One-command setup and execution of the complete research pipeline

set -e

echo "================================================"
echo "🔬 Agentic AI Research Tool - Quick Start"
echo "================================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "patterns" ]; then
    echo -e "${RED}❌ Error: This script must be run from the agentic AI patterns repository root${NC}"
    exit 1
fi

# Parse command line arguments
STEP_1=true
STEP_2=true
STEP_3=true
STEP_4=true
STEP_5=true
OLLAMA_MODEL=${OLLAMA_MODEL:-mistral}
RUN_INTEGRATION=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --steps)
            STEP_1=false
            STEP_2=false
            STEP_3=false
            STEP_4=false
            STEP_5=false
            shift
            while [[ $# -gt 0 ]] && [[ $1 =~ ^[0-9]$ ]]; do
                case $1 in
                    1) STEP_1=true ;;
                    2) STEP_2=true ;;
                    3) STEP_3=true ;;
                    4) STEP_4=true ;;
                    5) STEP_5=true ;;
                esac
                shift
            done
            ;;
        --model)
            OLLAMA_MODEL=$2
            shift 2
            ;;
        --integrate)
            RUN_INTEGRATION=true
            shift
            ;;
        --help)
            echo "Usage: ./quick_start_research.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --steps [1-5]          Run specific steps (default: all)"
            echo "  --model <name>         Ollama model to use (default: mistral)"
            echo "  --integrate            Run integration helper after research"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./quick_start_research.sh"
            echo "  ./quick_start_research.sh --steps 1 2 3"
            echo "  ./quick_start_research.sh --model neural-chat --steps 2 5"
            echo "  ./quick_start_research.sh --integrate"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Step 1: Check dependencies
echo ""
echo -e "${YELLOW}📋 Checking dependencies...${NC}"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check if Ollama is running
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama is not installed${NC}"
    echo "   Install from: https://ollama.ai"
    exit 1
fi
echo -e "${GREEN}✅ Ollama found${NC}"

# Check if Ollama daemon is running
if ! pgrep -f "ollama serve" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama daemon is not running${NC}"
    echo "   Start with: ollama serve"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Ollama model is available
echo -e "${YELLOW}Checking Ollama model: $OLLAMA_MODEL${NC}"
if ! ollama list | grep -q "$OLLAMA_MODEL"; then
    echo -e "${YELLOW}⚠️  Model not found. Pulling: $OLLAMA_MODEL${NC}"
    ollama pull "$OLLAMA_MODEL"
fi
echo -e "${GREEN}✅ Ollama model ready: $OLLAMA_MODEL${NC}"

# Step 2: Install Python dependencies
echo ""
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"

if pip list | grep -q requests; then
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
else
    echo "   Installing from research_requirements.txt..."
    pip install -r research_requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Step 3: Create research session directory
mkdir -p research_sessions
mkdir -p integration_reports

# Step 4: Run research tool
echo ""
echo -e "${YELLOW}🔬 Running Research Tool...${NC}"

STEPS_ARG=""
if [ "$STEP_1" = true ]; then STEPS_ARG="$STEPS_ARG 1"; fi
if [ "$STEP_2" = true ]; then STEPS_ARG="$STEPS_ARG 2"; fi
if [ "$STEP_3" = true ]; then STEPS_ARG="$STEPS_ARG 3"; fi
if [ "$STEP_4" = true ]; then STEPS_ARG="$STEPS_ARG 4"; fi
if [ "$STEP_5" = true ]; then STEPS_ARG="$STEPS_ARG 5"; fi

export OLLAMA_MODEL=$OLLAMA_MODEL

python3 agentic_ai_research_tool.py --steps $STEPS_ARG

# Get the latest session file
LATEST_SESSION=$(ls -t research_sessions/*.json | head -1)

echo -e "${GREEN}✅ Research tool completed${NC}"
echo "   Session: $(basename $LATEST_SESSION)"

# Step 5: Optional integration
if [ "$RUN_INTEGRATION" = true ]; then
    echo ""
    echo -e "${YELLOW}🔧 Running Integration Helper...${NC}"
    python3 integrate_research.py "$(basename $LATEST_SESSION)"
    echo -e "${GREEN}✅ Integration helper completed${NC}"
fi

# Final summary
echo ""
echo "================================================"
echo -e "${GREEN}✅ Research Pipeline Completed Successfully${NC}"
echo "================================================"
echo ""
echo "📁 Output files:"
echo "   - Session data: $LATEST_SESSION"
echo "   - Integration reports: integration_reports/"
echo ""
echo "📖 Next steps:"
echo "   1. Review session results: cat $LATEST_SESSION | python3 -m json.tool"
echo "   2. Generate integration report: python3 integrate_research.py $(basename $LATEST_SESSION)"
echo "   3. Review new patterns and updates"
echo "   4. Apply changes to pattern library"
echo ""
echo "💡 Tips:"
echo "   - Use --steps to run only specific steps"
echo "   - Use --model to change Ollama model"
echo "   - Check RESEARCH_TOOL_GUIDE.md for detailed documentation"
echo ""
