export async function runWithFallback(candidates, executeFn) {
  const errors = [];
  for (const candidate of candidates) {
    try {
      const result = await executeFn(candidate);
      return { winner: candidate, result, errors };
    } catch (err) {
      errors.push({ candidate, error: String(err) });
    }
  }
  throw new Error(`All fallbacks failed: ${JSON.stringify(errors)}`);
}
