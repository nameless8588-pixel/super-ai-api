
def search_internet(query):
    import os
    # Tavily se try karo
    try:
        import requests as _r
        key = os.getenv("TAVILY_KEY", "")
        if key:
            resp = _r.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": key,
                    "query": query,
                    "max_results": 5,
                    "search_depth": "advanced",
                    "include_domains": ["espncricinfo.com", "iplt20.com", "cricbuzz.com", "ndtv.com", "bbc.com", "reuters.com", "timesofindia.com"]
                },
                timeout=10
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    return " ".join([r.get("title","") + ": " + r.get("content","")[:300] for r in results])
    except:
        pass
    # Fallback: Google News RSS
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
