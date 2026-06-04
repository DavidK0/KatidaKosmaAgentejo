import argparse
import json
import re
from pathlib import Path

PATTERN = re.compile(
    r'<(?!(?:Component|TextColor|ActiveColor)\b)[^>]*\bName="([^"]+)"'
    r'|Label="([^"]+)"'
    r'|<Tooltip\b[^>]*\bValue="([^"]+)"'
)

def extract_strings(text: str) -> set[str]:
    results = set()

    for name_match, label_match, tooltip_match in PATTERN.findall(text):
        value = name_match or label_match or tooltip_match
        if value:
            results.add(value)

    return results

parser = argparse.ArgumentParser(
    description="Extract Name/Label attribute values from a text file."
)

parser.add_argument(
    "input_file",
    help="Path to the input text/XML file"
)

parser.add_argument(
    "output_file",
    help="Path to the output JSON file"
)

args = parser.parse_args()

input_path = Path(args.input_file)
output_path = Path(args.output_file)

# Read input file
text = input_path.read_text(encoding="utf-8")

# Extract unique values
results = sorted(extract_strings(text))

# Skip cases where the text is just "."
results = [value for value in results if value != "."]

results_all_caps = {value: "" for value in results if value.isupper()}
results_all_caps = {k: v for k, v in sorted(results_all_caps.items(), key=lambda item: len(item[0]))}
results_not_all_caps = {value: "" for value in results if not value.isupper()}
results_not_all_caps = {k: v for k, v in sorted(results_not_all_caps.items(), key=lambda item: len(item[0]))}
results = {**results_all_caps, **results_not_all_caps}

# Save as JSON
output_path.write_text(
    json.dumps(results, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Found {len(results)} unique entries.")
print(f"Saved to: {output_path}")