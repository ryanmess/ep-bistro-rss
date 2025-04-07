
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# CONFIG
LOCATION = "Punta Gorda"
TIDE_URL = "https://www.tide-forecast.com/locations/Punta-Gorda-Florida/tides/latest"
WEATHER_URL = "https://forecast.weather.gov/MapClick.php?lat=26.929&lon=-82.045"
OUTPUT_FEED = "tide-conditions.xml"

def get_tides():
    response = requests.get(TIDE_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.select("table.tide-table tbody tr")
    high, low = None, None

    for row in rows:
        if "High Tide" in row.text and not high:
            time = row.select_one("td.time").text.strip()
            height = row.select_one("td.height").text.strip()
            high = (time, height)
        elif "Low Tide" in row.text and not low:
            time = row.select_one("td.time").text.strip()
            height = row.select_one("td.height").text.strip()
            low = (time, height)
        if high and low:
            break

    return high, low

def get_wind():
    response = requests.get(WEATHER_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    wind_div = soup.select_one(".myforecast-current-sm")
    if wind_div:
        return wind_div.text.strip()
    return "Wind data unavailable"

def build_rss(high, low, wind):
    now = datetime.utcnow()
    pub_date = now.strftime("%a, %d %b %Y 12:00:00 GMT")
    last_build = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    desc = f"🌊 High Tide: {high[0]} ({high[1]})\n🌊 Low Tide: {low[0]} ({low[1]})\n💨 Wind: {wind}"
    item = f"""
    <item>
      <title>Marine Conditions for {now.strftime('%A, %B %d')}</title>
      <description>{desc}</description>
      <pubDate>{pub_date}</pubDate>
    </item>
    """

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Emerald Pointe – Tide & Wind Conditions</title>
    <description>Daily marine forecast with tide and wind info for Punta Gorda</description>
    <link>https://ryanmess.github.io/ep-bistro-rss/</link>
    <lastBuildDate>{last_build}</lastBuildDate>
    {item}
  </channel>
</rss>
"""
    return rss

def main():
    high, low = get_tides()
    wind = get_wind()

    if not high or not low:
        print("Failed to get tide data.")
        return

    rss = build_rss(high, low, wind)
    with open(OUTPUT_FEED, "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"RSS feed saved to {OUTPUT_FEED}")

if __name__ == "__main__":
    main()
