"""Extract mark scheme answers and match them to curated past paper questions.
For MC questions: extract "The only correct answer is X" 
For all questions: extract the answer text and additional guidance."""
import json, re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms_raw = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Parse mark schemes into a lookup: {(paper_code, q_number): ms_text}
# Paper code mapping:
# 8ch0-01 = Chem AS Paper 1 Core = "C1 Core"
# 8ch0-02 = Chem AS Paper 2 Core = "C2 Core"  
# 9ch0-01 = Chem A-Level Paper 1 Adv = "C1 Adv"
# 9ch0-02 = Chem A-Level Paper 2 Adv = "C2 Adv"
# 9ma0-01 = Maths Pure 1 = "P1"
# 9ma0-02 = Maths Pure 2 = "P2"
# 9ma0-31 = Maths Stats = "S1"
# 9ma0-32 = Maths Mech = "M1"

ms_lookup = {}

def extract_ms_answers(text, paper_code):
    """Parse mark scheme text into question-answer pairs."""
    # Split into question blocks using "Question Number" headers
    # Pattern: question number like 1(a), 1(b)(i), 2(a)(iv), etc.
    # Find all question blocks
    blocks = re.split(r'(?:Question\s*Number|Question)', text)
    
    for block in blocks[1:]:  # skip first (preamble)
        # Find the question number
        q_match = re.match(r'\s*(\d+\([a-z]\)(?:\([ivx]+\))?)', block.strip())
        if not q_match:
            # Try simpler pattern
            q_match = re.match(r'\s*(\d+[a-z]?(?:\([ivx]+\))?)', block.strip())
        if not q_match:
            continue
        
        q_num = q_match.group(1)
        
        # Extract "The only correct answer is X" for MC questions
        mc_match = re.search(r'[Tt]he (?:only )?correct answer is ([A-D])', block)
        
        # Extract answer text (between "Answer" and "Additional Guidance" or "Mark")
        answer_match = re.search(r'Answer\s*\n?\s*(.*?)(?=Additional Guidance|Mark\s*$)', block, re.DOTALL)
        
        # Extract marks
        marks_match = re.search(r'\((\d+)\)\s*$', block.strip())
        marks = int(marks_match.group(1)) if marks_match else None
        
        # Build ms text
        ms_text = ""
        if mc_match:
            ms_text = f"Correct answer is {mc_match.group(1)}. "
            # Also extract why wrong answers are wrong
            wrong_reasons = re.findall(r'([A-D]) is not correct because (.+?)(?=\n\n|\r\n\r\n|[A-D] is not|$)', block, re.DOTALL)
            for letter, reason in wrong_reasons:
                ms_text += f"{letter}: {reason.strip()}. "
        elif answer_match:
            ans = answer_match.group(1).strip()
            # Clean up whitespace
            ans = re.sub(r'\s+', ' ', ans)
            ms_text = ans
        
        if ms_text:
            key = (paper_code, q_num)
            ms_lookup[key] = ms_text.strip()

# Process chemistry mark schemes
chem_papers = [
    ('8ch0-01-rms-20230817.pdf', '2023 C1 Core'),
    ('8ch0-01-rms-20240815.pdf', '2024 C1 Core'),
    ('8ch0-02-rms-20230817.pdf', '2023 C2 Core'),
    ('8ch0-02-rms-20240815.pdf', '2024 C2 Core'),
    ('9ch0-01-rms-20230817.pdf', '2023 C1 Adv'),
    ('9ch0-01-rms-20240815.pdf', '2024 C1 Adv'),
    ('9ch0-02-rms-20230817.pdf', '2023 C2 Adv'),
    ('9ch0-02-rms-20240815.pdf', '2024 C2 Adv'),
]

for filename, paper_code in chem_papers:
    if filename in ms_raw:
        extract_ms_answers(ms_raw[filename], paper_code)
        print(f"Extracted {paper_code}: {sum(1 for k,v in ms_lookup.items() if k[0]==paper_code)} answers")

# Process maths mark schemes
maths_papers = [
    ('9ma0-01-rms-20230817.pdf', '2023 P1'),
    ('9ma0-01-rms-20240815.pdf', '2024 P1'),
    ('9ma0-02-rms-20230817.pdf', '2023 P2'),
    ('9ma0-02-rms-20240815.pdf', '2024 P2'),
    ('9ma0-31-rms-20230817.pdf', '2023 S1'),
    ('9ma0-31-rms-20240815.pdf', '2024 S1'),
    ('9ma0-32-rms-20230817.pdf', '2023 M1'),
    ('9ma0-32-rms-20240815.pdf', '2024 M1'),
]

