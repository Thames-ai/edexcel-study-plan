"""Better mark scheme parser - find each question block and extract its answer."""
import json, re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms_raw = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Paper to filename mapping
paper_to_file = {
    '2023 C1 Core': '8ch0-01-rms-20230817.pdf',
    '2024 C1 Core': '8ch0-01-rms-20240815.pdf', 
    '2023 C2 Core': '8ch0-02-rms-20230817.pdf',
    '2024 C2 Core': '8ch0-02-rms-20240815.pdf',
    '2023 C1 Adv': '9ch0-01-rms-20230817.pdf',
    '2024 C1 Adv': '9ch0-01-rms-20240815.pdf',
    '2023 C2 Adv': '9ch0-02-rms-20230817.pdf',
    '2024 C2 Adv': '9ch0-02-rms-20240815.pdf',
    '2023 P1': '9ma0-01-rms-20230817.pdf',
    '2024 P1': '9ma0-01-rms-20240815.pdf',
    '2023 P2': '9ma0-02-rms-20230817.pdf',
    '2024 P2': '9ma0-02-rms-20240815.pdf',
    '2023 S1': '9ma0-31-rms-20230817.pdf',
    '2024 S1': '9ma0-31-rms-20240815.pdf',
    '2023 M1': '9ma0-32-rms-20230817.pdf',
    '2024 M1': '9ma0-32-rms-20240815.pdf',
}

def parse_mark_scheme(text):
    """Parse mark scheme text into a dict of question_number -> answer text."""
    results = {}
    
    # Split by page markers and question headers
    # The format is typically:
    # Question Number | Answer | Additional Guidance | Mark
    # 1(a)            | ...    | ...                 | (1)
    
    # Find all question blocks using a more robust approach
    # Look for numbered items like "1(a)", "1(b)(i)", "2", "3(a)" etc.
    q_pattern = re.compile(r'(\d+)\s*\(([a-z])\)\s*(?:\(([ivx]+)\))?\s*')
    
    # Also find standalone question numbers like "Question 1"
    standalone_q = re.compile(r'(?:Question\s+)?(\d+)\s*(?:\(|$|\n)', re.IGNORECASE)
    
    # Find MC answers: "The only correct answer is X"
    mc_matches = list(re.finditer(r'(\d+)\s*\([a-z]\)\s*.*?[Tt]he (?:only )?correct answer is ([A-D])', text, re.DOTALL))
    
    # Alternative: find by MC answer directly
    mc_direct = list(re.finditer(r'[Tt]he (?:only )?correct answer is ([A-D])', text))
    
    # Find the question number preceding each MC answer
    for i, match in enumerate(mc_direct):
        # Look backward from this position to find the question number
        pos = match.start()
        # Search backwards for a question number
        before = text[max(0, pos-500):pos]
        q_num_m = re.search(r'(\d+)\s*\(([a-z])\)\s*(?:\(([ivx]+)\))?\s*$', before.strip())
        if not q_num_m:
            q_num_m = re.search(r'(\d+)\s*$()', before.strip())
        if q_num_m:
            q_num = q_num_m.group(1)
            sub = q_num_m.group(2) if len(q_num_m.groups()) > 1 else ''
            sub2 = q_num_m.group(3) if len(q_num_m.groups()) > 2 else ''
            
            key_parts = q_num
            if sub:
                key_parts += f"({sub})"
            if sub2:
                key_parts += f"({sub2})"
            
            answer_letter = match.group(1)
            
            # Also capture why wrong answers are wrong
            after_text = text[match.end():match.end()+500]
            wrong_parts = re.findall(r'([A-D]) is not correct because (.+?)(?=\s*[A-D] is not|\n\n|\r\n\r\n|$)', after_text, re.DOTALL)
            wrong_text = ""
            for letter, reason in wrong_parts:
                wrong_text += f" {letter}: {reason.strip()}."
            
            results[key_parts] = f"Correct answer is {answer_letter}.{wrong_text}"
    
    # For non-MC questions, extract answer text blocks
    # Split text into sections by question number
    sections = re.split(r'(?=(?:Question\s*)?\d+\s*\([a-z]\))', text)
    
    for section in sections:
        # Check if this section has a question number
        q_m = re.match(r'(?:Question\s*)?(\d+\s*\([a-z]\)(?:\s*\([ivx]+\))?)', section.strip())
        if q_m:
            q_key = q_m.group(1).replace(' ', '')
            # Already have MC answer?
            if q_key in results:
                continue
            # Extract answer text
            ans_m = re.search(r'(?:Answer|An answer that makes reference to)\s*(.*?)(?=Additional Guidance|Mark\s*\(\d|$)', section, re.DOTALL)
            if ans_m:
                ans_text = re.sub(r'\s+', ' ', ans_m.group(1)).strip()
                if len(ans_text) > 10 and len(ans_text) < 500:
                    results[q_key] = ans_text
    
    return results

