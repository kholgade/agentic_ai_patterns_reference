from enum import Enum
from typing import Protocol, Any
from dataclasses import dataclass
from openai import AsyncOpenAI

class RouteType(Enum):
    TECHNICAL_SUPPORT = "technical_support"
    BILLING = "billing"
    SALES = "sales"
    GENERAL = "general"
    FALLBACK = "fallback"

@dataclass
class RouteResult:
    route: RouteType
    confidence: float
    reasoning: str
    handler: Any

class Handler(Protocol):
    async def handle(self, input_text: str) -> str:
        ...

class Router:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.handlers: dict[RouteType, Handler] = {}
        self.route_descriptions = {
            RouteType.TECHNICAL_SUPPORT: "Technical issues, bugs, how-to questions",
            RouteType.BILLING: "Payments, invoices, subscriptions, refunds",
            RouteType.SALES: "Product inquiries, pricing, enterprise deals",
            RouteType.GENERAL: "Other questions and general information"
        }
    
    def register_handler(self, route: RouteType, handler: Handler):
        self.handlers[route] = handler
    
    async def classify(self, input_text: str) -> RouteResult:
        route_options = "\n".join(
            f"- {r.value}: {d}" 
            for r, d in self.route_descriptions.items()
        )
        
        prompt = f"""Classify this user query into ONE of these categories:
{route_options}

Query: {input_text}

Respond with only the category name and confidence (0-1). Format: category|confidence|reasoning"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        route_str, conf_str, reasoning = result.split("|")
        
        return RouteResult(
            route=RouteType(route_str.strip()),
            confidence=float(conf_str.strip()),
            reasoning=reasoning.strip(),
            handler=self.handlers.get(RouteType(route_str.strip()))
        )
    
    async def route(self, input_text: str) -> str:
        result = await self.classify(input_text)
        
        if result.route in self.handlers:
            return await result.handler.handle(input_text)
        
        return await self.handlers[RouteType.FALLBACK].handle(input_text)

class TechnicalHandler:
    async def handle(self, input_text: str) -> str:
        return f"[Technical Support] Processing: {input_text}"

class BillingHandler:
    async def handle(self, input_text: str) -> str:
        return f"[Billing] Processing: {input_text}"

# Usage
router = Router(client)
router.register_handler(RouteType.TECHNICAL_SUPPORT, TechnicalHandler())
router.register_handler(RouteType.BILLING, BillingHandler())
router.register_handler(RouteType.SALES, SalesHandler())
router.register_handler(RouteType.FALLBACK, FallbackHandler())

response = await router.route("How do I upgrade my subscription?")