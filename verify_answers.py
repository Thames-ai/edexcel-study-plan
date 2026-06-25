import json
import re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

###############################################################################
# Extract key answers from mark schemes for verification
# Focus on extracting the actual mathematical answers
###############################################################################

def extract_ms_blocks(text, paper_type='pure'):
    blocks = {}
    if paper_type == 'stats':
        positions = []
        for m in re.finditer(r'Qu\s+(\d+)\s*\n\s*Scheme', text):
            positions.append((int(m.group(1)), m.start()))
    else:
        positions = []
        for m in re.finditer(r'Question\s+Scheme\s+Marks\s+AOs', text):
            after = text[m.end():m.end()+50]
            q_match = re.match(r'\s*(\d+)', after)
            if q_match:
                positions.append((int(q_match.group(1)), m.start()))
    
    for i, (q_num, pos) in enumerate(positions):
        if i + 1 < len(positions):
            end_pos = positions[i+1][1]
        else:
            end_pos = len(text)
        blocks[q_num] = text[pos:end_pos]
    
    return blocks

ms_key_map = {
    '9ma0-01-rms-20230817.pdf': ('2023', 'P1', 'pure'),
    '9ma0-01-rms-20240815.pdf': ('2024', 'P1', 'pure'),
    '9ma0-02-rms-20230817.pdf': ('2023', 'P2', 'pure'),
    '9ma0-02-rms-20240815.pdf': ('2024', 'P2', 'pure'),
    '9ma0-31-rms-20230817.pdf': ('2023', 'S1', 'stats'),
    '9ma0-31-rms-20240815.pdf': ('2024', 'S1', 'stats'),
    '9ma0-32-rms-20230817.pdf': ('2023', 'M1', 'mech'),
    '9ma0-32-rms-20240815.pdf': ('2024', 'M1', 'mech'),
}

all_ms = {}
for key, (year, paper, ptype) in ms_key_map.items():
    parse_type = 'stats' if ptype == 'stats' else 'pure'
    blocks = extract_ms_blocks(ms[key], parse_type)
    all_ms[f"{year} {paper}"] = blocks

###############################################################################
# For each maths question, extract the official answer and compare
###############################################################################

def parse_q_id(qid):
    m = re.match(r'pp(\d{2})(p[12]|s1|m1)q(\d+)(\w*)', qid)
    if m:
        return '20' + m.group(1), m.group(2).upper(), int(m.group(3)), m.group(4) or None
    return None, None, None, None

def is_maths(q):
    return any(s in q.get('subject', '').lower() for s in ['pure', 'stats', 'mech'])

# Extract key numerical/final answers from MS blocks
def extract_key_answers(ms_text):
    """Extract key answers that appear in the mark scheme."""
    answers = {}
    
    # Look for underlined/bold answers (in PDF extraction these might appear differently)
    # Look for "awrt" patterns
    awrt_matches = re.findall(r'awrt\s+([\d.]+)', ms_text)
    if awrt_matches:
        answers['awrt'] = awrt_matches
    
    # Look for cao (correct answer only) patterns  
    cao_matches = re.findall(r'cao\s+([\d.]+)', ms_text)
    if cao_matches:
        answers['cao'] = cao_matches
    
    # Look for star-marked answers (A1*, B1*, etc - final answers)
    star_matches = re.findall(r'[AB]1\*\s*[:(]?\s*([^()\n]{3,50})', ms_text)
    if star_matches:
        answers['star'] = star_matches[:5]
    
    # Look for final numerical answers near A1 marks
    a1_matches = re.findall(r'A1\s+\d\.\d\w\s+([^()\n]{3,80})', ms_text)
    if a1_matches:
        answers['A1'] = a1_matches[:5]
    
    return answers

# Review each question
print("=" * 80)
print("QUESTION-BY-QUESTION VERIFICATION")
print("=" * 80)

issues = []

for q in qbank:
    if not (q['id'].startswith('pp23') or q['id'].startswith('pp24')):
        continue
    if not is_maths(q):
        continue
    
    year, paper, qnum, sub = parse_q_id(q['id'])
    if not year:
        continue
    
    ms_label = f"{year} {paper}"
    if ms_label not in all_ms or qnum not in all_ms[ms_label]:
        issues.append(f"MISSING MS: {q['id']} ({ms_label} Q{qnum})")
        continue
    
    ms_block = all_ms[ms_label][qnum]
    key_answers = extract_key_answers(ms_block)
    
    # Clean up MS text for display
    ms_clean = ms_block.replace('---PAGE---', ' ')
    ms_clean = re.sub(r'\s+', ' ', ms_clean).strip()
    
    # Show question info
    print(f"\n{q['id']} | {q['subject']} | {q['paper']}")
    print(f"  Q: {q['text'][:100]}")
    if q['type'] == 'mc':
        for i, opt in enumerate(q['options']):
            marker = " ←" if i == q['answer'] else ""
            print(f"    [{chr(65+i)}] {opt}{marker}")
    print(f"  Current answer: {q['answer']}")
    if key_answers:
        print(f"  Key MS answers: {key_answers}")
    print(f"  MS preview: {ms_clean[:300]}")
    
    # Check for specific known issues
    
    # pp24p1q1: k should be 12, none of options match
    if q['id'] == 'pp24p1q1':
        print("  *** ISSUE: k=12 from MS, but options are k=3/k=-3/k=6/k=-6")
        issues.append(f"WRONG OPTIONS: {q['id']} - MS says k=12 but no matching option")
    
    # pp23p2q11: coefficient of x^2 = 1/8, check which option
    if q['id'] == 'pp23p2q11':
        print("  *** Verify: MS says coefficient of x^2 is p^2/8 = 1/8")
    
    # pp23p2q6: range y>3
    if q['id'] == 'pp23p2q6':
        print("  *** Verify: MS says range y>3")

print(f"\n\n{'='*80}")
print(f"ISSUES FOUND: {len(issues)}")
for issue in issues:
    print(f"  {issue}")