# Parse each mark scheme
all_ms = {}
for paper, filename in paper_to_file.items():
    if filename in ms_raw:
        ms = parse_mark_scheme(ms_raw[filename])
        all_ms[paper] = ms
        print(f"{paper}: {len(ms)} answers parsed")
        # Show first few
        for k, v in list(ms.items())[:3]:
            print(f"  {k}: {v[:80]}")

print(f"\nTotal papers with answers: {len(all_ms)}")

# Now match to questions
matched = 0
for q in questions:
    if not q.get('paper'):
        continue
    
    paper = q['paper']
    if paper not in all_ms:
        continue
    
    qid = q['id']
    # Extract question number from ID
    # Pattern: pp23c1cq1 -> question 1
    # Pattern: pp23c1cq1b -> question 1(b)
    # Pattern: pp24p1q5 -> question 5
    # Pattern: pp23s1q3a -> question 3(a)
    
    # Extract the q-part
    q_part = re.search(r'q(\d+)([a-z]?)(\d*)', qid)
    if not q_part:
        continue
    
    q_num = q_part.group(1)
    q_sub = q_part.group(2)
    
    # Build lookup key
    if q_sub:
        lookup_key = f"{q_num}({q_sub})"
    else:
        lookup_key = q_num
    
    # Try to find matching mark scheme entry
    ms_text = all_ms[paper].get(lookup_key)
    if not ms_text:
        # Try without sub-part
        ms_text = all_ms[paper].get(q_num)
    if not ms_text:
        # Try with different formatting
        for key in all_ms[paper]:
            if key.startswith(q_num):
                ms_text = all_ms[paper][key]
                break
    
    if ms_text:
        q['mscheme'] = ms_text
        matched += 1

print(f"\nMatched {matched} questions to mark scheme answers")

# For questions that still don't have mscheme, let's do a more aggressive text search
for q in questions:
    if q.get('mscheme') or not q.get('paper'):
        continue
    
    paper = q['paper']
    filename = paper_to_file.get(paper)
    if not filename or filename not in ms_raw:
        continue
    
    ms_text = ms_raw[filename]
    
    # Search for the question number  
    q_part = re.search(r'q(\d+)', q['id'])
    if not q_part:
        continue
    q_num = q_part.group(1)
    
    # Find all occurrences of this question number followed by a sub-part
    q_pattern = re.compile(rf'\b{q_num}\s*\([a-z]\)')
    matches = list(q_pattern.finditer(ms_text))
    
    if matches:
        # Use the first match (or try to match the sub-part)
        start = matches[0].start()
        end = min(start + 1500, len(ms_text))
        section = ms_text[start:end]
        
        # Check for MC answer
        mc = re.search(r'[Tt]he (?:only )?correct answer is ([A-D])', section)
        if mc:
            q['mscheme'] = f"Mark scheme: Correct answer is {mc.group(1)}"
            matched += 1
            continue
        
        # Extract answer block
        ans_match = re.search(r'(?:Answer|An answer that makes reference to)[^.]*[.:]\s*(.*?)(?=Additional Guidance|Mark\s*\(\d|$)', section, re.DOTALL)
        if ans_match:
            ans = re.sub(r'\s+', ' ', ans_match.group(1)).strip()[:300]
            if len(ans) > 5:
                q['mscheme'] = f"Mark scheme: {ans}"
                matched += 1

print(f"After aggressive matching: {matched} questions with mscheme")

# Save
with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print("Saved")
