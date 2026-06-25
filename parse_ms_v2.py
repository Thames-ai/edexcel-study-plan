#!/usr/bin/env python3
"""
Parse Edexcel Chemistry mark schemes and update curated past paper question bank.
Use content-based matching to correctly align questions with mark scheme answers.
"""

import json
import re

# Load data
with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms_raw = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

# Chemistry mark scheme keys and their mappings
chem_ms_keys = {
    '8ch0-01-rms-20230817.pdf': '2023 C1 Core',
    '8ch0-02-rms-20230817.pdf': '2023 C2 Core',
    '8ch0-01-rms-20240815.pdf': '2024 C1 Core',
    '8ch0-02-rms-20240815.pdf': '2024 C2 Core',
    '9ch0-01-rms-20230817.pdf': '2023 C1 Adv',
    '9ch0-02-rms-20230817.pdf': '2023 C2 Adv',
    '9ch0-01-rms-20240815.pdf': '2024 C1 Adv',
    '9ch0-02-rms-20240815.pdf': '2024 C2 Adv',
}

def clean_text(t):
    """Clean text for comparison."""
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t

def parse_mark_scheme_questions(text):
    """
    Parse a mark scheme into structured question-answer pairs.
    Returns list of dicts with question_number, answer content, type (mc/long), etc.
    """
    text = re.sub(r'\r\n', '\n', text)
    
    results = []
    
    # Split by "Question Number" "Answer" patterns
    # Pattern: "Question\nNumber\nAnswer\n..." followed by question ID like "1(a)"
    blocks = re.split(r'(?=Question\s+Number\s+(?:\s+Answer)?(?:\s+Additional Guidance)?(?:\s+Mark)?\s*\n)', text)
    
    for block in blocks:
        # Find question number
        q_match = re.search(r'(\d+)\(([a-z])\)((?:\([^)]+\))*)', block)
        if not q_match:
            continue
        
        q_num = q_match.group(1)
        q_letter = q_match.group(2)
        q_subs = q_match.group(3)  # e.g., "(iii)" or "(i)"
        q_id = f"{q_num}({q_letter}){q_subs}"
        
        # Check for MC answer
        mc_match = re.search(r'The only correct answer is ([A-D])\s*(?:\(([^)]*)\))?', block)
        if mc_match:
            correct_letter = mc_match.group(1)
            correct_detail = mc_match.group(2) or ''
            
            # Get wrong answer explanations
            wrong_exps = []
            for wm in re.finditer(r'([A-D]) is not correct because (.*?)(?=\s*[A-D] is not correct|\n\s*\(\d+\)\s*\n|\Z)', block, re.DOTALL):
                exp_text = re.sub(r'\s+', ' ', wm.group(2)).strip()
                wrong_exps.append(f"{wm.group(1)}: {exp_text}")
            
            answer_text = f"The only correct answer is {correct_letter}"
            if correct_detail:
                answer_text += f" ({correct_detail})"
            if wrong_exps:
                answer_text += ". " + "; ".join(wrong_exps)
            
            answer_text = re.sub(r'\s+', ' ', answer_text).strip()
            
            results.append({
                'question_id': q_id,
                'type': 'mc',
                'correct_letter': correct_letter,
                'correct_detail': correct_detail,
                'full_answer': answer_text,
                'block_text': block[:500]  # for debugging
            })
        else:
            # Long-form answer
            # Extract the answer content
            # Find content between "Answer" and "Additional Guidance" or next "Question Number"
            ans_match = re.search(
                r'Answer\s*(?:\s+Additional\s+Guidance)?\s*(?:\s+Mark)?\s*\n(.*?)(?=\n\s*(?:Question\s+Number|Total\s+for\s+Question))',
                block, re.DOTALL
            )
            if ans_match:
                answer_text = ans_match.group(1).strip()
                # Clean up
                answer_text = re.sub(r'\n{3,}', '\n\n', answer_text)
                lines = [l.strip() for l in answer_text.split('\n') if l.strip()]
                # Remove header-like lines
                lines = [l for l in lines if l not in ('Additional Guidance', 'Mark', 'Answer', 'Question Number')]
                answer_text = '\n'.join(lines)
                
                if answer_text and len(answer_text) > 5:
                    results.append({
                        'question_id': q_id,
                        'type': 'long',
                        'full_answer': answer_text,
                        'block_text': block[:500]
                    })
    
    return results

