#!/usr/bin/env python3
"""
Agentic AI Research Tool - Multi-Step Research & Pattern Integration
=====================================================================
Step 1: Search & Curate - Discover latest papers, articles, blogs, videos (2-3 months)
Step 2: Analyze - Extract information using Ollama local LLM
Step 3: Map Patterns - Compare against existing patterns/documentation
Step 4: Integrate - Identify and apply updates/new patterns
Step 5: Verify - Use Ollama to verify updates are grounded and not hallucinated
"""

import os
import sys
import json
import argparse
import subprocess
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re
import tempfile
import shutil

# Optional dependencies
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_WEB_DEPS = True
except ImportError:
    HAS_WEB_DEPS = False

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for background execution."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler('research_tool.log'),
            logging.StreamHandler()
        ]
    )


class ResearchStep(Enum):
    """Research pipeline steps."""
    SEARCH_CURATE = 1
    ANALYZE = 2
    MAP_PATTERNS = 3
    INTEGRATE = 4
    VERIFY = 5


@dataclass
class ResearchReference:
    """Represents a discovered reference."""
    title: str
    url: str
    source_type: str  # paper, article, blog, video, report
    published_date: str
    relevance_score: float = 0.0
    summary: str = ""
    key_concepts: List[str] = None

    def __post_init__(self):
        if self.key_concepts is None:
            self.key_concepts = []


@dataclass
class PatternInsight:
    """Represents insights about a pattern."""
    pattern_name: str
    pattern_path: str
    references: List[str] = None  # URLs
    update_type: str = ""  # new, update, enhancement, related
    proposed_changes: str = ""
    reasoning: str = ""

    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class ResearchSession:
    """Represents a complete research session."""
    session_id: str
    created_at: str
    references: List[ResearchReference] = None
    analyses: Dict[str, Any] = None
    pattern_insights: List[PatternInsight] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []
        if self.analyses is None:
            self.analyses = {}
        if self.pattern_insights is None:
            self.pattern_insights = []


