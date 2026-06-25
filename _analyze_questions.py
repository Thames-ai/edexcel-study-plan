import json, re

with open('_questions_extracted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Analyze question types - find MC questions (with A/B/C/D options)
mc_questions = []
written_questions = []

for paper_name, questions in data.items():
    for q in questions:
        text = q['text']
        # Check for multiple choice options - look for A\t B\t C\t D pattern or A\n B\n etc
        has_options = bool(re.search(r'\nA[\t ]|\nB[\t ]|\nA\s{2,}', text))
        # Also check for "cross in a box" style MC
        is_mc = has_options or 'cross in a box' in text.lower()
        
        if is_mc:
            mc_questions.append((paper_name, q))
        else:
            written_questions.append((paper_name, q))

print(f"Multiple choice questions: {len(mc_questions)}")
print(f"Written/long-form questions: {len(written_questions)}")

print("\n=== MC Questions ===")
for paper, q in mc_questions[:20]:
    preview = q['text'][:150].replace('\n', ' ')
    print(f"  {paper} Q{q['number']}: {preview}...")

print(f"\n... and {len(mc_questions)-20} more MC questions")

# For chemistry papers specifically check the core papers (they tend to have more MC)
print("\n=== Chemistry Core MC analysis ===")
chem_mc = [q for p, q in mc_questions if 'chemistry' in p.lower() or 'core' in p.lower()]
print(f"Chemistry MC: {len(chem_mc)}")

# For maths - MC is less common, mostly written answers
maths_mc = [q for p, q in mc_questions if 'p1' in p.lower() or 'p2' in p.lower() or 'm1' in p.lower() or 's1' in p.lower()]
print(f"Maths MC: {len(maths_mc)}")
