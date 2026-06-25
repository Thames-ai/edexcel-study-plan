import json
import re

with open('_mark_schemes_raw.json', 'r', encoding='utf-8') as f:
    ms = json.load(f)

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    qbank = json.load(f)

# Map mark scheme keys to paper codes used in qbank
# Key format: 9ma0-XX-rms-YYYYMMDD.pdf
# Paper codes in qbank: "2023 P1", "2023 P2", "2023 S1", "2023 M1", "2024 P1", etc.

def ms_key_to_paper_info(key):
    """Extract paper code and year from mark scheme key"""
    parts = key.replace('.pdf', '').split('-')
    paper_code = parts[1]  # 01, 02, 31, 32
    date_str = parts[3]  # 20230817 or 20240815
    
    year = "2023" if date_str.startswith("2023") else "2024"
    
    paper_map = {
        "01": "P1",  # Pure Paper 1
        "02": "P2",  # Pure Paper 2
        "31": "S1",  # Statistics
        "32": "M1",  # Mechanics
    }
    
    paper = paper_map.get(paper_code, None)
    return year, paper

def get_q_paper_code(q):
    """Get paper code from question, e.g. '2023 P1' -> ('2023', 'P1')"""
    paper = q.get('paper', '')
    # Parse paper like "2023 P1", "2024 S1", etc.
    m = re.match(r'(\d{4})\s+(P[12]|S1|M1)', paper)
    if m:
        return m.group(1), m.group(2)
    return None, None

# Also map subject to paper type
def subject_to_paper_type(subject):
    """Map question subject to paper type"""
    s = subject.lower()
    if 'pure' in s:
        # Need to determine P1 vs P2 based on year/chapter
        return ['P1', 'P2']  # ambiguous
    elif 'stats' in s:
        return ['S1']
    elif 'mech' in s:
        return ['M1']
    return []

# Parse each maths mark scheme
all_ms_data = {}

for key in ms:
    if not key.startswith('9ma0'):
        continue
    
    year, paper = ms_key_to_paper_info(key)
    if not paper:
        continue
    
    paper_label = f"{year} {paper}"
    text = ms[key]
    
    # Find question blocks
    # Each block starts with "Question  Scheme  Marks  AOs"
    positions = []
    for m in re.finditer(r'Question\s+Scheme\s+Marks\s+AOs', text):
        positions.append(m.start())
    
    questions_in_ms = {}
    for i, pos in enumerate(positions):
        if i + 1 < len(positions):
            chunk = text[pos:positions[i+1]]
        else:
            chunk = text[pos:]
        
        # Try to extract question number
        # After "AOs" the next content is typically the question number
        after_aos = chunk[30:]  # skip "Question Scheme Marks AOs"
        
        # Look for question number patterns like "1 " or "2(a)" etc
        q_match = re.match(r'\s*(\d+)', after_aos)
        if q_match:
            q_num = int(q_match.group(1))
            
            # Clean up the text - remove page markers
            chunk_clean = chunk.replace('---PAGE---', ' ')
            chunk_clean = re.sub(r'\s+', ' ', chunk_clean).strip()
            
            if q_num not in questions_in_ms:
                questions_in_ms[q_num] = chunk_clean
    
    all_ms_data[paper_label] = questions_in_ms
    print(f"Parsed {paper_label}: {len(questions_in_ms)} questions found")
    for qn, content in sorted(questions_in_ms.items()):
        print(f"  Q{qn}: {content[:120]}...")

# Save for inspection
with open('_parsed_ms.json', 'w', encoding='utf-8') as f:
    json.dump(all_ms_data, f, indent=2, ensure_ascii=False)
