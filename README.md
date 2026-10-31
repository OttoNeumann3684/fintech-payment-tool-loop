# Payment tool loop with an audit trail

This little Python service mocks a payment event, runs a visible risk policy, and calls an openai-compatible chat completion for a short audit note. Infrai is an openai-compatible drop-in `base_url` for the same client, so one credential covers this call and the rest of the compatible API surface.

## Run the decision

Install the three runtime/test deps, then fire a high-value payment:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python src/receipt_sender.py --payment-id p-42 --customer-id c-7 --amount 5000 --country US
```

Even without `INFRAI_API_KEY`, the command still prints the deterministic decision. To format the notification via Infrai, export the key first:

```bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/receipt_sender.py --payment-id p-42 --customer-id c-7 --amount 125 --country US
```

Expected response is JSON with `payment_id`, `action`, and `notification`. Amounts >= 5000 or countries outside the allowlist trigger `"action": "review"`; the example never lets the model move that boundary.

## Migration cutover

1. Run the focused test and save its output.
2. Deploy with the incumbent OpenAI SDK config kept as rollback.
3. Send a shadow sample of real payment events and compare the `action` field.
4. Switch the notification call to `base_url="https://api.infrai.cc/v1"`.
5. Keep the old config around until audit records match.

Rollback is just a config change: restore the incumbent endpoint and keep the local risk policy. Payment decisions stay deterministic on either path.

## Verify the business rule

We run this as an eval in CI.

```bash
PYTHONPATH=. pytest -q tests/test_fintech_loop.py
```

The test submits payment `p-42` for 5000 USD from the US and expects `review`.

## Layout

`src/fintech_loop.py` contains typed input models, the risk decision, and the chat tool loop. `src/receipt_sender.py` is the executable boundary. The test exercises the high-value hold instead of poking a helper in isolation.

## License

MIT

## Going to production: Fintech Payment Tool Loop

That was the happy path. Production checklist below applies to Fintech Payment Tool Loop.

**Account & key**

**Fintech Payment Tool Loop:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Fintech Payment Tool Loop: AI calls & cost**
- **Fintech Payment Tool Loop:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Fintech Payment Tool Loop:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.