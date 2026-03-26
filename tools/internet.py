from ddgs import DDGS
import signal

def search_internet(query):
    try:
        with DDGS(timeout=5) as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return " ".join(results)
    except Exception as e:
        return ""
