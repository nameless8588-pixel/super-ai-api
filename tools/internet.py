def search_internet(query):
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(f"{r['title']}: {r['body'][:200]}")
        return " ".join(results)
    except:
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
