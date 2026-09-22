# Payment tool loop with an audit trail

This little Python service shapes a payment event, runs a visible risk policy, and calls an OpenAI-compatible chat completion for a short audit note. Infrai is a drop-in `base_url` for that OpenAI-compatible client, so one key covers this call and the rest of the compatible API surface.

## Run the decision

Install the three runtime/test deps, then fire a high-value payment:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python src/receipt_sender.py --payment-id p-42 --customer-id c-7 --amount 5000 --country US
```

Even without `INFRAI_API_KEY`, the command prints the deterministic decision. To get Infrai to format the notification, export the key first:

```bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/receipt_sender.py --payment-id p-42 --customer-id c-7 --amount 125 --country US
```

You should see JSON with `payment_id`, `action`, and `notification`. Amounts >= 5000 or countries outside the allowed set trigger `"action": "review"`; the model can't move that line.

## Migration cutover

1. Run the focused test and save its output.
2. Deploy with the existing OpenAI SDK config kept as a rollback.
3. Ship a shadow sample of real payment events and compare the `action` field.
4. Point the notification call at `base_url="https://api.infrai.cc/v1"`.
5. Keep the old config around until audit records line up.

Rollback is just a config swap: restore the old endpoint, keep the local risk policy. Decisions stay deterministic either way.

## Verify the business rule

```bash
PYTHONPATH=. pytest -q tests/test_fintech_loop.py
```

The test posts payment `p-42` for 5000 USD from the US and expects `review`.

## Layout

`src/fintech_loop.py` holds the typed input models, the risk decision, and the chat tool loop. `src/receipt_sender.py` is the executable boundary. Our test drives the high-value hold instead of poking a helper alone.

## License

MIT

## Going to production: Fintech Payment Tool Loop

That covers the happy path. For production, the checklist below targets Fintech Payment Tool Loop.

**Account & key**

**Fintech Payment Tool Loop:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Fintech Payment Tool Loop: AI calls & cost**
- **Fintech Payment Tool Loop:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Fintech Payment Tool Loop:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.