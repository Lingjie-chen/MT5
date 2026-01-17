
import os
import time
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection(symbol="ETHUSD"):
    print(f"Testing connection for {symbol}...")
    
    # Get config from env
    api_key = os.getenv(f"{symbol}_API_KEY")
    base_url = os.getenv(f"{symbol}_API_URL", "https://api.siliconflow.cn/v1")
    model = os.getenv(f"{symbol}_MODEL", "Qwen/Qwen3-VL-235B-A22B-Thinking")
    
    if not api_key:
        print(f"Error: {symbol}_API_KEY not found in .env")
        return

    print(f"URL: {base_url}")
    print(f"Model: {model}")
    print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 1. Simple Test (Small Payload)
    print("\n--- Test 1: Simple Hello World ---")
    payload_simple = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello, are you online? Reply with 'Yes' only."}
        ],
        "max_tokens": 10,
        "stream": False
    }
    
    start_time = time.time()
    try:
        session = requests.Session()
        # session.trust_env = False # Mimic the production code setting
        # Let's try WITH and WITHOUT trust_env to see if it makes a difference
        
        print("Sending request...")
        response = session.post(f"{base_url}/chat/completions", headers=headers, json=payload_simple, timeout=30)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {end_time - start_time:.2f}s")
        if response.status_code == 200:
            print("Response:", response.json()['choices'][0]['message']['content'])
        else:
            print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Test 1 Failed: {e}")

    # 2. Large Payload Test (Simulating Market Structure Analysis)
    print("\n--- Test 2: Large Payload (Simulated Analysis) ---")
    
    # Create dummy large data
    market_data = {
        "symbol": symbol,
        "candles": [{"time": i, "open": 100+i, "high": 105+i, "low": 95+i, "close": 102+i} for i in range(100)], # 100 candles
        "indicators": {"rsi": 50, "ema": 100}
    }
    
    prompt = f"Analyze this market data: {json.dumps(market_data)}"
    
    payload_large = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a trading assistant. Return JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "stream": False,
        "response_format": {"type": "json_object"}
    }
    
    start_time = time.time()
    try:
        print("Sending large request (timeout=600)...")
        # Mimic the production timeout
        response = session.post(f"{base_url}/chat/completions", headers=headers, json=payload_large, timeout=600)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {end_time - start_time:.2f}s")
        if response.status_code == 200:
            print("Response Length:", len(response.text))
        else:
            print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Test 2 Failed: {e}")

if __name__ == "__main__":
    test_connection("ETHUSD")
