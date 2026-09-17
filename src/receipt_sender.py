import argparse
import json

from fintech_loop import PaymentEvent, run_tool_loop


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one payment risk and notification cycle")
    parser.add_argument("--payment-id", required=True)
    parser.add_argument("--customer-id", required=True)
    parser.add_argument("--amount", type=float, required=True)
    parser.add_argument("--country", required=True)
    args = parser.parse_args()
    event = PaymentEvent(
        payment_id=args.payment_id,
        customer_id=args.customer_id,
        amount=args.amount,
        country=args.country,
    )
    print(json.dumps(run_tool_loop(event), sort_keys=True))


if __name__ == "__main__":
    main()
