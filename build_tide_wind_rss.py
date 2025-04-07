
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# CONFIG
OUTPUT_FEED = "tide-conditions.xml"
STATION_ID = "8725744"
NOAA_API_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
NWS_URL = "https://forecast.weather.gov/MapClick.php?lat=26.929&lon=-82.045"

def get_tides():
    params = {
        "product": "predictions",
        "datum": "MLLW",
        "station": STATION_ID,
        "time_zone": "lst_ldt",  # Local time
        "units": "english",
        "interval": "hilo",
        "format": "json",
        "begin_date": datetime.now().strftime("%Y%m%d"),
        "end_date": datetime.now().strftime("%Y%m%d"),
    }

    response = requests.get(NOAA_API_URL, params=params)
    data = response.json()["predictions"]

    # Get first high and low tide of the day
    high = next((p for p in data if p["type"] == "H"), None)
    low = next((p for p in data if p["type"] == "L"), None)

    return high, low

def get_wind():
    try:
        response = requests.get(NWS_URL)
        soup = BeautifulSoup(response.content, "html.parser")
        wind = soup.select_one(".myforecast-current-sm")
        return f"💨 Wind: {wind.text.strip()}" if wind else "💨 Wind: data unavailable"
    except Exception:
        return "💨 Wind: error"

def create_marquee_string(high, low):
    high_time = datetime.strptime(high["t"], "%Y-%m-%d %H:%M").strftime("%I:%M %p")
    low_time = datetime.strptime(low["t"], "%Y-%m-%d %H:%M").strftime("%I:%M %p")
    return (
        f"🌊 High Tide: {high_time} ({high['v']} ft)  ···  "
        f"🌊 Low Tide: {low_time} ({low['v']} ft)"
    )

def build_rss(text):
    now = datetime.utcnow()
    pub_date = now.strftime("%a, %d %b %Y 12:00:00 GMT")
    last_build = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Emerald Pointe – Tide &amp; Wind Conditions</title>
    <description>Daily marine forecast with tide &amp; wind info for Punta Gorda</description>
    <link>https://ryanmess.github.io/ep-bistro-rss/</link>
    <lastBuildDate>{last_build}</lastBuildDate>
    <item>
      <title>Marine Conditions for {now.strftime('%A, %B %d')}</title>
      <description>{text}</description>
      <pubDate>{pub_date}</pubDate>
    </item>
  </channel>
</rss>
"""
    return rss

def main():
    high, low = get_tides()
    if not high or not low:
        print("Tide data not found.")
        return

    wind = get_wind()
    summary = create_marquee_string(high, low) + "  ···  " + wind
    print("Generated summary:", summary)

    rss = build_rss(summary)
    with open(OUTPUT_FEED, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"RSS feed written to {OUTPUT_FEED}")

if __name__ == "__main__":
    main()
