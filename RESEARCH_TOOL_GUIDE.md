# Agentic AI Research Tool - Complete Guide

A comprehensive 5-step research pipeline for discovering, analyzing, and integrating latest agentic AI patterns, papers, articles, and best practices.

## Overview

This tool automates the process of staying current with agentic AI research and evolving your pattern library:

```
Step 1: Search & Curate      → Discover latest papers, articles, blogs, videos (2-3 months)
         ↓
Step 2: Analyze              → Extract insights and key concepts using Ollama
         ↓
Step 3: Map Patterns         → Compare against existing patterns in your library
         ↓
Step 4: Integrate            → Identify new patterns and updates to existing ones
         ↓
Step 5: Verify               → Use Ollama to verify insights are grounded, not hallucinated
```

## Quick Start

### Installation

1. Install research tool dependencies:
```bash
pip install -r research_requirements.txt
```

2. Install and run Ollama locally:
```bash
# Install from https://ollama.ai
# Run Ollama in the background
ollama serve

# In another terminal, pull a model
ollama pull mistral          # Lightweight, fast
# OR
ollama pull neural-chat      # Better for analysis
# OR
ollama pull llama2           # Most capable
```

3. Run the tool:
```bash
# Full pipeline
python agentic_ai_research_tool.py

# Specific steps only
python agentic_ai_research_tool.py --steps 1 2 3

# With custom Ollama model
OLLAMA_MODEL=neural-chat python agentic_ai_research_tool.py
```

## Step-by-Step Breakdown

### Step 1: Search & Curate

**What it does:**
- Searches arXiv for recent papers matching agentic AI keywords
- Searches web for articles, blogs, and reports
- Deduplicates and ranks results by relevance
- Keeps top 20 high-quality references

**Default search keywords:**
- "agentic AI"
- "multi-agent systems"
- "agent patterns"
- "AI agent architecture"
- "large language model agents"
- "agent reasoning"
- "agent coordination"
- "agent frameworks"
- "autonomous agents"
- "AI workflows"

**Output:**
```json
{
  "references": [
    {
      "title": "Agents as Graphs: AI Agents as Graph Neural Networks",
      "url": "https://arxiv.org/abs/2406.01234",
      "source_type": "paper",
      "published_date": "2024-06-01",
      "relevance_score": 0.95,
      "key_concepts": ["agent architecture", "graph reasoning", "multi-agent"]
    },
    ...
  ]
}
```

### Step 2: Analyze

**What it does:**
- For each reference, uses Ollama local LLM to extract:
  - Key insights (3-5 main points)
  - Core concepts mentioned
  - Relevance to agentic AI patterns
  - Relevant pattern categories
  - Actionable takeaways

**Ollama Prompt Template:**
```
Analyze the following academic/technical reference about agentic AI:
- Extract key insights
- Identify main concepts
- Rate relevance to patterns
- Suggest pattern categories
- Provide actionable takeaways
```

**Output:**
```json
{
  "https://arxiv.org/abs/2406.01234": {
    "reference": { /* reference data */ },
    "analysis": {
      "key_insights": [
        "Graph-based agent reasoning improves task decomposition",
        "Multi-agent coordination benefits from explicit graph structure",
        ...
      ],
      "concepts": ["agent architecture", "graph reasoning", "coordination"],
      "relevance": "high",
      "pattern_categories": ["orchestrator-workers", "hierarchical-team"],
      "actionable_takeaways": [...]
    }
  }
}
```

**Model recommendations:**
- **Mistral**: Fast, lightweight, good for basic analysis (~30GB memory)
- **Neural-Chat**: Balanced speed/quality, excellent for analysis (~40GB memory)
- **Llama2**: Most capable, slower, best quality (~50GB memory)

### Step 3: Map Patterns

**What it does:**
- Loads your existing pattern library
- For each analyzed reference, identifies related patterns
- Creates mapping between new research and existing patterns
- Flags patterns that could be enhanced or updated

**Matching algorithm:**
- Concept-to-pattern matching (case-insensitive)
- Pattern name decomposition
- Fuzzy string matching for related concepts

**Output:**
```json
{
  "insights": [
    {
      "pattern_name": "orchestrator-workers",
      "pattern_path": "patterns/orchestrator-workers",
      "references": ["https://arxiv.org/abs/2406.01234"],
      "update_type": "enhancement",
      "reasoning": "New graph-based approach could enhance pattern"
    },
    ...
  ]
}
```

### Step 4: Integrate

