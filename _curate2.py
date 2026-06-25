import json

qs = []

# Chemistry
qs.append({"id":"pp23c1cq1","subject":"Chem Y1","chapter":"Ch1 Atomic Structure","text":"Which are the correct data for a proton and a neutron?","type":"mc","options":["Proton: +1 charge, mass 1; Neutron: -1 charge, mass 0.0005","Proton: +1 charge, mass 1; Neutron: 0 charge, mass 1","Proton: -1 charge, mass 0.0005; Neutron: 0 charge, mass 1","Proton: 0 charge, mass 1; Neutron: +1 charge, mass 1"],"answer":1,"explain":"Proton: charge +1, mass 1. Neutron: charge 0, mass 1. Option A confuses neutron with electron.","improve":"Review subatomic particle properties","paper":"2023 C1 Core","marks":1})

qs.append({"id":"pp23c1cq1b","subject":"Chem Y1","chapter":"Ch1 Atomic Structure","text":"State the shape of the 2s orbital of a silicon atom.","type":"mc","options":["Dumbbell","Spherical","Clover-shaped","Planar"],"answer":1,"explain":"All s orbitals are spherical. p = dumbbell, d = clover.","improve":"s=spherical, p=dumbbell, d=clover","paper":"2023 C1 Core","marks":1})

qs.append({"id":"pp23c1cq1c","subject":"Chem Y1","chapter":"Ch1 Atomic Structure","text":"Silicon has 3 stable isotopes. Sample Ar=28.11, 28Si=92%, 30Si=4%. Abundance of 29Si?","type":"mc","options":["2%","4%","8%","10%"],"answer":1,"explain":"100-92-4=4%","improve":"Abundances sum to 100%","paper":"2023 C1 Core","marks":3})

qs.append({"id":"pp23c1cq2","subject":"Chem Y1","chapter":"Ch5 Moles & Equations","text":"% by mass of water in K2Mg(SO4)2.6H2O? (K=39,Mg=24,S=32,O=16,H=1)","type":"mc","options":["18.3%","22.6%","26.8%","31.2%"],"answer":2,"explain":"Mr=402, water=108, %=108/402*100=26.87%","improve":"%=component/total*100","paper":"2023 C1 Core","marks":3})

qs.append({"id":"pp23c1cq7","subject":"Chem Y1","chapter":"Ch3 Bonding","text":"Which compound contains BOTH ionic and covalent bonds?","type":"mc","options":["NaCl","CCl4","NaOH","CH4"],"answer":2,"explain":"NaOH: ionic Na+ to OH-, covalent O-H bond","improve":"Look for polyatomic ions","paper":"2023 C1 Core","marks":1})

qs.append({"id":"pp23c1cq9","subject":"Chem Y1","chapter":"Ch1 Atomic Structure","text":"Ionisation energies: 789,1577,3232,4356 kJ/mol. Which group?","type":"mc","options":["Group 1","Group 2","Group 3","Group 4"],"answer":1,"explain":"Big jump after 2nd IE = 2 outer electrons = Group 2","improve":"Count IEs before the big jump","paper":"2023 C1 Core","marks":2})

qs.append({"id":"pp23c1cq6","subject":"Chem Y1","chapter":"Ch6 Redox","text":"Fe2O3 + 3CO -> 2Fe + 3CO2. Which species is oxidised?","type":"mc","options":["Fe2O3","CO","Fe","CO2"],"answer":1,"explain":"C: +2 in CO, +4 in CO2. Oxidation state increases = oxidised","improve":"Assign oxidation numbers on both sides","paper":"2023 C1 Core","marks":2})

qs.append({"id":"pp23c2cq1","subject":"Chem Y1","chapter":"Ch9 Kinetics","text":"Maxwell-Boltzmann: what changes when T increases?","type":"mc","options":["Peak moves right, gets taller","Peak moves right, gets lower; broadens","Peak stays, gets taller","Curve shifts left"],"answer":1,"explain":"Higher T: peak shifts right, lowers, broadens. Same area.","improve":"Draw both curves at different T","paper":"2023 C2 Core","marks":2})

