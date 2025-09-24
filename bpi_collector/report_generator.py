import os
from pathlib import Path
from datetime import datetime
from PIL import Image as PILImage
from typing import List, Dict, Any

from .report_data.templates import get_price_row_template
from .report_data.images import encode_image_base64
from .report_data.formatting import (
    format_timestamp,
    format_time_short,
    calculate_duration,
)
from .report_data.timestamp_utils import (
    convert_timestamp_to_datetime,
    extract_price_stats,
)

from .report_data.templates import (
    get_graph_content_template,
    get_fallback_price_row_template,
    get_graph_container_template,
)
from .report_data.styles import (
    get_report_styles,
    get_table_styles,
    get_fallback_html_template,
    get_simple_html_template,
)

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)


class ReportGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.html_template_path = (
            Path(__file__).parent.parent / "templates" / "report_template_new.html"
        )
        self.styles = get_report_styles()

    @staticmethod
    def format_timestamp(ts) -> str:
        return format_timestamp(ts)

    @staticmethod
    def format_time_short(ts) -> str:
        return format_time_short(ts)

    @staticmethod
    def calculate_duration(start_ts, end_ts) -> str:
        return calculate_duration(start_ts, end_ts)

    @staticmethod
    def encode_image_base64(image_path: str) -> str:
        return encode_image_base64(image_path)

    def generate_html_report(
        self, samples: List[Dict[str, Any]], graph_path: str = None
    ) -> str:
        if not samples:
            return "No data available for report"

        template_path = (
            Path(__file__).parent.parent / "templates" / "report_template_simple.html"
        )
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        start_ts = samples[0]["ts"]
        end_ts = samples[-1]["ts"]

        start_time = convert_timestamp_to_datetime(start_ts)
        end_time = convert_timestamp_to_datetime(end_ts)

        pairs = (
            list(samples[0].get("prices", {}).keys())
            if samples[0].get("prices")
            else []
        )

        price_rows = []

        btc_prices = [
            s["prices"].get("BTC-USD", 0)
            for s in samples
            if "BTC-USD" in s.get("prices", {})
        ]

        if btc_prices:
            min_price = f"${min(btc_prices):,.2f}"
            max_price = f"${max(btc_prices):,.2f}"
            avg_price = f"${sum(btc_prices)/len(btc_prices):,.2f}"
        else:
            min_price = max_price = avg_price = "N/A"

        for pair in pairs:
            min_price, max_price, current, change = extract_price_stats(samples, pair)

            if min_price or max_price or current:
                color = (
                    "#28a745" if change > 0 else "#dc3545" if change < 0 else "#6c757d"
                )
                change_text = f"{change:+.2f}%" if change != 0 else "0.00%"
                price_row_template = get_price_row_template()
                price_rows.append(
                    price_row_template.format(
                        pair=pair,
                        min_price=min_price,
                        max_price=max_price,
                        current=current,
                        color=color,
                        change_text=change_text,
                    )
                )

        graph_content = ""
        if graph_path and os.path.exists(graph_path):
            encoded_image = self.encode_image_base64(graph_path)
            if encoded_image:
                graph_content = get_graph_content_template(True).format(
                    encoded_image=encoded_image
                )
            else:
                graph_content = get_graph_content_template(False)
        else:
            graph_content = get_graph_content_template(False)

        try:
            duration_str = self.calculate_duration(start_time, end_time)
            duration_seconds = (end_time - start_time).total_seconds()
            interval = duration_seconds / (len(samples) - 1) if len(samples) > 1 else 0

            # Ensure we're using the system timezone that's set via TZ environment variable
            local_now = datetime.now().astimezone()
            report_html = template.format(
                report_date=local_now.strftime("%B %d, %Y at %I:%M %p")
                + " (Local Time)",
                sample_count=len(samples),
                collection_period=duration_str,
                sample_interval=f"{interval:.1f}",
                min_price=min_price if "min_price" in locals() else "N/A",
                max_price=max_price if "max_price" in locals() else "N/A",
                avg_price=avg_price if "avg_price" in locals() else "N/A",
                price_rows="".join(price_rows),
            )
            return report_html
        except Exception as e:
            print(f"Template formatting failed: {e}")

            template = get_fallback_price_row_template()
            price_rows = "".join(
                template.format(pair=pair, price=samples[-1]["prices"][pair])
                for pair in samples[-1]["prices"]
            )

            return get_fallback_html_template().format(
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                sample_count=len(samples),
                price_rows=price_rows,
            )

    def _generate_simple_html_report(
        self, samples: list, graph_path: str = None
    ) -> str:

        start_ts = samples[0]["ts"]
        end_ts = samples[-1]["ts"]

        start_time = convert_timestamp_to_datetime(start_ts)
        end_time = convert_timestamp_to_datetime(end_ts)

        graph_content = ""
        if graph_path and os.path.exists(graph_path):
            encoded_image = self.encode_image_base64(graph_path)
            if encoded_image:
                content = get_graph_content_template(True).format(
                    encoded_image=encoded_image
                )
                graph_content = get_graph_container_template().format(content=content)

        html = get_simple_html_template().format(
            report_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            start_time=self.format_timestamp(start_time),
            end_time=self.format_timestamp(end_time),
            duration=self.calculate_duration(start_time, end_time),
            sample_count=len(samples),
            graph_content=graph_content,
        )

        return html

    def generate_report(self, samples: list, graph_path: str = None) -> str:
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=landscape(letter),
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        story = list()
        story.append(Paragraph("Bitcoin Price Index Report", self.styles["BPITitle"]))

        if samples:
            start_time = self.format_timestamp(samples[0]["ts"])
            end_time = self.format_timestamp(samples[-1]["ts"])

            pairs = (
                list(samples[0].get("prices", {}).keys())
                if samples[0].get("prices")
                else []
            )
            stats_data = []

            for pair in pairs:
                min_price, max_price, current, change = extract_price_stats(
                    samples, pair
                )

                if min_price or max_price or current:
                    stats_data.append(
                        [
                            pair,
                            f"${min_price:,.2f}",
                            f"${max_price:,.2f}",
                            f"${current:,.2f}",
                            f"{change:+.2f}%",
                        ]
                    )

            duration = self.calculate_duration(samples[0]["ts"], samples[-1]["ts"])
            info_data = [
                ["Collection Period", f"{start_time} to {end_time}"],
                ["Duration", duration],
                ["Total Samples", str(len(samples))],
                ["Currency Pairs", ", ".join(pairs)],
            ]

            info_table = Table(info_data, colWidths=[2.5 * inch, 4 * inch])
            info_table.setStyle(TableStyle(get_table_styles()["info_table"]))

            story.append(Paragraph("Session Overview", self.styles["BPIHeading"]))
            story.append(info_table)
            story.append(Spacer(1, 20))

            if stats_data:
                stats_table = Table(
                    [["Currency Pair", "Minimum", "Maximum", "Current", "Change"]]
                    + stats_data,
                    colWidths=[
                        1.5 * inch,
                        1.5 * inch,
                        1.5 * inch,
                        1.5 * inch,
                        1.5 * inch,
                    ],
                )
                stats_table.setStyle(TableStyle(get_table_styles()["stats_table"]))

                story.append(Paragraph("Price Statistics", self.styles["BPIHeading"]))
                story.append(stats_table)
                story.append(Spacer(1, 20))

        if graph_path and os.path.exists(graph_path):
            story.append(Paragraph("Price History", self.styles["BPIHeading"]))
            img = PILImage.open(graph_path)
            aspect = img.height / img.width
            img_width = 9 * inch  # Max width
            img_height = img_width * aspect

            story.append(Image(graph_path, width=img_width, height=img_height))

        doc.build(story)
        return self.output_path
