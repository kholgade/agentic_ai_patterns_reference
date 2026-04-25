def least_to_most(task: str, decompose_fn, solve_fn):
    steps = decompose_fn(
        f"Decompose from easiest to hardest:\n{task}"
    )
    memory = []
    for step in steps:
        context = "\n".join(memory)
        result = solve_fn(f"Solve step: {step}\nKnown results:\n{context}")
        memory.append(f"{step} -> {result}")
    return {"steps": steps, "trace": memory, "final": memory[-1] if memory else None}