# Strategy: For each question in qbank, we know the paper it came from.
# We need to find what question number it corresponds to in the actual paper.
# The qbank IDs encode question numbers that may not match the actual paper numbering.
# Best approach: Use the MC option text to search within the mark scheme.

# First, parse all mark schemes
all_ms_parsed = {}
for key, paper_name in chem_ms_keys.items():
    text = ms_raw[key]
    parsed = parse_mark_scheme_questions(text)
    all_ms_parsed[paper_name] = parsed
    print(f"\n=== {paper_name} ===")
    for p in parsed:
        if p['type'] == 'mc':
            print(f"  {p['question_id']}: MC Answer={p['correct_letter']} ({p['correct_detail'][:60]})")
        else:
            print(f"  {p['question_id']}: Long-form ({len(p['full_answer'])} chars)")

# Now for each Chem Y1 question, search within the matching paper's mark scheme
# to find the correct answer by matching MC option text or question keywords

print("\n\n" + "="*60)
print("MATCHING QUESTIONS TO MARK SCHEME ANSWERS")
print("="*60)

changes = []
corrections = []

for q in qbank:
    if q.get('subject') != 'Chem Y1':
        continue
    
    qid = q['id']
    paper = q.get('paper', '')
    
    # Determine which mark scheme to use
    if paper not in all_ms_parsed:
        print(f"WARNING: No MS for paper '{paper}' (question {qid})")
        continue
    
    ms_entries = all_ms_parsed[paper]
    matched_entry = None
    
    if q.get('type') == 'mc':
        # For MC questions, try to match by searching for option text in mark scheme
        options = q.get('options', [])
        
        # Try to find an MC answer in the MS whose correct_detail matches one of our options
        for ms in ms_entries:
            if ms['type'] != 'mc':
                continue
            
            detail_clean = clean_text(ms['correct_detail'])
            correct_letter = ms['correct_letter']
            ms_qid = ms['question_id']
            
            # Check if the MS correct detail matches any of our options
            for opt_idx, opt in enumerate(options):
                opt_clean = clean_text(opt)
                # Check if option text appears in MS detail or vice versa
                if opt_clean and detail_clean and (
                    opt_clean in detail_clean or detail_clean in opt_clean or
                    # Also try matching key phrases
                    any(phrase in detail_clean for phrase in opt_clean.split()[:3] if len(phrase) > 3)
                ):
                    # Potential match - but verify by checking wrong answer explanations too
                    matched_entry = ms
                    break
            
            if matched_entry:
                break
        
        # If no content match, try matching by question number from ID
        if not matched_entry:
            m = re.match(r'pp\d{2}c\d[ac]q(\d+)([a-z]?)', qid)
            if m:
                q_num = m.group(1)
                q_sub = m.group(2) or ''
                # Try matching with common sub-part patterns
                candidates = []
                for ms in ms_entries:
                    if ms['type'] != 'mc':
                        continue
                    ms_qnum = re.match(r'(\d+)\(', ms['question_id'])
                    if ms_qnum and ms_qnum.group(1) == q_num:
                        candidates.append(ms)
                
                if len(candidates) == 1:
                    matched_entry = candidates[0]
                elif len(candidates) > 1:
                    # Multiple candidates - try harder to match
                    # Search for option text in all candidates
                    for ms in candidates:
                        detail_clean = clean_text(ms['correct_detail'])
                        for opt_idx, opt in enumerate(options):
                            opt_clean = clean_text(opt)
                            if opt_clean and detail_clean and (
                                opt_clean in detail_clean or detail_clean in opt_clean
                            ):
                                matched_entry = ms
                                break
                        if matched_entry:
                            break
        
        # Alternative approach: search for key phrases from the question text in the MS
        if not matched_entry:
            # Extract distinctive keywords
            q_text = q.get('text', '')
            keywords = re.findall(r'[A-Za-z]{4,}', q_text)
            keywords = [k.lower() for k in keywords if k.lower() not in {
                'which', 'what', 'from', 'with', 'that', 'this', 'the', 'and',
                'are', 'for', 'has', 'been', 'when', 'where', 'than', 'then',
                'also', 'only', 'most', 'both', 'such', 'each', 'into'
            }]
            
            for ms in ms_entries:
                if ms['type'] != 'mc':
                    continue
                block_lower = clean_text(ms['block_text'])
                matches = sum(1 for kw in keywords if kw in block_lower)
                if matches >= 2 and (not matched_entry or matches > matched_entry.get('_score', 0)):
                    ms['_score'] = matches
                    matched_entry = ms
    
    else:
        # Long-form question
        m = re.match(r'pp\d{2}c\d[ac]q(\d+)([a-z]?)', qid)
        if m:
            q_num = m.group(1)
            candidates = [ms for ms in ms_entries if ms['type'] == 'long' and 
                         re.match(r'(\d+)\(', ms['question_id']) and 
                         re.match(r'(\d+)\(', ms['question_id']).group(1) == q_num]
            if len(candidates) == 1:
                matched_entry = candidates[0]
    
    if not matched_entry:
        print(f"WARNING: No MS match for {qid} (paper={paper})")
        continue
    
    # Update explain field
    old_explain = q.get('explain', '')
    new_explain = matched_entry['full_answer']
    
    if old_explain != new_explain:
        q['explain'] = new_explain
        changes.append({
            'id': qid,
            'paper': paper,
            'ms_qid': matched_entry['question_id'],
            'old_explain': old_explain[:100],
            'new_explain': new_explain[:100],
        })
    
    # For MC questions, verify/correct the answer
    if matched_entry['type'] == 'mc' and q.get('type') == 'mc':
        correct_letter = matched_entry['correct_letter']
        correct_index = ord(correct_letter) - ord('A')
        current_answer = q.get('answer')
        
        if current_answer != correct_index:
            # Verify the correction makes sense by checking option text
            ms_detail = matched_entry.get('correct_detail', '')
            options = q.get('options', [])
            
            if correct_index < len(options):
                correction = {
                    'id': qid,
                    'paper': paper,
                    'ms_qid': matched_entry['question_id'],
                    'old_answer': current_answer,
                    'old_answer_text': options[current_answer] if current_answer < len(options) else 'N/A',
                    'new_answer': correct_index,
                    'new_answer_text': options[correct_index] if correct_index < len(options) else 'N/A',
                    'correct_letter': correct_letter,
                    'ms_detail': ms_detail[:100],
                }
                corrections.append(correction)
                q['answer'] = correct_index

# Write updated qbank
with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)

# Print summary
print("\n" + "="*60)
print("SUMMARY OF ALL CHANGES")
print("="*60)

print(f"\nTotal explain fields updated: {len(changes)}")
for c in changes:
    print(f"\n  {c['id']} ({c['paper']}): MS matched to {c['ms_qid']}")
    print(f"    OLD: {c['old_explain']}")
    print(f"    NEW: {c['new_explain']}")

print(f"\n\nTotal answer corrections: {len(corrections)}")
for c in corrections:
    print(f"\n  ** CORRECTION ** {c['id']} ({c['paper']}): MS={c['ms_qid']}")
    print(f"    Old answer: option {c['old_answer']} = {c['old_answer_text']}")
    print(f"    New answer: {c['correct_letter']} (option {c['new_answer']}) = {c['new_answer_text']}")
    print(f"    MS detail: {c['ms_detail']}")
