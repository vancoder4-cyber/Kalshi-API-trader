import os
import sys
import json
import uuid
from dotenv import load_dotenv
from kalshi_client import KalshiClient, KalshiConfig


def main():
    load_dotenv()
    base_url = os.getenv("BASE_URL")
    api_key_id = os.getenv("API_KEY_ID")
    key_path = os.getenv("PRIVATE_KEY_PATH")
    if not all([base_url, api_key_id, key_path]):
        sys.exit("Missing BASE_URL, API_KEY_ID, or PRIVATE_KEY_PATH")

    cfg = KalshiConfig(base_url=base_url, api_key_id=api_key_id, private_key_path=key_path)
    client = KalshiClient(cfg)

    # Step 1: select an open market
    r = client.get("/trade-api/v2/markets", params={"status": "open", "limit": 1})
    if r.status_code != 200:
        sys.exit(f"Market fetch failed: {r.status_code} {r.text}")
    markets = r.json().get("markets", [])
    if not markets:
        sys.exit("No open markets returned")
    ticker = markets[0]["ticker"]
    print(f"Selected market ticker: {ticker}")

    # Step 2: build order request
    side = os.getenv("SIDE", "yes")
    price_cents = int(os.getenv("PRICE_CENTS", "1"))
    count = int(os.getenv("COUNT", "1"))
    tif = os.getenv("TIME_IN_FORCE") or None
    price_field = "yes_price" if side == "yes" else "no_price"
    body = {
        "ticker": ticker,
        "action": "buy",
        "side": side,
        "count": count,
        "type": "limit",
        price_field: price_cents,
        "client_order_id": str(uuid.uuid4()),
    }
    if tif:
        body["time_in_force"] = tif

    # Step 3: create order
    r = client.post("/trade-api/v2/portfolio/orders", json=body)
    if r.status_code != 201:
        sys.exit(f"Order creation failed: {r.status_code} {r.text}")
    order_id = r.json()["order"]["order_id"]
    print(f"Created order_id: {order_id}")

    # Step 4: fetch and verify
    r = client.get(f"/trade-api/v2/portfolio/orders/{order_id}")
    if r.status_code != 200:
        sys.exit(f"Order fetch failed: {r.status_code} {r.text}")
    order = r.json().get("order", {})
    for field in ["ticker", "side", "action", "type"]:
        if order.get(field) != body[field]:
            sys.exit(f"Mismatch for {field}")
    if order.get(price_field) != body[price_field]:
        sys.exit(f"Mismatch for {price_field}")
    filled = order.get("filled_count")
    remaining = order.get("remaining_count")
    if filled is not None and remaining is not None:
        if filled + remaining != count:
            sys.exit("Quantity conservation failed")
    print("\u2705 Request matches server order fields.")

    # Step 5: queue positions (best effort)
    r = client.get("/trade-api/v2/portfolio/orders/queue_positions")
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))


if __name__ == "__main__":
    main()
