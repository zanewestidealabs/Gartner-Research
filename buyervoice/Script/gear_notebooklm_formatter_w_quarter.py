"""
Gartner Interaction Data Formatter for NotebookLM - CSV Version (Text Output)
Converts CSV data into formatted text files with word count management.
Groups interactions by calendar quarter (derived from First Response Date).
"""

import pandas as pd
import os
from datetime import datetime

# Configuration
WORD_LIMIT_PER_FILE = 450000  # 10% safety buffer from NBLM's 500k word limit
SEPARATOR_LINE = "=" * 80

# Column mapping: CSV column name -> Output column name
COLUMN_MAPPING = {
    'Reference Number': 'Reference Number',
    'Associate Name': 'Analyst Name',
    'Purpose': 'Purpose',
    'Question Asked': 'Question Asked',
    'Discussion Summary': 'Discussion Summary',
    'First Response Date': 'Date',
    'Account Region': 'Buyer Region',
    'Enterprise Sector': 'Buyer Industry',
    'Role Name': 'Buyer Role'
}

# Desired output order
OUTPUT_ORDER = [
    'Date',
    'Reference Number',
    'Buyer Region',
    'Buyer Industry',
    'Buyer Role',
    'Purpose',
    'Question Asked',
    'Analyst Name',
    'Discussion Summary'
]

def count_words(text):
    """Count words in a string"""
    if pd.isna(text):
        return 0
    return len(str(text).split())

def format_interaction(row, columns):
    """Format a single interaction row into text with labels"""
    lines = []
    total_words = 0

    for col in columns:
        value = row[col]
        if pd.isna(value):
            value = "[Not provided]"

        line = f"{col}: {value}"
        lines.append(line)
        total_words += count_words(str(value))

    lines.append(SEPARATOR_LINE)
    lines.append("")  # Blank line after separator

    return "\n".join(lines), total_words

def build_header(base_filename, quarter, file_number, interaction_count):
    """Build the per-file header block."""
    lines = [
        SEPARATOR_LINE,
        f"{base_filename.upper()} - {quarter} - PART {file_number}",
        SEPARATOR_LINE,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
        f"Total Interactions: {interaction_count}",
        f"File: Part {file_number}",
        "",
        SEPARATOR_LINE,
        "",
    ]
    return "\n".join(lines)

def get_quarter_label(date_value):
    """Return a calendar-quarter label like '2024 Q2' from a date value."""
    dt = pd.to_datetime(date_value, errors='coerce')
    if pd.isna(dt):
        return 'UnknownDate'
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year} Q{q}"

def quarter_sort_key(label):
    """Chronological sort key so quarters order correctly across year boundaries."""
    if label == 'UnknownDate':
        return (9999, 9)  # push undated interactions to the end
    year = int(label[:4])
    q = int(label[-1])
    return (year, q)

def write_output_file(output_dir, base_filename, quarter, file_number, content, interaction_count):
    """Write one .txt file for a given quarter and part number."""
    filename = f"{base_filename} - {quarter} - {file_number:02d}.txt"
    filepath = os.path.join(output_dir, filename)
    header = build_header(base_filename, quarter, file_number, interaction_count)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header + "\n".join(content))
    print(f"  Wrote {filename} ({interaction_count} interactions)")

def process_csv(csv_path, base_filename):
    """Process CSV file and create formatted text files, grouped by quarter."""

    print(f"\nReading CSV file: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"Found {len(df)} total interactions")

    # Rename columns according to mapping
    df_renamed = df.rename(columns=COLUMN_MAPPING)

    # Select only the columns we want, in the desired order
    df_filtered = df_renamed[OUTPUT_ORDER].copy()

    # Derive quarter for grouping (not written into output)
    df_filtered['_Quarter'] = df_filtered['Date'].apply(get_quarter_label)

    # Create the NBLM Output folder next to the source CSV
    source_dir = os.path.dirname(csv_path) if os.path.dirname(csv_path) else "."
    output_dir = os.path.join(source_dir, "NBLM Output")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Writing output to: {output_dir}")

    # Process each quarter in chronological order
    unique_quarters = sorted(df_filtered['_Quarter'].unique(), key=quarter_sort_key)
    total_files = 0

    for quarter in unique_quarters:
        sub = df_filtered[df_filtered['_Quarter'] == quarter]
        print(f"\n{quarter}: {len(sub)} interactions")

        file_number = 1
        current_content = []
        current_word_count = 0
        current_interaction_count = 0

        for _, row in sub.iterrows():
            interaction_text, word_count = format_interaction(row, OUTPUT_ORDER)

            # If adding this interaction would exceed the limit, flush current file first
            if current_word_count + word_count > WORD_LIMIT_PER_FILE and current_content:
                write_output_file(output_dir, base_filename, quarter, file_number,
                                  current_content, current_interaction_count)
                total_files += 1
                file_number += 1
                current_content = []
                current_word_count = 0
                current_interaction_count = 0

            current_content.append(interaction_text)
            current_word_count += word_count
            current_interaction_count += 1

        # Flush the remaining content for this quarter
        if current_content:
            write_output_file(output_dir, base_filename, quarter, file_number,
                              current_content, current_interaction_count)
            total_files += 1

    print(f"\nDone. Wrote {total_files} file(s) across {len(unique_quarters)} quarter(s).")

if __name__ == "__main__":
    print("=" * 80)
    print("Gartner Interaction Data Formatter for NotebookLM")
    print("=" * 80)

    csv_path = input("\nEnter the path to your CSV file: ").strip().strip('"')
    base_filename = input("Enter a base name for the output files (e.g., 'SAP End User Interactions'): ").strip()

    process_csv(csv_path, base_filename)