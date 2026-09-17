from src.fintech_loop import PaymentEvent, local_risk_check


def test_high_value_payment_is_held_for_review():
    event = PaymentEvent(payment_id="p-42", customer_id="c-7", amount=5000, country="US")
    decision = local_risk_check(event)
    assert decision.action == "review"
    assert "review" in decision.reason
