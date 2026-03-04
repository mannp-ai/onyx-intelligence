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
