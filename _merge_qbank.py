"""Merge past paper questions into QBANK in index.html"""
import json, re, sys

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract QBANK JSON
start = content.index('var QBANK=') + len('var QBANK=')
# Find matching brace
depth = 0
end = start
for i in range(start, len(content)):
    if content[i] == '{': depth += 1
    elif content[i] == '}': 
        depth -= 1
        if depth == 0:
            end = i + 1
            break

qbank_str = content[start:end]
qbank = json.loads(qbank_str)
print(f"Loaded QBANK: {sum(len(v2) for v in qbank.values() for v2 in v.values())} existing questions across {sum(len(v) for v in qbank.values())} chapters")

# Load curated past paper questions
with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    pp_qs = json.load(f)

# Add each past paper question to the matching subject/chapter
added = 0
skipped = 0
for q in pp_qs:
    subj = q["subject"]
    ch = q["chapter"]
    
    # Normalize subject name to match QBANK keys
    subj_map = {
        "Chem Y1": "Chem Y1",
        "Pure Y1": "Pure Y1", 
        "Pure Y2": "Pure Y2",
        "Stats Y1": "Stats Y1",
        "Mech Y1": "Mech Y1",
        "Stats Y2": "Stats Y2",
        "Mech Y2": "Mech Y2",
        "Chem Y2": "Chem Y2"
    }
    
    normalized_subj = subj_map.get(subj, subj)
    
    if normalized_subj not in qbank:
        print(f"  SKIP: Subject '{normalized_subj}' not in QBANK (from '{subj}')")
        skipped += 1
        continue
    
    if ch not in qbank[normalized_subj]:
        # Try fuzzy match - find chapter that starts with same prefix
        matched = False
        for existing_ch in qbank[normalized_subj]:
            if existing_ch.startswith(ch[:6]) or ch.startswith(existing_ch[:6]):
                ch = existing_ch
                matched = True
                break
        if not matched:
            print(f"  SKIP: Chapter '{ch}' not in {normalized_subj} (available: {list(qbank[normalized_subj].keys())})")
            skipped += 1
            continue
    
    # Check for duplicate id
    existing_ids = {eq["id"] for eq in qbank[normalized_subj][ch]}
    if q["id"] in existing_ids:
        print(f"  DUP: {q['id']} already exists in {normalized_subj}/{ch}")
        skipped += 1
        continue
    
    # Add the question (keep paper field for badge display)
    qbank[normalized_subj][ch].append(q)
    added += 1

print(f"\nAdded {added} past paper questions, skipped {skipped}")

# Count totals
total = sum(len(v2) for v in qbank.values() for v2 in v.values())
pp_count = sum(1 for v in qbank.values() for v2 in v.values() for q in v2 if q.get("paper"))
print(f"Total QBANK questions: {total} ({pp_count} from past papers)")

# Replace QBANK in index.html
new_qbank_str = json.dumps(qbank, ensure_ascii=False, indent=None)
# Minify slightly - remove extra spaces after colons/commas for compactness
new_qbank_str = re.sub(r': ', ':', new_qbank_str)
new_qbank_str = re.sub(r', ', ',', new_qbank_str)

new_content = content[:start] + new_qbank_str + content[end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Written updated index.html (QBANK section: {len(new_qbank_str)} chars)")

# Verify by re-parsing using the same brace-matching approach
with open('index.html', 'r', encoding='utf-8') as f:
    verify = f.read()
v_start = verify.index('var QBANK=') + len('var QBANK=')
v_depth = 0
v_end = v_start
for i in range(v_start, len(verify)):
    if verify[i] == '{': v_depth += 1
    elif verify[i] == '}': 
        v_depth -= 1
        if v_depth == 0:
            v_end = i + 1
            break
verify_bank = json.loads(verify[v_start:v_end])
v_total = sum(len(v2) for v in verify_bank.values() for v2 in v.values())
print(f"Verified: {v_total} questions in QBANK")
