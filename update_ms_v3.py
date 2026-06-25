import json
import re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

###############################################################################
# Parse mark schemes by question number
# All 9ma0 papers use "Question  Scheme  Marks  AOs" format 
# (except Stats papers which use "Qu N  Scheme  Marks  AO" format)
###############################################################################

def extract_ms_blocks(text, paper_type='pure'):
    """Extract question blocks from mark scheme text."""
    blocks = {}
    
    if paper_type == 'stats':
        # Stats uses "Qu N" format
        positions = []
        for m in re.finditer(r'Qu\s+(\d+)\s*\n\s*Scheme', text):
            positions.append((int(m.group(1)), m.start()))
    else:
        # Pure and Mechanics both use "Question  Scheme  Marks  AOs" format
        positions = []
        for m in re.finditer(r'Question\s+Scheme\s+Marks\s+AOs', text):
            after = text[m.end():m.end()+50]
            # Question number follows - could be "1" or "1(a)" etc
            q_match = re.match(r'\s*(\d+)', after)
            if q_match:
                positions.append((int(q_match.group(1)), m.start()))
    
    for i, (q_num, pos) in enumerate(positions):
        if i + 1 < len(positions):
            end_pos = positions[i+1][1]
        else:
            end_pos = len(text)
        
        chunk = text[pos:end_pos]
        blocks[q_num] = chunk
    
    return blocks

# Map mark scheme keys - ALL 9ma0 maths papers
ms_key_map = {
    '9ma0-01-rms-20230817.pdf': ('2023', 'P1', 'pure'),
    '9ma0-01-rms-20240815.pdf': ('2024', 'P1', 'pure'),
    '9ma0-02-rms-20230817.pdf': ('2023', 'P2', 'pure'),
    '9ma0-02-rms-20240815.pdf': ('2024', 'P2', 'pure'),
    '9ma0-31-rms-20230817.pdf': ('2023', 'S1', 'stats'),
    '9ma0-31-rms-20240815.pdf': ('2024', 'S1', 'stats'),
    '9ma0-32-rms-20230817.pdf': ('2023', 'M1', 'mech'),  # Uses pure format!
    '9ma0-32-rms-20240815.pdf': ('2024', 'M1', 'mech'),  # Uses pure format!
}

all_ms = {}
for key, (year, paper, ptype) in ms_key_map.items():
    # All 9ma0 papers except stats use 'pure' format for parsing
    parse_type = 'stats' if ptype == 'stats' else 'pure'
    blocks = extract_ms_blocks(ms[key], parse_type)
    label = f"{year} {paper}"
    all_ms[label] = blocks
    print(f"{label}: {len(blocks)} questions - {sorted(blocks.keys())}")

###############################################################################
# Clean and extract answer text from mark scheme blocks
###############################################################################

def clean_ms_text(raw_text, sub_part=None):
    """Clean mark scheme text and optionally extract a sub-part."""
    # Remove page markers
    text = raw_text.replace('---PAGE---', ' ')
    # Normalize whitespace  
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove header
    text = re.sub(r'^Question\s+Scheme\s+Marks\s+AOs\s*', '', text)
    text = re.sub(r'^Qu\s+\d+\s+Scheme\s+Marks\s+AO\s*', '', text)
    
    # If sub_part specified (like 'a' or 'b'), extract that section
    if sub_part:
        # Look for "N(sub)" pattern e.g. "1(a)", "2(b)"
        pattern = r'\d+\(' + re.escape(sub_part) + r'\)'
        match = re.search(pattern, text)
        if match:
            # Find the NEXT sub-part (next letter after this one)
            next_letter = chr(ord(sub_part) + 1)
            next_pattern = r'\d+\(' + re.escape(next_letter) + r'\)'
            next_match = re.search(next_pattern, text[match.end():])
            if next_match:
                text = text[match.start():match.end() + next_match.start()]
            else:
                # Could also be start of next question number
                # Look for pattern like "2(" which would be next question
                next_q = re.search(r'\b\d+\([a-z]\)', text[match.end():])
                if next_q and next_match is None:
                    text = text[match.start():match.end() + next_q.start()]
                else:
                    text = text[match.start():]
    
    return text.strip()

###############################################################################
# Parse question IDs
###############################################################################

def parse_q_id(qid):
    """Parse question ID like pp23p1q1 or pp24m1q1a -> (year, paper, qnum, subpart)"""
    m = re.match(r'pp(\d{2})(p[12]|s1|m1)q(\d+)(\w*)', qid)
    if m:
        year = '20' + m.group(1)
        paper = m.group(2).upper()
        qnum = int(m.group(3))
        sub = m.group(4) if m.group(4) else None
        return year, paper, qnum, sub
    return None, None, None, None

