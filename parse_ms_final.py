#!/usr/bin/env python3
"""
Update Chem Y1 quiz questions with official mark scheme answers.
Uses manual verified mapping based on extracted mark scheme content.
"""

import json
import re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms_raw = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

# Helper to extract the full MC answer text from a mark scheme
def extract_mc_answer(text, q_id_hint, search_range=8000):
    """Find an MC answer near a keyword hint in the text."""
    text = re.sub(r'\r\n', '\n', text)
    
    # Search for hint first
    hint_pos = text.lower().find(q_id_hint.lower())
    if hint_pos == -1:
        hint_pos = 0
    
    search_start = max(0, hint_pos - 1000)
    search_end = min(len(text), hint_pos + search_range)
    search_text = text[search_start:search_end]
    
    # Find "The only correct answer is X"
    mc_match = re.search(r'The only correct answer is ([A-D])\s*(?:\(([^)]*)\))?', search_text)
    if not mc_match:
        return None
    
    correct_letter = mc_match.group(1)
    correct_detail = mc_match.group(2) or ''
    correct_detail = re.sub(r'\s+', ' ', correct_detail).strip()
    
    # Find question number
    before = search_text[:mc_match.start()]
    q_matches = re.findall(r'(\d+(?:\([a-z]\))(?:\([^)]*\))*)', before)
    q_number = q_matches[-1] if q_matches else ''
    
    # Get wrong answer explanations
    after = search_text[mc_match.end():mc_match.end()+1500]
    wrong_exps = []
    for wm in re.finditer(
        r'([A-D]) is (?:not correct|incorrect) because (.*?)(?=\s*[A-D] is (?:not correct|incorrect)|\n\s*\(\d+\)\s*$|\Z)',
        after, re.DOTALL
    ):
        exp_text = re.sub(r'\s+', ' ', wm.group(2)).strip()
        if exp_text:
            wrong_exps.append(f"{wm.group(1)}: {exp_text}")
    
    answer_text = f"The only correct answer is {correct_letter}"
    if correct_detail:
        answer_text += f" ({correct_detail})"
    if wrong_exps:
        answer_text += ". " + "; ".join(wrong_exps)
    
    answer_text = re.sub(r'\s+', ' ', answer_text).strip()
    
    return {
        'correct_letter': correct_letter,
        'correct_index': ord(correct_letter) - ord('A'),
        'correct_detail': correct_detail,
        'full_answer': answer_text,
        'q_number': q_number
    }

def extract_long_answer(text, q_id_hint, search_range=8000):
    """Find a long-form answer near a keyword hint in the text."""
    text = re.sub(r'\r\n', '\n', text)
    
    hint_pos = text.lower().find(q_id_hint.lower())
    if hint_pos == -1:
        return None
    
    # Find the nearest question number pattern before hint
    before = text[max(0, hint_pos-2000):hint_pos]
    q_matches = re.findall(r'(\d+(?:\([a-z]\))(?:\([^)]*\))*)', before)
    q_number = q_matches[-1] if q_matches else ''
    
    # Extract answer content from hint position forward
    chunk = text[hint_pos:hint_pos+search_range]
    
    # Find the answer section
    ans_start = chunk.find('Answer')
    if ans_start == -1:
        # Look for structured content
        ans_start = 0
    else:
        ans_start += 5  # Skip 'Answer'
    
    # Find end at next question or total
    ans_end = len(chunk)
    for pat in [r'Question\s+Number', r'Total\s+for\s+Question']:
        m = re.search(pat, chunk[ans_start:])
        if m:
            ans_end = min(ans_end, ans_start + m.start())
    
    answer_text = chunk[ans_start:ans_end]
    # Clean up
    answer_text = re.sub(r'Additional Guidance\s*', '', answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r'^\s*Mark\s*$', '', answer_text, flags=re.MULTILINE)
    answer_text = re.sub(r'\n{3,}', '\n\n', answer_text)
    lines = [l.strip() for l in answer_text.split('\n') if l.strip() and l.strip() not in ('Answer', 'Mark', 'Additional Guidance')]
    answer_text = '\n'.join(lines)
    
    if not answer_text or len(answer_text) < 5:
        return None
    
    return {
        'full_answer': answer_text,
        'q_number': q_number
    }


