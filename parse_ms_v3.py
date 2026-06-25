#!/usr/bin/env python3
"""
Parse Edexcel Chemistry mark schemes and update curated past paper question bank.
V3: Careful manual mapping with content verification.
"""

import json
import re

# Load data
with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms_raw = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

chem_ms_files = {
    '8ch0-01-rms-20230817.pdf': '2023 C1 Core',
    '8ch0-02-rms-20230817.pdf': '2023 C2 Core',
    '8ch0-01-rms-20240815.pdf': '2024 C1 Core',
    '8ch0-02-rms-20240815.pdf': '2024 C2 Core',
    '9ch0-01-rms-20230817.pdf': '2023 C1 Adv',
    '9ch0-02-rms-20230817.pdf': '2023 C2 Adv',
    '9ch0-01-rms-20240815.pdf': '2024 C1 Adv',
    '9ch0-02-rms-20240815.pdf': '2024 C2 Adv',
}

def search_ms_for_keywords(text, keywords):
    """Search mark scheme text for keywords and return matching positions with context."""
    text_lower = text.lower()
    results = []
    for kw in keywords:
        kw_lower = kw.lower()
        pos = 0
        while True:
            pos = text_lower.find(kw_lower, pos)
            if pos == -1:
                break
            # Get context around the match
            start = max(0, pos - 100)
            end = min(len(text), pos + len(kw) + 200)
            context = text[start:end].replace('\n', ' ').replace('\r', '')
            results.append((pos, kw, context))
            pos += len(kw)
    return results

def find_mc_answer_near_position(text, position, search_range=3000):
    """Find MC answer pattern near a position in mark scheme text."""
    # Search forward from position
    search_text = text[position:position + search_range]
    match = re.search(r'The only correct answer is ([A-D])\s*(?:\(([^)]*)\))?', search_text)
    if match:
        correct_letter = match.group(1)
        correct_detail = match.group(2) or ''
        
        # Get wrong answer explanations within the block
        wrong_exps = []
        for wm in re.finditer(r'([A-D]) is not correct because (.*?)(?=\s*[A-D] is not correct|\n\s*\(\d+\)\s*\n|\Z)', search_text, re.DOTALL):
            exp_text = re.sub(r'\s+', ' ', wm.group(2)).strip()
            wrong_exps.append(f"{wm.group(1)}: {exp_text}")
        
        answer_text = f"The only correct answer is {correct_letter}"
        if correct_detail:
            answer_text += f" ({correct_detail})"
        if wrong_exps:
            answer_text += ". " + "; ".join(wrong_exps)
        
        answer_text = re.sub(r'\s+', ' ', answer_text).strip()
        
        # Find the question number for this answer
        q_match = re.search(r'(\d+\([a-z]\)(?:\([^)]+\))*)', search_text[:match.start()+50])
        
        return {
            'found': True,
            'correct_letter': correct_letter,
            'correct_detail': correct_detail,
            'full_answer': answer_text,
            'question_id': q_match.group(1) if q_match else 'unknown'
        }
    
    # Also search backwards a bit
    search_text = text[max(0, position - 500):position + 2000]
    match = re.search(r'The only correct answer is ([A-D])\s*(?:\(([^)]*)\))?', search_text)
    if match:
        correct_letter = match.group(1)
        correct_detail = match.group(2) or ''
        
        wrong_exps = []
        for wm in re.finditer(r'([A-D]) is not correct because (.*?)(?=\s*[A-D] is not correct|\n\s*\(\d+\)\s*\n|\Z)', search_text, re.DOTALL):
            exp_text = re.sub(r'\s+', ' ', wm.group(2)).strip()
            wrong_exps.append(f"{wm.group(1)}: {exp_text}")
        
        answer_text = f"The only correct answer is {correct_letter}"
        if correct_detail:
            answer_text += f" ({correct_detail})"
        if wrong_exps:
            answer_text += ". " + "; ".join(wrong_exps)
        
        answer_text = re.sub(r'\s+', ' ', answer_text).strip()
        
        q_match = re.search(r'(\d+\([a-z]\)(?:\([^)]+\))*)', search_text[:match.start()+50])
        
        return {
            'found': True,
            'correct_letter': correct_letter,
            'correct_detail': correct_detail,
            'full_answer': answer_text,
            'question_id': q_match.group(1) if q_match else 'unknown'
        }
    
    return {'found': False}

