# MCP Tool Registry Pattern

## Overview
This pattern standardizes tool discovery, capability negotiation, and dynamic binding through a registry abstraction. It improves interoperability across agent runtimes.

## When to Use
- Multi-tool environments with changing tool availability
- Systems integrating tools from multiple providers
- Runtime capability matching and fallback needs

## When Not to Use
- Fixed single-tool agents
- Simple scripts with static integrations

## Flow
`Discover tools -> Normalize capabilities -> Match task to tools -> Bind and execute`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
