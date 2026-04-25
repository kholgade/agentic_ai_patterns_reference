class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, capabilities, handler):
        self._tools[name] = {"capabilities": set(capabilities), "handler": handler}

    def find(self, required_caps):
        req = set(required_caps)
        return [n for n, t in self._tools.items() if req.issubset(t["capabilities"])]

    def execute(self, name, payload):
        return self._tools[name]["handler"](payload)
