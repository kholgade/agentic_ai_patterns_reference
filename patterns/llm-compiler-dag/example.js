export async function runDag(nodes, runNode) {
  const done = new Map();
  const pending = new Map(nodes.map(n => [n.id, n]));

  while (pending.size) {
    const ready = [...pending.values()].filter(n => n.deps.every(d => done.has(d)));
    if (!ready.length) throw new Error("Cycle or unresolved dependency in DAG");
    await Promise.all(
      ready.map(async (node) => {
        const inputs = Object.fromEntries(node.deps.map(d => [d, done.get(d)]));
        done.set(node.id, await runNode(node, inputs));
        pending.delete(node.id);
      })
    );
  }

  return Object.fromEntries(done);
}
