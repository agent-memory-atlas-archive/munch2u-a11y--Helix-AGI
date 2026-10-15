"""Read the current search-results page without sampling or clipping it."""
import json
import sys
from urllib.parse import urlencode
from web_read import read


if __name__ == "__main__":
    query = json.load(sys.stdin)["query"]
    if not query.strip():
        raise ValueError("search query is empty")
    # A page is the remote protocol unit. Retain its complete text and links;
    # subsequent pages and destinations can be read with web_read.
    result = read("https://html.duckduckgo.com/html/?" + urlencode({"q": query}))
    result.update(query=query, search_scope="one complete remote results page")
    print(json.dumps(result, ensure_ascii=False))
