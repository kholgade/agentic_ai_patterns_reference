export async function compressContext(messages, scoreFn, summarizeFn, topK = 12) {
  const scored = [...messages].sort((a, b) => scoreFn(b) - scoreFn(a));
  const selected = scored.slice(0, topK);
  const summary = await summarizeFn(selected);
  return { selected, summary };
}