qs.append({"id":"pp23c2cq2","subject":"Chem Y1","chapter":"Ch13 Alkanes","text":"What is a saturated hydrocarbon?","type":"mc","options":["Contains C=C and H only","Contains only single C-C bonds and H only","Contains C,H,O only","Has both single and double bonds"],"answer":1,"explain":"Saturated=single bonds only. Hydrocarbon=C and H only.","improve":"Saturated=bonds(single only), hydrocarbon=C+H only","paper":"2023 C2 Core","marks":2})

qs.append({"id":"pp23c2cq3","subject":"Chem Y1","chapter":"Ch14 Alkenes","text":"Test to distinguish alkene from alkane?","type":"mc","options":["Add NaOH","Add Br2(aq) - alkene decolourises orange","Add HCl","Add water"],"answer":1,"explain":"Br2 orange. C=C reacts with Br2, decolourises. Alkanes: no reaction","improve":"Br2 decolourises with C=C","paper":"2023 C2 Core","marks":1})

qs.append({"id":"pp23c2cq7","subject":"Chem Y1","chapter":"Ch16 Alcohols","text":"Product of complete oxidation of butan-1-ol by acidified K2Cr2O7?","type":"mc","options":["Butanal only","Butanoic acid","Butanone","No reaction"],"answer":1,"explain":"Primary alcohol fully oxidised to carboxylic acid","improve":"Primary->aldehyde->acid. Secondary->ketone. Tertiary->no reaction","paper":"2023 C2 Core","marks":2})

qs.append({"id":"pp24c1cq1","subject":"Chem Y1","chapter":"Ch1 Atomic Structure","text":"Electronic configuration of phosphide ion P3-?","type":"mc","options":["1s2 2s2 2p6 3s2 3p3","1s2 2s2 2p6 3s2 3p6","1s2 2s2 2p6 3s2 3p4 4s1","1s2 2s2 2p6 3s2 3p5"],"answer":1,"explain":"P has 15e. P3- has 3 extra = 18e = 1s2 2s2 2p6 3s2 3p6 (Ar config)","improve":"Negative ions: ADD electrons","paper":"2024 C1 Core","marks":1})

qs.append({"id":"pp24c1cq2","subject":"Chem Y1","chapter":"Ch1 Atomic Structure","text":"First four IEs of Group 2 element?","type":"mc","options":["738,1451,7733,10541","578,1817,2745,11578","1000,2260,3400,4500","496,4562,6912,9544"],"answer":0,"explain":"Group 2: jump after 2nd IE. 1451->7733 is huge jump","paper":"2024 C1 Core","marks":1,"improve":"Count IEs before large jump"})

qs.append({"id":"pp24c2cq2","subject":"Chem Y1","chapter":"Ch10 Equilibria","text":"K2Cr2O7+H2O=2CrO4(2-)+2H+. Effect of adding NaOH?","type":"mc","options":["Shifts left - more orange","Shifts right - more yellow","No change","Shifts right - more orange"],"answer":1,"explain":"NaOH removes H+. Le Chatelier: shift RIGHT to replace H+, more CrO4(2-) yellow","improve":"Removing product shifts equilibrium right","paper":"2024 C2 Core","marks":2})

qs.append({"id":"pp24c2cq6","subject":"Chem Y1","chapter":"Ch9 Kinetics","text":"How to measure rate of Na2S2O3+2HCl reaction?","type":"mc","options":["Measure mass increase","Time for cross to disappear under flask","Measure gas volume","Measure pH"],"answer":1,"explain":"Sulfur precipitate clouds solution. Disappearing cross method","improve":"Disappearing cross for precipitation reactions","paper":"2024 C2 Core","marks":1})

