# translatesheet

**translatesheet** is a Python-based CLI app that allows you to translate text in any column of an Excel spreadsheet into another language using Google Translate. It's ideal for batch-localizing interface labels, support content, or multilingual datasets.

---

## 🚀 Features

- 📂 Load any Excel (.xlsx) file — all sheets are preserved in the output
- 📑 Choose which sheet and column to translate
- 🌐 Translate into any language using ISO codes (`fr`) or names (`French`)
- 💬 Adds translated text to a new column (`<column>_<lang>`)
- ⚡ Each distinct value is translated only once, so repeated text is fast
- 🔢 Numbers and other non-text cells are handled; blank cells stay blank
- 💾 Lets you name the output file, and asks before overwriting
- 🖥️ Interactive prompts, or pass everything as command-line options for scripting
- ⚠️ Built-in error handling with feedback messages

---

## 🛠️ Requirements

- Python 3.8 – 3.12 (`googletrans==3.1.0a0` does not import on Python 3.13+)
- pip packages (see `requirements.txt`):
  - `pandas`
  - `googletrans==3.1.0a0`
  - `openpyxl`

### 📦 Installation

```bash
pip install -r requirements.txt
```

### 📂 Usage

Interactive:

```bash
python translatesheet.py
```

Follow the prompts:

1. Enter the path to your Excel file (quoted paths are fine).
2. Pick the sheet (only asked if the workbook has more than one).
3. Select the column to translate.
4. Choose the target language (e.g., `cy` for Welsh, `fr` for French).
5. Optionally, name the output file.

Non-interactive — any option you leave out is prompted for:

```bash
python translatesheet.py data.xlsx --column Text --lang cy --output data_cy.xlsx
```

| Option | Description |
| --- | --- |
| `file` | Path to the input `.xlsx` file |
| `-c`, `--column` | Column to translate |
| `-l`, `--lang` | Target language code or name |
| `-s`, `--sheet` | Sheet to translate (default: first sheet) |
| `-o`, `--output` | Output file (default: `<input>_translated_<lang>.xlsx`) |
| `-y`, `--yes` | Overwrite the output file without asking |

### 🧪 Tests

```bash
pip install pytest
pytest
```

The tests use a fake translator, so they don't call Google Translate.

### 🌐 Language Codes

Use standard ISO 639-1 language codes:

- Welsh	`cy`
- French	`fr`
- Spanish	`es`
- German	`de`
- Japanese	`ja`

Full list: https://cloud.google.com/translate/docs/languages

### 🤝 License & Support

MIT License — free to use, adapt, and share.

No support or warranty provided
