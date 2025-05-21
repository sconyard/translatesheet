# translatesheet

**translatesheet** is a Python-based CLI app that allows you to translate text in any column of an Excel spreadsheet into another language using Google Translate. It's ideal for batch-localizing interface labels, support content, or multilingual datasets.

---

## 🚀 Features

- 📂 Load any Excel (.xlsx) file
- 📝 Choose the column to translate
- 🌐 Translate into any target language using ISO codes
- 💬 Adds translated text to a new column
- 💾 Lets you name the output file
- ⚠️ Built-in error handling with feedback messages

---

## 🛠️ Requirements

- Python 3.6+
- pip packages:
  - `pandas`
  - `googletrans==3.1.0a0`
  - `openpyxl`

### 📦 Installation

```bash
pip install pandas openpyxl googletrans==3.1.0a0
```

### 📂 Usage

python translatesheet.py

Follow the interactive prompts:

    Enter the path to your Excel file.

    Select the column to translate.

    Choose the target language (e.g., cy for Welsh, fr for French).

    Optionally, name the output file.

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