qs.append({"id":"pp23c1aq1","subject":"Chem Y1","chapter":"Ch2 Periodic Table","text":"Which is a d-block element in Period 4?","type":"mc","options":["Ca (Z=20)","Fe (Z=26)","Br (Z=35)","Kr (Z=36)"],"answer":1,"explain":"d-block = Groups 3-12. Fe is Group 8 Period 4","improve":"d-block = Groups 3-12","paper":"2023 C1 Adv","marks":1})

qs.append({"id":"pp23c1aq5","subject":"Chem Y1","chapter":"Ch10 Equilibria","text":"N2O4(g)=2NO2(g). 20% dissociated at 1atm. Kp?","type":"mc","options":["0.067","0.10","0.17","0.33"],"answer":2,"explain":"eq: 0.8 N2O4, 0.4 NO2. total=1.2. Kp=(1/3)^2/(2/3)=1/6=0.167","improve":"Kp uses partial pressures = mole fraction * total P","paper":"2023 C1 Adv","marks":3})

qs.append({"id":"pp23c2aq6","subject":"Chem Y1","chapter":"Ch9 Kinetics","text":"Rate=k[CH3COCH3][H+]. Effect of doubling [I2]?","type":"mc","options":["Rate doubles","Rate quadruples","Rate unchanged","Rate halves"],"answer":2,"explain":"I2 is zero order (not in rate equation). No effect on rate","improve":"Only species in rate equation affect rate","paper":"2023 C2 Adv","marks":1})

qs.append({"id":"pp23c2aq8","subject":"Chem Y1","chapter":"Ch17 Organic Analysis","text":"How many structural isomers of C4H9Br?","type":"mc","options":["2","3","4","5"],"answer":2,"explain":"1-bromobutane, 2-bromobutane, 1-bromo-2-methylpropane, 2-bromo-2-methylpropane","improve":"Draw all carbon skeletons then place Br","paper":"2023 C2 Adv","marks":1})

qs.append({"id":"pp24c1cq3","subject":"Chem Y1","chapter":"Ch2 Periodic Table","text":"Trend in atomic radii across Period 3 (Na to Ar)?","type":"mc","options":["Increases","Decreases","Stays constant","Decreases then increases"],"answer":1,"explain":"Increasing nuclear charge, same shell, electrons pulled closer","improve":"Across period: radius decreases. Down group: increases","paper":"2024 C1 Core","marks":1})

qs.append({"id":"pp24c1aq9","subject":"Chem Y1","chapter":"Ch5 Moles & Equations","text":"0.5g NaHCO3+HCl. Volume of CO2 at RTP? (Mr=84, molar vol=24dm3)","type":"mc","options":["72 cm3","100 cm3","143 cm3","200 cm3"],"answer":2,"explain":"n=0.5/84=0.00595mol. V=0.00595*24000=142.9cm3","improve":"n=mass/Mr, V=n*24000 at RTP","paper":"2024 C1 Adv","marks":2})

# Maths
qs.append({"id":"pp23m1q1a","subject":"Mech Y1","chapter":"Ch9 Constant Acceleration","text":"Car from rest, a=3.2 m/s^2. Speed after 5s?","type":"mc","options":["8.2 m/s","16.0 m/s","25.6 m/s","40.0 m/s"],"answer":1,"explain":"v=u+at=0+3.2*5=16","improve":"Basic suvat","paper":"2023 M1","marks":1})

qs.append({"id":"pp23m1q1b","subject":"Mech Y1","chapter":"Ch9 Constant Acceleration","text":"Car from rest, a=3.2 m/s^2 for 5s. Distance?","type":"mc","options":["16 m","25.6 m","40 m","80 m"],"answer":2,"explain":"s=ut+0.5at^2=0+0.5*3.2*25=40","improve":"s=ut+1/2 at^2","paper":"2023 M1","marks":2})

