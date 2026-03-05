from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import asyncio

# Import Pipeline Modules
from src.data.sec_fetcher import fetch_company_facts
from src.data.stock_fetcher import fetch_stock_history
from src.data.normalizer import normalize_financials

from src.engine.ratios import calculate_ratios
from src.engine.scorer import generate_sub_scores
from src.ml.predictor import ml_predictor
from src.engine.charts import generate_stock_chart_base64

from src.pdf.generator import ReportGenerator

app = FastAPI(title="ONYX MVP API", version="1.0")

# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("src/static/index.html")

class AnalyzeRequest(BaseModel):
    ticker: str

@app.post("/api/analyze")
async def analyze_company(req: AnalyzeRequest):
    ticker = req.ticker.upper().strip()
    # allow alphanumeric and dot (e.g. RELIANCE.NS) and up to 15 chars
    if len(ticker) > 15 or not ticker.replace('.', '').replace('-', '').isalnum():
         raise HTTPException(status_code=400, detail="Invalid ticker symbol")
    
    try:
        # 1. Data Pipeline
        sec_data = fetch_company_facts(ticker)
        stock_data = fetch_stock_history(ticker)
        
        if not sec_data and not stock_data:
            raise HTTPException(status_code=404, detail="Company data not found")
            
        normalized = normalize_financials(sec_data, stock_data)
        
        # 2. ML Engine (Random Forest Inference)
        ratios = calculate_ratios(normalized)
        sub_scores = generate_sub_scores(ratios)
        
        # Pass features to the True ML Predictor
        market_data = normalized.get("market_data", {})
        ml_verdict, ml_score, ml_confidence = ml_predictor.predict_verdict(ratios, market_data)
        
        verdict_data = {
            "onyx_score": ml_score,
            "verdict": ml_verdict,
            "confidence": ml_confidence,
            "top_drivers": ["Random Forest Inference Confidence:"] + [f"{k}: {v}%" for k,v in ml_confidence.items() if v > 0]
        }
        
        # 3. Visuals & Charts
        chart_b64 = generate_stock_chart_base64(stock_data.get("history", {}))
        
        # Merge for output
        response_data = {
            "status": "success",
            "ticker": ticker,
            "company_name": stock_data.get("info", {}).get("shortName", f"{ticker} Inc."),
            **verdict_data,
            "ratios": ratios, # Needed for PDF
            "sub_scores": sub_scores.get("scores", {}), # Needed for UI Radar
            "chart_b64": chart_b64 # Needed for UI
        }
        
        # Generate PDF asynchronously in the background?
        # For simplicity in MVP, we do it inline and save to disk
        pdf_gen = ReportGenerator(ticker, response_data["company_name"], response_data)
        pdf_gen.generate()
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal analysis engine error")

@app.get("/api/download/{ticker}")
async def download_report(ticker: str):
    ticker = ticker.upper()
    filepath = f"src/pdf/output/{ticker}_ONYX_Report.pdf"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="application/pdf", filename=f"{ticker}_Forensic_Report.pdf")
    raise HTTPException(status_code=404, detail="Report not found")
