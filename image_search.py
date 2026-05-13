import sys


def zoek_product_foto(query: str) -> str | None:
    """Zoek een echte productfoto via DuckDuckGo. Geeft URL terug of None."""
    if not query or not query.strip():
        return None
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            print(f"[image_search] geen DDG package: {e}", file=sys.stderr)
            return None

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                f"{query} gerecht",
                max_results=10,
                safesearch="moderate",
                type_image="photo",
                size="Medium",
            ))
            for r in results:
                url = r.get("image")
                if url and url.startswith("http"):
                    return url
            print(f"[image_search] geen resultaten voor '{query}'", file=sys.stderr)
    except Exception as e:
        print(f"[image_search] DDG fout: {type(e).__name__}: {e}", file=sys.stderr)
    return None
