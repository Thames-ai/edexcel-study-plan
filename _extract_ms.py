import fitz
import json, os

base = r"C:\Users\Administrator\Downloads\past paper"
results = {}

# Math mark schemes
math_dir = os.path.join(base, "mathmatics")
for f in sorted(os.listdir(math_dir)):
    if 'rms' in f.lower() and f.endswith('.pdf'):
        path = os.path.join(math_dir, f)
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n---PAGE---\n"
        doc.close()
        results[f] = text
        print(f"Extracted {f}: {len(text)} chars")

# Chemistry mark schemes
chem_dir = os.path.join(base, "chemistry")
for f in sorted(os.listdir(chem_dir)):
    if 'rms' in f.lower() and f.endswith('.pdf'):
        path = os.path.join(chem_dir, f)
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n---PAGE---\n"
        doc.close()
        results[f] = text
        print(f"Extracted {f}: {len(text)} chars")

with open("_mark_schemes_raw.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False)

print(f"\nTotal mark scheme files extracted: {len(results)}")
