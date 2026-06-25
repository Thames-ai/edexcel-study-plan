import json
import re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

###############################################################################
# STEP 1: Parse all maths mark schemes into question-level blocks
###############################################################################

def extract_question_blocks(text, paper_type='pure'):
    """Extract individual question blocks from mark scheme text."""
    blocks = {}
    
    if paper_type == 'stats':
        # Stats uses "Qu N" format
        positions = []
        for m in re.finditer(r'Qu\s+(\d+)\s*\n\s*Scheme', text):
            positions.append((int(m.group(1)), m.start()))
    else:
        # Pure/Mech use "Question  Scheme  Marks  AOs" format
        positions = []
        for m in re.finditer(r'Question\s+Scheme\s+Marks\s+AOs', text):
            # The question number follows after AOs
            after = text[m.end():m.end()+30]
            q_match = re.match(r'\s*(\d+)', after)
            if q_match:
                positions.append((int(q_match.group(1)), m.start()))
    
    for i, (q_num, pos) in enumerate(positions):
        if i + 1 < len(positions):
            end_pos = positions[i+1][1]
        else:
            end_pos = len(text)
        
        chunk = text[pos:end_pos]
        # Clean up
        chunk_clean = chunk.replace('---PAGE---', ' ')
        chunk_clean = re.sub(r'\r\n', '\n', chunk_clean)
        chunk_clean = re.sub(r' +', ' ', chunk_clean)
        
        blocks[q_num] = chunk_clean
    
    return blocks

# Map mark scheme keys
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
    blocks = extract_question_blocks(ms[key], ptype)
    label = f"{year} {paper}"
    all_ms[label] = blocks
    print(f"{label}: {len(blocks)} questions - {list(blocks.keys())}")

###############################################################################
# STEP 2: Map qbank questions to mark scheme question numbers
###############################################################################

# Parse question IDs to extract paper and question number
def parse_q_id(q):
    """Parse question ID like pp23p1q1 -> year=2023, paper=P1, qnum=1"""
    qid = q['id']
    m = re.match(r'pp(\d{2})(p[12]|s1|m1)q(\d+)', qid)
    if m:
        year_short = m.group(1)
        year = '20' + year_short
        paper_code = m.group(2).upper()
        q_num = int(m.group(3))
        return year, paper_code, q_num
    return None, None, None

# Identify maths questions (Pure, Stats, Mech)
def is_maths_question(q):
    subject = q.get('subject', '').lower()
    return any(s in subject for s in ['pure', 'stats', 'mech'])

###############################################################################
# STEP 3: Extract clean mark scheme answer text from blocks
###############################################################################

def extract_ms_answer(block_text):
    """Extract the key answer content from a mark scheme block, removing boilerplate."""
    # Remove the header part "Question Scheme Marks AOs N"
    text = re.sub(r'Question\s+Scheme\s+Marks\s+AOs\s*\d+', '', block_text)
    text = re.sub(r'Qu\s+\d+\s*Scheme\s*Marks\s*AO', '', text)
    
    # Extract lines that contain actual mathematical content or mark annotations
    lines = text.split('\n')
    content_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip purely structural lines
        if line in ['Scheme', 'Marks', 'AOs', 'Notes', 'Question']:
            continue
        content_lines.append(line)
    
    return ' '.join(content_lines)

###############################################################################
# STEP 4: Main matching and update logic
###############################################################################

changes = []
answer_corrections = []

for q in qbank:
    if not (q['id'].startswith('pp23') or q['id'].startswith('pp24')):
        continue
    
    if not is_maths_question(q):
        continue
    
    year, paper_code, q_num = parse_q_id(q)
    if not year:
        continue
    
    ms_label = f"{year} {paper_code}"
    
    if ms_label not in all_ms:
        print(f"WARNING: No mark scheme for {ms_label}")
        continue
    
    if q_num not in all_ms[ms_label]:
        print(f"WARNING: No Q{q_num} in {ms_label} mark scheme (have: {list(all_ms[ms_label].keys())})")
        continue
    
    ms_block = all_ms[ms_label][q_num]
    ms_answer = extract_ms_answer(ms_block)
    
    # Only update if we got meaningful content
    if len(ms_answer) > 20:
        old_explain = q.get('explain', '')
        q['explain'] = ms_answer
        changes.append({
            'id': q['id'],
            'paper': ms_label,
            'q_num': q_num,
            'old_explain_len': len(old_explain),
            'new_explain_len': len(ms_answer),
            'new_explain_preview': ms_answer[:200]
        })

###############################################################################
# STEP 5: Write back
###############################################################################

with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)

print(f"\n=== SUMMARY ===")
print(f"Total maths questions updated: {len(changes)}")
for c in changes:
    print(f"  {c['id']} ({c['paper']} Q{c['q_num']}): {c['old_explain_len']} -> {c['new_explain_len']} chars")
    print(f"    Preview: {c['new_explain_preview'][:150]}...")