qs.append({"id":"pp23p1q1","subject":"Pure Y1","chapter":"Ch10 Integration","text":"Integrate (3x^5 - 2x^(1/2) + 1/x^2) dx","type":"mc","options":["x^6/2 - (4/3)x^(3/2) - 1/x + C","15x^4 - x^(-1/2) - 2x^(-3) + C","x^6/2 - (4/3)x^(3/2) + 1/x + C","3x^6/6 - 2x^(3/2)/3 - x^{-1} + C"],"answer":0,"explain":"Add 1 to power, divide by new power. 3x^6/6=x^6/2, -2x^(3/2)/(3/2)=-(4/3)x^(3/2), x^{-2+1}/(-1)=-1/x","improve":"Integrate each term separately. 1/x^2=x^{-2}","paper":"2023 P1","marks":4})

qs.append({"id":"pp23p1q6","subject":"Pure Y1","chapter":"Ch12 Exponentials & Logs","text":"a=log2(x), b=log2(x+8). Express log2(x^2+8x) in a and b.","type":"mc","options":["a + b","ab","2a + b","a^2 + b"],"answer":0,"explain":"log2(x^2+8x)=log2(x(x+8))=log2(x)+log2(x+8)=a+b","improve":"log(AB)=log A + log B","paper":"2023 P1","marks":2})

qs.append({"id":"pp23p1q14","subject":"Pure Y1","chapter":"Ch7 Algebraic Methods","text":"Prove (n+1)^3 - n^3 is odd. Correct approach?","type":"mc","options":["Expand to 3n^2+3n+1=3n(n+1)+1. n(n+1) always even, 3*even+1 is odd","Test n=1,2,3","Say its odd because terms are positive","Factorise as difference of cubes"],"answer":0,"explain":"n(n+1)=consecutive integers=always even. 3*even+1=odd","improve":"Consecutive integer product always even. Proofs ALWAYS general","paper":"2023 P1","marks":4})

qs.append({"id":"pp23p2q1","subject":"Pure Y2","chapter":"Ch9 Differentiation","text":"f(x)=x^3+2x^2-8x+5. Find f double prime.","type":"mc","options":["3x^2+4x-8","6x+4","6","3x+2"],"answer":1,"explain":"f prime=3x^2+4x-8, f double prime=6x+4","improve":"Differentiate twice","paper":"2023 P2","marks":2})

qs.append({"id":"pp23p2q8","subject":"Pure Y2","chapter":"Ch7 Trigonometry & Modelling","text":"2cos(theta)+8sin(theta) as Rcos(theta-alpha). R and alpha?","type":"mc","options":["R=8.25, alpha=75.96","R=6.32, alpha=63.43","R=10.00, alpha=53.13","R=8.25, alpha=14.04"],"answer":0,"explain":"R=sqrt(4+64)=sqrt(68)=8.246. tan(alpha)=8/2=4, alpha=75.96 deg","improve":"R=sqrt(a^2+b^2), tan(alpha)=b/a","paper":"2023 P2","marks":4})

qs.append({"id":"pp23p2q3","subject":"Pure Y2","chapter":"Ch1 Algebraic Methods","text":"log2(x+3)+log2(x+10)=2+2log2(x). Resulting equation?","type":"mc","options":["3x^2-13x-30=0","x^2+13x+30=0","3x^2+13x+30=0","x^2-13x-30=0"],"answer":0,"explain":"LHS=log2[(x+3)(x+10)]. RHS=log2(4x^2). So x^2+13x+30=4x^2 giving 3x^2-13x-30=0","improve":"log A + log B = log(AB)","paper":"2023 P2","marks":3})

qs.append({"id":"pp24p1q2","subject":"Pure Y1","chapter":"Ch8 Binomial Expansion","text":"First 4 terms of (1+x/9)^(1/2)?","type":"mc","options":["1+x/18-x^2/648+x^3/34992","1+x/18-x^2/324+x^3/17496","1+x/9-x^2/162+x^3/4374","1+x/6-x^2/72+x^3/1296"],"answer":0,"explain":"Use binomial series with n=1/2, substitute x/9","improve":"(1+x)^n = 1+nx+n(n-1)/2! x^2+n(n-1)(n-2)/3! x^3","paper":"2024 P1","marks":3})

