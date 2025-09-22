import os
import base64
from datetime import datetime, timezone
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from PIL import Image as PILImage
from pathlib import Path

class ReportGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.html_template_path = Path(__file__).parent.parent / "templates" / "report_template_new.html"
        self.styles = getSampleStyleSheet()
        # Create custom styles
        self.styles.add(ParagraphStyle(
            name='BPITitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#667eea'),
        ))
        self.styles.add(ParagraphStyle(
            name='BPIHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50'),
        ))
        self.styles.add(ParagraphStyle(
            name='BPIText',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
        ))

    def format_timestamp(self, ts) -> str:
        """Format ISO timestamp to readable format."""
        if isinstance(ts, str):
            # Handle different timestamp formats
            if ts.endswith('Z'):
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            elif '+' in ts or ts.endswith('UTC'):
                dt = datetime.fromisoformat(ts.replace('UTC', '').strip())
            else:
                # Assume it's a plain ISO format
                dt = datetime.fromisoformat(ts)
        else:
            dt = ts
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    
    def format_time_short(self, ts) -> str:
        """Format timestamp to short time format."""
        if isinstance(ts, str):
            # Handle different timestamp formats
            if ts.endswith('Z'):
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            elif '+' in ts or ts.endswith('UTC'):
                dt = datetime.fromisoformat(ts.replace('UTC', '').strip())
            else:
                # Assume it's a plain ISO format
                dt = datetime.fromisoformat(ts)
        else:
            dt = ts
        return dt.strftime('%H:%M')
    
    def calculate_duration(self, start_ts, end_ts) -> str:
        """Calculate duration between two timestamps."""
        if isinstance(start_ts, str):
            if start_ts.endswith('Z'):
                start_dt = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
            elif '+' in start_ts or start_ts.endswith('UTC'):
                start_dt = datetime.fromisoformat(start_ts.replace('UTC', '').strip())
            else:
                start_dt = datetime.fromisoformat(start_ts)
        else:
            start_dt = start_ts
        
        if isinstance(end_ts, str):
            if end_ts.endswith('Z'):
                end_dt = datetime.fromisoformat(end_ts.replace('Z', '+00:00'))
            elif '+' in end_ts or end_ts.endswith('UTC'):
                end_dt = datetime.fromisoformat(end_ts.replace('UTC', '').strip())
            else:
                end_dt = datetime.fromisoformat(end_ts)
        else:
            end_dt = end_ts
            
        duration = end_dt - start_dt
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"
    
    def encode_image_base64(self, image_path: str) -> str:
        """Encode image to base64 for HTML embedding."""
        if not os.path.exists(image_path):
            return ""
        
        with open(image_path, 'rb') as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded}"

    def generate_html_report(self, samples: List[Dict[str, Any]], graph_path: str = None) -> str:
        """Generate HTML report from samples."""
        if not samples:
            return "No data available for report"

        # Load simpler template
        template_path = Path(__file__).parent.parent / "templates" / "report_template_simple.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Calculate statistics
        start_ts = samples[0]['ts']
        end_ts = samples[-1]['ts']
        
        # Parse timestamps properly
        if isinstance(start_ts, str):
            if start_ts.endswith('Z'):
                start_time = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
            else:
                start_time = datetime.fromisoformat(start_ts)
        else:
            start_time = start_ts
            
        if isinstance(end_ts, str):
            if end_ts.endswith('Z'):
                end_time = datetime.fromisoformat(end_ts.replace('Z', '+00:00'))
            else:
                end_time = datetime.fromisoformat(end_ts)
        else:
            end_time = end_ts
        
        # Get price data for each pair
        pairs = list(samples[0].get('prices', {}).keys()) if samples[0].get('prices') else []
        price_rows = []
        
        # Calculate BTC-USD statistics for summary
        btc_prices = [s['prices'].get('BTC-USD', 0) for s in samples if 'BTC-USD' in s.get('prices', {})]
        if btc_prices:
            min_price = f"${min(btc_prices):,.2f}"
            max_price = f"${max(btc_prices):,.2f}"
            avg_price = f"${sum(btc_prices)/len(btc_prices):,.2f}"
        else:
            min_price = max_price = avg_price = "N/A"
        
        for pair in pairs:
            prices = []
            for s in samples:
                if s.get('prices') and s.get('prices').get(pair) is not None:
                    prices.append(s['prices'][pair])
            
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                current = prices[-1]
                change = ((current - prices[0]) / prices[0] * 100) if prices[0] else 0
                
                change_class = "price-positive" if change > 0 else "price-negative" if change < 0 else "price-neutral"
                change_text = f"{change:+.2f}%" if change != 0 else "0.00%"
                
                price_rows.append(f"""
                    <tr>
                        <td><strong>{pair}</strong></td>
                        <td>${min_price:,.2f}</td>
                        <td>${max_price:,.2f}</td>
                        <td>${current:,.2f}</td>
                        <td class="{change_class}">{change_text}</td>
                    </tr>
                """)
        
        # Prepare graph content
        graph_content = ""
        if graph_path and os.path.exists(graph_path):
            encoded_image = self.encode_image_base64(graph_path)
            if encoded_image:
                graph_content = f'<img src="{encoded_image}" alt="Bitcoin Price History Graph" />'
            else:
                graph_content = '<p style="color: #6c757d; font-style: italic;">Graph not available</p>'
        else:
            graph_content = '<p style="color: #6c757d; font-style: italic;">Graph not available</p>'
        
        # Fill template
        try:
            # Calculate duration
            duration_str = self.calculate_duration(start_time, end_time)
            duration_seconds = (end_time - start_time).total_seconds()
            interval = duration_seconds / (len(samples) - 1) if len(samples) > 1 else 0
            
            report_html = template.format(
                report_date=datetime.now().strftime('%B %d, %Y at %H:%M UTC'),
                sample_count=len(samples),
                collection_period=duration_str,
                sample_interval=f"{interval:.1f}",
                min_price=min_price if 'min_price' in locals() else "N/A",
                max_price=max_price if 'max_price' in locals() else "N/A",
                avg_price=avg_price if 'avg_price' in locals() else "N/A",
                price_rows=''.join(price_rows)
            )
            return report_html
        except Exception as e:
            # Log the error and fall back to a very simple format
            print(f"Template formatting failed: {e}")
            return f"""
                <html>
                <body>
                <h1>Bitcoin Price Index Report</h1>
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p>Samples collected: {len(samples)}</p>
                <table border="1">
                    <tr><th>Currency Pair</th><th>Latest Price</th></tr>
                    {''.join(f'<tr><td>{pair}</td><td>${samples[-1]["prices"][pair]:,.2f}</td></tr>' 
                            for pair in samples[-1]['prices'])}
                </table>
                </body>
                </html>
            """
        
        return report_html
    
    def _generate_simple_html_report(self, samples: list, graph_path: str = None) -> str:
        """Generate a simple HTML report if template is not available."""
        start_ts = samples[0]['ts']
        end_ts = samples[-1]['ts']
        
        # Parse timestamps properly
        if isinstance(start_ts, str):
            if start_ts.endswith('Z'):
                start_time = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
            else:
                start_time = datetime.fromisoformat(start_ts)
        else:
            start_time = start_ts
            
        if isinstance(end_ts, str):
            if end_ts.endswith('Z'):
                end_time = datetime.fromisoformat(end_ts.replace('Z', '+00:00'))
            else:
                end_time = datetime.fromisoformat(end_ts)
        else:
            end_time = end_ts
        
        pairs = list(samples[0].get('prices', {}).keys()) if samples[0].get('prices') else []
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>BPI Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</h2>
            <p><strong>Session:</strong> {self.format_timestamp(start_time)} to {self.format_timestamp(end_time)}</p>
            <p><strong>Duration:</strong> {self.calculate_duration(start_time, end_time)}</p>
            <p><strong>Samples:</strong> {len(samples)}</p>
        """
        
        if graph_path and os.path.exists(graph_path):
            encoded_image = self.encode_image_base64(graph_path)
            if encoded_image:
                html += f'<div style="text-align: center; margin: 20px 0;"><img src="{encoded_image}" alt="Price Graph" style="max-width: 100%; height: auto;" /></div>'
        
        html += "</div>"
        return html

    def generate_report(self, samples: list, graph_path: str = None) -> str:
        """Generate a PDF report with price history and statistics."""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=landscape(letter),
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        # Prepare story (content elements)
        story = []

        # Title
        story.append(Paragraph("Bitcoin Price Index Report", self.styles['BPITitle']))
        
        # Summary statistics
        if samples:
            start_time = self.format_timestamp(samples[0]['ts'])
            end_time = self.format_timestamp(samples[-1]['ts'])
            
            # Get price data for each pair
            pairs = list(samples[0].get('prices', {}).keys()) if samples[0].get('prices') else []
            stats_data = []
            
            for pair in pairs:
                prices = []
                for s in samples:
                    if s.get('prices') and s.get('prices').get(pair) is not None:
                        prices.append(s['prices'][pair])
                
                if prices:
                    min_price = min(prices)
                    max_price = max(prices)
                    current = prices[-1]
                    change = ((current - prices[0]) / prices[0] * 100) if prices[0] else 0
                    
                    stats_data.append([
                        pair,
                        f"${min_price:,.2f}",
                        f"${max_price:,.2f}",
                        f"${current:,.2f}",
                        f"{change:+.2f}%"
                    ])

            # Collection info
            duration = self.calculate_duration(samples[0]['ts'], samples[-1]['ts'])
            info_data = [
                ["Collection Period", f"{start_time} to {end_time}"],
                ["Duration", duration],
                ["Total Samples", str(len(samples))],
                ["Currency Pairs", ", ".join(pairs)]
            ]
            
            info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e9ecef')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(Paragraph("Session Overview", self.styles['BPIHeading']))
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Price statistics table
            if stats_data:
                stats_table = Table(
                    [["Currency Pair", "Minimum", "Maximum", "Current", "Change"]] + stats_data,
                    colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]
                )
                stats_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e9ecef')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('PADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(Paragraph("Price Statistics", self.styles['BPIHeading']))
                story.append(stats_table)
                story.append(Spacer(1, 20))

        # Add the price graph if available
        if graph_path and os.path.exists(graph_path):
            story.append(Paragraph("Price History", self.styles['BPIHeading']))
            # Process the graph image
            img = PILImage.open(graph_path)
            # Calculate aspect ratio for proper sizing
            aspect = img.height / img.width
            img_width = 9 * inch  # Max width
            img_height = img_width * aspect
            
            story.append(Image(graph_path, width=img_width, height=img_height))

        # Generate the PDF
        doc.build(story)
        return self.output_path