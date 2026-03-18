from duckduckgo_search import DDGS

def search_internet(query):
    try:
        with DDGS() as ddgs:
            # Sirf top 2 results nikal rahe hain
            results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return " ".join(results)
    except Exception as e:
        return f"Internet search fail ho gaya: {e}"