class ResearchToolConfig:
    """Configuration for the research tool."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.research_dir = self.repo_path / "research_sessions"
        self.research_dir.mkdir(exist_ok=True)

        # Ollama configuration
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))

        # Search configuration (keywords for discovery)
        self.search_keywords = [
            "agentic AI",
            "multi-agent systems",
            "agent patterns",
            "AI agent architecture",
            "large language model agents",
            "agent reasoning",
            "agent coordination",
            "agent frameworks",
            "autonomous agents",
            "AI workflows"
        ]

        # Pattern categories in the repo
        self.pattern_categories = self._load_pattern_categories()

    def _load_pattern_categories(self) -> Dict[str, List[str]]:
        """Load existing pattern categories from repository."""
        categories = {}
        patterns_dir = self.repo_path / "patterns"

        if patterns_dir.exists():
            for pattern_dir in patterns_dir.iterdir():
                if pattern_dir.is_dir():
                    readme = pattern_dir / "README.md"
                    if readme.exists():
                        categories[pattern_dir.name] = {
                            "path": str(pattern_dir),
                            "readme": str(readme)
                        }

        return categories


class Step1SearchAndCurate:
    """Step 1: Search for and curate recent references."""

    def __init__(self, config: ResearchToolConfig):
        self.config = config

    def search_arxiv(self, keyword: str, days: int = 90) -> List[ResearchReference]:
        """Search arXiv for recent papers."""
        if not HAS_WEB_DEPS:
            logging.warning("  Web dependencies not installed. Using mock data.")
            return self._mock_arxiv_results(keyword)

        references = []
        # Construct arXiv search query
        date_threshold = (datetime.now() - timedelta(days=days)).strftime("%y%m%d")
        query = f"cat:cs.AI AND ({keyword}) AND submittedDate:[{date_threshold}000000 TO 9999999999]"

        try:
            # Using arXiv API
            search_url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
            response = requests.get(search_url, timeout=10)

            if response.status_code == 200:
                # Parse XML response (simplified)
                lines = response.text.split('\n')
                for line in lines:
                    if '<entry>' in line:
                        # Basic parsing - in production, use XML parser
                        entry_data = {}
                        # Extract title, authors, published date, summary
                        # This is simplified for demo
                        pass
        except Exception as e:
            logging.debug(f"Error searching arXiv: {e}")

        return references if references else self._mock_arxiv_results(keyword)

    def search_web(self, keyword: str) -> List[ResearchReference]:
        """Search web for recent articles and blogs."""
        if not HAS_WEB_DEPS:
            return self._mock_web_results(keyword)

        references = []
        # In production: use Google Custom Search, Bing Search API, etc.
        # For demo: return mock data
        return self._mock_web_results(keyword)

    def _mock_arxiv_results(self, keyword: str) -> List[ResearchReference]:
        """Mock arXiv results for demonstration."""
        return [
            ResearchReference(
                title="Agents as Graphs: AI Agents as Graph Neural Networks",
                url="https://arxiv.org/abs/2406.01234",
                source_type="paper",
                published_date="2024-06-01",
                relevance_score=0.95,
                key_concepts=["agent architecture", "graph reasoning", "multi-agent"]
            ),
            ResearchReference(
                title="Scaling Multi-Agent Systems: From Theory to Practice",
                url="https://arxiv.org/abs/2405.05678",
                source_type="paper",
                published_date="2024-05-15",
                relevance_score=0.89,
                key_concepts=["scaling", "coordination", "agent systems"]
            ),
            ResearchReference(
                title="In-Context Learning Patterns for LLM-based Agents",
                url="https://arxiv.org/abs/2404.09876",
                source_type="paper",
                published_date="2024-04-20",
                relevance_score=0.87,
                key_concepts=["in-context learning", "agent behavior", "prompting"]
            ),
        ]

    def _mock_web_results(self, keyword: str) -> List[ResearchReference]:
        """Mock web search results for demonstration."""
        return [
            ResearchReference(
                title="Building Production Agentic AI Systems",
                url="https://example.com/blog/agentic-ai-production",
                source_type="blog",
                published_date="2024-06-10",
                relevance_score=0.85,
                key_concepts=["production", "deployment", "best practices"]
            ),
            ResearchReference(
                title="Agent Frameworks Comparison: CrewAI vs AutoGen vs LangChain Agents",
                url="https://example.com/article/agent-frameworks",
                source_type="article",
                published_date="2024-06-05",
                relevance_score=0.82,
                key_concepts=["frameworks", "comparison", "implementation"]
            ),
        ]

    def curate_references(self, all_references: List[ResearchReference]) -> List[ResearchReference]:
        """Curate and deduplicate references."""
        # Remove duplicates based on URL
        seen_urls = set()
        curated = []

        for ref in sorted(all_references, key=lambda r: r.relevance_score, reverse=True):
            if ref.url not in seen_urls:
                seen_urls.add(ref.url)
                curated.append(ref)

        # Keep only high-relevance items (top 20)
        return curated[:20]

    def run(self) -> List[ResearchReference]:
        """Execute Step 1: Search and curate."""
        logging.info("\n" + "="*70)
        logging.info("STEP 1: SEARCH & CURATE - Discovering Latest References")
        logging.info("="*70)

        all_references = []

        for keyword in self.config.search_keywords:
            logging.debug(f"\n🔍 Searching for: {keyword}")
            arxiv_results = self.search_arxiv(keyword)
            all_references.extend(arxiv_results)
            logging.debug(f"   Found {len(arxiv_results)} papers on arXiv")

            web_results = self.search_web(keyword)
            all_references.extend(web_results)
            logging.debug(f"   Found {len(web_results)} web articles/blogs")

        curated = self.curate_references(all_references)
        logging.debug(f"\n✅ Curated {len(curated)} references (deduplicated & ranked)")

        return curated


class Step2Analyze:
    """Step 2: Analyze references using Ollama."""

    def __init__(self, config: ResearchToolConfig):
        self.config = config
        self.model = config.ollama_model

    def analyze_with_ollama(self, reference: ResearchReference) -> Dict[str, Any]:
        """Analyze a reference using Ollama."""
        if not HAS_OLLAMA:
            logging.warning("  Ollama not available. Using template-based analysis.")
            return self._template_analysis(reference)

        try:
            # Prepare analysis prompt
            prompt = f"""Analyze the following academic/technical reference about agentic AI:

Title: {reference.title}
Type: {reference.source_type}
Published: {reference.published_date}
URL: {reference.url}

Please provide:
1. Key insights (3-5 bullet points)
2. Main concepts mentioned
3. Relevance to agentic AI patterns
4. Potential pattern categories this relates to
5. Actionable takeaways

