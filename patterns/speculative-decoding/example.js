export async function speculativeStep(prefix, draftFn, verifyFn, k = 8) {
  const draft = await draftFn(prefix, k);
  const accepted = await verifyFn(prefix, draft);
  return { draft, accepted, nextPrefix: `${prefix}${accepted}` };
}
