# Pattern Selection Guide

## If task is:
- deterministic → use DAG (ReWOO)
- uncertain → use ReAct
- long horizon → Plan-and-Solve
- cost sensitive → DAG / routing
- parallelizable → multi-agent or DAG

## Anti-patterns
- using multi-agent for simple tasks
- using ReAct for fixed pipelines
- using DAG for uncertain environments