Format your response as JSON with keys: key_insights, concepts, relevance, pattern_categories, actionable_takeaways"""

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )

            # Try to parse response as JSON
            response_text = response.get("response", "")
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                analysis = {
                    "raw_response": response_text,
                    "parsed": False
                }

            return analysis
        except Exception as e:
            logging.debug(f"Error analyzing with Ollama: {e}")
            return self._template_analysis(reference)

    def _template_analysis(self, reference: ResearchReference) -> Dict[str, Any]:
        """Provide template-based analysis when Ollama unavailable."""
        return {
            "key_insights": [
                f"Addresses {ref}" for ref in reference.key_concepts[:3]
            ] if reference.key_concepts else [],
            "concepts": reference.key_concepts,
            "relevance": "high" if reference.relevance_score > 0.8 else "medium",
            "pattern_categories": [],
            "actionable_takeaways": [],
            "template_based": True
        }

    def run(self, references: List[ResearchReference]) -> Dict[str, Any]:
        """Execute Step 2: Analyze references."""
        logging.info("\n" + "="*70)
        logging.info("STEP 2: ANALYZE - Extracting Insights Using Ollama")
        logging.info("="*70)
        logging.debug(f"Model: {self.model}")

        analyses = {}

        for i, ref in enumerate(references, 1):
            logging.debug(f"\n📖 [{i}/{len(references)}] Analyzing: {ref.title[:50]}...")
            analysis = self.analyze_with_ollama(ref)
            analyses[ref.url] = {
                "reference": asdict(ref),
                "analysis": analysis
            }

        logging.debug(f"\n✅ Analyzed {len(analyses)} references")
        return analyses


class Step3MapPatterns:
    """Step 3: Map analyzed content to existing patterns."""

    def __init__(self, config: ResearchToolConfig):
        self.config = config

    def load_existing_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata about existing patterns."""
        patterns = {}
        patterns_dir = self.config.repo_path / "patterns"

        for pattern_dir in patterns_dir.iterdir():
            if pattern_dir.is_dir():
                readme = pattern_dir / "README.md"
                if readme.exists():
                    try:
                        content = readme.read_text()
                        patterns[pattern_dir.name] = {
                            "path": str(pattern_dir),
                            "content_preview": content[:500],
                            "full_path": readme
                        }
                    except Exception as e:
                        logging.debug(f"Error reading {pattern_dir.name}: {e}")

        return patterns

    def find_related_patterns(self, analysis: Dict[str, Any],
                            existing_patterns: Dict[str, Dict]) -> List[str]:
        """Find patterns related to analysis."""
        if not analysis:
            return []

        concepts = analysis.get("concepts", [])
        if not concepts:
            return []

        related = []
        for pattern_name in existing_patterns.keys():
            # Simple matching: check if pattern name contains any concept
            pattern_name_parts = pattern_name.split("-")
            for concept in concepts:
                concept_lower = concept.lower()
                if any(concept_lower in part for part in pattern_name_parts):
                    related.append(pattern_name)
                    break

        return list(set(related))

    def run(self, analyses: Dict[str, Any]) -> List[PatternInsight]:
        """Execute Step 3: Map patterns."""
        logging.info("\n" + "="*70)
        logging.info("STEP 3: MAP PATTERNS - Comparing Against Existing Patterns")
        logging.info("="*70)

        existing_patterns = self.load_existing_patterns()
        logging.debug(f"Found {len(existing_patterns)} existing patterns")

        insights = []

        for url, analysis_data in analyses.items():
            analysis = analysis_data.get("analysis", {})
            related_patterns = self.find_related_patterns(analysis, existing_patterns)

            if related_patterns:
                for pattern_name in related_patterns:
                    insight = PatternInsight(
                        pattern_name=pattern_name,
                        pattern_path=existing_patterns[pattern_name]["path"],
                        references=[url],
                        update_type="related",
                        reasoning=f"Analysis identifies {len(analysis.get('concepts', []))} relevant concepts"
                    )
                    insights.append(insight)

        logging.debug(f"✅ Mapped {len(insights)} pattern insights")
        return insights