def is_maths_question(q):
    subject = q.get('subject', '').lower()
    return any(s in subject for s in ['pure', 'stats', 'mech'])

###############################################################################
# Look for MC answer indicators in mark scheme text
###############################################################################

def find_mc_answer(ms_text):
    """Try to find MC answer in mark scheme text. Returns (letter, index) or None."""
    # Pattern 1: "The only correct answer is X"
    m = re.search(r'(?:The only )?correct answer is\s*([A-D])', ms_text, re.IGNORECASE)
    if m:
        letter = m.group(1).upper()
        return letter, ord(letter) - ord('A')
    
    # Pattern 2: "Answer: A" etc
    m = re.search(r'(?:Answer|Ans)\s*[:.]?\s*\b([A-D])\b', ms_text, re.IGNORECASE)
    if m:
        letter = m.group(1).upper()
        return letter, ord(letter) - ord('A')
    
    return None

###############################################################################
# Also verify mathematical answers against mark scheme extracted values
###############################################################################

def extract_numerical_answers(ms_text):
    """Extract key numerical answers/values from mark scheme text."""
    answers = []
    # Look for "awrt" (answers which round to) patterns
    for m in re.finditer(r'awrt\s+([0-9]+\.[0-9]+)', ms_text):
        answers.append(float(m.group(1)))
    # Look for bold/highlighted final answers pattern  
    for m in re.finditer(r'\*\s*([A-Z0-9]+\.[0-9]+)', ms_text):
        answers.append(m.group(1))
    return answers

###############################################################################
# Main update loop
###############################################################################

changes = []
answer_corrections = []

for q in qbank:
    if not (q['id'].startswith('pp23') or q['id'].startswith('pp24')):
        continue
    
    if not is_maths_question(q):
        continue
    
    year, paper, qnum, sub = parse_q_id(q['id'])
    if not year:
        continue
    
    ms_label = f"{year} {paper}"
    
    if ms_label not in all_ms:
        print(f"WARNING: No mark scheme for {ms_label}")
        continue
    
    if qnum not in all_ms[ms_label]:
        print(f"WARNING: No Q{qnum} in {ms_label} mark scheme (have: {sorted(all_ms[ms_label].keys())})")
        continue
    
    ms_block = all_ms[ms_label][qnum]
    
    # Clean the text, extracting sub-part if applicable
    ms_clean = clean_ms_text(ms_block, sub)
    
    # Only update if we got meaningful content (> 30 chars)
    if len(ms_clean) > 30:
        old_explain = q.get('explain', '')
        new_explain = ms_clean
        
        # For MC questions, look for answer indicators
        if q['type'] == 'mc':
            mc_result = find_mc_answer(ms_block)
            if mc_result:
                mc_letter, mc_index = mc_result
                current_answer = q.get('answer')
                if current_answer != mc_index:
                    answer_corrections.append({
                        'id': q['id'],
                        'paper': ms_label,
                        'q_num': qnum,
                        'old_answer': current_answer,
                        'old_answer_letter': chr(ord('A') + current_answer) if isinstance(current_answer, int) and 0 <= current_answer <= 3 else '?',
                        'new_answer': mc_index,
                        'new_answer_letter': mc_letter,
                        'question_text': q.get('text', '')[:100]
                    })
                    q['answer'] = mc_index
        
        q['explain'] = new_explain
        changes.append({
            'id': q['id'],
            'paper': ms_label,
            'q_num': qnum,
            'sub': sub,
            'old_explain_len': len(old_explain),
            'new_explain_len': len(new_explain),
            'explain_preview': new_explain[:200]
        })

###############################################################################
# Write back
###############################################################################

with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)

print(f"\n=== SUMMARY ===")
print(f"Total maths questions updated: {len(changes)}")
for c in changes:
    sub_str = f"({c['sub']})" if c['sub'] else ""
    print(f"  {c['id']} ({c['paper']} Q{c['q_num']}{sub_str}): {c['old_explain_len']} -> {c['new_explain_len']} chars")
    print(f"    Preview: {c['explain_preview'][:150]}...")
    print()

print(f"\nAnswer corrections found: {len(answer_corrections)}")
for ac in answer_corrections:
    print(f"  {ac['id']} ({ac['paper']} Q{ac['q_num']}): answer {ac['old_answer']} ({ac['old_answer_letter']}) -> {ac['new_answer']} ({ac['new_answer_letter']})")
    print(f"    Question: {ac['question_text']}")
