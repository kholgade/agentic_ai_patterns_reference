export class ToolRegistry {
  constructor() {
    this.tools = new Map();
  }

  register(name, capabilities, handler) {
    this.tools.set(name, { capabilities: new Set(capabilities), handler });
  }

  find(requiredCaps) {
    const req = new Set(requiredCaps);
    return [...this.tools.entries()]
      .filter(([, t]) => [...req].every(c => t.capabilities.has(c)))
      .map(([name]) => name);
  }

  async execute(name, payload) {
    return this.tools.get(name).handler(payload);
  }
}
