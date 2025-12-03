import requests
import pandas as pd
from datetime import datetime
import json
import os

def fetch_predictit_data_from_file(filepath="predictit_data.json"):
    """Load PredictIt data from a local JSON file"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}. Please download data manually.")
    
    with open(filepath, 'r') as f:
        return json.load(f)

def fetch_predictit_data():
    """Fetch market data from PredictIt (JSON API)"""
    url = "https://www.predictit.org/api/marketdata/all/"
    
    # Try multiple approaches
    headers_list = [
        # Approach 1: Full browser headers
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.predictit.org/",
            "Origin": "https://www.predictit.org",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        # Approach 2: Minimal headers
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    ]
    
    for i, headers in enumerate(headers_list):
        try:
            print(f"Attempting fetch with header set {i+1}...")
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                print("✓ Successfully fetched data from API")
                return r.json()
            else:
                print(f"✗ Got status code: {r.status_code}")
        except Exception as e:
            print(f"✗ Attempt {i+1} failed: {e}")
    
    # If all attempts fail, try to load from file
    print("\n⚠ All API attempts failed. Trying to load from local file...")
    try:
        return fetch_predictit_data_from_file()
    except FileNotFoundError:
        print("\n" + "="*60)
        print("MANUAL DATA DOWNLOAD REQUIRED")
        print("="*60)
        print("1. Open your browser and go to:")
        print("   https://www.predictit.org/api/marketdata/all/")
        print("\n2. Save the JSON response to:")
        print(f"   {os.path.abspath('predictit_data.json')}")
        print("\n3. Run this script again")
        print("="*60)
        raise Exception("Unable to fetch data from API. Please download manually.")

def markets_to_dataframe(data):
    """Flatten PredictIt JSON markets + contracts into a DataFrame"""
    rows = []

    for market in data.get("markets", []):
        market_id = market["id"]
        market_name = market["name"]
        market_status = market["status"]
        market_url = market.get("url", "")

        for contract in market["contracts"]:
            rows.append({
                "timestamp": datetime.utcnow().isoformat(),
                "market_id": market_id,
                "market_name": market_name,
                "market_status": market_status,
                "market_url": market_url,

                "contract_id": contract["id"],
                "contract_name": contract["name"],
                "contract_short_name": contract["shortName"],
                "contract_status": contract["status"],

                "last_trade_price": contract.get("lastTradePrice"),
                "best_buy_yes": contract.get("bestBuyYesCost"),
                "best_buy_no": contract.get("bestBuyNoCost"),
                "best_sell_yes": contract.get("bestSellYesCost"),
                "best_sell_no": contract.get("bestSellNoCost"),
                "last_close_price": contract.get("lastClosePrice"),

                "date_end": contract.get("dateEnd")
            })

    return pd.DataFrame(rows)
