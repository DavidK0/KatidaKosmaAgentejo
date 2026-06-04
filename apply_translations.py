import argparse
import json
import re
from pathlib import Path

PATTERN = re.compile(
    r'<(?!(?:Component|TextColor|ActiveColor)\b)[^>]*\bName="([^"]+)"'
    r'|Label="([^"]+)"'
    r'|<Tooltip\b[^>]*\bValue="([^"]+)"'
)

def xml_escape_attr(value: str) -> str:
    return (
        value
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def apply_translations(text: str, translations: dict[str, str]) -> str:
    def replace_match(match: re.Match) -> str:
        original_value = match.group(1) or match.group(2) or match.group(3)

        translated_value = translations.get(original_value)

        # Skip missing, empty, or placeholder translations
        if not translated_value or translated_value == "":
            return match.group(0)

        # Skip cases where the text is just "."
        if original_value == ".":
            return match.group(0)

        translated_value = xml_escape_attr(translated_value)

        if match.group(1):
            return match.group(0).replace(
                f'Name="{original_value}"',
                f'Name="{translated_value}"',
                1
            )

        if match.group(2):
            return match.group(0).replace(
                f'Label="{original_value}"',
                f'Label="{translated_value}"',
                1
            )

        if match.group(3):
            return match.group(0).replace(
                f'Value="{original_value}"',
                f'Value="{translated_value}"',
                1
            )

        return match.group(0)

    return PATTERN.sub(replace_match, text)

parser = argparse.ArgumentParser(
    description="Apply translations from a JSON file to a reference XML file."
)

parser.add_argument(
    "json_file",
    help="Path to the translated JSON file"
)

parser.add_argument(
    "input_xml",
    help="Path to the reference/input XML file"
)

parser.add_argument(
    "output_xml",
    help="Path to the output translated XML file"
)

args = parser.parse_args()

json_path = Path(args.json_file)
input_xml_path = Path(args.input_xml)
output_xml_path = Path(args.output_xml)

translations = json.loads(json_path.read_text(encoding="utf-8"))
text = input_xml_path.read_text(encoding="utf-8")

translated_text = apply_translations(text, translations)

output_xml_path.write_text(translated_text, encoding="utf-8")

applied_count = sum(
    1
    for original, translated in translations.items()
    if translated and translated != "" and original in text
)

print(f"Applied up to {applied_count} translated entries.")
print(f"Saved to: {output_xml_path}")