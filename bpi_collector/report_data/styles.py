from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def get_report_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BPITitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#667eea"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="BPIHeading",
            parent=styles["Heading2"],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor("#2c3e50"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="BPIText",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#333333"),
        )
    )

    return styles


def get_table_styles():
    return {
        "info_table": [
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e9ecef")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ],
        "stats_table": [
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e9ecef")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("PADDING", (0, 0), (-1, -1), 8),
        ],
    }


def get_fallback_html_template():
    return """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #2c3e50;">Bitcoin Price Index Report</h1>
    <p>Report generated on {current_time}</p>
    <p>Samples collected: {sample_count}</p>
    <table border="1" style="width: 100%; border-collapse: collapse;">
        <tr style="background-color: #f1f1f1;">
            <th style="padding: 10px; text-align: left;">Currency Pair</th>
            <th style="padding: 10px; text-align: left;">Min Price</th>
            <th style="padding: 10px; text-align: left;">Max Price</th>
            <th style="padding: 10px; text-align: left;">Current Price</th>
            <th style="padding: 10px; text-align: left;">Change</th>
        </tr>
        {price_rows}
    </table>
    </body>
    </html>
    """


def get_simple_html_template():
    return """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>BPI Report - {report_date}</h2>
        <p><strong>Session:</strong> {start_time} to {end_time}</p>
        <p><strong>Duration:</strong> {duration}</p>
        <p><strong>Samples:</strong> {sample_count}</p>
        {graph_content}
    </div>
    """
