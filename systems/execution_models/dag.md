# DAG Execution Model

## Description
Precompiled execution graph with variable dependencies.

## Used by
- ReWOO → [rewoo](../../patterns/rewoo/README.md)
- LLM Compiler → [llm-compiler-dag](../../patterns/llm-compiler-dag/README.md)

## Properties
- deterministic
- parallelizable
- low latency

## When NOT to use
- uncertain environments
- tasks requiring runtime branching