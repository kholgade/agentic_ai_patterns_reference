#!/usr/bin/env python3
"""
Integration Helper - Apply Research Tool Findings to Pattern Library

This script helps apply research tool findings:
1. Review high-confidence insights from research session
2. Generate update recommendations for patterns
3. Create new pattern templates from discovered patterns
4. Update REFERENCE_MATERIALS.md with new references
5. Generate commit-ready documentation
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import argparse


class ResearchIntegrator:
    """Apply research findings to pattern library."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.patterns_dir = self.repo_path / "patterns"
        self.references_file = self.repo_path / "REFERENCE_MATERIALS.md"

    def load_session(self, session_file: str) -> Dict[str, Any]:
        """Load a research session file."""
        session_path = self.repo_path / "research_sessions" / session_file
        if not session_path.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")

        with open(session_path) as f:
            return json.load(f)

    def extract_high_confidence_insights(self, session: Dict[str, Any],
                                        threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Extract insights above confidence threshold."""
        insights = []

        if 5 not in session.get("steps", {}):
            logging.warning("  No verification data (Step 5) in session")
            return insights

        verifications = session["steps"][5].get("verifications", {})

        for pattern_name, verification in verifications.items():
            confidence = verification.get("confidence", 0)
            if confidence >= threshold:
                insights.append({
                    "pattern_name": pattern_name,
                    "confidence": confidence,
                    "verification": verification
                })

        return sorted(insights, key=lambda x: x["confidence"], reverse=True)

    def generate_pattern_update_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive pattern update report."""
        report = {
            "session_id": session.get("session_id"),
            "generated_at": datetime.now().isoformat(),
            "high_confidence_insights": self.extract_high_confidence_insights(session, 0.8),
            "medium_confidence_insights": self.extract_high_confidence_insights(session, 0.6),
            "update_recommendations": [],
            "new_pattern_candidates": [],
            "references_to_add": []
        }

        # Extract new patterns
        if 4 in session.get("steps", {}):
            integration = session["steps"][4]
            new_patterns = integration.get("new_patterns", [])
            report["new_pattern_candidates"] = new_patterns

        # Extract references
        if 1 in session.get("steps", {}):
            references = session["steps"][1].get("references", [])
            report["references_to_add"] = references

        return report

    def generate_new_pattern_template(self, pattern_name: str,
                                     analysis: Dict[str, Any],
                                     references: List[Dict[str, str]]) -> str:
        """Generate a new pattern README template."""
        template = f"""# {pattern_name.replace('-', ' ').title()}

## Overview

This is an emerging pattern discovered through research analysis.

**Key Concepts**: {', '.join(analysis.get('concepts', []))}

## What It Does

[Description based on research analysis...]

## When to Use

- [Use case 1]
- [Use case 2]
- [Use case 3]

## When NOT to Use

- [Anti-pattern 1]
- [Anti-pattern 2]

## Architecture Diagram

```
[ASCII diagram of pattern flow]
```

## Real-World Examples

### Example 1

[Example description and code]

### Example 2

[Example description and code]

## Implementation Guide

### Python Example

```python
# Implementation example
```

### JavaScript/TypeScript Example

```javascript
// Implementation example
```

## Related Patterns

- [Related pattern 1]
- [Related pattern 2]
- [Related pattern 3]

## Pros & Cons

### Advantages

- [Advantage 1]
- [Advantage 2]

### Disadvantages

- [Disadvantage 1]
- [Disadvantage 2]

## Trade-offs

| Aspect | Trade-off |
|--------|-----------|
| Complexity | [Trade-off description] |
| Performance | [Trade-off description] |
| Cost | [Trade-off description] |

## Key References

{self._format_references(references)}

## Additional Resources

- [Resource 1]
- [Resource 2]

---

**Status**: Emerging Pattern (Discovered {datetime.now().strftime('%Y-%m-%d')})
**Confidence**: Based on research analysis
"""
        return template

    def _format_references(self, references: List[Dict[str, str]]) -> str:
        """Format references as markdown."""
        lines = []
        for i, ref in enumerate(references, 1):
            title = ref.get("title", "Reference")
            url = ref.get("url", "#")
            lines.append(f"{i}. [{title}]({url})")
        return "\n".join(lines)

    def generate_reference_additions(self, references: List[Dict[str, str]]) -> str:
        """Generate markdown for new references to add to REFERENCE_MATERIALS.md."""
        lines = [
            f"\n## New References (Added {datetime.now().strftime('%Y-%m-%d')})\n",
            "| Ref Article Name | Link | Referenced In (Pattern/System) |",
            "|---|---|---|"
        ]

        for ref in references:
            title = ref.get("title", "Untitled")
            url = ref.get("url", "#")
            pattern = ref.get("pattern", "to-be-determined")
            lines.append(f"| {title} | [{url}]({url}) | {pattern} |")

        return "\n".join(lines)

    def create_update_checklist(self, report: Dict[str, Any]) -> str:
        """Generate a checklist for applying updates."""
        checklist = f"""# Research Integration Checklist

Session: {report.get('session_id')}
Generated: {report.get('generated_at')}

## High-Confidence Updates ({len(report.get('high_confidence_insights', []))} items)

These should be prioritized for integration:

"""

        for insight in report.get("high_confidence_insights", []):
            pattern = insight.get("pattern_name", "unknown")
            confidence = insight.get("confidence", 0)
            checklist += f"- [ ] **{pattern}** (confidence: {confidence:.2%})\n"

        checklist += f"""
## Medium-Confidence Insights ({len(report.get('medium_confidence_insights', []))} items)

These should be reviewed and considered:

"""

        for insight in report.get("medium_confidence_insights", []):
            pattern = insight.get("pattern_name", "unknown")
            confidence = insight.get("confidence", 0)
            checklist += f"- [ ] **{pattern}** (confidence: {confidence:.2%})\n"

        checklist += f"""
## New Pattern Candidates ({len(report.get('new_pattern_candidates', []))} items)

Consider creating new patterns for:

"""

        for pattern in report.get("new_pattern_candidates", []):
            name = pattern.get("pattern_name", "unnamed")
            checklist += f"- [ ] Create: `{name}`\n"

        checklist += f"""
## Integration Steps

1. [ ] Review all insights and verify alignment with existing patterns
2. [ ] Create new pattern templates for new candidates
3. [ ] Update existing pattern documentation with enhancements
4. [ ] Add new references to REFERENCE_MATERIALS.md
5. [ ] Test pattern examples and verify documentation
6. [ ] Update main README.md with any category changes
7. [ ] Create git commit with all changes
8. [ ] Push changes to feature branch

## Notes

[Add notes about specific insights and decisions here]

---

Generated: {datetime.now().isoformat()}
"""
        return checklist

    def run(self, session_file: str, output_dir: Optional[str] = None):
        """Run integration assistant."""
        logging.debug("\n" + "="*70)
        logging.info(" RESEARCH INTEGRATION HELPER")
        logging.debug("="*70)

        # Load session
        logging.debug(f"\n📂 Loading session: {session_file}")
        try:
            session = self.load_session(session_file)
        except FileNotFoundError as e:
            logging.debug(f"❌ Error: {e}")
            return

        # Generate report
        logging.debug("\n📊 Generating integration report...")
        report = self.generate_pattern_update_report(session)

        # Output path
        output_path = Path(output_dir or "integration_reports")
        output_path.mkdir(exist_ok=True)

        # Save report
        report_file = output_path / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        logging.debug(f"✅ Report saved: {report_file}")

        # Generate checklist
        logging.debug("\n📋 Generating integration checklist...")
        checklist = self.create_update_checklist(report)
        checklist_file = output_path / f"checklist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(checklist_file, "w") as f:
            f.write(checklist)
        logging.debug(f"✅ Checklist saved: {checklist_file}")

        # Generate new pattern templates
        new_patterns = report.get("new_pattern_candidates", [])
        if new_patterns:
            logging.debug(f"\n🆕 Generating {len(new_patterns)} new pattern templates...")
            templates_dir = output_path / "new_patterns"
            templates_dir.mkdir(exist_ok=True)

            for pattern in new_patterns[:3]:  # Limit to 3 templates
                pattern_name = pattern.get("pattern_name", "unnamed")
                template = self.generate_new_pattern_template(
                    pattern_name,
                    {},
                    report.get("references_to_add", [])[:3]
                )

                template_file = templates_dir / f"{pattern_name}_README.md"
                with open(template_file, "w") as f:
                    f.write(template)
                logging.debug(f"   ✅ {pattern_name}")

        # Generate reference additions
        references = report.get("references_to_add", [])
        if references:
            logging.debug(f"\n📚 Generating reference additions ({len(references)} items)...")
            ref_additions = self.generate_reference_additions(references[:10])
            ref_file = output_path / f"references_to_add_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(ref_file, "w") as f:
                f.write(ref_additions)
            logging.debug(f"✅ References file: {ref_file}")

        # Print summary
        logging.debug("\n" + "="*70)
        logging.debug("📈 INTEGRATION SUMMARY")
        logging.debug("="*70)
        logging.debug(f"Session ID: {report.get('session_id')}")
        logging.debug(f"High-confidence insights: {len(report.get('high_confidence_insights', []))}")
        logging.debug(f"Medium-confidence insights: {len(report.get('medium_confidence_insights', []))}")
        logging.debug(f"New pattern candidates: {len(new_patterns)}")
        logging.debug(f"References to add: {len(references)}")
        logging.debug(f"\nGenerated in: {output_path}")
        logging.debug("\nNext steps:")
        logging.debug(f"1. Review checklist: {checklist_file}")
        logging.debug(f"2. Check new pattern templates in: {output_path}/new_patterns/")
        logging.debug(f"3. Apply updates to existing patterns")
        logging.debug(f"4. Commit changes with research references")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Integration Helper - Apply Research Tool Findings to Pattern Library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process latest research session
  python integrate_research.py session_20240615_103000.json

  # Process with custom output directory
  python integrate_research.py session_20240615_103000.json -o my_reports/

  # List available sessions
  ls -la research_sessions/
        """
    )

    parser.add_argument(
        "session",
        nargs="?",
        help="Research session filename (in research_sessions/ directory)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory for integration artifacts (default: integration_reports)"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to agentic AI patterns repository"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available research sessions"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('research_integration.log'),
            logging.StreamHandler()
        ]
    )

    repo_path = Path(args.repo)
    sessions_dir = repo_path / "research_sessions"

    if args.list or not args.session:
        logging.debug("\n📂 Available Research Sessions:\n")
        if sessions_dir.exists():
            for session_file in sorted(sessions_dir.glob("*.json"), reverse=True):
                logging.debug(f"  {session_file.name}")
        else:
            logging.debug("  (No sessions found. Run agentic_ai_research_tool.py first)")
        sys.exit(0)

    try:
        integrator = ResearchIntegrator(str(repo_path))
        integrator.run(args.session, args.output)
    except Exception as e:
        logging.debug(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
