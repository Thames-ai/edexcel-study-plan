#!/usr/bin/env python3
"""
Parse Edexcel Chemistry mark schemes and update curated past paper question bank.
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
    '8ch0-01-rms-20230817.pdf': '2023 C1 Core',   # AS Paper 1 Core Inorganic/Physical
    '8ch0-02-rms-20230817.pdf': '2023 C2 Core',   # AS Paper 2 Core Organic/Physical
    '8ch0-01-rms-20240815.pdf': '2024 C1 Core',
    '8ch0-02-rms-20240815.pdf': '2024 C2 Core',
    '9ch0-01-rms-20230817.pdf': '2023 C1 Adv',    # A2 Paper 1 Advanced Inorganic/Physical
    '9ch0-02-rms-20230817.pdf': '2023 C2 Adv',    # A2 Paper 2 Advanced Organic/Physical
    '9ch0-01-rms-20240815.pdf': '2024 C1 Adv',
    '9ch0-02-rms-20240815.pdf': '2024 C2 Adv',
}

def parse_mark_scheme(text):
    """Parse a mark scheme text into a dict of question_number -> answer_text."""
    # Remove page markers
    text = text.replace('\r\n---PAGE---\r\n', '\n---PAGE---\n')
    
    # Split into question blocks using "Question \n Number \n Answer" pattern
    # We'll look for question number patterns like "1(a)", "2(b)(iii)", etc.
    
    answers = {}
    
    # Pattern to find question blocks - they start with Question Number Answer
    # Find all MC answers first: "The only correct answer is X"
    mc_pattern = re.compile(
        r'(\d+\([a-z]\)(?:\([a-z]+\)(?:\([ivx]+\))?)?)\s*\n\s*\n\s*\n\s*The only correct answer is ([A-D])\s*(?:\(([^)]*)\))?\s*\n(.*?)(?=\n\s*Question\s+Number|\n\s*\(Total for Question|\Z)',
        re.DOTALL
    )
    
    # Pattern for long-form answers
    long_pattern = re.compile(
        r'(\d+\([a-z]\)(?:\([a-z]+\)(?:\([ivx]+\))?)?)\s*\n\s*\n\s*\n\s*An answer that makes reference to (.*?)(?=\n\s*Question\s+Number|\n\s*\(Total for Question|\Z)',
        re.DOTALL
    )
    
    # Alternative: split text by "Question Number" headers
    # More robust approach: find question numbers and extract content until next one
    q_blocks = re.split(r'(?=Question\s+Number\s+Answer)', text)
    
    for block in q_blocks:
        # Extract question number
        q_match = re.search(r'(\d+)\(([a-z])\)((?:\(([a-z]+)\))?(?:\(([ivx]+)\))?)?', block)
        if not q_match:
            continue
        
        q_num = q_match.group(1)
        q_letter = q_match.group(2)
        q_sub = q_match.group(3) or ''
        q_subsub = q_match.group(4) or ''
        
        q_id = f"{q_num}({q_letter})"
        if q_sub:
            q_id += f"({q_sub})"
        if q_subsub:
            q_id += f"({q_subsub})"
        
        # Check for MC answer
        mc_match = re.search(r'The only correct answer is ([A-D])\s*(?:\(([^)]*)\))?', block)
        if mc_match:
            correct_letter = mc_match.group(1)
            correct_detail = mc_match.group(2) or ''
            
            # Get explanations for wrong answers
            wrong_explanations = []
            for wm in re.finditer(r'([A-D]) is not correct because (.*?)(?=\n\s*[A-D] is not correct|\n\s*\(\d+\)\s*\n|\Z)', block, re.DOTALL):
                wrong_explanations.append(f"{wm.group(1)}: {wm.group(2).strip()}")
            
            answer_text = f"The only correct answer is {correct_letter}"
            if correct_detail:
                answer_text += f" ({correct_detail})"
            if wrong_explanations:
                answer_text += ". " + "; ".join(wrong_explanations)
            
            # Clean up whitespace
            answer_text = re.sub(r'\s+', ' ', answer_text).strip()
            
            answers[q_id] = {
                'type': 'mc',
                'correct_letter': correct_letter,
                'correct_detail': correct_detail,
                'full_answer': answer_text
            }
        else:
            # Long-form answer
            # Extract the answer content between "Answer" and "Additional Guidance" or "Mark"
            answer_section = re.search(r'Answer\s*(?:\s+Additional Guidance)?\s*Mark\s*\n(.*?)(?=\n\s*\(Total for Question|\Z)', block, re.DOTALL)
            if answer_section:
                answer_text = answer_section.group(1).strip()
                # Clean up
                answer_text = re.sub(r'\n\s*\n', '\n', answer_text)
                answer_text = re.sub(r'^\s+', '', answer_text, flags=re.MULTILINE)
                # Remove trailing mark indicators like (1), (2), etc and "Question Number Answer Additional Guidance Mark"
                answer_text = re.sub(r'Question\s+Number.*$', '', answer_text, flags=re.DOTALL)
                answer_text = answer_text.strip()
                
                if answer_text:
                    answers[q_id] = {
                        'type': 'long',
                        'full_answer': answer_text
                    }
    
    return answers


def extract_all_ms_answers(text):
    """
    More robust extraction: find each question number heading and its answer content.
    Uses the structure: Question Number / Answer / [Additional Guidance] / Mark
    """
    answers = {}
    
    # Normalize whitespace
    text = re.sub(r'\r\n', '\n', text)
    
    # Find all positions where question numbers appear (like "1(a)", "2(b)(iii)")
    # Preceded by "Question Number Answer" or similar header
    q_positions = []
    for m in re.finditer(r'(?:Question\s+Number\s+)?(\d+\([a-z]\)(?:\([^)]+\))*)', text):
        q_positions.append((m.start(), m.group(1)))
    
    for i, (pos, q_id) in enumerate(q_positions):
        # Get text from this position to the next question or end
        if i + 1 < len(q_positions):
            end_pos = q_positions[i+1][0]
        else:
            end_pos = len(text)
        
        block = text[pos:end_pos]
        
        # Check for MC answer
        mc_match = re.search(r'The only correct answer is ([A-D])\s*(?:\(([^)]*)\))?', block)
        if mc_match:
            correct_letter = mc_match.group(1)
            correct_detail = mc_match.group(2) or ''
            
            # Get wrong answer explanations
            wrong_exps = []
            for wm in re.finditer(r'([A-D]) is not correct because (.*?)(?=\s*[A-D] is not correct|\n\s*\(\d+\)\s*\n|\Z)', block, re.DOTALL):
                wrong_exps.append(f"{wm.group(1)}: {wm.group(2).strip()}")
            
            answer_text = f"The only correct answer is {correct_letter}"
            if correct_detail:
                answer_text += f" ({correct_detail})"
            for we in wrong_exps:
                answer_text += f". {we}"
            
            answer_text = re.sub(r'\s+', ' ', answer_text).strip()
            
            answers[q_id] = {
                'type': 'mc',
                'correct_letter': correct_letter,
                'correct_detail': correct_detail,
                'full_answer': answer_text
            }
        else:
            # Long-form: extract answer bullet points and example calculations
            # Find content after "Answer" keyword
            ans_match = re.search(r'Answer\s*(?:\s+Additional Guidance\s+Mark|\s+Mark)?\s*\n(.*?)(?=\n\s*Question\s+Number|\n\s*\(Total\s+for\s+Question|\Z)', block, re.DOTALL)
            if ans_match:
                answer_text = ans_match.group(1).strip()
                # Remove trailing "(1)" type marks except within calculations
                # Clean whitespace
                answer_text = re.sub(r'\n{3,}', '\n\n', answer_text)
                lines = [l.strip() for l in answer_text.split('\n') if l.strip()]
                # Filter out "Additional Guidance" and "Mark" header lines
                lines = [l for l in lines if l not in ('Additional Guidance', 'Mark', 'Answer')]
                answer_text = '\n'.join(lines)
                
                if answer_text:
                    answers[q_id] = {
                        'type': 'long',
                        'full_answer': answer_text
                    }
    
    return answers


# Parse all chemistry mark schemes
all_ms = {}
for key, paper_name in chem_ms_keys.items():
    text = ms_raw[key]
    parsed = extract_all_ms_answers(text)
    all_ms[paper_name] = parsed
    print(f"\n=== {key} -> {paper_name} ===")
    for qid, ans in sorted(parsed.items()):
        if ans['type'] == 'mc':
            print(f"  {qid}: MC Answer={ans['correct_letter']} ({ans.get('correct_detail','')[:60]})")
        else:
            print(f"  {qid}: Long-form ({len(ans['full_answer'])} chars)")

# Now match questions to mark scheme answers
# Question ID format: pp23c1cq1 -> 2023, C1 Core, Q1
# pp24c2aq3 -> 2024, C2 Adv, Q3

def decode_question_id(qid):
    """Decode question ID to extract year, paper, question components."""
    # Pattern: pp{YY}{paper_code}q{number}{optional_letter}
    m = re.match(r'pp(\d{2})(c\d[ac])q(\d+)([a-z]?)', qid)
    if not m:
        return None
    year_short = m.group(1)  # e.g., "23"
    paper_code = m.group(2)  # e.g., "c1c" or "c2a"
    q_number = int(m.group(3))
    q_subletter = m.group(4) or ''
    
    year = '20' + year_short  # e.g., "2023"
    
    # Map paper_code to paper name
    paper_map = {
        'c1c': 'C1 Core',
        'c2c': 'C2 Core',
        'c1a': 'C1 Adv',
        'c2a': 'C2 Adv',
    }
    paper = paper_map.get(paper_code, '')
    
    paper_full = f"{year} {paper}"
    
    # Build mark scheme question ID
    if q_subletter:
        ms_qid = f"{q_number}({q_subletter})"
    else:
        # Question without sub-letter - might be a full question
        ms_qid = str(q_number)
    
    return paper_full, ms_qid


def build_ms_qid_variants(q_number, q_subletter=''):
    """Build possible mark scheme question IDs to search for."""
    variants = []
    if q_subletter:
        # Could be "1(a)" or "1(a)(i)" etc.
        variants.append(f"{q_number}({q_subletter})")
        # Also try with (i) appended
        variants.append(f"{q_number}({q_subletter})(i)")
    else:
        # Whole question like Q7 - might match Q7(a), Q7(c), etc.
        variants.append(str(q_number))
        # Also common sub-questions
        for letter in 'abcdefgh':
            variants.append(f"{q_number}({letter})")
            for sub in ['i', 'ii', 'iii', 'iv', 'v']:
                variants.append(f"{q_number}({letter})({sub})")
    return variants


# Process each Chem Y1 question
changes = []
corrections = []

for q in qbank:
    if q.get('subject') != 'Chem Y1':
        continue
    
    qid = q['id']
    paper = q.get('paper', '')
    
    # Decode the paper field
    # Format: "2023 C1 Core", "2024 C2 Adv", etc.
    paper_parts = paper.split()
    if len(paper_parts) < 3:
        continue
    
    year = paper_parts[0]
    paper_name = ' '.join(paper_parts[1:])
    
    # Find the right mark scheme
    ms_paper_key = f"{year} {paper_name}"
    if ms_paper_key not in all_ms:
        print(f"WARNING: No mark scheme found for paper '{ms_paper_key}' (question {qid})")
        continue
    
    ms = all_ms[ms_paper_key]
    
    # Extract question number from ID
    m = re.match(r'pp\d{2}c\d[ac]q(\d+)([a-z]?)', qid)
    if not m:
        continue
    
    q_number = int(m.group(1))
    q_subletter = m.group(2) or ''
    
    # Try to find matching mark scheme entry
    matched_ms = None
    matched_qid = None
    
    # Direct match
    if q_subletter:
        ms_qid = f"{q_number}({q_subletter})"
        if ms_qid in ms:
            matched_ms = ms[ms_qid]
            matched_qid = ms_qid
        else:
            # Try with (i) subpart
            for sub in ['i', 'ii', 'iii', 'iv', 'v']:
                test_qid = f"{q_number}({q_subletter})({sub})"
                if test_qid in ms:
                    matched_ms = ms[test_qid]
                    matched_qid = test_qid
                    break
    else:
        # Try common patterns
        for letter in 'abcdefgh':
            test_qid = f"{q_number}({letter})"
            if test_qid in ms:
                matched_ms = ms[test_qid]
                matched_qid = test_qid
                break
    
    if not matched_ms:
        print(f"WARNING: No mark scheme match for {qid} (tried {q_number}({q_subletter}) etc.) in {ms_paper_key}")
        continue
    
    # Update explain field
    old_explain = q.get('explain', '')
    new_explain = matched_ms['full_answer']
    
    if old_explain != new_explain:
        q['explain'] = new_explain
        changes.append({
            'id': qid,
            'paper': paper,
            'ms_qid': matched_qid,
            'old_explain': old_explain[:80],
            'new_explain': new_explain[:80],
            'type': 'explain_update'
        })
    
    # For MC questions, check and correct answer
    if matched_ms['type'] == 'mc' and q.get('type') == 'mc':
        correct_letter = matched_ms['correct_letter']
        # Convert letter to index: A=0, B=1, C=2, D=3
        correct_index = ord(correct_letter) - ord('A')
        current_answer = q.get('answer')
        
        if current_answer != correct_index:
            corrections.append({
                'id': qid,
                'paper': paper,
                'ms_qid': matched_qid,
                'old_answer': current_answer,
                'old_answer_text': q['options'][current_answer] if current_answer < len(q['options']) else 'N/A',
                'new_answer': correct_index,
                'new_answer_text': q['options'][correct_index] if correct_index < len(q['options']) else 'N/A',
                'correct_letter': correct_letter,
                'ms_detail': matched_ms.get('correct_detail', '')[:100]
            })
            q['answer'] = correct_index

# Write updated qbank
with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)

# Print summary
print("\n" + "="*60)
print("SUMMARY OF CHANGES")
print("="*60)

print(f"\nTotal explain fields updated: {len(changes)}")
for c in changes:
    print(f"  {c['id']} ({c['paper']}): {c['ms_qid']}")
    print(f"    OLD: {c['old_explain']}")
    print(f"    NEW: {c['new_explain']}")

print(f"\nTotal answer corrections: {len(corrections)}")
for c in corrections:
    print(f"  ** CORRECTION ** {c['id']} ({c['paper']}): {c['ms_qid']}")
    print(f"    Old answer: {c['old_answer']} ({c['old_answer_text']})")
    print(f"    New answer: {c['new_answer']} ({c['new_answer_text']}) [Mark scheme: {c['correct_letter']}]")
    print(f"    MS detail: {c['ms_detail']}")
