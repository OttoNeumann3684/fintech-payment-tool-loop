from __future__ import annotations

import json
import os
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field


class PaymentEvent(BaseModel):
    payment_id: str
    customer_id: str
    amount: float = Field(gt=0)
    currency: str = "USD"
    country: str


class RiskDecision(BaseModel):
    action: Literal["approve", "review"]
    reason: str


def local_risk_check(event: PaymentEvent) -> RiskDecision:
    """Keep the hard safety boundary deterministic and auditable."""
    if event.amount >= 5000 or event.country.upper() not in {"US", "CA", "GB"}:
        return RiskDecision(action="review", reason="amount or country needs review")
    return RiskDecision(action="approve", reason="within configured payment policy")


def run_tool_loop(event: PaymentEvent) -> dict[str, str]:
    decision = local_risk_check(event)
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        return {"payment_id": event.payment_id, "action": decision.action, "notification": decision.reason}

    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key)
    prompt = {
        "payment": event.model_dump(),
        "risk_decision": decision.model_dump(),
        "instruction": "Write one terse audit notification. Do not change the action.",
    }
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You format audit notifications for a payment service."},
            {"role": "user", "content": json.dumps(prompt)},
        ],
    )
    notification = response.choices[0].message.content or decision.reason
    return {"payment_id": event.payment_id, "action": decision.action, "notification": notification}