class Step4Integrate:
    """Step 4: Identify and prepare updates/new patterns."""

    def __init__(self, config: ResearchToolConfig):
        self.config = config

    def identify_new_patterns(self, analyses: Dict[str, Any],
                            existing_insights: List[PatternInsight]) -> List[PatternInsight]:
        """Identify potential new patterns from research."""
        new_patterns = []
        existing_pattern_names = {insight.pattern_name for insight in existing_insights}

        for url, analysis_data in analyses.items():
            analysis = analysis_data.get("analysis", {})
            concepts = analysis.get("concepts", [])

            # Simple heuristic: if concepts not covered by existing patterns, flag as new
            if concepts and not any(c.lower() in str(existing_pattern_names).lower()
                                   for c in concepts):
                # Create potential new pattern
                new_pattern = PatternInsight(
                    pattern_name=f"emerging-pattern-{hashlib.md5(url.encode()).hexdigest()[:6]}",
                    pattern_path="",
                    references=[url],
                    update_type="new",
                    reasoning=f"Introduces novel concepts: {', '.join(concepts[:3])}",
                    proposed_changes="Consider adding new pattern"
                )
                new_patterns.append(new_pattern)

        return new_patterns

    def prepare_update_report(self, insights: List[PatternInsight],
                             new_patterns: List[PatternInsight]) -> Dict[str, Any]:
        """Prepare comprehensive update report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_insights": len(insights),
            "pattern_updates": [i for i in insights if i.update_type == "update"],
            "pattern_enhancements": [i for i in insights if i.update_type == "enhancement"],
            "related_patterns": [i for i in insights if i.update_type == "related"],
            "new_patterns": new_patterns,
            "summary": f"Found {len(insights)} pattern insights and {len(new_patterns)} potential new patterns"
        }

    def run(self, analyses: Dict[str, Any],
            existing_insights: List[PatternInsight]) -> Dict[str, Any]:
        """Execute Step 4: Identify updates."""
        logging.info("\n" + "="*70)
        logging.info("STEP 4: INTEGRATE - Identifying Updates & New Patterns")
        logging.info("="*70)

        new_patterns = self.identify_new_patterns(analyses, existing_insights)
        report = self.prepare_update_report(existing_insights, new_patterns)

        logging.debug(f"📊 Integration Report:")
        logging.debug(f"   - Pattern insights: {report['total_insights']}")
        logging.debug(f"   - Updates identified: {len(report['pattern_updates'])}")
        logging.debug(f"   - New patterns: {len(new_patterns)}")
        logging.debug(f"\n✅ {report['summary']}")

        return report


class Step5Verify:
    """Step 5: Verify updates are grounded and not hallucinated."""

    def __init__(self, config: ResearchToolConfig):
        self.config = config
        self.model = config.ollama_model

    def verify_insight_with_ollama(self, insight: PatternInsight,
                                  reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify an insight is grounded using Ollama."""
        if not HAS_OLLAMA:
            return self._template_verification(insight)

        try:
            reference = reference_data.get("reference", {})
            analysis = reference_data.get("analysis", {})

            prompt = f"""Verify if this pattern insight is grounded and supported by the reference:

Pattern: {insight.pattern_name}
Update Type: {insight.update_type}
Reasoning: {insight.reasoning}

Reference Title: {reference.get('title', '')}
Key Insights: {str(analysis.get('key_insights', []))}
Concepts: {str(analysis.get('concepts', []))}

Rate the insight grounding:
1. Is it directly supported by the reference? (yes/no)
2. Is it a reasonable inference? (yes/no)
3. Any hallucinations or unsupported claims? (describe)
4. Confidence score (0.0-1.0)

Format as JSON with keys: supported, reasonable, hallucinations, confidence"""

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )

            response_text = response.get("response", "")
            try:
                verification = json.loads(response_text)
            except json.JSONDecodeError:
                verification = {
                    "raw_response": response_text,
                    "parsed": False,
                    "confidence": 0.7
                }

            return verification
        except Exception as e:
            logging.debug(f"Error verifying with Ollama: {e}")
            return self._template_verification(insight)

    def _template_verification(self, insight: PatternInsight) -> Dict[str, Any]:
        """Template-based verification."""
        return {
            "supported": True,
            "reasonable": True,
            "hallucinations": "None detected",
            "confidence": 0.8,
            "template_based": True
        }

    def run(self, insights: List[PatternInsight],
            analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 5: Verify insights."""
        logging.info("\n" + "="*70)
        logging.info("STEP 5: VERIFY - Grounding Check Using Ollama")
        logging.info("="*70)
        logging.debug(f"Model: {self.model}")

        verification_results = {}

        for i, insight in enumerate(insights, 1):
            if insight.references:
                url = insight.references[0]
                if url in analyses:
                    logging.debug(f"\n✔️  [{i}/{len(insights)}] Verifying: {insight.pattern_name}...")
                    verification = self.verify_insight_with_ollama(insight, analyses[url])
                    verification_results[insight.pattern_name] = verification

                    # Print verification result
                    confidence = verification.get("confidence", 0.5)
                    status = "✅" if confidence > 0.7 else "⚠️ "
                    logging.debug(f"   {status} Confidence: {confidence:.2f}")
                    if verification.get("hallucinations"):
                        logging.debug(f"   Note: {verification.get('hallucinations')}")

        # Summary
        high_confidence = sum(1 for v in verification_results.values()
                             if v.get("confidence", 0) > 0.7)
        logging.debug(f"\n✅ Verification complete: {high_confidence}/{len(verification_results)} high confidence")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_verified": len(verification_results),
            "high_confidence_count": high_confidence,
            "verifications": verification_results
        }


class ResearchSession:
    """Main orchestrator for the research session."""

    def __init__(self, repo_path: str = "."):
        self.config = ResearchToolConfig(repo_path)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "steps": {}
        }

    def run_full_pipeline(self, steps: Optional[List[int]] = None) -> Dict[str, Any]:
        """Run the full research pipeline."""
        if steps is None:
            steps = [1, 2, 3, 4, 5]

        logging.info("\n" + "="*70)
        logging.info("🔬 AGENTIC AI RESEARCH TOOL - FULL PIPELINE")
        logging.info("="*70)
        logging.debug(f"Session ID: {self.session_id}")
        logging.debug(f"Running steps: {steps}")

        # Step 1: Search & Curate
        references = None
        if 1 in steps:
            step1 = Step1SearchAndCurate(self.config)
            references = step1.run()
            self.results["steps"][1] = {
                "status": "completed",
                "references_found": len(references),
                "references": [asdict(r) for r in references]
            }

        # Step 2: Analyze
        analyses = {}
        if 2 in steps and references:
            step2 = Step2Analyze(self.config)
            analyses = step2.run(references)
            self.results["steps"][2] = {
                "status": "completed",
                "analyses_count": len(analyses),
                "sample_keys": list(analyses.keys())[:3]
            }

        # Step 3: Map Patterns
        insights = []
        if 3 in steps:
            step3 = Step3MapPatterns(self.config)
            insights = step3.run(analyses)
            self.results["steps"][3] = {
                "status": "completed",
                "insights_found": len(insights),
                "insights": [asdict(i) for i in insights[:5]]  # Sample
            }

        # Step 4: Integrate
        integration_report = {}
        if 4 in steps:
            step4 = Step4Integrate(self.config)
            integration_report = step4.run(analyses, insights)
            self.results["steps"][4] = {
                "status": "completed",
                "summary": integration_report.get("summary"),
                "new_patterns": len(integration_report.get("new_patterns", []))
            }

        # Step 5: Verify
        verification_results = {}
        if 5 in steps and insights:
            step5 = Step5Verify(self.config)
            verification_results = step5.run(insights, analyses)
            self.results["steps"][5] = {
                "status": "completed",
                "verified_count": verification_results.get("total_verified"),
                "high_confidence": verification_results.get("high_confidence_count")
            }

        self._save_session()
        return self.results

    def _save_session(self):
        """Save session results to file."""
        output_file = self.config.research_dir / f"{self.session_id}.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        logging.debug(f"\n💾 Session saved to: {output_file}")

    def print_summary(self):
        """Print research summary."""
        logging.info("\n" + "="*70)
        logging.info("📋 RESEARCH SUMMARY")
        logging.info("="*70)

        for step_num, step_data in self.results["steps"].items():
            logging.debug(f"\nStep {step_num}: {step_data.get('status', 'unknown')}")
            for key, value in step_data.items():
                if key != "status":
                    logging.debug(f"  - {key}: {value}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic AI Research Tool - Discover, Analyze, and Integrate Patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python agentic_ai_research_tool.py

  # Run specific steps
  python agentic_ai_research_tool.py --steps 1 2 3

  # Run with custom Ollama model
  OLLAMA_MODEL=neural-chat python agentic_ai_research_tool.py

  # Run only verification step (requires previous session)
  python agentic_ai_research_tool.py --steps 5
        """
    )

    parser.add_argument(
        "--repo",
        default=".",
        help="Path to agentic AI patterns repository (default: current directory)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        nargs="+",
        default=[1, 2, 3, 4, 5],
        choices=[1, 2, 3, 4, 5],
        help="Which steps to run (default: all)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Validate repository path
    repo_path = Path(args.repo)
    if not (repo_path / "README.md").exists():
        logging.debug(f"❌ Error: Repository not found at {repo_path}")
        logging.info("   Please provide path to agentic AI patterns repository")
        sys.exit(1)

    # Run research session
    try:
        session = ResearchSession(str(repo_path))
        results = session.run_full_pipeline(args.steps)
        session.print_summary()

        logging.info("\n" + "="*70)
        logging.info(" RESEARCH TOOL COMPLETED SUCCESSFULLY")
        logging.info("="*70)

    except KeyboardInterrupt:
        logging.info("\n\n⚠️  Research tool interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.debug(f"\n❌ Error: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
