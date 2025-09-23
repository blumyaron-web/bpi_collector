from .images import encode_image_base64
from .formatting import format_timestamp, format_time_short, calculate_duration
from .timestamp_utils import convert_timestamp_to_datetime, extract_price_stats
from .templates import (
    get_graph_content_template,
    get_fallback_price_row_template,
    get_price_row_template,
)
from .styles import (
    get_report_styles,
    get_table_styles,
    get_fallback_html_template,
    get_simple_html_template,
)
