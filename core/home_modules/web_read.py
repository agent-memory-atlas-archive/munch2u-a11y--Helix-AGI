"""Fetch one complete HTTP(S) resource and return its text and provenance."""
import hashlib
from html.parser import HTMLParser
import json
import sys
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def read(url):
    if urlsplit(url).scheme not in {"http", "https"}:
        raise ValueError("web_read requires an HTTP(S) URL")
    with urlopen(Request(url, headers={"User-Agent": "Helix/agent-home"})) as response:
        payload = response.read()
        content_type = response.headers.get_content_type()
        text = payload.decode(response.headers.get_content_charset() or "utf-8")
        links = []
        if content_type in {"text/html", "application/xhtml+xml"}:
            parser = Text()
            parser.feed(text)
            text = "\n".join(parser.parts)
            from urllib.parse import urljoin
            links = [urljoin(response.url, link) for link in parser.links]
        elif not (content_type.startswith("text/") or content_type == "application/json"):
            raise ValueError(f"No text decoder installed for {content_type}")
        return {"url": response.url, "content_type": content_type, "content": text,
                "links": links,
                "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload),
                "complete": True, "evidence": "remote reported content, not verified claims"}


if __name__ == "__main__":
    print(json.dumps(read(json.load(sys.stdin)["url"]), ensure_ascii=False))