**What it does:**
- Identifies insights that map to existing patterns (enhancement candidates)
- Detects insights for new patterns not in library
- Generates comprehensive integration report
- Prepares update recommendations

**Update types:**
- **new**: Introduces pattern not in current library
- **update**: Substantive change to existing pattern
- **enhancement**: Improvement or refinement to existing pattern
- **related**: Related research but not direct pattern

**Output:**
```json
{
  "timestamp": "2024-06-15T10:30:00",
  "total_insights": 15,
  "pattern_updates": 3,
  "pattern_enhancements": 5,
  "related_patterns": 4,
  "new_patterns": 3,
  "summary": "Found 15 pattern insights and 3 potential new patterns"
}
```

### Step 5: Verify

**What it does:**
- For each pattern insight, uses Ollama to verify:
  - Is it directly supported by the reference?
  - Is it a reasonable inference?
  - Are there any hallucinations or unsupported claims?
  - Assigns confidence score (0.0-1.0)

**Verification prompt template:**
```
Verify if this pattern insight is grounded:
- Pattern name
- Update type
- Original reasoning
- Reference title, insights, concepts

Rate:
- Is it supported by reference?
- Is it reasonable inference?
- Hallucinations detected?
- Confidence score
```

**Output:**
```json
{
  "timestamp": "2024-06-15T10:35:00",
  "total_verified": 12,
  "high_confidence_count": 10,
  "verifications": {
    "orchestrator-workers": {
      "supported": true,
      "reasonable": true,
      "hallucinations": "None detected",
      "confidence": 0.92
    },
    ...
  }
}
```

## Understanding Results

### Session Output

Each research session generates:

1. **Console output** - Real-time progress and summaries
2. **JSON session file** - Complete session data in `research_sessions/session_YYYYMMDD_HHMMSS.json`

### Key Metrics

- **Relevance Score** (0.0-1.0): How relevant is the reference to agentic AI?
- **Confidence Score** (0.0-1.0): How confident is the verification that insight is grounded?
- **High Confidence**: Insights with confidence > 0.7

### Interpreting Insights

**Green flag insights** (confidence > 0.8):
- Directly supported by academic sources
- Clear pattern mapping
- Ready for integration into library

**Yellow flag insights** (0.6-0.8 confidence):
- Reasonable inferences with good basis
- May need additional research/validation
- Good candidates for "emerging" or "experimental" sections

**Red flag insights** (< 0.6 confidence):
- Require additional verification
- Possible hallucinations
- Skip for now, revisit after more research

## Advanced Usage

### Custom Search Keywords

Edit the search keywords in the tool:

```python
self.search_keywords = [
    "your-custom-keyword-1",
    "your-custom-keyword-2",
    # ...
]
```

### Using Different Ollama Models

```bash
# List available models
ollama list

# Use specific model for analysis
OLLAMA_MODEL=llama2 python agentic_ai_research_tool.py

# Use specific model for verification
OLLAMA_MODEL=neural-chat python agentic_ai_research_tool.py --steps 5
```

### Running Specific Steps

```bash
# Only search and curate
python agentic_ai_research_tool.py --steps 1

# Skip search, only analyze existing references
python agentic_ai_research_tool.py --steps 2

# Only map and integrate
python agentic_ai_research_tool.py --steps 3 4

# Only verify with new model
OLLAMA_MODEL=llama2 python agentic_ai_research_tool.py --steps 5
```

### Verbose Output

```bash
python agentic_ai_research_tool.py --verbose
```

### Custom Repository Path

```bash
python agentic_ai_research_tool.py --repo /path/to/patterns/repo
```

## Integration Workflow

### Recommended Process

1. **Run research tool** - Discovers latest research and creates analysis
2. **Review high-confidence insights** - Focus on confidence > 0.8
3. **Check existing patterns** - See what maps and what's new
4. **Create update plan** - Plan pattern updates/additions
5. **Implement changes** - Update pattern documentation
6. **Run verification** - Re-verify after implementation
7. **Update REFERENCE_MATERIALS.md** - Add new references

### Creating New Patterns from Research

When a new pattern emerges:

1. Create pattern directory: `patterns/new-pattern-name/`
2. Create README.md with:
   - What it does
   - When to use / when NOT to use
   - ASCII diagram
   - Real-world examples
   - Academic references (cite the research that inspired it)
   - Related patterns
3. Create code.py with implementation example
4. Add to pattern-groups/ if similar to existing patterns
5. Update main README.md categories
6. Add references to REFERENCE_MATERIALS.md

