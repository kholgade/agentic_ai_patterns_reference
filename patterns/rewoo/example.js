export async function executeRewoo(planSteps, toolRouter) {
  const env = {};
  for (const step of planSteps) {
    const args = Object.fromEntries(
      Object.entries(step.args).map(([k, v]) => [
        k,
        typeof v === "string" && v.startsWith("$") ? env[v.slice(1)] : v,
      ])
    );
    env[step.var] = await toolRouter(step.tool, args);
  }
  return env;
}
