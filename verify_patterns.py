#!/usr/bin/env python3
"""
Pattern Verification Runner
============================
Verify that existing patterns are well-grounded in research and identify:
- Patterns with research backing
- Patterns lacking references
- Patterns that may be outdated
- Opportunities for enhancement
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import argparse
import re

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


class PatternVerifier:
    """Verify patterns against research and best practices."""

    def __init__(self, repo_path: str = ".", model: str = "mistral"):
        self.repo_path = Path(repo_path)
        self.patterns_dir = self.repo_path / "patterns"
        self.model = model

    def load_pattern_readme(self, pattern_dir: Path) -> Optional[str]:
        """Load pattern README content."""
        readme = pattern_dir / "README.md"
        if readme.exists():
            return readme.read_text()
        return None

    def extract_references_from_readme(self, content: str) -> List[str]:
        """Extract URLs from pattern README."""
        # Match markdown links and regular URLs
        urls = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', content)
        urls.extend(re.findall(r'(https?://[^\s\)]+)', content))
        return list(set(urls))

    def extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from pattern README."""
        # Look for bold text and headers
        concepts = re.findall(r'\*\*(.*?)\*\*', content)
        concepts.extend(re.findall(r'^## (.*?)$', content, re.MULTILINE))
        return list(set(c.strip() for c in concepts if c.strip()))

    def check_pattern_completeness(self, content: str) -> Dict[str, bool]:
        """Check if pattern has all essential sections."""
        required_sections = [
            ("Overview", r"(## Overview|# Overview)"),
            ("When to Use", r"(## When to Use|# When to Use)"),
            ("When NOT to Use", r"(## When NOT to Use|# When NOT to Use)"),
            ("Examples", r"(## .*Example|# .*Example)"),
            ("References", r"(## Reference|# Reference)"),
        ]

        checks = {}
        for section_name, pattern in required_sections:
            checks[section_name] = bool(re.search(pattern, content, re.IGNORECASE))

        return checks

    def verify_pattern_with_ollama(self, pattern_name: str, content: str) -> Dict[str, Any]:
        """Use Ollama to verify pattern quality."""
        if not HAS_OLLAMA:
            return self._template_verification(pattern_name, content)

        try:
            # Extract content preview
            preview = content[:1500]

            prompt = f"""Evaluate the quality and research grounding of this AI pattern documentation:

Pattern Name: {pattern_name}

Documentation Preview:
{preview}

Please assess:
1. Is it well-documented? (yes/no)
2. Are there sufficient examples? (yes/no)
3. Does it cite academic references? (yes/no)
4. Is it current with latest research? (yes/no)
5. Key strengths (2-3 points)
6. Areas for improvement (2-3 points)
7. Overall quality score (0.0-1.0)

Format as JSON with keys: well_documented, sufficient_examples, has_references, current, strengths, improvements, quality_score"""

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
                    "quality_score": 0.5
                }

            return verification
        except Exception as e:
            print(f"  ⚠️  Ollama error: {e}")
            return self._template_verification(pattern_name, content)

    def _template_verification(self, pattern_name: str, content: str) -> Dict[str, Any]:
        """Template-based verification."""
        completeness = self.check_pattern_completeness(content)
        has_refs = bool(self.extract_references_from_readme(content))

        return {
            "well_documented": len(content) > 1000,
            "sufficient_examples": "Example" in content,
            "has_references": has_refs,
            "current": "2024" in content or "2023" in content,
            "completeness": completeness,
            "quality_score": 0.6 if has_refs else 0.4,
            "template_based": True
        }

    def run_verification(self) -> Dict[str, Any]:
        """Run verification on all patterns."""
        print("\n" + "="*70)
        print("🔍 PATTERN VERIFICATION RUNNER")
        print("="*70)
        print(f"Repository: {self.repo_path}")
        print(f"Ollama Model: {self.model}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "patterns_verified": 0,
            "patterns_with_issues": 0,
            "average_quality": 0.0,
            "patterns": {}
        }

        patterns_to_verify = []
        if self.patterns_dir.exists():
            patterns_to_verify = [d for d in self.patterns_dir.iterdir() if d.is_dir()]

        print(f"\nFound {len(patterns_to_verify)} patterns to verify\n")

        total_quality = 0

        for i, pattern_dir in enumerate(sorted(patterns_to_verify), 1):
            pattern_name = pattern_dir.name
            print(f"[{i}/{len(patterns_to_verify)}] Verifying: {pattern_name}...", end=" ")

            content = self.load_pattern_readme(pattern_dir)
            if not content:
                print("❌ No README found")
                continue

            # Extract information
            references = self.extract_references_from_readme(content)
            concepts = self.extract_concepts(content)
            completeness = self.check_pattern_completeness(content)

            # Verify with Ollama
            verification = self.verify_pattern_with_ollama(pattern_name, content)
            quality_score = verification.get("quality_score", 0.5)

            # Assess status
            if quality_score >= 0.8:
                status = "✅"
                results["patterns_verified"] += 1
            elif quality_score >= 0.6:
                status = "⚠️ "
                results["patterns_with_issues"] += 1
            else:
                status = "❌"
                results["patterns_with_issues"] += 1

            print(f"{status} Quality: {quality_score:.2f}")

            # Store results
            results["patterns"][pattern_name] = {
                "quality_score": quality_score,
                "status": status.strip(),
                "references_count": len(references),
                "concepts": concepts[:5],
                "completeness": completeness,
                "verification": verification,
                "recommendations": self._generate_recommendations(
                    pattern_name, references, completeness, quality_score
                )
            }

            total_quality += quality_score

        # Calculate averages
        if results["patterns"]:
            results["average_quality"] = total_quality / len(results["patterns"])
            results["patterns_verified"] = len([p for p in results["patterns"].values()
                                              if p["quality_score"] >= 0.8])

        return results

    def _generate_recommendations(self, pattern_name: str, references: List[str],
                                  completeness: Dict[str, bool], quality: float) -> List[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []

        if quality < 0.6:
            recommendations.append("Review and rewrite documentation for clarity")

        if len(references) < 3:
            recommendations.append("Add more academic references to strengthen grounding")

        if not completeness.get("When NOT to Use"):
            recommendations.append("Add 'When NOT to Use' section for better context")

        if not completeness.get("Examples"):
            recommendations.append("Add concrete code examples and use cases")

        if quality < 0.8 and completeness.get("References"):
            recommendations.append("Update references with latest papers (2024)")

        return recommendations[:3]  # Return top 3

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed verification report."""
        report = f"""# Pattern Verification Report

Generated: {results.get('timestamp')}

## Executive Summary

- **Total Patterns Verified**: {len(results.get('patterns', {}))}
- **High Quality (>0.8)**: {results.get('patterns_verified', 0)}
- **Patterns with Issues**: {results.get('patterns_with_issues', 0)}
- **Average Quality Score**: {results.get('average_quality', 0):.2f}/1.0

## Detailed Results

### High Quality Patterns (>0.8)

"""
        high_quality = [
            (name, data) for name, data in results.get('patterns', {}).items()
            if data.get('quality_score', 0) > 0.8
        ]
        for name, data in sorted(high_quality, key=lambda x: x[1]['quality_score'], reverse=True):
            report += f"- **{name}** ({data['quality_score']:.2f}) - {data['status']}\n"

        report += "\n### Patterns Needing Improvement (< 0.8)\n\n"
        needs_work = [
            (name, data) for name, data in results.get('patterns', {}).items()
            if data.get('quality_score', 0) <= 0.8
        ]
        for name, data in sorted(needs_work, key=lambda x: x[1]['quality_score']):
            report += f"- **{name}** ({data['quality_score']:.2f}) - {data['status']}\n"
            report += f"  - References: {data.get('references_count', 0)}\n"
            for rec in data.get('recommendations', []):
                report += f"  - 📝 {rec}\n"

        report += "\n## Recommendations by Category\n\n"

        report += "### Missing Academic References\n"
        needs_refs = [
            name for name, data in results.get('patterns', {}).items()
            if data.get('references_count', 0) < 3
        ]
        for name in needs_refs[:10]:
            report += f"- [ ] Add references to `{name}`\n"

        report += "\n### Documentation Improvements\n"
        needs_docs = [
            name for name, data in results.get('patterns', {}).items()
            if not all(data.get('completeness', {}).values())
        ]
        for name in needs_docs[:10]:
            report += f"- [ ] Enhance documentation for `{name}`\n"

        report += f"""

## Next Steps

1. [ ] Address high-priority pattern improvements
2. [ ] Add missing references to patterns
3. [ ] Create missing pattern sections
4. [ ] Update outdated content
5. [ ] Re-verify after updates

---

Report generated: {datetime.now().isoformat()}
"""
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify Pattern Quality and Research Grounding"
    )

    parser.add_argument(
        "--repo",
        default=".",
        help="Path to agentic AI patterns repository"
    )
    parser.add_argument(
        "--model",
        default="mistral",
        help="Ollama model to use for verification"
    )
    parser.add_argument(
        "--output",
        help="Save report to file"
    )
    parser.add_argument(
        "--skip-ollama",
        action="store_true",
        help="Skip Ollama verification, use template-based only"
    )

    args = parser.parse_args()

    if args.skip_ollama:
        globals()['HAS_OLLAMA'] = False
        print("⚠️  Skipping Ollama verification")

    try:
        verifier = PatternVerifier(args.repo, args.model)
        results = verifier.run_verification()

        # Generate report
        report = verifier.generate_report(results)

        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report)
            print(f"\n💾 Report saved to: {output_path}")

        # Print summary
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        print(f"Average Quality: {results.get('average_quality', 0):.2f}/1.0")
        print(f"High Quality: {results.get('patterns_verified', 0)}/{len(results.get('patterns', {}))}")
        print(f"Needs Improvement: {results.get('patterns_with_issues', 0)}/{len(results.get('patterns', {}))}")

        # Print report
        print("\n" + report)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
