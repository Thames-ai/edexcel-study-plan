import json
import re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

###############################################################################
# Parse mark schemes by question and sub-question
###############################################################################

def extract_ms_blocks(text, paper_type='pure'):
    """Extract question blocks from mark scheme text, split by sub-question."""
    blocks = {}
    
    if paper_type in ('stats', 'mech'):
        # Stats/Mech use "Qu N" format
        positions = []
        for m in re.finditer(r'Qu\s+(\d+)\s*\n\s*Scheme', text):
            positions.append((int(m.group(1)), m.start()))
    else:
        # Pure uses "Question  Scheme  Marks  AOs" format
        positions = []
        for m in re.finditer(r'Question\s+Scheme\s+Marks\s+AOs', text):
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
        blocks[q_num] = chunk
    
    return blocks

def clean_ms_text(raw_text, sub_part=None):
    """Clean mark scheme text and optionally extract a sub-part."""
    # Remove page markers
    text = raw_text.replace('---PAGE---', ' ')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove header
    text = re.sub(r'^Question\s+Scheme\s+Marks\s+AOs\s+\d+', '', text)
    text = re.sub(r'^Qu\s+\d+\s+Scheme\s+Marks\s+AO', '', text)
    
    # If sub_part specified (like 'a' or 'b'), try to extract that section
    if sub:
        next_letters = [chr(ord(sub) + i + 1) for i in range(5) if ord(sub) + i + 1 <= ord('z')]
        next_pattern = r'\d*\([' + ''.join(re.escape(l) for l in next_letters) + r']\)'
        match = re.search(r'\d*\(' + re.escape(sub) + r'\)', text)
        if match:
            next_sub = re.search(next_pattern, text[match.end():])
            if next_sub:
                text = text[match.start():match.end() + next_sub.start()]
            else:
                text = text[match.start():]
    
    return text.strip()

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
    blocks = extract_ms_blocks(ms[key], ptype)
    label = f"{year} {paper}"
    all_ms[label] = blocks
    print(f"{label}: {len(blocks)} questions - {sorted(blocks.keys())}")

###############################################################################
# Parse question IDs to match with mark schemes  
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
# Look for MC answer patterns in mark scheme text
###############################################################################

def find_mc_answer(ms_text):
    """Try to find MC answer in mark scheme text. Returns (option_letter, option_index) or None."""
    # Pattern 1: "The only correct answer is A/B/C/D"
    m = re.search(r'(?:The only )?correct answer is\s*([A-D])', ms_text, re.IGNORECASE)
    if m:
        letter = m.group(1).upper()
        return letter, ord(letter) - ord('A')
    
    # Pattern 2: "Answer: A" or "Ans: B"
    m = re.search(r'(?:Answer|Ans)\s*[:.]?\s*([A-D])\b', ms_text, re.IGNORECASE)
    if m:
        letter = m.group(1).upper()
        return letter, ord(letter) - ord('A')
    
    # Pattern 3: Look for Option A/B/C/D with "correct" or "✓" or tick mark
    # Not commonly in Edexcel format, but check
    
    return None

###############################################################################
# Build comprehensive explain text from mark scheme
###############################################################################

def build_explain(ms_text, q_type='mc'):
    """Build a clean explain field from mark scheme text."""
    # Extract the key scheme content (marks and answers), not the notes
    # Split on "Notes" section if present
    parts = re.split(r'\bNotes?\b', ms_text, maxsplit=1)
    scheme_part = parts[0] if parts else ms_text
    
    # Clean up
    scheme_clean = clean_ms_text(scheme_part)
    
    # If it's too long, try to condense
    if len(scheme_clean) > 2000:
        # Take first 2000 chars and add truncation note
        scheme_clean = scheme_clean[:2000] + '...'
    
    return scheme_clean

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
        print(f"WARNING: No Q{qnum} in {ms_label} mark scheme")
        continue
    
    ms_block = all_ms[ms_label][qnum]
    
    # Clean the text
    if sub:
        ms_clean = clean_ms_text(ms_block, sub)
    else:
        ms_clean = clean_ms_text(ms_block)
    
    # Only update if we got meaningful content
    if len(ms_clean) > 30:
        old_explain = q.get('explain', '')
        new_explain = ms_clean
        
        # For MC questions, try to find the correct answer
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
                        'new_answer': mc_index,
                        'new_letter': mc_letter
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
            'explain_preview': new_explain[:150]
        })

###############################################################################
# Write back
###############################################################################

with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)

print(f"\n=== SUMMARY ===")
print(f"Total maths questions updated: {len(changes)}")
for c in changes:
    print(f"  {c['id']} ({c['paper']} Q{c['q_num']}{'('+c['sub']+')' if c['sub'] else ''}): {c['old_explain_len']} -> {c['new_explain_len']} chars")
    print(f"    Preview: {c['explain_preview'][:120]}...")

print(f"\nAnswer corrections found: {len(answer_corrections)}")
for ac in answer_corrections:
    print(f"  {ac['id']}: answer {ac['old_answer']} -> {ac['new_answer']} ({ac['new_letter']})")