qs.append({"id":"pp23s1q1","subject":"Stats Y1","chapter":"Ch5 Probability","text":"Venn diagram with A,B,C. B and C independent. Which gives P(A)?","type":"mc","options":["A only region","All regions inside A circle","A only + intersections with A","Cannot determine"],"answer":1,"explain":"P(A)=sum of ALL probabilities inside circle A including intersections","improve":"P(A) = all regions in circle A","paper":"2023 S1","marks":3})

qs.append({"id":"pp24s1q1","subject":"Stats Y1","chapter":"Ch6 Statistical Distributions","text":"X~B(10,1/6). Find P(X=3).","type":"mc","options":["0.155","0.250","0.350","0.500"],"answer":0,"explain":"C(10,3)*(1/6)^3*(5/6)^7 = 0.155","improve":"Use calculator binompdf(10,1/6,3)","paper":"2024 S1","marks":2})

qs.append({"id":"pp24p1q4","subject":"Pure Y1","chapter":"Ch9 Differentiation","text":"Differentiation from first principles of y=x^2. First step?","type":"mc","options":["Find f(x+h)=(x+h)^2=x^2+2xh+h^2, then [f(x+h)-f(x)]/h","Differentiate directly","Use chain rule","Integrate then differentiate"],"answer":0,"explain":"f prime = lim[h->0] [f(x+h)-f(x)]/h. Expand, simplify, take limit","improve":"Show ALL steps for full marks","paper":"2024 P1","marks":4})

# Additional questions from 2024 papers
qs.append({"id":"pp24c2cq3","subject":"Chem Y1","chapter":"Ch14 Alkenes","text":"But-1-ene, but-2-ene and methylpropene are isomeric alkenes. Which isomer has E/Z isomerism?","type":"mc","options":["But-1-ene only","But-2-ene only","Methylpropene only","Both but-1-ene and but-2-ene"],"answer":1,"explain":"E/Z isomerism requires a C=C with TWO different groups on EACH carbon. But-2-ene: each C of C=C has H and CH3. But-1-ene: C1 has 2H (same), no E/Z. Methylpropene: C2 has 2CH3 groups (same).","improve":"For E/Z: each C in C=C must have 2 DIFFERENT groups","paper":"2024 C2 Core","marks":1})

qs.append({"id":"pp24c2cq5","subject":"Chem Y1","chapter":"Ch15 Halogenoalkanes","text":"In the conversion of butan-1-ol to 1-bromobutane using NaBr and H2SO4, what is the role of H2SO4?","type":"mc","options":["Oxidising agent","Reducing agent","Source of H+ to protonate -OH and provide Br-","Catalyst only"],"answer":2,"explain":"H2SO4 provides H+ (protonates -OH turning it into good leaving group -OH2+) and reacts with NaBr to generate HBr (source of Br-)","improve":"H2SO4 acts as acid and reacts with NaBr to form HBr reagent","paper":"2024 C2 Core","marks":1})

qs.append({"id":"pp24m1q1a","subject":"Mech Y1","chapter":"Ch10 Forces & Motion","text":"Particle P mass 0.5kg on rough horizontal plane. Normal reaction magnitude?","type":"mc","options":["0.5 N","4.9 N","9.8 N","49 N"],"answer":1,"explain":"R = mg = 0.5 * 9.8 = 4.9 N. Normal reaction equals weight on horizontal surface","improve":"On horizontal surface: R = mg","paper":"2024 M1","marks":1})

with open("_curated_pastpaper_qbank.json", "w", encoding="utf-8") as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

print(f"Total: {len(qs)} curated past paper questions")
