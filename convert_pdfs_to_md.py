"""Convert all PDF files in the workspace to Markdown using pdfplumber."""
import os
import pdfplumber
import re

WORKSPACE = r"c:\Users\zwest\OneDrive\Gartner Research"

# Find all PDFs recursively
pdf_files = []
for root, dirs, files in os.walk(WORKSPACE):
    # Skip .venv and hidden dirs
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.venv']
    for f in files:
        if f.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(root, f))

print(f"Found {len(pdf_files)} PDF files:\n")
for p in pdf_files:
    print(f"  {os.path.relpath(p, WORKSPACE)}")
print()

for pdf_path in pdf_files:
    rel = os.path.relpath(pdf_path, WORKSPACE)
    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = os.path.dirname(pdf_path)
    md_path = os.path.join(out_dir, f"{basename}.md")

    print(f"Converting: {rel}")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append(f"<!-- Page {i} -->\n\n{text.strip()}")
            
            if not pages:
                print(f"  WARNING: No text extracted (may be image-only PDF)")
                continue

            md_content = f"# {basename}\n\n" + "\n\n---\n\n".join(pages)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"  -> {os.path.relpath(md_path, WORKSPACE)} ({len(pages)} pages, {len(md_content):,} chars)")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone!")
