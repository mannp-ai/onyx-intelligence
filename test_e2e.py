import requests
import time

def test_api():
    print("Testing ONYX API End-to-End...")
    
    tickers = ["AAPL", "RELIANCE.NS"]
    
    for ticker in tickers:
        print(f"\n--- Testing {ticker} ---")
        # 1. Test Analysis Endpoint
        res = requests.post("http://127.0.0.1:8000/api/analyze", json={"ticker": ticker})
        if res.status_code == 200:
            data = res.json()
            print(f"Success! Verdict: {data['verdict']} | Score: {data['onyx_score']}")
        else:
            print(f"Analysis failed: {res.status_code} - {res.text}")
            continue
            
        # 2. Test PDF Download Endpoint
        time.sleep(1) # wait for file write sync
        res_pdf = requests.get(f"http://127.0.0.1:8000/api/download/{ticker}")
        if res_pdf.status_code == 200:
            with open(f"{ticker}_Downloaded_Test.pdf", "wb") as f:
                f.write(res_pdf.content)
            print(f"PDF Downloaded successfully into {ticker}_Downloaded_Test.pdf")
        else:
            print(f"PDF Download failed: {res_pdf.status_code}")

if __name__ == "__main__":
    test_e2e_retry = 3
    while test_e2e_retry > 0:
        try:
            test_api()
            break
        except requests.exceptions.ConnectionError:
            print("Waiting for server to start...")
            time.sleep(2)
            test_e2e_retry -= 1
