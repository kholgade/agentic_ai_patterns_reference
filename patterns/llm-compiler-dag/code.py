def run_dag(nodes, run_node):
    done = {}
    pending = {n["id"]: n for n in nodes}

    while pending:
        ready = [n for n in pending.values() if all(dep in done for dep in n["deps"])]
        if not ready:
            raise ValueError("Cycle or unresolved dependency in DAG")
        for node in ready:
            inputs = {dep: done[dep] for dep in node["deps"]}
            done[node["id"]] = run_node(node, inputs)
            del pending[node["id"]]

    return done