### Updating Existing Patterns

When research enhances existing patterns:

1. Review the specific insights and references
2. Check current pattern documentation
3. Identify what's missing or outdated
4. Update README.md with new information
5. Add new code examples if relevant
6. Update references section
7. Consider updating related pattern-groups

## Troubleshooting

### Ollama Not Available

```
⚠️  Ollama not available. Using template-based analysis.
```

**Solution:** Install and run Ollama:
```bash
# Install from https://ollama.ai
ollama serve  # in one terminal

# Pull a model in another terminal
ollama pull mistral
```

### Web Dependencies Missing

```
⚠️  Web dependencies not installed. Using mock data.
```

**Solution:** Install web dependencies:
```bash
pip install requests beautifulsoup4 lxml arxiv
```

### Ollama Model Not Found

```
Error: model 'your-model-name' not found
```

**Solution:** Pull the model first:
```bash
ollama pull your-model-name
ollama list  # verify it's available
```

### Session Not Saving

Check that `research_sessions/` directory exists:
```bash
mkdir -p research_sessions
```

### Slow Analysis

Using more capable models (llama2) takes longer:
- Mistral: ~2-3 minutes per reference
- Neural-Chat: ~3-5 minutes per reference
- Llama2: ~5-10 minutes per reference

Use `--steps` to run only needed steps and avoid redundant analysis.

## Performance Tips

1. **Start with Mistral** - Fastest for initial discovery
2. **Use Neural-Chat for detailed analysis** - Better concept extraction
3. **Run Step 5 separately** - Verification takes longest, can be parallelized
4. **Reuse analyses** - Save session outputs and rerun only Step 5 with different model
5. **Batch processing** - Group multiple searches into one session

## Configuration

### Environment Variables

```bash
# Specify Ollama model
export OLLAMA_MODEL=neural-chat

# Specify Ollama timeout (seconds)
export OLLAMA_TIMEOUT=120

# Enable debug logging
export DEBUG=1
```

### Custom Configuration File

Create `.env` file in repo root:
```
OLLAMA_MODEL=neural-chat
OLLAMA_TIMEOUT=180
DEBUG=0
```

## Output Structure

```
research_sessions/
├── session_20240615_103000.json
├── session_20240614_150000.json
└── ...
```

Each session file contains:
```json
{
  "session_id": "session_20240615_103000",
  "created_at": "2024-06-15T10:30:00",
  "steps": {
    "1": { "status": "completed", "references_found": 20, ... },
    "2": { "status": "completed", "analyses_count": 20, ... },
    "3": { "status": "completed", "insights_found": 15, ... },
    "4": { "status": "completed", "summary": "...", ... },
    "5": { "status": "completed", "verified_count": 12, ... }
  }
}
```

## Best Practices

1. **Run regularly** - Monthly or quarterly to stay current
2. **Focus on high-confidence insights** - Use verification scores to filter
3. **Document reasoning** - Keep notes on why patterns were added/updated
4. **Cross-reference** - Verify insights against multiple papers when possible
5. **Version control** - Commit pattern changes with reference links
6. **Update REFERENCE_MATERIALS.md** - Maintain comprehensive reference list

## API Integration (Advanced)

### Using with Custom Search APIs

Extend `Step1SearchAndCurate` class:

```python
class CustomSearchStep(Step1SearchAndCurate):
    def search_custom_api(self, keyword: str) -> List[ResearchReference]:
        # Implement your custom API search
        pass

    def run(self) -> List[ResearchReference]:
        # Include your custom search
        all_references.extend(self.search_custom_api(keyword))
        return self.curate_references(all_references)
```

### Integrating with LangChain/Other Frameworks

```python
from langchain.llms import Ollama

# Replace Ollama direct calls with LangChain integration
llm = Ollama(model="mistral")
result = llm.predict(prompt)
```

## Contributing Back

If research tool discovers significant new patterns or improvements:

1. Create detailed pull request with research documentation
2. Include links to academic papers supporting the pattern
3. Provide code examples and use cases
4. Update all relevant documentation
5. Cross-reference with existing patterns

## Resources

- **Ollama**: https://ollama.ai
- **arXiv**: https://arxiv.org
- **LangChain**: https://langchain.com
- **CrewAI**: https://crewai.com
- **AutoGen**: https://microsoft.github.io/autogen/

## License

This research tool follows the same license as the main agentic AI patterns repository.

---

Last updated: 2024-06-15
Tool version: 1.0
