# kalshi-v1

Minimal CLI to place and verify a single limit order on the Kalshi REST v2 Demo API.

## Quickstart

1. Generate a Demo API key and RSA private key from Kalshi.
2. Save the private key to a file and note the API key id.
3. Copy `.env.example` to `.env` and fill `BASE_URL`, `API_KEY_ID`, and `PRIVATE_KEY_PATH`.
4. Optional overrides: `SIDE` (`yes` or `no`), `PRICE_CENTS` (`1..99`), `COUNT` (integer), `TIME_IN_FORCE` (`fill_or_kill` or `immediate_or_cancel`).
5. Install dependencies: `pip install -r requirements.txt`.
6. Run the script: `python place_and_verify.py`.

The program prints the selected ticker, created `order_id`, verification status, and queue positions if available.

## Verification

The script verifies that the server order fields exactly match the request for `ticker`, `side`, `action`, `type`, and the chosen price field. When both `filled_count` and `remaining_count` are present, it also checks `filled_count + remaining_count == requested count` to ensure quantity conservation.
