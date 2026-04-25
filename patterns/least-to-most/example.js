export async function leastToMost(task, decomposeFn, solveFn) {
  const steps = await decomposeFn(`Decompose easiest->hardest:\n${task}`);
  const trace = [];
  for (const step of steps) {
    const context = trace.join("\n");
    const result = await solveFn(`Solve: ${step}\nKnown:\n${context}`);
    trace.push(`${step} -> ${result}`);
  }
  return { steps, trace, final: trace.at(-1) ?? null };
}