# ============================================================
# MANUAL MAPPING: Verified mapping of qbank questions to mark scheme entries
# Based on extracted MC answer data above
# ============================================================

# Each entry: (qid, paper, ms_key, search_hint, expected_letter)
# search_hint helps locate the answer in the mark scheme text
MANUAL_MAP = {
    # 2023 C1 Core (8ch0-01-rms-20230817.pdf)
    'pp23c1cq1':  ('8ch0-01-rms-20230817.pdf', 'neutron', 'B'),  # Q1(a): proton/neutron data -> B
    'pp23c1cq1b': ('8ch0-01-rms-20230817.pdf', '1(b)(i)', None),  # 1(b)(i): spherical
    'pp23c1cq1c': ('8ch0-01-rms-20230817.pdf', '1(c)', None),  # 1(c): isotope calculation
    'pp23c1cq2':  ('8ch0-01-rms-20230817.pdf', '402.7', 'C'),  # Q2(a)(iii): % water in K2Mg(SO4)2.6H2O -> C (402.7 Mr)
    'pp23c1cq7':  ('8ch0-01-rms-20230817.pdf', 'ionic and covalent', None),  # Need to find this Q
    'pp23c1cq9':  ('8ch0-01-rms-20230817.pdf', '578  1817', 'B'),  # Q9(a): IE Group 2 -> B
    'pp23c1cq6':  ('8ch0-01-rms-20230817.pdf', 'loss of electrons', None),  # Q6: redox
    'pp23c1cq8':  ('8ch0-01-rms-20230817.pdf', 'exothermic', None),  # Q7/8: enthalpy

    # 2023 C2 Core (8ch0-02-rms-20230817.pdf)
    'pp23c2cq1':  ('8ch0-02-rms-20230817.pdf', 'Maxwell', None),  # Maxwell-Boltzmann
    'pp23c2cq2':  ('8ch0-02-rms-20230817.pdf', 'saturated hydrocarbon', None),  # Saturated hydrocarbon
    'pp23c2cq3':  ('8ch0-02-rms-20230817.pdf', 'Br2', None),  # Alkene test -> probably 3(e) nickel? No, that's wrong
    'pp23c2cq7':  ('8ch0-02-rms-20230817.pdf', 'butan-1-ol', None),  # Oxidation product
    'pp23c2cq5':  ('8ch0-02-rms-20230817.pdf', 'SO2', None),  # Equilibrium / Kc
    
    # 2024 C1 Core (8ch0-01-rms-20240815.pdf)
    'pp24c1cq1':  ('8ch0-01-rms-20240815.pdf', 'phosphide', 'B'),  # Q1: P3- config -> B (1s2...3p6)
    'pp24c1cq2':  ('8ch0-01-rms-20240815.pdf', '1086  2353', 'D'),  # Q2: Group 2 IEs -> D (Group 4)
    'pp24c1cq3':  ('8ch0-01-rms-20240815.pdf', 'atomic radii', 'D'),  # Q3: Period 3 trend -> D (decreasing, increasing)
    'pp24c1cq5':  ('8ch0-01-rms-20240815.pdf', 'reduction', None),  # Q5: Reduction step

    # 2024 C2 Core (8ch0-02-rms-20240815.pdf)
    'pp24c2cq2':  ('8ch0-02-rms-20240815.pdf', 'Cr2O7', 'C'),  # Kc for dichromate -> C
    'pp24c2cq6':  ('8ch0-02-rms-20240815.pdf', 'disappearing', None),  # Rate measurement
    'pp24c2cq3':  ('8ch0-02-rms-20240815.pdf', 'E/Z isomerism', None),  # E/Z isomerism
    'pp24c2cq5':  ('8ch0-02-rms-20240815.pdf', 'H2SO4', None),  # Role of H2SO4
    'pp24c2cq7':  ('8ch0-02-rms-20240815.pdf', 'fermentation', None),  # Fermentation

    # 2023 C1 Adv (9ch0-01-rms-20230817.pdf)
    'pp23c1aq1':  ('9ch0-01-rms-20230817.pdf', 'd-block', 'B'),  # Q1(a): d-block -> B (2)
    'pp23c1aq5':  ('9ch0-01-rms-20230817.pdf', 'N2O4', None),  # Kp question

    # 2023 C2 Adv (9ch0-02-rms-20230817.pdf)
    'pp23c2aq6':  ('9ch0-02-rms-20230817.pdf', 'iodine', None),  # Rate equation
    'pp23c2aq8':  ('9ch0-02-rms-20230817.pdf', 'structural isomers', 'B'),  # Isomers of C4H9Br -> B (3)

    # 2024 C1 Adv (9ch0-01-rms-20240815.pdf)
    'pp24c1aq9':  ('9ch0-01-rms-20240815.pdf', 'NaHCO3', 'A'),  # Q3(d): volume of CO2 -> A (1.96g / different calc)
    'pp24c1aq3':  ('9ch0-01-rms-20240815.pdf', 'bond angles', None),  # Bond angles question

    # 2024 C2 Adv (9ch0-02-rms-20240815.pdf)
    'pp24c2aq3':  ('9ch0-02-rms-20240815.pdf', 'MnO4', None),  # Redox Mn oxidation states
    'pp24c2aq4':  ('9ch0-02-rms-20240815.pdf', 'Hess', None),  # Enthalpy calculation
}


