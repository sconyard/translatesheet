import pandas as pd
from googletrans import Translator
import os

def get_output_filename(default_name):
    """
    Prompt the user to enter a name for the output file.
    If the input is blank, use the default. Ensures .xlsx extension.
    """
    user_input = input(f"💾 Enter a name for the output Excel file (or press Enter to use '{default_name}'): ").strip()
    if not user_input:
        return default_name
    if not user_input.endswith(".xlsx"):
        user_input += ".xlsx"
    return user_input

def main():
    print("🌍 Excel Translation Tool")
    print("=========================")

    # Step 1: File selection
    file_path = input("📁 Enter the path to your Excel file: ").strip()
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # Step 2: Load Excel file
    try:
        df = pd.read_excel(file_path)
        print(f"✅ Loaded file with {len(df)} rows and {len(df.columns)} columns.")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    print(f"📊 Columns: {list(df.columns)}")
    column_name = input("📝 Enter the name of the column to translate: ").strip()
    if column_name not in df.columns:
        print(f"❌ Column '{column_name}' not found.")
        return

    # Step 3: Select language
    lang_code = input("🌐 Enter the target language code (e.g., 'cy' for Welsh, 'fr' for French): ").strip()

    # Step 4: Translate
    translator = Translator()
    output_column = f"{column_name}_{lang_code}"

    def safe_translate(text):
        if pd.isna(text):
            return ''
        try:
            result = translator.translate(text, dest=lang_code)
            print(f"🔄 Translating: '{text[:30]}...' → '{result.text[:30]}...'")
            return result.text
        except Exception as e:
            print(f"⚠️ Error translating '{text}': {e}")
            return "[Translation error]"

    print(f"🔁 Translating column '{column_name}' to language '{lang_code}'...")
    df[output_column] = df[column_name].apply(safe_translate)

    # Step 5: Save file
    default_output = os.path.splitext(os.path.basename(file_path))[0] + f"_translated_{lang_code}.xlsx"
    output_file = get_output_filename(default_output)
    
    try:
        df.to_excel(output_file, index=False)
        print(f"✅ Done! Translated file saved as: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")

if __name__ == "__main__":
    main()
