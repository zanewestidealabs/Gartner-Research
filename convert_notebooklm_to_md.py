"""
Convert NotebookLM HTML exports in Documents/ to clean Markdown files.

NotebookLM saves pages as Angular apps with content in:
  - .notebook-summary / .summary-content  -> overview text
  - .chat-message-pair                    -> Q&A exchanges
    - .from-user-container               -> user prompt
    - .to-user-container                 -> AI response (rich HTML)

This script extracts those elements and converts them to Markdown.
"""

import os
import re
import glob
from bs4 import BeautifulSoup, NavigableString
import html2text


def make_html2text_converter():
    """Configure html2text for clean markdown output."""
    h = html2text.HTML2Text()
    h.body_width = 0          # No wrapping
    h.unicode_snob = True     # Use unicode instead of ascii
    h.skip_internal_links = True
    h.ignore_images = False
    h.ignore_emphasis = False
    h.ignore_links = False
    h.protect_links = True
    h.single_line_break = False
    h.mark_code = True
    return h


def clean_notebooklm_noise(text):
    """Remove NotebookLM UI artifacts from extracted text."""
    # Remove Material icon text that leaked through
    icon_words = [
        'more_vert', 'keyboard_arrow_down', 'search_spark', 'arrow_forward',
        'dock_to_right', 'trending_up', 'tune', 'add', 'search', 'language',
        'drive_pdf', 'content_copy', 'thumb_up', 'thumb_down', 'share',
        'settings', 'Settings', 'Analytics', 'Share', 'PRO', 'Sources',
        'Create notebook', 'Add sources', 'Fast Research', 'Select all sources',
        'Web', 'Chat', 'Loading', 'Search results', 'No emoji found',
        'Recently used',
    ]
    for icon in icon_words:
        text = text.replace(icon, '')

    # Clean up excessive whitespace from icon removal
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n[ \t]+\n', '\n\n', text)

    return text.strip()


def extract_rich_html(element):
    """Extract the inner HTML of an element, preserving formatting tags."""
    if element is None:
        return ""
    # Get the inner HTML
    return element.decode_contents()


def convert_response_html_to_md(html_content, converter):
    """Convert a NotebookLM response HTML block to markdown."""
    # Parse the response content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove citation superscript numbers (they reference NotebookLM sources)
    for sup in soup.find_all('sup'):
        sup.decompose()

    # Remove button elements (copy, thumbs up, etc.)
    for btn in soup.find_all(['button', 'mat-icon']):
        btn.decompose()

    # Get cleaned HTML
    cleaned_html = str(soup)

    # Convert to markdown
    md = converter.handle(cleaned_html)

    return clean_notebooklm_noise(md)


def extract_user_message(pair_element):
    """Extract user message text from a chat message pair."""
    user_container = pair_element.find(class_='from-user-container')
    if not user_container:
        return None
    msg_div = user_container.find(class_='message-text-content')
    if not msg_div:
        msg_div = user_container.find('mat-card-content')
    if not msg_div:
        return None
    return msg_div.get_text(strip=True)


def extract_ai_response(pair_element):
    """Extract AI response HTML from a chat message pair."""
    ai_container = pair_element.find(class_='to-user-container')
    if not ai_container:
        return None
    msg_div = ai_container.find(class_='message-text-content')
    if not msg_div:
        msg_div = ai_container.find('mat-card-content')
    if not msg_div:
        return None
    return extract_rich_html(msg_div)


