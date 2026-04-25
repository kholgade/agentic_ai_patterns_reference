export async function chainOfVerification(question, draftFn, checkGenFn, verifyFn, reviseFn) {
  const draft = await draftFn(question);
  const checks = await checkGenFn(draft);
  const results = [];
  for (const check of checks) results.push(await verifyFn(check));
  const final = await reviseFn(question, draft, checks, results);
  return { draft, checks, results, final };
}
