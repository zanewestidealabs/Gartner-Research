"""Debug: test text extraction on working URLs."""
import urllib.request, re
from html import unescape
from html.parser import HTMLParser
from typing import List

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

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"

test_urls = [
    "https://www.crowdstrike.com/en-us/platform/",
    "https://arcticwolf.com/solutions/managed-detection-and-response/",
    "https://www.paloaltonetworks.com/cortex/managed-detection-and-response",
]

for url in test_urls:
    print(f"\n{'='*60}")
    print(f"URL: {url}")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": ua,
            "Accept": "text/html,*/*",
            "Accept-Encoding": "identity",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            html = raw.decode("utf-8", errors="replace")
            print(f"HTML length: {len(html)}")
            
            parser = _TextExtractor()
            parser.feed(html)
            text = unescape(parser.get_text())
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            text = text.strip()
            print(f"Extracted text length: {len(text)}")
            if text:
                # Show first 500 chars
                print(f"Preview: {text[:500]}")
            else:
                # Check if JSON data in page
                json_match = re.search(r'__NEXT_DATA__.*?({.*?})', html[:5000])
                print(f"Empty text. Has __NEXT_DATA__: {'__NEXT_DATA__' in html}")
                print(f"Has <noscript>: {'<noscript' in html.lower()}")
                # Show raw body content around text
                body = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
                if body:
                    print(f"Body length: {len(body.group(1))}")
                    # Find visible text in body
                    visible = re.findall(r'>([^<]{20,})<', body.group(1))
                    print(f"Found {len(visible)} visible text chunks")
                    for v in visible[:5]:
                        print(f"  -> {v.strip()[:100]}")
    except Exception as e:
        print(f"Error: {e}")
