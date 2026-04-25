def run_pal(problem: str, codegen_fn, sandbox_exec_fn):
    code = codegen_fn(
        "Write Python code only to solve:\n" + problem
    )
    result = sandbox_exec_fn(code)
    return {"generated_code": code, "execution_result": result}
