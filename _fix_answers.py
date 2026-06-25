"""Fix incorrectly matched mark scheme answers with verified correct answers."""
import json

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixes = {
    'pp23c2aq8': {'answer': 2, 'mscheme': "Correct answer is C (4 structural isomers): 1-bromobutane, 2-bromobutane, 1-bromo-2-methylpropane, 2-bromo-2-methylpropane"},
    'pp24c1aq3': {'answer': 2, 'mscheme': "Correct answer is C. CH3COOH (ethanoic acid): CH3 tetrahedral (109.5 deg), COOH trig planar (120 deg)"},
    'pp24c2cq3': {'answer': 1, 'mscheme': "Correct answer is B. But-2-ene: each C of C=C has H and CH3 (2 different groups) = E/Z possible"},
    'pp24c2cq6': {'answer': 1, 'mscheme': "Correct answer is B. Disappearing cross method: time for sulfur precipitate to obscure cross"},
    'pp24c1cq1': {'answer': 1, 'mscheme': "Correct answer is B. P3- gains 3e: 1s2 2s2 2p6 3s2 3p6 (isoelectronic with Ar)"},
    'pp24c1cq2': {'answer': 0, 'mscheme': "Correct answer is A (Mg: 738, 1451, 7733, 10541). Group 2: 1st+2nd IEs close, then big jump for 3rd IE"},
    'pp23c2cq7': {'answer': 1, 'mscheme': "Correct answer is B. Complete oxidation of primary alcohol = carboxylic acid (butanoic acid)"},
}

fixed = 0
for q in data:
    if q['id'] in fixes:
        for k, v in fixes[q['id']].items():
            q[k] = v
        fixed += 1
        print(f"Fixed {q['id']}: answer={q.get('answer')}, ms={q.get('mscheme','')[:60]}")

with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\nFixed {fixed} questions, saved")
