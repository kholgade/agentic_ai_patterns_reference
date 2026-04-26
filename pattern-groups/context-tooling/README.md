---
group: "Context & Tooling Infrastructure"
patterns: ["Context Compression", "MCP Tool Registry"]
decision_axis: "resource-management"
spectrum: "memory-to-tools"
problem_statement: "How to stabilize long-running agent systems"
pattern_relationship: "complementary"
---

# Context & Tooling Infrastructure Patterns

## Overview

These patterns stabilize long-running agent systems. Context Compression controls token growth; MCP Tool Registry controls tool discovery and compatibility.

---

## Pattern Comparison

### Context Compression
- Maintains high-signal memory under context-window limits
- Best for long sessions and memory-bounded workflows

### MCP Tool Registry
- Normalizes tool capabilities and dynamic binding
- Best for multi-tool, multi-provider interoperability

---

## Side-by-Side

| Aspect | Context Compression | MCP Tool Registry |
|--------|---------------------|-------------------|
| Primary resource managed | Context tokens | Tool capabilities |
| System concern | Memory efficiency | Interface interoperability |
| Best for | Long-running chats/agents | Dynamic tool ecosystems |
| Failure avoided | Context overflow/noise | Tool mismatch/brittle integrations |

---

## Summary

- **Context Compression**: Keep memory compact and relevant.
- **MCP Tool Registry**: Keep tool integration dynamic and standardized.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
