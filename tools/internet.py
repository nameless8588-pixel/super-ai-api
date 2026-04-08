
def search_internet(query):
    import os, requests as _r
    # SerpAPI - Google real search
    try:
        key = os.getenv("SERPAPI_KEY", "")
        if key:
            resp = _r.get(
                "https://serpapi.com/search",
                params={
                    "q": query,
                    "api_key": key,
                    "num": 5,
                    "hl": "en",
                    "gl": "in"
                },
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for r in data.get("organic_results", [])[:5]:
                    results.append(r.get("title","") + ": " + r.get("snippet","")[:300])
                if results:
                    return " ".join(results)
    except:
        pass
    # Fallback Google News RSS
    try:
        import urllib.request, urllib.parse, xml.etree.ElementTree as ET
        encoded = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        root = ET.fromstring(resp.read())
        results = []
        for item in root.findall(".//item")[:5]:
            title = item.findtext("title", "")
            desc = item.findtext("description", "")[:300]
            pub_date = item.findtext("pubDate", "")
            results.append(f"{title} ({pub_date}): {desc}")
        return " ".join(results)
    except:
        return ""
