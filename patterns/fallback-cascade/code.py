def run_with_fallback(candidates, execute_fn):
    errors = []
    for candidate in candidates:
        try:
            return {"winner": candidate, "result": execute_fn(candidate), "errors": errors}
        except Exception as exc:
            errors.append({"candidate": candidate, "error": str(exc)})
    raise RuntimeError(f"All fallbacks failed: {errors}")
