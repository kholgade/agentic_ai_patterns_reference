def compress_context(messages, score_fn, summarize_fn, top_k=12):
    scored = sorted(messages, key=score_fn, reverse=True)
    selected = scored[:top_k]
    summary = summarize_fn(selected)
    return {"selected": selected, "summary": summary}
