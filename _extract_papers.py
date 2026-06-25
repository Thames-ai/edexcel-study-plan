import fitz  # pymupdf
import json, os

base = r"C:\Users\Administrator\Downloads\past paper"
files = []

# Maths papers - in 'mathmatics' subfolder
math_dir = os.path.join(base, 'mathmatics')
for f in sorted(os.listdir(math_dir)):
    if f.endswith('.pdf'):
        files.append(('maths', os.path.join(math_dir, f), f))

# Chemistry papers - in 'chemistry' subfolder
chem_dir = os.path.join(base, 'chemistry')
for f in sorted(os.listdir(chem_dir)):
    if f.endswith('.pdf'):
        files.append(('chemistry', os.path.join(chem_dir, f), f))

results = {}
for cat, path, name in files:
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n---PAGE---\n"
        doc.close()
        results[name] = text
        print(f"OK: {cat}/{name} ({len(text)} chars, {len(text.split('---PAGE---'))} pages)")
    except Exception as e:
        results[name] = ""
        print(f"ERR: {name}: {e}")

with open('_past_papers_raw.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False)

print(f"\nTotal papers: {len(results)}, Total chars: {sum(len(v) for v in results.values())}")