def find_long_answer_near_position(text, position, search_range=5000):
    """Find long-form answer content near a position in mark scheme text."""
    search_text = text[max(0, position - 200):position + search_range]
    # Find the question number pattern
    q_match = re.search(r'(\d+\([a-z]\)(?:\([^)]+\))*)', search_text[:200])
    if not q_match:
        return {'found': False}
    
    q_id = q_match.group(1)
    
    # Extract answer content
    # Look for the structured answer content that follows
    ans_start = search_text.find('Answer', 50)
    if ans_start == -1:
        return {'found': False, 'question_id': q_id}
    
    # Get everything until the next "Question Number" or "Total for Question"
    end_patterns = [r'Question\s+Number', r'Total\s+for\s+Question']
    ans_end = len(search_text)
    for pat in end_patterns:
        m = re.search(pat, search_text[ans_start:])
        if m and ans_start + m.start() < ans_end:
            ans_end = ans_start + m.start()
    
    answer_text = search_text[ans_start:ans_end]
    # Clean up
    answer_text = re.sub(r'Additional Guidance', '', answer_text)
    answer_text = re.sub(r'^Answer\s*', '', answer_text)
    answer_text = re.sub(r'^Mark\s*', '', answer_text, flags=re.MULTILINE)
    answer_text = re.sub(r'\n{3,}', '\n\n', answer_text)
    lines = [l.strip() for l in answer_text.split('\n') if l.strip()]
    answer_text = '\n'.join(lines)
    
    return {
        'found': True,
        'question_id': q_id,
        'full_answer': answer_text
    }



# For each Chem Y1 question, search the corresponding mark scheme
# using distinctive keywords from the question text

print("Matching questions to mark schemes...")
print("="*70)

changes = []
corrections = []

