"""translatesheet - translate a column of an Excel spreadsheet with Google Translate.

Run interactively:

    python translatesheet.py

or pass any of the options on the command line to skip the matching prompt:

    python translatesheet.py data.xlsx --column Text --lang fr --output data_fr.xlsx
"""

import argparse
import os
import sys

import pandas as pd

try:
    from googletrans import LANGCODES, LANGUAGES
except ImportError:  # pragma: no cover - only hit when googletrans is missing
    LANGUAGES, LANGCODES = {}, {}

ERROR_PLACEHOLDER = "[Translation error]"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_path(path):
    """Strip whitespace and surrounding quotes (e.g. from Windows 'Copy as path')."""
    path = path.strip()
    if len(path) >= 2 and path[0] == path[-1] and path[0] in "\"'":
        path = path[1:-1]
    return path


def resolve_language(value):
    """Return a normalised Google Translate language code.

    Accepts a code ('fr', 'zh-CN') or an English language name ('French').
    Raises ValueError if the language is not supported.
    """
    value = value.strip().lower()
    if not value:
        raise ValueError("No target language given.")
    if not LANGUAGES:  # googletrans unavailable; let the API decide
        return value
    if value in LANGUAGES:
        return value
    if value in LANGCODES:
        return LANGCODES[value]
    raise ValueError(
        f"Unsupported language '{value}'. "
        "See https://cloud.google.com/translate/docs/languages for valid codes."
    )


def find_column(df, name):
    """Find a column by name, matching on its string form (headers may be numbers)."""
    for col in df.columns:
        if str(col) == name:
            return col
    for col in df.columns:  # fall back to a case-insensitive match
        if str(col).strip().lower() == name.strip().lower():
            return col
    return None


def default_output_name(input_path, lang_code):
    base = os.path.splitext(os.path.basename(input_path))[0]
    return f"{base}_translated_{lang_code}.xlsx"


def ensure_xlsx(name):
    return name if name.lower().endswith(".xlsx") else name + ".xlsx"


def preview(text, width=30):
    return text if len(text) <= width else text[:width] + "..."


def translate_series(series, translate, log=print):
    """Translate every non-empty value in *series* using *translate(text) -> str*.

    Each distinct value is only sent to the translator once. Blank cells stay
    blank, and failures are replaced with ERROR_PLACEHOLDER.
    Returns (translated_series, error_count).
    """
    cache = {}
    errors = 0

    def convert(value):
        nonlocal errors
        if pd.isna(value):
            return ""
        text = str(value)
        if not text.strip():
            return text
        if text not in cache:
            try:
                result = translate(text)
                log(f"🔄 '{preview(text)}' → '{preview(result)}'")
            except Exception as e:  # network errors, API changes, etc.
                log(f"⚠️ Error translating '{preview(text)}': {e}")
                result = ERROR_PLACEHOLDER
                errors += 1
            cache[text] = result
        return cache[text]

    return series.map(convert), errors


def make_translator(lang_code):
    from googletrans import Translator

    translator = Translator()
    return lambda text: translator.translate(text, dest=lang_code).text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Translate a column of an Excel spreadsheet using Google Translate. "
        "Any option you leave out will be asked for interactively."
    )
    parser.add_argument("file", nargs="?", help="path to the input .xlsx file")
    parser.add_argument("-c", "--column", help="name of the column to translate")
    parser.add_argument("-l", "--lang", help="target language code or name (e.g. cy, fr, French)")
    parser.add_argument("-s", "--sheet", help="sheet to translate (default: the first sheet)")
    parser.add_argument("-o", "--output", help="output file name (default: <input>_translated_<lang>.xlsx)")
    parser.add_argument("-y", "--yes", action="store_true", help="overwrite the output file without asking")
    return parser.parse_args(argv)


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def main(argv=None, translator_factory=make_translator):
    args = parse_args(argv)

    print("🌍 Excel Translation Tool")
    print("=========================")

    # Step 1: File selection
    file_path = clean_path(args.file or ask("📁 Enter the path to your Excel file: "))
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}")
        return 1

    # Step 2: Load workbook (all sheets, so none are lost when saving)
    try:
        sheets = pd.read_excel(file_path, sheet_name=None)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 1
    if not sheets:
        print("❌ The workbook contains no sheets.")
        return 1

    sheet_names = list(sheets)
    sheet_name = args.sheet
    if sheet_name is None and len(sheet_names) > 1:
        print(f"📑 Sheets: {sheet_names}")
        sheet_name = ask(f"📑 Enter the sheet to translate (or press Enter for '{sheet_names[0]}'): ")
    sheet_name = sheet_name or sheet_names[0]
    if sheet_name not in sheets:
        print(f"❌ Sheet '{sheet_name}' not found. Available sheets: {sheet_names}")
        return 1

    df = sheets[sheet_name]
    print(f"✅ Loaded sheet '{sheet_name}' with {len(df)} rows and {len(df.columns)} columns.")

    print(f"📊 Columns: {[str(c) for c in df.columns]}")
    column_name = args.column or ask("📝 Enter the name of the column to translate: ")
    column = find_column(df, column_name)
    if column is None:
        print(f"❌ Column '{column_name}' not found.")
        return 1

    # Step 3: Select language
    lang_input = args.lang or ask(
        "🌐 Enter the target language code (e.g., 'cy' for Welsh, 'fr' for French): "
    )
    try:
        lang_code = resolve_language(lang_input)
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    # Step 4: Choose output file before the (slow) translation step
    default_output = default_output_name(file_path, lang_code)
    output_file = args.output or ask(
        f"💾 Enter a name for the output Excel file (or press Enter to use '{default_output}'): "
    )
    output_file = ensure_xlsx(clean_path(output_file)) if output_file else default_output

    if os.path.abspath(output_file) == os.path.abspath(file_path):
        print("❌ The output file must be different from the input file.")
        return 1
    if os.path.exists(output_file) and not args.yes:
        if ask(f"⚠️ '{output_file}' already exists. Overwrite? [y/N]: ").lower() not in ("y", "yes"):
            print("❎ Cancelled.")
            return 1

    # Step 5: Translate
    try:
        translate = translator_factory(lang_code)
    except Exception as e:
        print(f"❌ Could not start the translator: {e}")
        return 1

    print(f"🔁 Translating column '{column}' to '{lang_code}'...")
    output_column = f"{column}_{lang_code}"
    df[output_column], errors = translate_series(df[column], translate)

    # Step 6: Save every sheet back out
    try:
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for name, sheet in sheets.items():
                sheet.to_excel(writer, sheet_name=name, index=False)
    except Exception as e:
        print(f"❌ Failed to save file: {e}")
        return 1

    if errors:
        print(f"⚠️ {errors} value(s) could not be translated and were marked '{ERROR_PLACEHOLDER}'.")
    print(f"✅ Done! Translated file saved as: {output_file}")
    return 0


if __name__ == "__main__":
    # Emoji output can fail on legacy Windows code pages when output is redirected.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    sys.exit(main())
