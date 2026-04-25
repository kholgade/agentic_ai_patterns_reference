def speculative_step(prefix, draft_fn, verify_fn, k=8):
    draft = draft_fn(prefix, k)
    accepted = verify_fn(prefix, draft)
    return {"draft": draft, "accepted": accepted, "next_prefix": prefix + accepted}
