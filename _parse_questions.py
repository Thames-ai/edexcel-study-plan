import json, re, os

with open('_past_papers_raw.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

# Parse questions from each paper
# Maths papers: questions start with "1.\t", "2.\t", etc.
# Chemistry papers: questions start with "1\t", "2\t", etc.  
# Each question ends at the next question number or end of paper

def extract_questions(text, paper_name):
    """Extract individual questions from a paper's text."""
    # Remove page headers/footers
    text = re.sub(r'\*P\d+A\d+\*\n?', '', text)
    text = re.sub(r'Turn over\s*', '', text)
    text = re.sub(r'DO NOT WRITE IN THIS AREA.*?(?=\n)', '', text, flags=re.DOTALL)
    text = re.sub(r'_{5,}', '', text)  # Remove answer lines
    text = re.sub(r'_____________________________________________________________________________________', '', text)
    
    # Find question boundaries - match "1." or "1\t" at start of line
    # Questions are numbered 1-15 for P1/P2, 1-6 for S1/M1, 1-20ish for chemistry
    q_pattern = re.compile(r'(?:^|\n)\s*(\d{1,2})[\.\t]\s')
    
    matches = list(q_pattern.finditer(text))
    questions = []
    
    for i, m in enumerate(matches):
        q_num = int(m.group(1))
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        q_text = text[start:end].strip()
        
        # Clean up
        q_text = re.sub(r'\n{3,}', '\n\n', q_text)
        q_text = re.sub(r'---PAGE---', '', q_text)
        q_text = q_text.strip()
        
        if len(q_text) > 20:  # Skip empty/short matches
            questions.append({
                'number': q_num,
                'text': q_text,
                'paper': paper_name
            })
    
    return questions

all_questions = {}

for paper_name, text in raw.items():
    qs = extract_questions(text, paper_name)
    all_questions[paper_name] = qs
    print(f"{paper_name}: {len(qs)} questions extracted")
    for q in qs:
        preview = q['text'][:80].replace('\n', ' ')
        print(f"  Q{q['number']}: {preview}...")

with open('_questions_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in all_questions.values())
print(f"\nTotal questions extracted: {total}")
