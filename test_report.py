#!/usr/bin/env python3
"""Test script to generate and preview the new HTML report."""

from datetime import datetime, timedelta
from bpi_collector.report_generator import ReportGenerator
import webbrowser
import tempfile
import os


def create_test_data():
    """Create realistic test data for demonstration."""
    base_time = datetime.now()
    samples = []

    # Generate 10 samples over the last hour with realistic price changes
    base_btc = 45000
    base_eth = 2800

    for i in range(10):
        time_offset = timedelta(minutes=i * 6)  # Every 6 minutes
        timestamp = base_time - timedelta(hours=1) + time_offset

        # Simulate price fluctuations
        btc_change = (-100 + (i * 50)) + (i % 3 - 1) * 200
        eth_change = (-50 + (i * 20)) + (i % 2 - 0.5) * 100

        sample = {
            "ts": timestamp.isoformat() + "Z",
            "prices": {
                "BTC-USD": base_btc + btc_change,
                "ETH-USD": base_eth + eth_change,
                "LTC-USD": 150 + (i * 2) + (i % 4 - 2) * 5,
            },
        }
        samples.append(sample)

    return samples


def main():
    print("🚀 Testing BPI Report Generator")
    print("=" * 50)

    # Create test data
    samples = create_test_data()
    print(f"✅ Created {len(samples)} test samples")

    # Generate HTML report
    generator = ReportGenerator("")
    html_content = generator.generate_html_report(samples)
    print("✅ Generated HTML report")

    # Save to temporary file and open in browser
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    print(f"✅ Saved report to: {temp_path}")

    # Try to open in browser
    try:
        webbrowser.open(f"file://{temp_path}")
        print("✅ Opened report in browser")
    except:
        print("⚠️  Could not open browser automatically")

    print(
        f"""
📊 Report Summary:
   • Samples: {len(samples)}
   • Time range: {samples[0]['ts'][:19]} to {samples[-1]['ts'][:19]}
   • Currency pairs: {', '.join(samples[0]['prices'].keys())}
   • HTML size: {len(html_content):,} characters
   
🌐 To view the report manually, open: {temp_path}
"""
    )

    input("Press Enter to clean up and exit...")

    # Clean up
    try:
        os.unlink(temp_path)
        print("✅ Cleaned up temporary file")
    except:
        pass


if __name__ == "__main__":
    main()