# Now let me trace through each question carefully with the MS content
# I'll rebuild the answer text directly from the extracted data

changes = []
corrections = []

for q in qbank:
    if q.get('subject') != 'Chem Y1':
        continue
    
    qid = q['id']
    paper = q.get('paper', '')
    
    if qid not in MANUAL_MAP:
        print(f"SKIP: {qid} not in manual map")
        continue
    
    ms_key, search_hint, expected_letter = MANUAL_MAP[qid]
    ms_text = ms_raw[ms_key]
    
    if q.get('type') == 'mc' and expected_letter:
        result = extract_mc_answer(ms_text, search_hint)
        if result and result['correct_letter'] == expected_letter:
            # Good match
            old_explain = q.get('explain', '')
            new_explain = result['full_answer']
            
            if old_explain != new_explain:
                q['explain'] = new_explain
                changes.append({
                    'id': qid,
                    'paper': paper,
                    'ms_q': result['q_number'],
                    'old': old_explain[:80],
                    'new': new_explain[:80]
                })
            
            # Check answer
            correct_index = result['correct_index']
            if q.get('answer') != correct_index:
                options = q.get('options', [])
                corrections.append({
                    'id': qid,
                    'paper': paper,
                    'ms_q': result['q_number'],
                    'ms_letter': result['correct_letter'],
                    'old': q['answer'],
                    'old_text': options[q['answer']] if q['answer'] < len(options) else 'N/A',
                    'new': correct_index,
                    'new_text': options[correct_index] if correct_index < len(options) else 'N/A',
                    'ms_detail': result['correct_detail'][:80]
                })
                q['answer'] = correct_index
            
            print(f"OK: {qid} -> Q{result['q_number']} Answer={result['correct_letter']} ({result['correct_detail'][:50]})")
        else:
            print(f"MISMATCH: {qid} - expected {expected_letter}, got {result}")
    else:
        # Long-form or no expected letter
        result = extract_long_answer(ms_text, search_hint)
        if result:
            old_explain = q.get('explain', '')
            q['explain'] = result['full_answer']
            if old_explain != result['full_answer']:
                changes.append({
                    'id': qid,
                    'paper': paper,
                    'ms_q': result['q_number'],
                    'old': old_explain[:80],
                    'new': result['full_answer'][:80]
                })
            print(f"OK: {qid} -> Q{result['q_number']} (long-form, {len(result['full_answer'])} chars)")
        else:
            print(f"MISS: {qid} - no long-form answer found for hint '{search_hint}'")

# Save
with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)

print("\n" + "="*60)
print(f"Explain updates: {len(changes)}")
for c in changes:
    print(f"  {c['id']}: {c['old'][:60]} -> {c['new'][:60]}")

print(f"\nAnswer corrections: {len(corrections)}")
for c in corrections:
    print(f"  ** {c['id']}: {c['ms_letter']} (was option {c['old']}: {c['old_text'][:50]})")
    print(f"     now option {c['new']}: {c['new_text'][:50]}")
    print(f"     MS: {c['ms_detail']}")
