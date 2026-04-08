
def search_internet(query):
    try:
        import requests as _r, os
        key = os.getenv("TAVILY_KEY", "")
        if key:
            resp = _r.post(
                "https://api.tavily.com/search",
                json={"api_key": key, "query": query, "max_results": 5},
                timeout=10
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                return " ".join([r.get("title","") + ": " + r.get("content","")[:200] for r in results])
    except:
        pass
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
            desc = item.findtext("description", "")[:200]
            results.append(f"{title}: {desc}")
        return " ".join(results)
    except:
        return ""
