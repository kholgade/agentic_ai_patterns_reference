def chain_of_verification(question, draft_fn, check_gen_fn, verify_fn, revise_fn):
    draft = draft_fn(question)
    checks = check_gen_fn(draft)
    results = [verify_fn(c) for c in checks]
    final = revise_fn(question, draft, checks, results)
    return {"draft": draft, "checks": checks, "results": results, "final": final}
