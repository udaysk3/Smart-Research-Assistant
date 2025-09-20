#!/usr/bin/env python3
"""
Setup Pathway for live data ingestion
"""
import os
import requests
import time
from datetime import datetime

def setup_pathway():
    print("🚀 Setting up Pathway for live data ingestion...")
    print("=" * 60)
    
    # Check if Pathway is running
    pathway_host = os.getenv("PATHWAY_HOST", "localhost")
    pathway_port = os.getenv("PATHWAY_PORT", "8001")
    pathway_url = f"http://{pathway_host}:{pathway_port}"
    
    try:
        response = requests.get(f"{pathway_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Pathway is already running!")
            return True
    except:
        print("❌ Pathway is not running. Starting Pathway...")
    
    # Start Pathway server
    print("🔧 Starting Pathway server...")
    print("📝 Note: You need to install Pathway first:")
    print("   pip install pathway")
    print("   pathway --help")
    
    # Create a simple Pathway script for live data
    pathway_script = """
import pathway as pw
import requests
import feedparser
from datetime import datetime

# Define data sources
rss_feeds = [
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://rss.cnn.com/rss/edition_technology.rss",
    "https://feeds.feedburner.com/oreilly/radar",
]

# Create a table for live data
class LiveDataSchema(pw.Schema):
    title: str
    content: str
    source: str
    published: str
    url: str
    timestamp: str

# Function to fetch RSS data
def fetch_rss_data():
    data = []
    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:  # Get latest 5 articles
                data.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", ""),
                    "source": feed.feed.get("title", feed_url),
                    "published": entry.get("published", ""),
                    "url": entry.get("link", ""),
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
    return data

# Create live data table
live_data = pw.Table.from_pandas(pd.DataFrame(fetch_rss_data()))

# Output the data
pw.io.csv.write(live_data, "live_data_output.csv")

# Run the pipeline
pw.run()
"""
    
    with open("pathway_live_data.py", "w") as f:
        f.write(pathway_script)
    
    print("✅ Created pathway_live_data.py")
    print("📋 To run Pathway:")
    print("   1. Install Pathway: pip install pathway")
    print("   2. Run: python pathway_live_data.py")
    print("   3. Or use Pathway CLI: pathway run pathway_live_data.py")
    
    return False

if __name__ == "__main__":
    setup_pathway()
