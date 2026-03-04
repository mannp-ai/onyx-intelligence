from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch
import os
import io
import base64
from datetime import datetime

class ReportGenerator:
    def __init__(self, ticker: str, company_name: str, analysis_data: dict, output_dir: str = "src/pdf/output"):
        self.ticker = ticker.upper()
        self.company_name = company_name
        self.data = analysis_data
        self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.filepath = os.path.join(self.output_dir, f"{self.ticker}_ONYX_Report.pdf")
        
        # Styles
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle('Title', parent=self.styles['Heading1'], fontSize=24, spaceAfter=20, textColor=colors.HexColor('#0d1117'))
        self.h2_style = ParagraphStyle('H2', parent=self.styles['Heading2'], fontSize=16, spaceAfter=10, textColor=colors.HexColor('#3182ce'))
        self.normal_style = self.styles['Normal']
        self.verdict_style = ParagraphStyle('Verdict', parent=self.styles['Heading1'], fontSize=28, alignment=1, spaceAfter=30)
        
    def generate(self) -> str:
        """Builds and saves the PDF report."""
        doc = SimpleDocTemplate(self.filepath, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        elements = []
        
        # Page 1: Cover & Executive Summary
        elements.extend(self._build_cover())
        elements.extend(self._build_executive_summary())
        elements.append(PageBreak())
        
        # Page 2: Financial Breakdown
        elements.extend(self._build_financials())
        
        doc.build(elements)
        return self.filepath
        
    def _build_cover(self) -> list:
        date_str = datetime.now().strftime("%B %d, %Y")
        return [
            Paragraph("ONYX Project", self.title_style),
            Paragraph("Forensic Investment Intelligence Report", self.h2_style),
            Spacer(1, 30),
            Paragraph(f"<b>Company:</b> {self.company_name} ({self.ticker})", self.normal_style),
            Paragraph(f"<b>Date Generated:</b> {date_str}", self.normal_style),
            Spacer(1, 40)
        ]
        
    def _build_executive_summary(self) -> list:
        score = self.data.get("onyx_score", 0)
        verdict = self.data.get("verdict", "N/A")
        
        # Color based on verdict
        v_color = colors.HexColor('#1f2937')
        if "BUY" in verdict: v_color = colors.HexColor('#2ea043')
        elif "SELL" in verdict: v_color = colors.HexColor('#f85149')
        elif "HOLD" in verdict: v_color = colors.HexColor('#d29922')
        
        v_style = ParagraphStyle('VS', parent=self.verdict_style, textColor=v_color)
        
        elements = [
            Paragraph("Executive Summary", self.h2_style),
            Spacer(1, 10),
            Paragraph(f"ONYX Score: {score} / 100", ParagraphStyle('Score', fontSize=20, alignment=1, spaceAfter=10)),
            Paragraph(f"Verdict: {verdict}", v_style),
            Spacer(1, 20),
            Paragraph("<b>Top Strengths:</b>", self.normal_style)
        ]
        
        for sig in self.data.get("top_signals", []):
            elements.append(Paragraph(f"• <font color='green'>{sig}</font>", self.normal_style))
            
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Key Risks:</b>", self.normal_style))
        for sig in self.data.get("risk_signals", []):
            elements.append(Paragraph(f"• <font color='red'>{sig}</font>", self.normal_style))
            
        return elements
        
    def _build_financials(self) -> list:
        elements = [Paragraph("Financial Details & Ratios", self.h2_style), Spacer(1, 10)]
        
        # Raw Data Table Placeholder
        data = [['Metric', 'Value']]
        
        # Extract normalized info representing ratios
        ratios = self.data.get("ratios", {})
        for cat, values in ratios.items():
            for k, v in values.items():
                data.append([k.replace("_", " ").title(), str(v)])
                
        table = Table(data, colWidths=[200, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1117')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e6edf3')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 40))
        
        # Add Chart if present
        b64_chart = self.data.get("chart_b64", "")
        if b64_chart:
            try:
                # Strip data URI metadata if present
                img_data = b64_chart.split(",")[1] if "," in b64_chart else b64_chart
                img_io = io.BytesIO(base64.b64decode(img_data))
                
                # Render Image in ReportLab
                img = Image(img_io, width=6*inch, height=3*inch)
                elements.append(Paragraph("5-Year Stock Performance", self.h2_style))
                elements.append(img)
                elements.append(Spacer(1, 40))
            except Exception as e:
                print(f"Failed to embed graph in PDF: {e}")
        
        elements.append(Paragraph("<i>Disclaimer: ONYX is an analytical tool and does not constitute financial advice. All data should be verified independently.</i>", self.normal_style))
        return elements
