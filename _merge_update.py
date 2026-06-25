"""Merge updated past paper questions (with mscheme + corrected answers) into QBANK in index.html"""
import json, re

with open('index.html', 'r', encoding='utf-8', errors='surrogatepass') as f:
    content = f.read()

# Extract QBANK JSON using brace-matching
start = content.index('var QBANK=') + len('var QBANK=')
depth = 0
end = start
for i in range(start, len(content)):
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    if depth == 0:
        end = i + 1
        break

qbank_json = content[start:end]
qbank = json.loads(qbank_json)
print(f"Loaded QBANK: {sum(len(v) for vs in qbank.values() for v in vs.values())} questions")

# Load updated curated questions
with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    pp_questions = json.load(f)

# Build lookup by ID
pp_by_id = {q['id']: q for q in pp_questions}

# Update existing questions in QBANK
updated = 0
for subj, chapters in qbank.items():
    for chapter, questions in chapters.items():
        for i, q in enumerate(questions):
            if q['id'] in pp_by_id:
                pp_q = pp_by_id[q['id']]
                # Update relevant fields from the curated version
                for field in ['answer', 'explain', 'mscheme', 'paper', 'marks', 'improve', 'text', 'options']:
                    if field in pp_q and pp_q[field]:
                        questions[i][field] = pp_q[field]
                updated += 1

print(f"Updated {updated} existing past paper questions with latest data")

# Write back
new_qbank_json = json.dumps(qbank, ensure_ascii=False, indent=0)
# Minimize size
new_qbank_json = re.sub(r'\n\s*', ' ', new_qbank_json)
new_qbank_json = re.sub(r'(?<=[\[{,]) | (?=[\]},])', '', new_qbank_json)

content = content[:start] + new_qbank_json + content[end:]

with open('index.html', 'w', encoding='utf-8', errors='surrogatepass') as f:
    f.write(content)

total = sum(len(v) for vs in qbank.values() for v in vs.values())
print(f"Total QBANK questions: {total}")
print("Saved index.html")