for q in qbank:
    if q.get('subject') != 'Chem Y1':
        continue
    
    qid = q['id']
    paper = q.get('paper', '')
    q_text = q.get('text', '')
    q_type = q.get('type', '')
    current_answer = q.get('answer')
    options = q.get('options', [])
    
    # Determine which MS file to use
    ms_file = None
    for f, pname in chem_ms_files.items():
        if pname == paper:
            ms_file = f
            break
    
    if not ms_file:
        print(f"  WARNING: No MS file for paper '{paper}' ({qid})")
        continue
    
    ms_text = ms_raw[ms_file]
    
    # Extract distinctive keywords from question text
    # For each question, we'll use carefully chosen search terms
    
    # Let's define manual keyword searches for each question
    # based on the question content
    
    search_keywords = []
    
    # Generate keywords from question text - pick distinctive terms
    words = re.findall(r'[A-Za-z0-9]{3,}', q_text)
    # Filter common/stop words
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
                  'had', 'her', 'was', 'one', 'our', 'out', 'has', 'have', 'from',
                  'what', 'which', 'that', 'this', 'with', 'when', 'where', 'than',
                  'then', 'also', 'into', 'does', 'will', 'each', 'make', 'like',
                  'been', 'long', 'very', 'after', 'just', 'only', 'most', 'over',
                  'such', 'take', 'some', 'them', 'what', 'about'}
    chem_stop = {'ion', 'mole', 'atom', 'bond', 'ions', 'acid'}
    
    distinctive_words = [w for w in words if w.lower() not in stop_words and w.lower() not in chem_stop and len(w) >= 3]
    
    # Take most distinctive 3-5 words
    search_keywords = distinctive_words[:5]
    
    # Search MS for these keywords
    matches = search_ms_for_keywords(ms_text, search_keywords)
    
    if not matches:
        # Try with fewer/different keywords
        search_keywords = distinctive_words[:3]
        matches = search_ms_for_keywords(ms_text, search_keywords)
    
    if not matches:
        # Try individual keywords
        for w in distinctive_words[:8]:
            matches = search_ms_for_keywords(ms_text, [w])
            if matches:
                break
    
    if not matches:
        print(f"  NO MATCH: {qid} | {paper} | keywords tried: {search_keywords}")
        continue
    
    # Find the best position - choose the one with most keyword hits nearby
    # Group matches by proximity
    best_pos = matches[0][0]
    best_count = 1
    
    positions = sorted([m[0] for m in matches])
    # Find cluster of positions
    for i, pos in enumerate(positions):
        nearby = sum(1 for p in positions if abs(p - pos) < 2000)
        if nearby > best_count:
            best_count = nearby
            best_pos = pos
    
    # Now find the MC answer near this position
    if q_type == 'mc':
        mc_result = find_mc_answer_near_position(ms_text, best_pos)
        
        if mc_result['found']:
            correct_letter = mc_result['correct_letter']
            correct_index = ord(correct_letter) - ord('A')
            
            # Verify: check if the MS correct detail matches any option
            ms_detail_clean = re.sub(r'\s+', ' ', mc_result.get('correct_detail', '')).strip().lower()
            option_matched = False
            matched_option = -1
            
            for opt_idx, opt in enumerate(options):
                opt_clean = re.sub(r'\s+', ' ', opt).strip().lower()
                if ms_detail_clean and opt_clean and (
                    ms_detail_clean in opt_clean or opt_clean in ms_detail_clean
                ):
                    option_matched = True
                    matched_option = opt_idx
                    break
            
            # Additional verification: some MS details may be truncated from PDF extraction
            # If option_matched and matched_option != correct_index, the matching is wrong
            if option_matched and matched_option != correct_index:
                print(f"  MISMATCH WARNING: {qid} - MS says {correct_letter} but detail matches option {matched_option}")
                print(f"    MS detail: {mc_result['correct_detail'][:80]}")
                print(f"    Matched option: {options[matched_option][:80]}")
                # Use the option-matched index instead
                correct_index = matched_option
                correct_letter = chr(ord('A') + matched_option)
            
            # Update explain field
            old_explain = q.get('explain', '')
            new_explain = mc_result['full_answer']
            
            if old_explain != new_explain:
                q['explain'] = new_explain
                changes.append({
                    'id': qid,
                    'paper': paper,
                    'ms_qid': mc_result['question_id'],
                    'ms_letter': correct_letter,
                    'old_explain': old_explain[:80],
                    'new_explain': new_explain[:80],
                })
            
            # Check answer
            if current_answer != correct_index:
                corrections.append({
                    'id': qid,
                    'paper': paper,
                    'ms_qid': mc_result['question_id'],
                    'old_answer': current_answer,
                    'old_answer_text': options[current_answer] if current_answer < len(options) else 'N/A',
                    'new_answer': correct_index,
                    'new_answer_text': options[correct_index] if correct_index < len(options) else 'N/A',
                    'correct_letter': correct_letter,
                    'ms_detail': mc_result.get('correct_detail', '')[:100],
                    'option_matched': option_matched
                })
                q['answer'] = correct_index
            
            print(f"  MATCH: {qid} -> MS Q{mc_result['question_id']} Answer={correct_letter} ({mc_result['correct_detail'][:50]}){' [VERIFIED]' if option_matched else ' [UNVERIFIED]'}")
        else:
            print(f"  MC NOT FOUND: {qid} | position={best_pos}")
    else:
        # Long-form question
        lf_result = find_long_answer_near_position(ms_text, best_pos)
        if lf_result['found']:
            old_explain = q.get('explain', '')
            q['explain'] = lf_result['full_answer']
            if old_explain != lf_result['full_answer']:
                changes.append({
                    'id': qid,
                    'paper': paper,
                    'ms_qid': lf_result['question_id'],
                    'old_explain': old_explain[:80],
                    'new_explain': lf_result['full_answer'][:80],
                })
            print(f"  MATCH: {qid} -> MS Q{lf_result['question_id']} (long-form, {len(lf_result['full_answer'])} chars)")
        else:
            print(f"  LONG NOT FOUND: {qid} | position={best_pos}")

# Write updated qbank
with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)

print("\n" + "="*70)
print(f"Total explain fields updated: {len(changes)}")
print(f"Total answer corrections: {len(corrections)}")

print("\n--- CORRECTIONS ---")
for c in corrections:
    print(f"  {c['id']} ({c['paper']}): MS Q{c['ms_qid']} says {c['correct_letter']}")
    print(f"    WAS: {c['old_answer']} ({c['old_answer_text']})")
    print(f"    NOW: {c['new_answer']} ({c['new_answer_text']})")
    print(f"    MS detail: {c['ms_detail']}")
    print(f"    Option matched: {c['option_matched']}")
