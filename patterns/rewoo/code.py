def execute_rewoo(plan_steps, tool_router):
    env = {}
    for step in plan_steps:
        var = step["var"]
        tool = step["tool"]
        args = step["args"]
        resolved_args = {
            k: (env[v[1:]] if isinstance(v, str) and v.startswith("$") else v)
            for k, v in args.items()
        }
        env[var] = tool_router(tool, resolved_args)
    return env
