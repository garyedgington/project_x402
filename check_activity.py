"""
SchemaCheck Agent — activity monitor.

Run this any time to get a quick status report:
    python check_activity.py

Shows:
  - Service health
  - Call counts for the current Railway session
  - USDC balance in the receiving wallet (on-chain, permanent record of paid calls)
  - A live trial call to confirm the endpoint is responding correctly
"""

import json
import requests

BASE_URL       = "https://projectx402-production.up.railway.app"
RECEIVING_WALLET = "0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F"
USDC_CONTRACT  = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
PRICE_ATOMIC   = 5000  # $0.005 USDC per call (6 decimals)

TRIAL_BODY = {
    "json_schema": {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"]
    },
    "payload": {"name": "Alice", "age": 30},
    "explain": True
}


def check_health():
    print("── Service health ──────────────────────────")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        data = r.json()
        status = data.get("status", "unknown")
        version = data.get("version", "?")
        print(f"  Status  : {'✓ ok' if status == 'ok' else '✗ ' + status}")
        print(f"  Version : {version}")
        print(f"  HTTP    : {r.status_code}")
    except Exception as e:
        print(f"  ERROR   : {e}")
    print()


def check_session_stats():
    print("── Session call counts (resets on restart) ─")
    try:
        r = requests.get(f"{BASE_URL}/v1/stats", timeout=10)
        data = r.json()
        print(f"  Paid calls   : {data.get('paid_calls_this_session', '?')}")
        print(f"  Trial calls  : {data.get('trial_calls_this_session', '?')}")
        print(f"  Total        : {data.get('total_this_session', '?')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()


def check_wallet_balance():
    print("── On-chain USDC balance (Base mainnet) ────")
    try:
        url = (
            "https://api.basescan.org/api"
            f"?module=account&action=tokenbalance"
            f"&contractaddress={USDC_CONTRACT}"
            f"&address={RECEIVING_WALLET}"
            f"&tag=latest"
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("status") == "1":
            atomic = int(data["result"])
            usdc = atomic / 1_000_000
            estimated_calls = atomic // PRICE_ATOMIC
            print(f"  Balance          : ${usdc:.4f} USDC")
            print(f"  Estimated calls  : ~{estimated_calls} paid calls received")
        else:
            print(f"  Basescan response: {data}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print(f"  Wallet  : {RECEIVING_WALLET}")
    print(f"  Basescan: https://basescan.org/address/{RECEIVING_WALLET}")
    print()


def run_trial_call():
    print("── Live trial call ─────────────────────────")
    try:
        r = requests.post(f"{BASE_URL}/v1/schema-check/trial", json=TRIAL_BODY, timeout=15)
        data = r.json()
        valid = data.get("valid")
        summary = data.get("summary", "")
        print(f"  HTTP status : {r.status_code}")
        print(f"  valid       : {valid}")
        print(f"  summary     : {summary}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()


if __name__ == "__main__":
    print()
    print("SchemaCheck Agent — Activity Monitor")
    print("=" * 44)
    print()
    check_health()
    check_session_stats()
    check_wallet_balance()
    run_trial_call()
    print("Railway logs : https://railway.com/project/7c8b7de8-53e1-476f-88c3-d964022f3092/logs")
    print()
