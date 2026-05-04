"""Quick test of synonym expansion."""
from research_trism_v1_claims import _term_in_text, _matched_terms_in_text, _count_trism_terms_in_text

# Test synonym expansion
tests = [
    ("prompt injection", "we detect adversarial prompting attacks", True),
    ("ai transparency", "our explainable ai dashboard", True),
    ("data classification", "automated data categorization tools", True),
    ("confidential computing", "using trusted execution environment", True),
    ("model monitoring", "ml observability platform", True),
    ("hallucination detection", "built-in factuality checking", True),
    ("data masking", "data anonymization capabilities", True),
    ("dlp", "enterprise data loss prevention solution", True),
    ("generative ai", "our genai platform", True),
    ("ai governance", "we sell insurance", False),
]
print("=== Synonym matching tests ===")
for term, text, expected in tests:
    result = _term_in_text(term, text)
    status = "OK" if result == expected else "FAIL"
    print(f"  {status}: '{term}' in '{text[:50]}' = {result}")

# Test _matched_terms_in_text
terms = ["ai governance", "prompt injection", "data masking"]
text = "our artificial intelligence governance and data anonymization tools"
matched = _matched_terms_in_text(terms, text)
print(f"\nMatched terms: {matched}")

# Test improved term counting
old_text = "we provide ai oversight and trustworthy ai with adversarial prompting detection"
count = _count_trism_terms_in_text(old_text)
print(f"TRiSM terms in synonym-rich text: {count} (should be > 0)")

# Compare old vs new counting
plain_text = "ai governance prompt injection data classification"
count2 = _count_trism_terms_in_text(plain_text)
print(f"TRiSM terms in exact-match text: {count2}")

synonym_text = "artificial intelligence governance adversarial prompting data categorization"
count3 = _count_trism_terms_in_text(synonym_text)
print(f"TRiSM terms with ONLY synonyms: {count3} (would be 0 without expansion)")

print("\nAll tests passed!" if all(
    _term_in_text(t, tx) == ex for t, tx, ex in tests
) else "\nSOME TESTS FAILED!")
