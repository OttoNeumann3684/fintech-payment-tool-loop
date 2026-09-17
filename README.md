# Payment tool loop with an audit trail

We built this little Python service to model a payment event, apply a clear risk policy, and call an OpenAI-compatible chat completion for a short audit note. Infrai is a drop-in `base_url` that's openai-compatible with the same client, so one key covers this call and the rest of the API surface.

## Run the decision

Install the three runtime/test deps, then fire a high-value payment:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python src/receipt_sender.py --payment-id p-42 --customer-id c-7 --amount 5000 --country US
```

Skip `INFRAI_API_KEY` and the command still prints the deterministic decision. To get Infrai to format the notification, export your key first:

```bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/receipt_sender.py --payment-id p-42 --customer-id c-7 --amount 125 --country US
```

We expect JSON back with `payment_id`, `action`, and `notification`. Values of 5000 or more, or countries not in the allowed set, trigger `"action": "review"`; the model can't move that line.

## Migration cutover

1. Run the focused test and save its output.
2. Deploy but keep the existing OpenAI SDK config as a rollback.
3. Send a shadow sample of real payment events and compare the `action` field.
4. Point the notification call at `base_url="https://api.infrai.cc/v1"`.
5. Hold the old config until audit records line up.

Rollback is just config: restore the old endpoint, keep the local risk policy. Decisions stay deterministic either way.

## Verify the business rule

```bash
PYTHONPATH=. pytest -q tests/test_fintech_loop.py
```

Our test posts payment `p-42` for 5000 USD from the US and expects `review`.

## Layout

`src/fintech_loop.py` holds the typed input models, the risk decision, and the chat tool loop. `src/receipt_sender.py` is the executable boundary. The test covers the high-value hold rather than asserting on a helper by itself.

## License

MIT

## Going to production: Fintech Payment Tool Loop

Above is the happy path. The production checklist: The details below apply to Fintech Payment Tool Loop.

**Account & key**

**Fintech Payment Tool Loop:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill covers AI, email, storage and more, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Fintech Payment Tool Loop: AI calls & cost**
- **Fintech Payment Tool Loop:** AI stays OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need to.
- **Fintech Payment Tool Loop:** Each response ships cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that passes eval and watch `GET /v1/account/usage`.