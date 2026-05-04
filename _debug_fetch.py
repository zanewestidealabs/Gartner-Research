"""Debug fetch: try to actually download and inspect raw HTML."""
import urllib.request, urllib.error
import re
from html import unescape
from html.parser import HTMLParser
from typing import List

url = "https://www.crowdstrike.com/en-us/services/managed-detection-and-response/"

class _TextExtractor(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "head", "meta", "link"}
    def __init__(self):
        super().__init__()
        self._parts: List[str] = []
        self._skip = 0
    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.SKIP_TAGS:
            self._skip += 1
        elif tag.lower() in ("br", "p", "div", "h1", "h2", "h3", "h4", "li", "tr"):
            self._parts.append("\n")
    def handle_endtag(self, tag):
        if tag.lower() in self.SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
    def handle_data(self, data):
        if self._skip == 0:
            self._parts.append(data)
    def get_text(self) -> str:
        return " ".join(self._parts)

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

try:
    req = urllib.request.Request(url, headers={
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"Status: {resp.status}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        raw = resp.read()
        html = raw.decode("utf-8", errors="replace")
        print(f"HTML length: {len(html)}")
        
        # Check if it's JS-rendered
        has_body_text = bool(re.search(r'<body[^>]*>.*\w{20,}.*</body>', html, re.DOTALL))
        has_noscript = '<noscript' in html.lower()
        js_only = '__NEXT_DATA__' in html or 'window.__remixContext' in html
        print(f"Has body text: {has_body_text}, noscript: {has_noscript}, JS framework: {js_only}")
        
        # Try extraction
        parser = _TextExtractor()
        parser.feed(html)
        text = unescape(parser.get_text())
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        print(f"\nExtracted text length: {len(text)}")
        print(f"Text:\n{text[:1000]}")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