for filename, paper_code in maths_papers:
    if filename in ms_raw:
        extract_ms_answers(ms_raw[filename], paper_code)
        print(f"Extracted {paper_code}: {sum(1 for k,v in ms_lookup.items() if k[0]==paper_code)} answers")

print(f"\nTotal mark scheme answers extracted: {len(ms_lookup)}")

# Now match to curated questions
# Question IDs follow patterns like:
# pp23c1cq1 = paper 2023, chem paper 1 core, question 1
# pp24p1q5 = paper 2024, pure paper 1, question 5
# pp23s1q3 = paper 2023, stats paper 1, question 3
matched = 0
for q in questions:
    if not q.get('paper'):
        continue
    
    # Parse question ID to figure out which mark scheme to look up
    qid = q['id']
    paper = q['paper']
    
    # Try to extract question number from ID
    # Pattern: pp{year}{paper_code}q{number}{optional_sub}
    m = re.match(r'pp(\d{2})([a-z]+)(\d+)q(\d+)([a-z]?)', qid)
    if not m:
        # Try alternate patterns
        m = re.match(r'pp(\d{2})([cpms])(\d)([ca]?)(\d+)q?(\d+)([a-z]?)', qid)
    
    if m:
        # Build the question number for mark scheme lookup
        # e.g., "1(a)", "2(b)(i)"
        q_num_from_id = re.search(r'q(\d+)([a-z]?)(\d*)', qid)
        if q_num_from_id:
            base = q_num_from_id.group(1)
            sub = q_num_from_id.group(2)
            q_num = f"{base}({sub})" if sub else base
            
            # Look up in ms_lookup
            key = (paper, q_num)
            alt_keys = [
                (paper, base),
                (paper, f"Q{base}"),
            ]
            
            ms_text = ms_lookup.get(key)
            if not ms_text:
                for ak in alt_keys:
                    ms_text = ms_lookup.get(ak)
                    if ms_text:
                        break
            
            if ms_text:
                q['mscheme'] = ms_text
                matched += 1

print(f"Matched {matched} questions to mark scheme answers")

# Also try a simpler matching: for each question, search the mark scheme text
# for the question text or number
for q in questions:
    if q.get('mscheme') or not q.get('paper'):
        continue
    
    paper = q['paper']
    # Find the corresponding mark scheme file
    year = '2023' if '23' in paper or '2023' in paper else '2024'
    
    # Map paper code to filename
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
    
    ms_file = paper_to_file.get(paper)
    if ms_file and ms_file in ms_raw:
        # Extract question number from ID
        q_num_match = re.search(r'q(\d+)', q['id'])
        if q_num_match:
            q_num = q_num_match.group(1)
            ms_text = ms_raw[ms_file]
            # Search for this question number in the mark scheme
            # Find the section starting with this question number
            patterns = [
                re.compile(rf'\b{q_num}\b\s*[\(（]', re.IGNORECASE),
                re.compile(rf'Question\s*(?:Number\s*)?\b{q_num}\b', re.IGNORECASE),
            ]
            for pat in patterns:
                matches = list(pat.finditer(ms_text))
                if matches:
                    # Extract text from this question
                    start = matches[0].start()
                    # Find next question or end
                    end = len(ms_text)
                    next_q = re.search(rf'\b{int(q_num)+1}\b\s*[\(（]', ms_text[start+10:])
                    if next_q:
                        end = start + 10 + next_q.start()
                    section = ms_text[start:end]
                    
                    # Check for MC answer
                    mc = re.search(r'[Tt]he (?:only )?correct answer is ([A-D])', section)
                    if mc:
                        q['mscheme'] = f"Mark scheme: Correct answer is {mc.group(1)}"
                        matched += 1
                        break
                    else:
                        # Extract answer text
                        ans_m = re.search(r'Answer\s*(.*?)(?=Additional Guidance|Mark\s*\(\d)', section, re.DOTALL)
                        if ans_m:
                            ans = re.sub(r'\s+', ' ', ans_m.group(1)).strip()[:200]
                            q['mscheme'] = f"Mark scheme: {ans}"
                            matched += 1
                            break

print(f"After extended matching: {matched} questions with mscheme")
print(f"Questions with paper field: {sum(1 for q in questions if q.get('paper'))}")

# Save updated questions
with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print("Saved updated questions")
