import matplotlib
matplotlib.use('Agg') # MUST BE SET BEFORE pyplot IMPORT
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from matplotlib.dates import DateFormatter

def generate_stock_chart_base64(hist_data: dict) -> str:
    """Generates a base64 encoded PNG chart from historical stock data."""
    if not hist_data:
        return ""
        
    try:
        # Convert dictionary back to DataFrame
        df = pd.DataFrame.from_dict(hist_data, orient='index')
        df.index = pd.to_datetime(df.index)
        
        # We want the 'Close' prices
        if 'Close' not in df.columns:
            return ""
            
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5))
        
        ax.plot(df.index, df['Close'], color='#58a6ff', linewidth=2)
        
        ax.set_title('5-Year Stock Price History', color='white', fontsize=14, pad=15)
        ax.set_ylabel('Price (USD)', color='#8b949e', fontsize=12)
        
        # Formatting axes
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.tick_params(colors='#8b949e')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
            
        ax.xaxis.set_major_formatter(DateFormatter('%Y'))
        
        plt.tight_layout()
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#0d1117', edgecolor='none')
        buf.seek(0)
        
        # Encode to Base64
        base64_img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{base64_img}"
        
    except Exception as e:
        print(f"Error generating chart: {e}")
        return ""

def generate_confidence_chart_base64(confidence_data: dict) -> str:
    """Generates a pie chart of the Random Forest confidence scores."""
    if not confidence_data:
        return ""
        
    try:
        labels = []
        sizes = []
        colors_map = {
            "STRONG SELL": "#f85149",
            "SELL": "#fb8f67",
            "HOLD": "#d29922",
            "BUY": "#2ea043",
            "STRONG BUY": "#238636"
        }
        
        for k, v in confidence_data.items():
            if v > 0:
                labels.append(k)
                sizes.append(v)
                
        colors_list = [colors_map.get(k, '#8b949e') for k in labels]
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 6))
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors_list, 
            autopct='%1.1f%%', startangle=90, 
            textprops=dict(color="w", fontsize=10),
            wedgeprops=dict(edgecolor='#0d1117', linewidth=2)
        )
        
        ax.set_title('ML Model Confidence', color='white', fontsize=14, pad=15)
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#0d1117', edgecolor='none')
        buf.seek(0)
        
        # Encode to Base64
        base64_img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{base64_img}"
        
    except Exception as e:
        print(f"Error generating confidence chart: {e}")
        return ""

def generate_subscores_chart_base64(sub_scores: dict) -> str:
    """Generates a bar chart of the financial health sub-scores."""
    if not sub_scores:
        return ""
        
    try:
        # Standardize names
        labels = ['Health', 'Profit', 'Value', 'Risk']
        values = [
            sub_scores.get('financial_health', 0),
            sub_scores.get('profitability', 0),
            sub_scores.get('valuation', 0),
            sub_scores.get('risk', 0)
        ]
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 4))
        
        bars = ax.bar(labels, values, color='#58a6ff')
        
        ax.set_title('Financial Sub-Scores Breakdown', color='white', fontsize=14, pad=15)
        ax.set_ylabel('Score (0-100)', color='#8b949e', fontsize=12)
        ax.set_ylim(0, 100)
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', color='white', fontsize=10)
        
        # Formatting axes
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)
        ax.tick_params(colors='#8b949e')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
            
        plt.tight_layout()
        
        # Save to BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#0d1117', edgecolor='none')
        buf.seek(0)
        
        # Encode to Base64
        base64_img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{base64_img}"
        
    except Exception as e:
        print(f"Error generating subscores chart: {e}")
        return ""