def convert_notebooklm_html(html_path, output_path):
    """Convert a single NotebookLM HTML file to Markdown."""
    print(f"\nProcessing: {os.path.basename(html_path)}")
    print(f"  Size: {os.path.getsize(html_path):,} bytes")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    converter = make_html2text_converter()

    # Extract title from <title> tag
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else os.path.splitext(os.path.basename(html_path))[0]
    # Clean "- NotebookLM" suffix
    title = re.sub(r'\s*[-–]\s*NotebookLM\s*$', '', title)

    md_parts = []
    md_parts.append(f"# {title}\n")
    md_parts.append(f"*Converted from NotebookLM export: {os.path.basename(html_path)}*\n")

    # Extract notebook summary
    summary_el = soup.find(class_='summary-content')
    if not summary_el:
        summary_el = soup.find(class_='notebook-summary')
    if summary_el:
        summary_html = extract_rich_html(summary_el)
        summary_md = converter.handle(summary_html)
        summary_md = clean_notebooklm_noise(summary_md)
        if summary_md.strip():
            md_parts.append("## Notebook Summary\n")
            md_parts.append(summary_md.strip())
            md_parts.append("")

    # Extract chat message pairs
    pairs = soup.find_all(class_='chat-message-pair')
    print(f"  Found {len(pairs)} conversation exchanges")

    exchange_num = 0
    for pair in pairs:
        user_msg = extract_user_message(pair)
        ai_html = extract_ai_response(pair)

        if not ai_html and not user_msg:
            continue

        exchange_num += 1
        md_parts.append(f"\n---\n")
        md_parts.append(f"## Exchange {exchange_num}\n")

        if user_msg:
            # Format user message as blockquote
            user_lines = user_msg.strip().split('\n')
            quoted = '\n'.join(f"> {line}" for line in user_lines)
            md_parts.append(f"### Prompt\n")
            md_parts.append(quoted)
            md_parts.append("")

        if ai_html:
            ai_md = convert_response_html_to_md(ai_html, converter)
            if ai_md.strip():
                md_parts.append(f"### Response\n")
                md_parts.append(ai_md.strip())
                md_parts.append("")

    # Also look for standalone response containers outside pairs
    # (some NotebookLM exports have a different structure)
    if exchange_num == 0:
        print("  No chat-message-pairs found, trying alternative extraction...")
        # Try finding all to-user containers directly
        responses = soup.find_all(class_='to-user-container')
        for i, resp in enumerate(responses):
            msg_div = resp.find(class_='message-text-content')
            if not msg_div:
                msg_div = resp.find('mat-card-content')
            if msg_div:
                resp_html = extract_rich_html(msg_div)
                resp_md = convert_response_html_to_md(resp_html, converter)
                if resp_md.strip() and len(resp_md.strip()) > 50:
                    exchange_num += 1
                    md_parts.append(f"\n---\n")
                    md_parts.append(f"## Section {exchange_num}\n")
                    md_parts.append(resp_md.strip())
                    md_parts.append("")

    # Finalize
    final_md = '\n'.join(md_parts)

    # Final cleanup passes
    final_md = re.sub(r'\n{4,}', '\n\n\n', final_md)
    final_md = final_md.strip() + '\n'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_md)

    line_count = final_md.count('\n')
    print(f"  Output: {os.path.basename(output_path)} ({len(final_md):,} chars, {line_count} lines)")
    print(f"  Exchanges extracted: {exchange_num}")

    return exchange_num


def main():
    docs_dir = os.path.join(os.path.dirname(__file__), "Documents")
    html_files = glob.glob(os.path.join(docs_dir, "*.html"))

    if not html_files:
        print("No HTML files found in Documents/")
        return

    print(f"Found {len(html_files)} HTML files to convert:\n")
    for f in html_files:
        print(f"  - {os.path.basename(f)}")

    total_exchanges = 0
    converted = 0

    for html_path in html_files:
        base_name = os.path.splitext(os.path.basename(html_path))[0]
        # Clean up the filename for markdown
        md_name = base_name.replace(' - NotebookLM', '')
        output_path = os.path.join(docs_dir, f"{md_name}.md")

        try:
            exchanges = convert_notebooklm_html(html_path, output_path)
            total_exchanges += exchanges
            converted += 1
        except Exception as e:
            print(f"\n  ERROR processing {os.path.basename(html_path)}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Conversion complete!")
    print(f"  Files converted: {converted}/{len(html_files)}")
    print(f"  Total exchanges extracted: {total_exchanges}")
    print(f"  Output directory: {docs_dir}")


if __name__ == "__main__":
    main()
