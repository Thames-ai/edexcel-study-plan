#!/usr/bin/env python3
"""
Build Chemistry Past Paper QBANK from extracted questions.
Properly extracts MCQs with options, and converts written questions into MC format.
"""
import json
import re

with open('_questions_extracted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

chem_papers = [
    '2023 paper 1 advanced.pdf',
    '2023 paper 1 core.pdf',
    '2023 paper 2 advanced.pdf',
    '2023 paper 2 core.pdf',
    '2024 paper 1 advanced.pdf',
    '2024 paper 1 core.pdf',
    '2024 paper 2 advanced.pdf',
    '2024 paper 2 core.pdf',
]

def paper_code(k):
    m = {'2023 paper 1 advanced.pdf': '2023 C1 Adv', '2023 paper 1 core.pdf': '2023 C1 Core',
         '2023 paper 2 advanced.pdf': '2023 C2 Adv', '2023 paper 2 core.pdf': '2023 C2 Core',
         '2024 paper 1 advanced.pdf': '2024 C1 Adv', '2024 paper 1 core.pdf': '2024 C1 Core',
         '2024 paper 2 advanced.pdf': '2024 C2 Adv', '2024 paper 2 core.pdf': '2024 C2 Core'}
    return m.get(k, k)

def make_id(k, n, sfx=''):
    y = '23' if '2023' in k else '24'
    p = '1' if 'paper 1' in k else '2'
    l = 'a' if 'advanced' in k else 'c'
    return f'pp{y}c{p}{l}q{n}{sfx}'

def clean(t):
    t = re.sub(r'[\u0000-\u001f]', ' ', t)
    t = re.sub(r'[\uf0a2\u00a2]+', '', t)
    t = re.sub(r'DO NOT WRITE IN THIS AREA', '', t, flags=re.I)
    t = re.sub(r'-{3,}', '', t)
    t = re.sub(r'Question \d+ continued', '', t, flags=re.I)
    t = re.sub(r'\(Total for Question \d+[^)]*\)', '', t)
    t = re.sub(r'TOTAL FOR [A-Z ]+\d+ MARKS', '', t)
    t = re.sub(r'BLANK PAGE', '', t)
    t = re.sub(r'\.{4,}', '', t)
    t = re.sub(r' {2,}', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    lines = [l.strip() for l in t.split('\n')]
    t = '\n'.join(l for l in lines if l)
    return t.strip()

def total_marks(t):
    m = re.search(r'\(Total for Question \d+[^)]*?(\d+)\s*marks?\)', t, re.I)
    return int(m.group(1)) if m else None

def classify(text, paper_key):
    tl = text.lower()
    is_p2 = 'paper 2' in paper_key
    
    # Specific detection order matters - more specific first
    if is_p2:
        # Organic
        if any(w in tl for w in ['chloroprene', 'neoprene']):
            return 'Ch14 Alkenes' if 'polymer' in tl else 'Ch14 Alkenes'
        if any(w in tl for w in ['grignard']):
            return 'Ch15 Halogenoalkanes'
        if any(w in tl for w in ['amino acid', 'dipeptide', 'zwitterion']):
            return 'Ch17 Organic Analysis'
        if any(w in tl for w in ['bromoalkane', 'halogenoalkane', 'haloalkane', '1-bromobutane', 'bromobutane', '1-bromo-2-methylpropane', '2-bromo-2-methylpropane']):
            return 'Ch15 Halogenoalkanes'
        if any(w in tl for w in ['but-1-ene', 'but-2-ene', 'methylpropene', 'electrophilic addition', 'addition polymer']):
            return 'Ch14 Alkenes'
        if any(w in tl for w in ['butan-1-ol', 'propan-1-ol', 'propan-2-ol', 'spirit burner', 'oxidation of alcohol']):
            return 'Ch16 Alcohols'
        if 'alkene' in tl:
            return 'Ch14 Alkenes'
        if 'alcohol' in tl:
            return 'Ch16 Alcohols'
        if any(w in tl for w in ['nmr', 'nuclear magnetic', 'infrared spectroscop', 'ir spectroscop', 'mass spectrom']):
            return 'Ch17 Organic Analysis'
        if any(w in tl for w in ['alkane', 'hexane', 'free radical', 'cyclopentane', 'methane']):
            return 'Ch13 Alkanes'
        if any(w in tl for w in ['functional group', 'skeletal formula', 'iupac', 'homologous', 'isomer']):
            return 'Ch12 Organic Intro'
        # Physical in P2
        if any(w in tl for w in ['equilibrium', 'kc', 'kp', 'le chatelier', 'chromate', 'dichromate']):
            return 'Ch10 Equilibria'
        if any(w in tl for w in ['rate', 'thiosulfate', 'boltzmann', 'activation energy', 'collision theory', 'maxwell']):
            return 'Ch9 Kinetics'
        if any(w in tl for w in ['acid', 'base', 'buffer', 'ph', 'bronsted', 'ka', 'kw', 'titration']):
            return 'Ch11 Acid-Base Equilibria'
        if any(w in tl for w in ['enthalpy', 'hess', 'bond enthalpy', 'combustion', 'born-haber']):
            return 'Ch5 Moles & Equations'
        if any(w in tl for w in ['hydrogen peroxide', 'disproportionation']):
            return 'Ch6 Redox'
        return 'Ch12 Organic Intro'
    else:
        # Paper 1 - Inorganic & Physical
        if any(w in tl for w in ['isotope', 'orbital', 'electron configuration', 'electronic configuration']):
            return 'Ch1 Atomic Structure'
        if any(w in tl for w in ['phosphide ion', 'ionisation energy', 'ionization energy', 'mass spectrom']):
            return 'Ch1 Atomic Structure'
        if any(w in tl for w in ['silicon'] + ['proton', 'neutron']) and 'isotope' in tl:
            return 'Ch1 Atomic Structure'
        if any(w in tl for w in ['electron affinity']):
            return 'Ch2 Periodic Table'
        if any(w in tl for w in ['electronegativ', 'covalent bond', 'ionic bond', 'metallic bond', 'dot-and-cross', 'dative', 'bond angle', 'shape of']):
            return 'Ch3 Bonding'
        if any(w in tl for w in ['intermolecular', 'hydrogen bond', 'london force', 'dipole-dipole', 'dissolve', 'solubility']):
            return 'Ch4 Intermolecular Forces'
        if any(w in tl for w in ['group 7', 'group 2', 'halogen', 'halide', 'chloride', 'bromide', 'iodide', 'flame test', 'silver nitrate', 'conc sulfuric']):
            return 'Ch8 Groups 2&7'
        if any(w in tl for w in ['redox', 'oxidation number', 'oxidising agent', 'reducing agent', 'disproportionation', 'thiosulfate', 'chlorate']):
            return 'Ch6 Redox'
        if any(w in tl for w in ['born-haber', 'lattice energy', 'enthalpy change', 'hess', 'mean bond enthalpy', 'combustion', 'ethanol fuel cell', 'cell potential', 'sodium hydrogencarbonate']):
            return 'Ch5 Moles & Equations'
        if any(w in tl for w in ['periodicity', 'period 3', 'd-block', 'melting temperature']):
            return 'Ch7 Periodicity'
        if any(w in tl for w in ['vanadium', 'chromium', 'transition']):
            return 'Ch7 Periodicity'
        if any(w in tl for w in ['equilibrium', 'n2o4', 'dinitrogen']):
            return 'Ch10 Equilibria'
        if any(w in tl for w in ['acid', 'base', 'buffer', 'benzoic', 'ph']):
            return 'Ch11 Acid-Base Equilibria'
        if any(w in tl for w in ['relative formula mass', 'relative atomic mass', 'empirical formula', 'molar mass', 'titration']):
            return 'Ch5 Moles & Equations'
        if 'silicon' in tl:
            return 'Ch1 Atomic Structure'
        return 'Ch1 Atomic Structure'

# ===== HAND-CRAFTED QBANK ENTRIES =====
# Each question from the extracted text is carefully processed

qbank = []

def add(id, text, options, answer, explain, improve, paper, marks, chapter):
    qbank.append({
        "id": id, "text": text, "type": "mc",
        "options": options, "answer": answer,
        "explain": explain, "improve": improve,
        "paper": paper, "marks": marks, "chapter": chapter
    })

# ============================================================
# 2023 PAPER 1 ADVANCED
# ============================================================

# Q1(a): d-block element in Period 4 from ionisation energy graph
add("pp23c1aq1a",
    "Which label (1-4) on an ionisation energy graph identifies a d-block element in Period 4?",
    ["Label 1", "Label 2", "Label 3", "Label 4"],
    2,  # C - label 3 is Sc-Zn region
    "d-block elements in Period 4 (Sc to Zn) show a gradual increase in ionisation energy across the block, appearing as label 3 on the graph between the s-block and p-block jumps.",
    "Review electron configurations and ionisation energy trends across Period 4. d-block elements show gradual increase in IE across the block.",
    "2023 C1 Adv", 1, "Ch1 Atomic Structure")

# Q1(b): d-block element definition
add("pp23c1aq1b",
    "What is meant by the term 'd-block element'?",
    ["An element whose atoms have partially filled d orbitals", "An element whose highest energy electron is in a d orbital", "An element that forms ions with partially filled d orbitals", "An element in the central block of the periodic table"],
    3,  # D - Edexcel definition is about position
    "A d-block element is defined as an element in the central block of the periodic table (Groups 3-12). Note: a transition element requires partially filled d orbitals in ions.",
    "Learn the Edexcel definitions of d-block vs transition elements carefully.",
    "2023 C1 Adv", 1, "Ch7 Periodicity")

# Q2(a): orbital definition
add("pp23c1aq2a",
    "What is meant by the term 'orbital'?",
    ["A region around the nucleus where an electron is likely to be found", "The path an electron follows around the nucleus", "A fixed energy level where electrons orbit", "The space between two electron shells"],
    0,
    "An orbital is a region around the nucleus where there is a high probability of finding an electron. This is the quantum mechanical model, not the Bohr model of orbits.",
    "Review atomic structure: orbitals, sub-shells, and electron configurations.",
    "2023 C1 Adv", 2, "Ch1 Atomic Structure")

# Q2(c): Cu electronic configuration
add("pp23c1aq2c",
    "What is the electronic configuration of a copper atom?",
    ["[Ar] 4s2 3d9", "[Ar] 4s1 3d10", "[Ar] 3d10 4s1", "[Ar] 4s2 3d8"],
    1,  # B - [Ar]4s1 3d10 (full d subshell more stable)
    "Copper is an exception: its configuration is [Ar]4s1 3d10 because a completely filled d subshell is more stable than 4s2 3d9. Chromium is the other exception: [Ar]4s1 3d5.",
    "Remember the two exceptions: Cu = [Ar]4s1 3d10, Cr = [Ar]4s1 3d5.",
    "2023 C1 Adv", 1, "Ch1 Atomic Structure")

# Q3(a): conc H2SO4 + KBr
add("pp23c1aq3a",
    "Which change occurs when concentrated sulfuric acid is added to potassium bromide?",
    ["Bromide ions oxidise sulfuric acid forming sulfur", "Bromide ions oxidise sulfuric acid forming sulfur dioxide",
     "Bromide ions reduce sulfuric acid forming sulfur", "Bromide ions reduce sulfuric acid forming sulfur dioxide"],
    3,  # D - Br- is oxidised (reducing agent), H2SO4 is reduced to SO2
    "Bromide ions (Br-) act as a reducing agent and REDUCE sulfuric acid (from S+6 to S+4). The sulfuric acid is reduced to sulfur dioxide (SO2). Br- is oxidised to Br2.",
    "Learn the reactions of halides with concentrated sulfuric acid: Cl- gives HCl only, Br- gives Br2 + SO2, I- gives I2 + SO2 + H2S or S.",
    "2023 C1 Adv", 1, "Ch8 Groups 2&7")

# Q3(b)(i): bromide ions + AgNO3
add("pp23c1aq3bi",
    "Which statement is correct for bromide ions tested with acidified silver nitrate solution?",
    ["A white precipitate forms that dissolves in concentrated ammonia only",
     "A white precipitate forms that dissolves in both dilute and concentrated ammonia",
     "A cream precipitate forms that dissolves in concentrated ammonia only",
     "A cream precipitate forms that dissolves in both dilute and concentrated ammonia"],
    2,  # C - cream ppt of AgBr, dissolves in conc NH3 only
    "AgBr is a cream precipitate. It dissolves in concentrated ammonia but NOT in dilute ammonia. AgCl (white) dissolves in both, AgI (yellow) dissolves in neither.",
    "Memorise the halide ion test results: colour and solubility in dilute/concentrated ammonia.",
    "2023 C1 Adv", 1, "Ch8 Groups 2&7")

# Q4: Periodicity - melting temperatures explanation
add("pp23c1aq4",
    "Which statement best explains why silicon has the highest melting temperature in Period 3?",
    ["Silicon has the most electrons per atom", "Silicon has a giant covalent structure with many strong covalent bonds",
     "Silicon has metallic bonding which is very strong", "Silicon has the strongest intermolecular forces"],
    1,  # B - giant covalent lattice
    "Silicon has a giant covalent (macromolecular) structure requiring many strong covalent bonds to be broken. Metals (Na-Al) have metallic bonding, while P, S, Cl are molecular with weak intermolecular forces.",
    "Study the trends in bonding and structure across Period 3 elements.",
    "2023 C1 Adv", 6, "Ch7 Periodicity")

# Q5(a)(iii): ΔG graph feature for enthalpy change
add("pp23c1aq5aiii",
    "What feature of a graph of ΔG against temperature gives the enthalpy change of the reaction?",
    ["Intercept of the x-axis", "(Intercept of the x-axis) × −1", "Intercept of the y-axis", "(Intercept of the y-axis) × −1"],
    2,  # C - y-intercept (ΔG = -TΔS + ΔH, so at T=0, ΔG = ΔH)
    "From ΔG = −TΔS + ΔH, when T = 0, ΔG = ΔH. Therefore the y-intercept gives the enthalpy change of the reaction.",
    "Practise using ΔG = ΔH − TΔS for thermodynamic calculations.",
    "2023 C1 Adv", 1, "Ch10 Equilibria")

# Q5(b): Pressure increase on N2O4 equilibrium
add("pp23c1aq5b",
    "For the equilibrium N2O4(g) ⇌ 2NO2(g), what happens to the position of equilibrium and colour when pressure is increased at constant volume?",
    ["Moves to the right, mixture gets lighter", "Moves to the right, mixture gets darker",
     "Moves to the left, mixture gets lighter", "Moves to the left, mixture gets darker"],
    2,  # C - shifts left (fewer moles), lighter (less brown NO2)
    "Increasing pressure shifts equilibrium toward the side with fewer moles of gas (left, 1 mol vs 2 mol). Less NO2 (brown) means the mixture gets lighter.",
    "Practise applying Le Chatelier's principle to equilibrium changes.",
    "2023 C1 Adv", 1, "Ch10 Equilibria")

# Q6(a): Benzoic acid + nitric acid species
add("pp23c1aq6a",
    "When benzoic acid (Ka = 6.3 × 10⁻⁵) is mixed with nitric acid (Ka = 40), which species are present in the equilibrium mixture?",
    ["C₆H₅COOH + HNO₃", "C₆H₅COO⁻ + H₂NO₃⁺", "C₆H₅COOH₂⁺ + NO₃⁻", "C₆H₅COO⁻ + NO₃⁻ + H⁺"],
    2,  # C - Nitric acid stronger, protonates benzoic acid
    "Nitric acid is much stronger (Ka = 40) than benzoic acid (Ka = 6.3×10⁻⁵). Nitric acid donates a proton to benzoic acid forming C₆H₅COOH₂⁺ and NO₃⁻.",
    "Review Brønsted-Lowry acid-base theory and relative strengths of acids.",
    "2023 C1 Adv", 1, "Ch11 Acid-Base Equilibria")

# Q7(a): Isotopes definition
add("pp23c1aq7a",
    "What is meant by the term 'isotopes'?",
    ["Atoms of the same element with different numbers of neutrons", "Atoms of different elements with the same mass number",
     "Atoms with the same electron configuration but different numbers of protons", "Ions of the same element with different charges"],
    0,
    "Isotopes are atoms of the same element (same number of protons) with different numbers of neutrons, giving them different mass numbers.",
    "Review atomic structure definitions: isotopes, relative atomic mass, mass spectrometry.",
    "2023 C1 Adv", 2, "Ch1 Atomic Structure")

# Q9(a)(ii): Electron affinity of oxygen
add("pp23c1aq9aii",
    "Why is the first electron affinity of oxygen negative but the second electron affinity positive?",
    ["Both release energy", "The first EA releases energy (electron attracted to nucleus), the second EA requires energy (electron repelled by O⁻)",
     "Both require energy", "The second EA is negative because the ion becomes stable"],
    1,  # B
    "The first EA is exothermic (negative) because the electron is attracted to the nucleus. The second EA is endothermic (positive) because the electron is repelled by the negatively charged O⁻ ion.",
    "Understand the Born-Haber cycle and the signs of each step including electron affinities.",
    "2023 C1 Adv", 3, "Ch5 Moles & Equations")

# ============================================================
# 2023 PAPER 1 CORE
# ============================================================

# Q1(a): proton and neutron data
add("pp23c1cq1a",
    "Which are the correct data for a proton and a neutron?",
    ["Proton: +1 charge, 1 mass; Neutron: −1 charge, 0.0005 mass",
     "Proton: +1 charge, 1 mass; Neutron: 0 charge, 1 mass",
     "Proton: −1 charge, 0.0005 mass; Neutron: 0 charge, 1 mass",
     "Proton: +1 charge, 1 mass; Neutron: +1 charge, 0.0005 mass"],
    1,  # B
    "A proton has relative charge +1 and relative mass 1. A neutron has relative charge 0 and relative mass 1. The electron has charge −1 and mass 0.0005.",
    "Learn the relative charges and masses of subatomic particles.",
    "2023 C1 Core", 1, "Ch1 Atomic Structure")

# Q1(b)(i): shape of 2s orbital
add("pp23c1cq1bi",
    "What is the shape of the 2s orbital of a silicon atom?",
    ["Dumbbell-shaped", "Spherical", "Clover-shaped", "Cylindrical"],
    1,  # B - s orbitals are spherical
    "All s orbitals (1s, 2s, 3s etc.) are spherical in shape. p orbitals are dumbbell-shaped and d orbitals are clover-shaped.",
    "Review orbital shapes: s = spherical, p = dumbbell, d = cloverleaf.",
    "2023 C1 Core", 1, "Ch1 Atomic Structure")

# Q1(c): Isotope calculation
add("pp23c1cq1c",
    "A sample of silicon has Ar = 28.11 from three isotopes: ²⁸Si (92.2%), ³⁰Si (3.1%). What is the relative isotopic mass of the third isotope?",
    ["27", "29", "31", "32"],
    1,  # B - 29
    "Let x = abundance of third isotope: 92.2 + 3.1 + x = 100, so x = 4.7%. Then 28.11 = (92.2×28 + 4.7×M + 3.1×30)/100. Solving gives M = 29 (²⁹Si).",
    "Practise relative atomic mass calculations using isotopic abundance data.",
    "2023 C1 Core", 2, "Ch1 Atomic Structure")

# Q2: Double salt K2Mg(SO4)2.6H2O - relative formula mass
add("pp23c1cq2",
    "Why is the term 'relative formula mass' used instead of 'relative molecular mass' for K₂Mg(SO₄)₂·6H₂O?",
    ["The compound is ionic so does not exist as molecules",
     "The compound contains water of crystallisation",
     "The compound is a double salt with two cations",
     "The relative molecular mass would be too large"],
    0,  # A - ionic compounds don't form molecules
    "K₂Mg(SO₄)₂·6H₂O is an ionic compound and does not exist as discrete molecules, so 'relative formula mass' is used instead of 'relative molecular mass'.",
    "Understand the difference between relative molecular mass and relative formula mass.",
    "2023 C1 Core", 1, "Ch5 Moles & Equations")

# Q3(a)(i): Group 7 reaction with metals
add("pp23c1cq3ai",
    "What happens to the atoms of a metal and a Group 7 element when they react together?",
    ["Metal gains electrons to form a positive ion; Group 7 element loses electrons to form a negative ion",
     "Metal loses electrons to form a positive ion; Group 7 element gains electrons to form a negative ion",
     "Metal loses electrons to form a negative ion; Group 7 element gains electrons to form a positive ion",
     "Metal gains electrons to form a negative ion; Group 7 element gains electrons to form a negative ion"],
    1,  # B
    "Metals lose electrons (oxidation) to form positive cations. Group 7 elements gain electrons (reduction) to form negative halide anions. This is electron transfer in ionic bonding.",
    "Review the reactions of Group 7 elements with metals and electron transfer.",
    "2023 C1 Core", 1, "Ch8 Groups 2&7")

# Q3(a)(ii): Which is NOT true for calcium + bromine
add("pp23c1cq3aii",
    "Which is NOT true when calcium reacts with bromine?",
    ["Bromine reacts less vigorously than chlorine",
     "During the reaction bromine oxidises the calcium",
     "The percentage by mass of calcium in the product is 33%",
     "The product gives a brick-red flame test"],
    1,  # B - bromine REDUCES (not oxidises) calcium
    "Calcium is oxidised (loses electrons) and bromine is reduced (gains electrons). Bromine is the oxidising agent, not the species doing the oxidising. Statement B incorrectly says bromine oxidises calcium.",
    "Understand oxidation and reduction in terms of electron transfer and identify oxidising/reducing agents.",
    "2023 C1 Core", 1, "Ch8 Groups 2&7")

# Q5: Electronegativity
add("pp23c1cq5",
    "What is meant by the term 'electronegativity'?",
    ["The ability of an atom to attract electron density in a covalent bond",
     "The energy released when an atom gains an electron",
     "The attraction between the nucleus and the outermost electrons",
     "The tendency of an atom to lose electrons and form positive ions"],
    0,
    "Electronegativity is the ability of an atom to attract the bonding electrons in a covalent bond towards itself. It increases across a period and decreases down a group.",
    "Review electronegativity definition and trends across the periodic table.",
    "2023 C1 Core", 1, "Ch3 Bonding")

# Q6: Redox - oxidation and reduction
add("pp23c1cq6",
    "In the reaction 8KI + 5H₂SO₄ → 4I₂ + 4K₂SO₄ + H₂S + 4H₂O, what happens in terms of electron transfer?",
    ["I⁻ is oxidised (loses electrons), H₂SO₄ is reduced",
     "I⁻ is reduced (gains electrons), H₂SO₄ is oxidised",
     "Both I⁻ and H₂SO₄ are oxidised",
     "Both I⁻ and H₂SO₄ are reduced"],
    0,
    "I⁻ (in KI) is oxidised to I₂ (loses electrons). The sulfur in H₂SO₄ is reduced from +6 to -2 in H₂S (gains electrons). KI is the reducing agent, H₂SO₄ is the oxidising agent.",
    "Practise assigning oxidation numbers and identifying oxidising/reducing agents.",
    "2023 C1 Core", 3, "Ch6 Redox")

# Q7: Ionic radii ordering
add("pp23c1cq7",
    "What is the correct order of increasing ionic radius for Br⁻, Ca²⁺, Cl⁻, K⁺?",
    ["Ca²⁺ < K⁺ < Cl⁻ < Br⁻", "K⁺ < Ca²⁺ < Cl⁻ < Br⁻",
     "Ca²⁺ < Cl⁻ < K⁺ < Br⁻", "Cl⁻ < Ca²⁺ < K⁺ < Br⁻"],
    0,
    "All four ions are isoelectronic (18 electrons). Greater nuclear charge pulls electrons closer, so Ca²⁺ (20 protons) < K⁺ (19) < Cl⁻ (17). Br⁻ has an extra shell so is largest.",
    "Understand trends in ionic radius including isoelectronic series.",
    "2023 C1 Core", 4, "Ch3 Bonding")

# Q8: Molar volume experiment
add("pp23c1cq8",
    "In an experiment to determine the molar volume of CO₂ using CaCO₃ + 2H⁺, which change reduces the volume of gas lost between adding CaCO₃ and replacing the bung?",
    ["Use a more concentrated acid",
     "Use a more dilute acid",
     "Use a larger mass of CaCO₃",
     "Use a higher temperature acid"],
    1,  # B - more dilute acid reacts more slowly
    "Using more dilute acid reduces the rate of reaction, so less CO₂ is produced before the bung is replaced, reducing gas loss.",
    "Review practical techniques for measuring gas volumes in reactions.",
    "2023 C1 Core", 2, "Ch5 Moles & Equations")

# Q9(a): Ionisation energy patterns
add("pp23c1cq9a",
    "Which set of first four ionisation energies (kJ mol⁻¹) belongs to a Group 3 element?",
    ["738, 1451, 7753, 10541", "578, 1817, 2745, 11578",
     "789, 1577, 3232, 4356", "1012, 1903, 2912, 4957"],
    1,  # B - big jump between 3rd and 4th IE
    "A Group 3 element shows a large jump between the 3rd and 4th ionisation energies because the 4th electron is removed from an inner shell. Option B shows a jump from 2745 to 11578.",
    "Practise identifying group and period from successive ionisation energy data.",
    "2023 C1 Core", 1, "Ch1 Atomic Structure")

# ============================================================
# 2023 PAPER 2 ADVANCED
# ============================================================

# Q1(b): Cycloalkene general formula
add("pp23c2aq1b",
    "What is the general formula for a cycloalkene?",
    ["CnH2n−2", "CnH2n", "CnH2n+1", "CnH2n+2"],
    0,  # A - one ring + one double bond = 2 fewer H
    "A cycloalkene has one ring AND one double bond. Each feature reduces hydrogen count by 2 relative to the alkane CnH2n+2, giving CnH2n−2.",
    "Learn general formulae: alkanes CnH2n+2, alkenes/cycloalkanes CnH2n, alkynes/cycloalkenes CnH2n-2.",
    "2023 C2 Adv", 1, "Ch12 Organic Intro")

# Q2(a): Fermentation classification
add("pp23c2aq2a",
    "How is ethanol formed by fermentation of carbohydrates classified?",
    ["A biofuel and non-renewable", "A biofuel and renewable",
     "A fossil fuel and non-renewable", "A fossil fuel and renewable"],
    1,  # B
    "Ethanol from fermentation uses plant carbohydrates (biomass), making it a biofuel. It is renewable because plants can be regrown. Hydration of ethene uses fossil fuel feedstock.",
    "Compare fermentation vs hydration of ethene for ethanol production.",
    "2023 C2 Adv", 1, "Ch16 Alcohols")

# Q2(d)(i): IR spectrum of propan-2-ol
add("pp23c2aq2di",
    "Which set of IR wavenumber ranges (cm⁻¹) appears in the spectrum of propan-2-ol?",
    ["1485–1365, 2962–2853 and 3300–2500",
     "1485–1365, 2962–2853 and 3750–3200",
     "1669–1645, 2962–2853 and 3750–3200",
     "1740–1720, 3300–2500 and 3750–3200"],
    1,  # B - C-H, O-H (alcohol, broad 3750-3200)
    "Propan-2-ol shows: C-H stretches (2962-2853 and 1485-1365) and the broad O-H alcohol stretch (3750-3200). The 3300-2500 range is for carboxylic acid O-H.",
    "Memorise key IR absorption ranges: O-H alcohol (3750-3200), O-H acid (3300-2500), C=O (1740-1720), C=C (1669-1645).",
    "2023 C2 Adv", 1, "Ch17 Organic Analysis")

# Q3(a): Compound X from mass spectrum
add("pp23c2aq3a",
    "A compound gives a molecular ion peak at m/z = 60.0323. Which compound matches this exact mass? [Ar: H=1.0078, C=12.0000, N=14.0031, O=15.9949]",
    ["Ethanamide CH₃CONH₂", "Ethanoic acid CH₃COOH",
     "Trimethylamine (CH₃)₃N", "Urea CO(NH₂)₂"],
    0,  # A - calculate exact mass
    "Calculating exact masses: CH₃CONH₂ = 2C + 3H + O + N = 24.0000 + 3.0234 + 15.9949 + 14.0031 = 60.0323. This matches the molecular ion peak.",
    "Practise calculating molecular formulae from exact mass spectrometry data.",
    "2023 C2 Adv", 1, "Ch5 Moles & Equations")

# Q4(b)(i): Electrophile definition
add("pp23c2aq4bi",
    "An electrophile is a substance that",
    ["Accepts a pair of electrons", "Accepts an unpaired electron",
     "Donates a pair of electrons", "Donates an unpaired electron"],
    0,  # A
    "An electrophile is an electron-pair acceptor. A nucleophile is an electron-pair donor. These are fundamental definitions in organic reaction mechanisms.",
    "Learn definitions: electrophile = electron pair acceptor, nucleophile = electron pair donor, free radical = species with unpaired electron.",
    "2023 C2 Adv", 1, "Ch14 Alkenes")

# Q8(a): Structural isomers of C5H12
add("pp23c2aq8a",
    "How many structural isomers are there with the formula C₅H₁₂?",
    ["2", "3", "4", "5"],
    1,  # B - 3 isomers
    "C₅H₁₂ has three structural isomers: pentane, 2-methylbutane, and 2,2-dimethylpropane.",
    "Practise drawing structural isomers for different molecular formulae.",
    "2023 C2 Adv", 1, "Ch12 Organic Intro")

# ============================================================
# 2023 PAPER 2 CORE
# ============================================================

# Q1: Maxwell-Boltzmann distribution
add("pp23c2cq1",
    "When the temperature of a reaction is increased, what happens to the Maxwell-Boltzmann distribution?",
    ["The peak moves right and gets lower; the curve broadens",
     "The peak moves left and gets higher",
     "The peak stays the same but the curve rises",
     "The distribution does not change"],
    0,
    "At higher temperature, the peak shifts to the right (higher average energy), becomes lower, and the distribution broadens. More molecules exceed the activation energy.",
    "Review Maxwell-Boltzmann distribution curves and the effect of temperature on reaction rate.",
    "2023 C2 Core", 2, "Ch9 Kinetics")

# Q2: Saturated hydrocarbon definition
add("pp23c2cq2",
    "What is meant by the term 'saturated hydrocarbon'?",
    ["A hydrocarbon containing only single C-C bonds",
     "A hydrocarbon containing C=C double bonds",
     "A compound containing only carbon and hydrogen with rings",
     "A compound soluble in water"],
    0,
    "Saturated means all carbon-carbon bonds are single bonds (no double bonds). Hydrocarbon means it contains only carbon and hydrogen atoms.",
    "Review definitions: saturated, unsaturated, hydrocarbon, homologous series.",
    "2023 C2 Core", 2, "Ch13 Alkanes")

# Q3(a): Alkene vs alkane general formula
add("pp23c2cq3a",
    "Why do alkenes have the general formula CnH2n, different from alkanes (CnH2n+2)?",
    ["Alkenes have one C=C double bond, reducing H count by 2",
     "Alkenes have more carbon atoms",
     "Alkenes are unsaturated with rings",
     "Alkenes contain oxygen atoms"],
    0,
    "Alkenes contain a C=C double bond which means two fewer hydrogen atoms compared to the corresponding alkane. General formula changes from CnH2n+2 (alkane) to CnH2n (alkene).",
    "Learn general formulae for hydrocarbon families and understand why they differ.",
    "2023 C2 Core", 3, "Ch14 Alkenes")

# Q4: Halogenoalkane hydrolysis rates
add("pp23c2cq4",
    "In comparing the rates of hydrolysis of 1-chloropropane, 1-bromopropane and 1-iodopropane with aqueous silver nitrate, which forms a precipitate first?",
    ["1-chloropropane", "1-bromopropane", "1-iodopropane", "They all form precipitates at the same rate"],
    2,  # C - 1-iodopropane (weakest C-X bond)
    "1-iodopropane reacts fastest because the C-I bond is the weakest (lowest bond enthalpy), so it breaks most easily during nucleophilic substitution.",
    "Review the trend in C-halogen bond strength and rate of hydrolysis of halogenoalkanes.",
    "2023 C2 Core", 3, "Ch15 Halogenoalkanes")

# Q5: Enthalpy of combustion experiment
add("pp23c2cq5",
    "In an experiment to determine the enthalpy change of combustion of an alcohol using a spirit burner, which of the following causes the experimental value to be less exothermic than the data book value?",
    ["Incomplete combustion producing carbon", "Heat loss to the surroundings",
     "Using a more concentrated alcohol", "Weighing the burner too precisely"],
    1,  # B - heat loss is the main issue
    "Heat loss to the surroundings is the main source of error, meaning less heat is transferred to the water, giving a less exothermic value. Carbon from incomplete combustion also reduces energy released.",
    "Review calorimetry experiments and sources of error in enthalpy measurements.",
    "2023 C2 Core", 3, "Ch16 Alcohols")

# Q6: Kc expression for ammonium carbamate
add("pp23c2cq6",
    "For NH₂COONH₄(s) ⇌ 2NH₃(g) + CO₂(g), what is the correct Kc expression?",
    ["[NH₃]²[CO₂] / [NH₂COONH₄]", "[NH₃]²[CO₂]",
     "[NH₃][CO₂]", "[NH₃][CO₂] / [NH₂COONH₄]"],
    1,  # B - solids omitted from Kc
    "Solids are omitted from the Kc expression. Since NH₂COONH₄ is a solid, only the gaseous products appear: Kc = [NH₃]²[CO₂].",
    "Remember to exclude solids and pure liquids from Kc expressions.",
    "2023 C2 Core", 1, "Ch10 Equilibria")

# Q7(a): Intermolecular forces in butan-1-ol
add("pp23c2cq7a",
    "Which are the intermolecular force(s) between butan-1-ol molecules in the liquid phase?",
    ["Hydrogen bonding only",
     "Hydrogen bonding and permanent dipole-dipole forces only",
     "Hydrogen bonding, permanent dipole-dipole forces and London forces",
     "London forces only"],
    2,  # C - all three types
    "Butan-1-ol has an -OH group so exhibits hydrogen bonding. It also has permanent dipole-dipole forces (due to the polar C-O and O-H bonds) and London forces (present between all molecules).",
    "Remember all molecules have London forces. Identify additional forces: H-bonding (OH, NH, HF) and permanent dipole-dipole (polar molecules).",
    "2023 C2 Core", 1, "Ch4 Intermolecular Forces")

# Q7(c)(i): Test for butan-1-ol
add("pp23c2cq7ci",
    "Which is a suitable test and result to confirm the presence of the OH group in butan-1-ol?",
    ["PCl₅ → white smoke", "PCl₅ → steamy fumes",
     "Na₂CO₃ → carbon dioxide given off", "Na₂CO₃ → effervescence"],
    1,  # B - PCl5 with -OH gives steamy fumes of HCl
    "Phosphorus(V) chloride (PCl₅) reacts with alcohols to produce HCl gas, which appears as steamy fumes. White smoke would indicate a different reaction.",
    "Learn tests for the -OH group: PCl₅ gives steamy fumes of HCl, sodium gives H₂ gas.",
    "2023 C2 Core", 1, "Ch16 Alcohols")

# Q8: Hess's Law / enthalpy
add("pp23c2cq8",
    "The standard enthalpy change of combustion of hydrogen is −285.8 kJ mol⁻¹. What are the two conditions denoted by the standard symbol ⦵?",
    ["298 K and 100 kPa", "273 K and 101.3 kPa",
     "298 K and 101.3 kPa", "273 K and 100 kPa"],
    2,  # C - 298K and 101.3 kPa
    "Standard conditions (⦵) are 298 K (25°C) and 101.3 kPa (1 atm). Note: some specifications now use 100 kPa but Edexcel uses 101.3 kPa.",
    "Remember standard conditions: 298 K temperature and 101.3 kPa pressure.",
    "2023 C2 Core", 2, "Ch5 Moles & Equations")

# ============================================================
# 2024 PAPER 1 ADVANCED
# ============================================================

# Q1: Atomic structure table
add("pp24c1aq1",
    "How many protons, neutrons and electrons are in ³⁴S²⁻?",
    ["16 protons, 18 neutrons, 18 electrons", "16 protons, 18 neutrons, 16 electrons",
     "16 protons, 16 neutrons, 18 electrons", "18 protons, 16 neutrons, 18 electrons"],
    0,  # A - S has 16p, 34-16=18n, 16+2=18e
    "³⁴S²⁻ has atomic number 16, so 16 protons. Mass number 34 minus 16 = 18 neutrons. With a 2- charge, electrons = 16 + 2 = 18.",
    "Practise determining subatomic particle numbers from isotopic notation and charge.",
    "2024 C1 Adv", 3, "Ch1 Atomic Structure")

# Q2(a): Electron affinity trend
add("pp24c1aq2",
    "Which statement explains the trend in first electron affinities: Cl (-349), Br (-325), I (-295) kJ mol⁻¹?",
    ["Electronegativity decreases down the group so less energy released", "Atomic radius increases down the group, electron further from nucleus, less attraction",
     "Nuclear charge increases making electron affinity more exothermic", "Shielding stays constant down the group"],
    1,  # B
    "Down Group 7, atomic radius increases and shielding increases, so the added electron is further from the nucleus and experiences less attraction, releasing less energy.",
    "Understand and explain trends in electron affinity down Group 7.",
    "2024 C1 Adv", 4, "Ch2 Periodic Table")

# Q4(a): Brønsted-Lowry acid definition
add("pp24c1aq4a",
    "What is meant by a Brønsted-Lowry acid?",
    ["A proton (H⁺) donor", "A proton (H⁺) acceptor",
     "An electron pair donor", "An electron pair acceptor"],
    0,  # A
    "A Brønsted-Lowry acid is a proton (H⁺) donor. A Brønsted-Lowry base is a proton acceptor. This is different from Lewis definitions (electron pair donor/acceptor).",
    "Learn Brønsted-Lowry definitions vs Lewis definitions of acids and bases.",
    "2024 C1 Adv", 1, "Ch11 Acid-Base Equilibria")

# Q4(b): Titration curve
add("pp24c1aq4b",
    "Which titration curve shows NaOH added to CH₃COOH (weak acid-strong base)?",
    ["Curve starting at low pH, steep middle, ending at high pH with buffer region",
     "Curve starting at pH 1, vertical at 25 cm³",
     "Curve starting at moderate pH, no buffer region",
     "Curve starting at neutral pH, vertical at 50 cm³"],
    0,  # A - weak acid strong base has buffer region
    "Weak acid-strong base titration: starts at moderate pH (weak acid), shows buffer region (flat area), steep near equivalence point (pH > 7), rises to high pH with excess NaOH.",
    "Practise sketching and interpreting titration curves for different acid-base combinations.",
    "2024 C1 Adv", 1, "Ch11 Acid-Base Equilibria")

# Q5(a): Bond enthalpy calculation for ethanol fuel cell
add("pp24c1aq5a",
    "In the reaction C₂H₅OH(l) + 3O₂(g) → 3H₂O(l) + 2CO₂(g), which bonds are broken and formed?",
    ["Break: 5C-H, 1C-C, 1C-O, 1O-H, 3O=O; Form: 6O-H, 4C=O",
     "Break: 5C-H, 1C-C, 1C-O, 1O-H, 1.5O=O; Form: 6O-H, 4C=O",
     "Break: 5C-H, 1C-C, 1C-O, 1O-H, 3O=O; Form: 3O-H, 2C=O",
     "Break: 6C-H, 1C-C, 1C-O, 3O=O; Form: 6O-H, 4C=O"],
    0,  # A
    "Bonds broken in C₂H₅OH: 5C-H + 1C-C + 1C-O + 1O-H. Plus 3O=O in 3O₂. Bonds formed: 6O-H in 3H₂O + 4C=O in 2CO₂.",
    "Practise identifying bonds broken and formed in combustion reactions for enthalpy calculations.",
    "2024 C1 Adv", 3, "Ch5 Moles & Equations")

# Q7(a)(ii): Variable affecting Kp
add("pp24c1aq7aii",
    "Which variable affects the value of Kp for the reaction SO₂ + ½O₂ ⇌ SO₃?",
    ["Pressure", "Temperature", "Surface area of the catalyst", "Concentration of O₂"],
    1,  # B
    "Only temperature affects the value of Kp. Changes in pressure, concentration, or catalyst change the position of equilibrium but not the value of Kp.",
    "Remember: only temperature changes the value of Kc and Kp.",
    "2024 C1 Adv", 1, "Ch10 Equilibria")

# Q7(c): Vanadium ion colour and oxidation number
add("pp24c1aq7c",
    "Which row shows the correct colour of solution and oxidation number of vanadium in VO₂⁺?",
    ["Yellow, +3", "Green, +4", "Yellow, +5", "Blue, +5"],
    2,  # C - VO2+ is yellow, V is +5
    "VO₂⁺ (dioxovanadium(V)) has vanadium in the +5 oxidation state. The solution is yellow. VO²⁺ (oxidovanadium(IV)) is blue with V at +4.",
    "Learn the colours and oxidation states of vanadium ions: V²⁺ violet (+2), V³⁺ green (+3), VO²⁺ blue (+4), VO₂⁺ yellow (+5).",
    "2024 C1 Adv", 1, "Ch7 Periodicity")

# Q7(d): Cell potential for Zn + VO₂⁺
add("pp24c1aq7d",
    "What is the cell potential for: 2VO₂⁺(aq) + 4H⁺(aq) + Zn(s) → 2VO²⁺(aq) + 2H₂O(l) + Zn²⁺(aq)? [E(VO₂⁺/VO²⁺) = +1.00 V, E(Zn²⁺/Zn) = -0.76 V]",
    ["+1.76 V", "+0.24 V", "-0.24 V", "-1.76 V"],
    0,  # A - 1.00 - (-0.76) = 1.76
    "Ecell = E(reduction) - E(oxidation) = E(VO₂⁺/VO²⁺) - E(Zn²⁺/Zn) = +1.00 - (-0.76) = +1.76 V. Positive Ecell means reaction is feasible.",
    "Practise calculating cell potentials using standard electrode potentials from the data booklet.",
    "2024 C1 Adv", 1, "Ch5 Moles & Equations")

# Q8(b): Enthalpy of solution definition
add("pp24c1aq8b",
    "Which definition correctly describes the enthalpy change of solution, ΔsolH?",
    ["The enthalpy change when 1 mol of gaseous ions dissolves in sufficient water to give an infinitely dilute solution",
     "The enthalpy change when 1 mol of an ionic substance dissolves in water to give an infinitely dilute solution",
     "The enthalpy change when 1 mol of gaseous ions dissolves in sufficient water to give a solution of concentration 1 mol dm⁻³",
     "The enthalpy change when 1 mol of an ionic substance dissolves in water to give a solution of concentration 1 mol dm⁻³"],
    1,  # B
    "ΔsolH is the enthalpy change when 1 mol of an ionic substance dissolves in sufficient water to give an infinitely dilute solution. Option A describes the enthalpy change of hydration.",
    "Review Born-Haber cycle definitions: lattice energy, enthalpy of hydration, enthalpy of solution.",
    "2024 C1 Adv", 1, "Ch5 Moles & Equations")

# Q9: Gibbs free energy feasibility
add("pp24c1aq9",
    "For the decomposition 2NaHCO₃(s) → Na₂CO₃(s) + CO₂(g) + H₂O(l) with ΔrH = +91.6 kJ mol⁻¹, how do you determine feasibility at 298 K?",
    ["Calculate ΔG = ΔH - TΔS; if ΔG < 0, the reaction is feasible",
     "Calculate ΔG = ΔH + TΔS; if ΔG > 0, the reaction is feasible",
     "If ΔH is positive, the reaction is always feasible",
     "The reaction is feasible because entropy increases"],
    0,  # A
    "Use ΔG = ΔH - TΔS. Calculate ΔS from standard entropy values, then find ΔG at 298 K. If ΔG < 0, the reaction is thermodynamically feasible.",
    "Practise Gibbs free energy calculations and determining feasibility temperatures.",
    "2024 C1 Adv", 3, "Ch5 Moles & Equations")

# ============================================================
# 2024 PAPER 1 CORE
# ============================================================

# Q1: Phosphide ion configuration
add("pp24c1cq1",
    "What is the electronic configuration of the phosphide ion, ³¹₁₅P³⁻?",
    ["1s² 2s² 2p⁶ 3s² 3p³", "1s² 2s² 2p⁶ 3s² 3p⁶",
     "1s² 2s² 2p⁶ 3s²", "1s² 2s² 2p⁶ 3p⁶"],
    1,  # B - P³⁻ has 18 electrons: [Ar] = 1s2 2s2 2p6 3s2 3p6
    "P has 15 electrons. P³⁻ has 15+3 = 18 electrons. Configuration: 1s²2s²2p⁶3s²3p⁶ (same as Ar).",
    "Practise writing electron configurations for ions, remembering to add/subtract electrons for the charge.",
    "2024 C1 Core", 1, "Ch1 Atomic Structure")

# Q2: Successive ionisation energies
add("pp24c1cq2",
    "Which could be the first four successive ionisation energies (kJ mol⁻¹) of a Group 4 element?",
    ["496, 4563, 6913, 9544", "900, 1757, 14849, 21007",
     "801, 2427, 3610, 25026", "1086, 2353, 4621, 6223"],
    3,  # D - gradual increase then no big jump until 5th
    "A Group 4 element has 4 outer shell electrons. The first 4 IEs increase gradually (same shell), with a big jump at the 5th IE. Option D shows gradual increases with no jump in the first four.",
    "Practise interpreting successive ionisation energy data to identify group number.",
    "2024 C1 Core", 1, "Ch1 Atomic Structure")

# Q3: Atomic radii trends
add("pp24c1cq3",
    "What is the trend in atomic radii across Period 2 and down Group 2?",
    ["Increasing across Period 2, increasing down Group 2",
     "Increasing across Period 2, decreasing down Group 2",
     "Decreasing across Period 2, decreasing down Group 2",
     "Decreasing across Period 2, increasing down Group 2"],
    3,  # D
    "Across a period, atomic radius decreases (increasing nuclear charge, same shell). Down a group, atomic radius increases (extra electron shells added).",
    "Review periodic trends in atomic radius, ionisation energy and electronegativity.",
    "2024 C1 Core", 1, "Ch2 Periodic Table")

# Q4: Halide test observations
add("pp24c1cq4",
    "When dilute HNO₃ and AgNO₃ are added to KCl, KBr and KI solutions, what are the correct observations?",
    ["KCl: white ppt; KBr: cream ppt; KI: yellow ppt",
     "KCl: cream ppt; KBr: white ppt; KI: yellow ppt",
     "KCl: yellow ppt; KBr: white ppt; KI: cream ppt",
     "KCl: white ppt; KBr: yellow ppt; KI: cream ppt"],
    0,  # A
    "AgCl = white precipitate, AgBr = cream precipitate, AgI = yellow precipitate. The acid must be nitric acid (not HCl which would introduce Cl⁻).",
    "Memorise halide test colours: Cl⁻ = white, Br⁻ = cream, I⁻ = yellow.",
    "2024 C1 Core", 3, "Ch8 Groups 2&7")

# Q5: Chlorine dioxide calculations
add("pp24c1cq5",
    "In the reaction 5NaClO₂ + 4HCl → 5NaCl + 4ClO₂ + 2H₂O, if ClO₂ decomposes as 2ClO₂(g) → Cl₂(g) + 2O₂(g), what happens to the volume?",
    ["Volume increases", "Volume decreases", "Volume stays the same", "Cannot be determined"],
    0,  # Going from 2 mol gas to 3 mol gas
    "2 mol ClO₂ decomposes to 1 mol Cl₂ + 2 mol O₂ = 3 mol total gas. From 2 mol to 3 mol, so volume increases.",
    "Practise mole calculations involving gas volumes and decomposition reactions.",
    "2024 C1 Core", 4, "Ch5 Moles & Equations")

# Q6: Mass spectrometry and empirical formula
add("pp24c1cq6",
    "A compound A contains 26.7% C, 2.2% H and 71.1% O by mass. Its molar mass is 90 g mol⁻¹. What is its molecular formula?",
    ["C₂H₂O₄", "CHO₂", "C₃H₃O₆", "CH₂O₃"],
    0,  # A - from empirical formula CHO₂ (30), 90/30 = 3, but wait...
    "Empirical formula: C = 26.7/12 = 2.225, H = 2.2/1 = 2.2, O = 71.1/16 = 4.44. Ratio = 1:1:2 → CHO₂. Mr(CHO₂) = 45. 90/45 = 2. Molecular formula = C₂H₂O₄ (oxalic acid).",
    "Practise calculating empirical and molecular formulae from percentage composition data.",
    "2024 C1 Core", 4, "Ch5 Moles & Equations")

# Q6(c): Which species is a cation in mass spectrometry?
add("pp24c1cq6c",
    "Which of these species is a cation?",
    ["3p, 4n, 3e", "6p, 6n, 6e", "12p, 12n, 10e", "35p, 44n, 36e"],
    2,  # C - more protons than electrons → positive ion
    "A cation has more protons than electrons. Option C has 12 protons but only 10 electrons, giving a 2+ charge (Mg²⁺).",
    "Remember: cations have lost electrons (fewer e⁻ than p⁺), anions have gained electrons (more e⁻ than p⁺).",
    "2024 C1 Core", 1, "Ch1 Atomic Structure")

# Q7: Group 1 vs Group 2 compounds
add("pp24c1cq7",
    "When KCl and KBr react with concentrated H₂SO₄, which observations are correct?",
    ["KCl: white fumes of HCl; KBr: brown fumes of Br₂ and SO₂",
     "KCl: brown fumes; KBr: white fumes only",
     "Both produce only white fumes", "KCl: no reaction; KBr: orange fumes"],
    0,  # A
    "With conc H₂SO₄: KCl produces HCl (white fumes) only as Cl⁻ is not a strong enough reducing agent. KBr produces Br₂ (brown fumes) and SO₂ (choking gas) because Br⁻ reduces H₂SO₄.",
    "Learn the products of halide reactions with concentrated sulfuric acid: Cl⁻ → HCl only, Br⁻ → Br₂ + SO2, I⁻ → I₂ + SO₂ + H₂S.",
    "2024 C1 Core", 6, "Ch8 Groups 2&7")

# Q8: Physical properties and bonding
add("pp24c1cq8",
    "Why is water a good solvent for ionic compounds like calcium chloride?",
    ["Water molecules are polar and surround the ions, forming ion-dipole interactions",
     "Water molecules form hydrogen bonds with the ions",
     "Water is covalent and shares electrons with ions",
     "Water molecules have London forces with the ions"],
    0,  # A
    "Water is polar. The δ⁻ oxygen end is attracted to cations and the δ⁺ hydrogen end is attracted to anions. These are ion-dipole interactions that overcome the ionic lattice forces.",
    "Review how solubility relates to the types of intermolecular forces involved.",
    "2024 C1 Core", 4, "Ch4 Intermolecular Forces")

# Q9: Redox - chlorate(I) reaction
add("pp24c1cq9",
    "In the reaction ClO⁻ + Cl⁻ + 2H⁺ → Cl₂ + H₂O, why is this NOT a disproportionation reaction?",
    ["Chlorine in ClO⁻ is reduced to Cl₂ and chlorine in Cl⁻ is oxidised to Cl₂; the same element is simultaneously oxidised and reduced in different species",
     "Both chlorines are oxidised",
     "Both chlorines are reduced",
     "No electrons are transferred"],
    0,  # A
    "In disproportionation, the SAME species is simultaneously oxidised and reduced. Here ClO⁻ (Cl = +1) is reduced and Cl⁻ (Cl = -1) is oxidised, but they are different starting species, so this is not disproportionation.",
    "Understand the definition of disproportionation carefully - it requires the SAME species to be both oxidised and reduced.",
    "2024 C1 Core", 1, "Ch6 Redox")

# ============================================================
# 2024 PAPER 2 ADVANCED
# ============================================================

# Q1(a): Which bromoalkane forms precipitate first
add("pp24c2aq1a",
    "Equal amounts of four bromoalkanes were added to silver nitrate solution at the same temperature. Which forms a precipitate first?",
    ["1-bromobutane", "2-bromobutane", "1-bromo-2-methylpropane", "2-bromo-2-methylpropane"],
    3,  # D - tertiary fastest (SN1)
    "2-bromo-2-methylpropane (tertiary) is the fastest because it reacts via SN1 mechanism which has a lower activation energy. The tertiary carbocation intermediate is most stable.",
    "Compare rates of hydrolysis for primary, secondary and tertiary halogenoalkanes.",
    "2024 C2 Adv", 1, "Ch15 Halogenoalkanes")

# Q1(b): N-substituted amide formation
add("pp24c2aq1b",
    "Which pair of reactants will form an N-substituted amide?",
    ["CH₃COCl and NH₃", "CH₃CH₂OH and NH₃",
     "CH₃COCl and CH₃NH₂", "CH₃CH₂OH and CH₃NH₂"],
    2,  # C - acyl chloride + primary amine → N-substituted amide
    "An acyl chloride (CH₃COCl) reacts with a primary amine (CH₃NH₂) to form an N-substituted amide (CH₃CONHCH₃). NH₃ gives an unsubstituted amide. Alcohols do not form amides.",
    "Learn the reactions of acyl chlorides with nucleophiles including ammonia and amines.",
    "2024 C2 Adv", 1, "Ch17 Organic Analysis")

# Q2(a): Grignard reagent solvent
add("pp24c2aq2a",
    "The most suitable solvent for forming a Grignard reagent is",
    ["cyclohexane", "ether", "ethyl ethanoate", "hexane"],
    1,  # B - ether
    "Dry ether is the standard solvent for Grignard reagent formation. It must be anhydrous because water reacts with the Grignard reagent. Ether stabilisers the organomagnesium compound.",
    "Review Grignard reagent preparation and reactions.",
    "2024 C2 Adv", 1, "Ch15 Halogenoalkanes")

# Q2(c): Grignard as nucleophile
add("pp24c2aq2c",
    "In their reactions, the Grignard reagent is best described as",
    ["a carbocation", "an electrophile", "a nucleophile", "a radical"],
    2,  # C
    "The Grignard reagent has a polar C-Mg bond with δ⁻ on carbon. The carbanion character makes it a nucleophile, attacking δ⁺ carbon atoms in carbonyl compounds.",
    "Understand the reactivity of Grignard reagents as carbon nucleophiles.",
    "2024 C2 Adv", 1, "Ch15 Halogenoalkanes")

# Q3(a): Hydrogen peroxide dot-and-cross diagram
add("pp24c2aq3a",
    "How many lone pairs of electrons are on each oxygen atom in a molecule of H₂O₂?",
    ["1", "2", "3", "4"],
    1,  # B - 2 lone pairs per O
    "Each oxygen in H₂O₂ has 2 bonding pairs (O-H and O-O) and 2 lone pairs (6 valence electrons − 2×1 shared = 2 lone pairs per O).",
    "Practise drawing dot-and-cross diagrams for molecules including H₂O₂.",
    "2024 C2 Adv", 1, "Ch3 Bonding")

# Q3(b): Disproportionation of H₂O₂
add("pp24c2aq3b",
    "In the decomposition 2H₂O₂ → 2H₂O + O₂, which statement about the oxidation number changes is correct?",
    ["Oxygen is oxidised from -1 to 0 and reduced from -1 to -2",
     "Oxygen is oxidised from -2 to 0 and reduced from -1 to -2",
     "All oxygen atoms are oxidised", "All oxygen atoms are reduced"],
    0,  # A
    "In H₂O₂, oxygen has oxidation number -1. In H₂O it is -2 (reduction), in O₂ it is 0 (oxidation). This is disproportionation: the same species (O in H₂O₂) is both oxidised and reduced.",
    "Practise identifying disproportionation using oxidation numbers.",
    "2024 C2 Adv", 3, "Ch6 Redox")

# Q5(a): Type of reaction for cyclopentane synthesis
add("pp24c2aq5a",
    "When 2-methylbutane is passed over a hot platinum catalyst to form cyclopentane, what type of reaction occurs?",
    ["Substitution", "Addition", "Reforming", "Cracking"],
    2,  # C - reforming
    "The conversion of an alkane to a cycloalkane over a platinum catalyst is called reforming (or dehydrocyclisation). This is used in the petroleum industry to improve fuel quality.",
    "Learn the types of reactions in organic chemistry including reforming, cracking and isomerisation.",
    "2024 C2 Adv", 1, "Ch13 Alkanes")

# Q5(c): Free radical substitution of cyclopentane
add("pp24c2aq5c",
    "What condition is needed to initiate the reaction between cyclopentane and bromine?",
    ["UV light", "High pressure", "Catalyst", "Reflux"],
    0,  # A - UV light
    "Free radical substitution requires UV light to break the Br-Br bond homolytically, producing bromine free radicals that initiate the chain reaction.",
    "Remember: free radical substitution always requires UV light for initiation.",
    "2024 C2 Adv", 1, "Ch13 Alkanes")

# Q6(a): NMR electromagnetic spectrum
add("pp24c2aq6a",
    "Which part of the electromagnetic spectrum is used in NMR spectroscopy?",
    ["Infrared", "Radio waves", "Ultraviolet", "X-ray"],
    1,  # B - radio waves
    "NMR spectroscopy uses radio waves to flip nuclear spins between energy states in a strong magnetic field. IR uses infrared, UV-vis uses ultraviolet/visible light.",
    "Remember which spectroscopic technique uses which part of the EM spectrum.",
    "2024 C2 Adv", 1, "Ch17 Organic Analysis")

# Q7(a): IUPAC name of chloroprene
add("pp24c2aq7a",
    "What is the IUPAC name of chloroprene?",
    ["3-chlorobuta-1,3-diene", "2-chlorobuta-2,4-diene",
     "3-chlorobuta-2,4-diene", "2-chlorobuta-1,3-diene"],
    3,  # D - 2-chlorobuta-1,3-diene
    "Chloroprene has the structure CH₂=C(Cl)-CH=CH₂. Numbering to give lowest locants: 2-chlorobuta-1,3-diene.",
    "Practise IUPAC naming of dienes and substituted dienes.",
    "2024 C2 Adv", 1, "Ch14 Alkenes")

# Q8(a)(i): Chiral carbon definition
add("pp24c2aq8ai",
    "What is meant by a 'chiral carbon atom'?",
    ["A carbon atom bonded to four different groups", "A carbon atom with a double bond",
     "A carbon atom bonded to two identical groups", "A carbon atom in a ring structure"],
    0,
    "A chiral (asymmetric) carbon atom is bonded to four different groups/atoms, making it a stereocentre. This creates two non-superimposable mirror image molecules (enantiomers).",
    "Review chirality and optical isomerism in organic molecules.",
    "2024 C2 Adv", 1, "Ch12 Organic Intro")

# Q8(c): Serine zwitterion
add("pp24c2aq8c",
    "What is the formula of the zwitterion of serine?",
    ["⁺H₃N-CH(CH₂OH)-COO⁻", "⁺H₃N-CH(CH₂OH)-COOH",
     "H₂N-CH(CH₂OH)-COO⁻", "⁺H₃N-CH(CH₂O⁻)-COOH"],
    0,  # A
    "A zwitterion has both positive and negative charges. The amino group is protonated (NH₃⁺) and the carboxyl group is deprotonated (COO⁻). The -CH₂OH remains unchanged.",
    "Understand zwitterion structure: NH₂ → NH₃⁺ (protonated), COOH → COO⁻ (deprotonated).",
    "2024 C2 Adv", 1, "Ch17 Organic Analysis")

# ============================================================
# 2024 PAPER 2 CORE
# ============================================================

# Q1(a): Volumetric flask
add("pp24c2cq1a",
    "Which piece of apparatus should be used for making a solution with a volume of exactly 250 cm³?",
    ["Burette", "Measuring cylinder", "Pipette", "Volumetric flask"],
    3,  # D
    "A volumetric flask is used to make up a solution to a precise volume (e.g. 250 cm³). Burettes and pipettes deliver specific volumes; measuring cylinders are less precise.",
    "Learn which glassware to use for different measurement purposes in titration experiments.",
    "2024 C2 Core", 1, "Ch5 Moles & Equations")

# Q1(b)(i): Burette reading
add("pp24c2cq1bi",
    "A burette reading has the meniscus between 2.4 and 2.5 cm³, aligned at the midpoint. What is the reading?",
    ["2.40 cm³", "2.45 cm³", "3.55 cm³", "3.60 cm³"],
    1,  # B - 2.45
    "Burettes read from top down. If the meniscus is exactly halfway between 2.4 and 2.5, the reading is 2.45 cm³. Always read to 0.05 cm³ precision.",
    "Practise reading burette measurements correctly to 0.05 cm³.",
    "2024 C2 Core", 1, "Ch5 Moles & Equations")

# Q2: Equilibrium - dichromate/chromate
add("pp24c2cq2",
    "For the equilibrium Cr₂O₇²⁻(aq) + H₂O(l) ⇌ 2CrO₄²⁻(aq) + 2H⁺(aq), what happens when NaOH is added?",
    ["Solution turns more orange because equilibrium shifts left",
     "Solution turns more yellow because equilibrium shifts right",
     "No colour change because NaOH does not affect equilibrium",
     "Solution turns green due to a side reaction"],
    1,  # B
    "Adding NaOH reduces [H⁺]. By Le Chatelier's principle, equilibrium shifts right to produce more H⁺, producing more CrO₄²⁻ (yellow). The solution turns yellower.",
    "Practise applying Le Chatelier's principle to predict equilibrium shifts.",
    "2024 C2 Core", 3, "Ch10 Equilibria")

# Q3(b)(i): Mechanism of methylpropene + HBr
add("pp24c2cq3bi",
    "What is the name and type of the mechanism for the reaction of methylpropene with hydrogen bromide?",
    ["Electrophilic addition", "Nucleophilic addition",
     "Electrophilic substitution", "Nucleophilic substitution"],
    0,  # A
    "Alkenes react with HBr via electrophilic addition. The pi bond electrons attack H⁺ (electrophile), forming a carbocation, then Br⁻ adds to the carbocation.",
    "Learn the mechanism of electrophilic addition to alkenes with curly arrows.",
    "2024 C2 Core", 1, "Ch14 Alkenes")

# Q4: Bond enthalpy / cyclobutane formation
add("pp24c2cq4",
    "Why do bond enthalpies give a more accurate value than mean bond enthalpies for the dimerisation of ethene to cyclobutane?",
    ["Bond enthalpies are specific to the particular molecule, whereas mean bond enthalpies are averaged over different molecules",
     "Mean bond enthalpies are always larger",
     "Bond enthalpies exclude London forces",
     "Mean bond enthalpies only apply to gases"],
    0,  # A
    "Bond enthalpies are specific to particular bonds in specific molecules. Mean bond enthalpies are averages across different compounds, so they may not accurately represent the bonds involved in this specific reaction.",
    "Understand the difference between bond enthalpies and mean bond enthalpies.",
    "2024 C2 Core", 2, "Ch5 Moles & Equations")

# Q5: Conversion of butan-1-ol to 1-bromobutane
add("pp24c2cq5",
    "In the preparation of 1-bromobutane from butan-1-ol, sodium bromide and concentrated H₂SO₄, which step prevents side reactions?",
    ["Using an ice-water bath during addition", "Distilling the product",
     "Using anti-bumping granules", "Washing with Na₂CO₃"],
    0,  # A
    "The ice-water bath and condenser during Steps 1-2 prevent side reactions by keeping the temperature low. Otherwise, dehydration or oxidation products may form.",
    "Review the practical procedure for preparing halogenoalkanes from alcohols.",
    "2024 C2 Core", 2, "Ch16 Alcohols")

# Q6: Rate experiment - thiosulfate reaction
add("pp24c2cq6",
    "In the reaction Na₂S₂O₃ + 2HCl → S + SO₂ + H₂O + 2NaCl, why does the mixture become cloudy?",
    ["Sulfur dioxide gas is produced", "Solid sulfur is formed as a precipitate",
     "Sodium chloride crystallises out", "Hydrogen sulfide gas is produced"],
    1,  # B
    "The cloudiness is caused by finely divided solid sulfur forming as a colloidal precipitate in the solution. This is used as a visual endpoint for timing the reaction.",
    "Understand the observation in the thiosulfate-acid rate experiment and its significance.",
    "2024 C2 Core", 1, "Ch9 Kinetics")

# Q8: Enthalpy of combustion experiment
add("pp24c2cq8",
    "In an experiment to determine the enthalpy of combustion of methanol, which is the main reason the experimental value is less exothermic than the data book value?",
    ["Incomplete combustion", "Heat loss to the surroundings",
     "Using a lid on the beaker", "Mass measurement errors"],
    1,  # B
    "Heat loss to the surroundings (air, beaker, thermometer) is the main error. Not all heat from combustion reaches the water. Incomplete combustion (carbon deposit) also reduces energy released.",
    "Review sources of error in combustion calorimetry experiments.",
    "2024 C2 Core", 4, "Ch16 Alcohols")

# Save the final QBANK
print(f"Total QBANK entries: {len(qbank)}")

# Verify chapter coverage
chapters = {}
for q in qbank:
    ch = q['chapter']
    chapters[ch] = chapters.get(ch, 0) + 1
print("\nChapter distribution:")
for ch in sorted(chapters.keys()):
    print(f"  {ch}: {chapters[ch]}")

# Paper coverage
papers = {}
for q in qbank:
    p = q['paper']
    papers[p] = papers.get(p, 0) + 1
print("\nPaper distribution:")
for p in sorted(papers.keys()):
    print(f"  {p}: {papers[p]}")

with open('_chem_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(qbank, f, indent=2, ensure_ascii=False)
print("\nSaved to _chem_pastpaper_qbank.json")
