#!/usr/bin/env python3
import json
import re

def clean_vendor_json():
    # Read the file
    with open('vendor3-3.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Step 1: Analyzing file structure...")
    print(f"  File size: {len(content)} characters")
    
    # Remove all the labeled part keys and their opening quotes
    # Pattern: "dfir_market_mapping_2026_part_XX":"  -> ""
    print("Step 2: Removing labeled part markers...")
    pattern = r'"dfir_market_mapping_2026_part_\d+(?:_to_\d+)?":"'
    content_cleaned = re.sub(pattern, '', content)
    removed_count = len(re.findall(pattern, content))
    print(f"  Removed {removed_count} labeled parts")
    
    # Extract vendor objects by finding patterns { "vendor": ... }
    print("Step 3: Extracting vendor objects...")
    
    # Find all vendor objects in the cleaned content
    # Look for opening { followed by "vendor":
    vendors = []
    
    # Use regex to find all vendor object patterns
    vendor_pattern = r'\{\s*"vendor"\s*:'
    matches = list(re.finditer(vendor_pattern, content_cleaned))
    print(f"  Found {len(matches)} potential vendor objects")
    
    # Extract each vendor object
    for match in matches:
        start = match.start()
        # Find the matching closing brace
        brace_count = 1
        pos = start + 1
        
        while pos < len(content_cleaned) and brace_count > 0:
            if content_cleaned[pos] == '{':
                brace_count += 1
            elif content_cleaned[pos] == '}':
                brace_count -= 1
            pos += 1
        
        vendor_str = content_cleaned[start:pos]
        try:
            vendor_obj = json.loads(vendor_str)
            vendors.append(vendor_obj)
        except json.JSONDecodeError as e:
            print(f"  Warning: Could not parse vendor object at position {start}: {e}")
    
    # Validate result
    print(f"\nStep 4: Validating data...")
    print(f"  Total vendors extracted: {len(vendors)}")
    
    if len(vendors) > 0:
        first = vendors[0]
        if isinstance(first, dict):
            print(f"  First vendor: {first.get('vendor', 'N/A')}")
            print(f"  Sample fields: {list(first.keys())[:5]}")
    
    if len(vendors) == 0:
        print("  ✗ No vendors found!")
        return False
    
    # Save the cleaned data as JSON array
    print(f"\nStep 5: Saving cleaned JSON...")
    with open('vendor3-3.json', 'w', encoding='utf-8') as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Saved {len(vendors)} vendors")
    return True

if __name__ == '__main__':
    try:
        success = clean_vendor_json()
        if success:
            print("\n✅ JSON cleaning complete!")
        else:
            print("\n❌ JSON cleaning failed")
            exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
