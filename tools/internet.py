from ddgs import DDGS
import signal

def search_internet(query):
    try:
        with DDGS(timeout=10) as ddgs:
            results = [r["body"] for r in ddgs.text(query, max_results=5, region="in-en")]
            return " ".join(results)
    except Exception as e:
        try:
            from duckduckgo_search import DDGS as DDGS2
            with DDGS2(timeout=10) as ddgs:
                results = [r["body"] for r in ddgs.text(query, max_results=5)]
                return " ".join(results)
        except:
            return ""
