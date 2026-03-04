# ONYX: ML-Powered Investment Intelligence

ONYX is a financial forensics platform that generates comprehensive, data-driven investment reports on publicly traded US companies. By pulling live SEC filings (10-K, 10-Q) and historical stock data, ONYX calculates core financial ratios and outputs an explainable **"ONYX Score"**, a clear investment verdict (Buy/Hold/Sell), and a premium PDF report.

This project was built to demystify complex financial analysis using structured software engineering and an explainable Artificial Intelligence proxy (a Deterministic Expert System).

---

## Features

- **Automated Data Pipeline:** Dynamically fetches US-GAAP financial data from the official SEC EDGAR database and 5-year stock data via `yfinance`.
- **Explainable Scoring Engine:** Calculates financial formulas (Current Ratios, Debt-to-Equity, Margins, Beta) and feeds them into a deterministic Rule-Based Expert System to evaluate Health, Risk, Profitability, and Valuation out of 100.
- **Premium Web Dashboard:** A responsive, glassmorphic UI built with Vanilla JS that visually maps the analysis progression and renders interactive charts and sub-score metrics.
- **Forensic PDF Synthesis:** Automatically compiles a multi-page, branded PDF report containing Executive Summaries, Visual Charts, and Verdict rationale.

---

## Technical Architecture

The platform is designed for high performance and strict explainability:
1. **Frontend:** HTML, CSS Variables, and Vanilla JavaScript.
2. **Backend API:** Python with **FastAPI**.
3. **Data Ingestion:** `requests` (for SEC EDGAR JSON APIs) and `yfinance`.
4. **Machine Learning Proxy:** Custom Rule-Based Evaluation Engine written in Python. This approach was chosen specifically over a deep neural network to guarantee **100% explainability** in financial decision-making. 
5. **Visualization & PDF:** `matplotlib` and `reportlab`.

---

## Setup & Installation

To run ONYX locally, you will need Python 3 installed.

### 1. Clone & Set Up Environment
```bash
# Clone the repository (or navigate to the project folder)
cd ONYX

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the required dependencies
pip install -r src/requirements.txt
```

### 2. Run the Application
Start the FastAPI server:
```bash
uvicorn src.main:app --reload
```
Once the server is running, open a web browser and navigate to:
**http://127.0.0.1:8000**

---

## How to Use
1. Enter a valid US stock ticker (e.g., `AAPL`, `MSFT`, `TSLA`).
2. Click **Generate Report**. The system will track live progress as it ingests SEC data, runs the scoring engine, and generates the PDF.
3. Review the on-screen metrics and 5-Year Stock Performance chart.
4. Click **Download Full Forensic PDF** to view the comprehensive financial document.

---

*Disclaimer: ONYX is an analytical tool engineered for demonstration and educational purposes. It does not constitute actual financial advice.*
