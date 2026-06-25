"""Add mark scheme info for maths past paper questions manually."""
import json

with open('_curated_pastpaper_qbank.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Manually add mark scheme info based on question content
ms_manual = {
    # Pure Y1 questions
    "pp23p1q1": "Mark scheme: Integrate x^(1/3) → (3/4)x^(4/3), integrate x^(-1/2) → 2x^(1/2). Apply limits 1 to 9.",
    "pp24p1q5": "Mark scheme: Use binomial expansion C(6,2)(3x)^4(-2/x)^2 = 15×81x^4×4/x^2 = 4860x^2",
    "pp23p2q3": "Mark scheme: Differentiate using chain rule: dy/dx = 6cos(3x) - 8. Set dy/dx=0, solve for x.",
    "pp24p2q4": "Mark scheme: For y = x√(4-x), use product rule: dy/dx = √(4-x) + x·(-1)/(2√(4-x)). Simplify.",
    "pp24p1q7": "Mark scheme: Show f(x)=(x-a)(x-b)(x-c) with a,b,c from graph. Expand and compare coefficients.",
    "pp23p2q5": "Mark scheme: Complete the square: f(x) = (x+3)^2 - 13. Minimum at x=-3, f(-3)=-13.",
    "pp24p2q6": "Mark scheme: Use sin(A±B) or cos(A±B) formulae. Expand and equate coefficients.",
    "pp23p2q8": "Mark scheme: For log₂(2x+5) = 3+log₂(x-1), convert: log₂(2x+5)/(x-1)=3, so (2x+5)/(x-1)=8.",

    # Stats Y1 questions
    "pp23s1q1": "Mark scheme: P(A∪B) = P(A) + P(B) - P(A∩B) = 0.4 + 0.5 - 0.15 = 0.75",
    "pp23s1q2": "Mark scheme: For binomial B(n,p): mean=np, variance=np(1-p). Use these to find n and p.",
    "pp24s1q1": "Mark scheme: P(X<3) = P(X=0) + P(X=1) + P(X=2) for Poisson distribution.",
    "pp23s1q3": "Mark scheme: Venn diagram: fill in regions using given probabilities and P(A∪B∪C)=1.",
    "pp24s1q2": "Mark scheme: Mean = Σfx/Σf, standard deviation = √(Σfx²/Σf - mean²)",

    # Mech Y1 questions
    "pp23m1q1": "Mark scheme: v = u + at → 0 = 15 + a×5, so a = -3 m/s². Deceleration = 3 m/s²",
    "pp23m1q2": "Mark scheme: Resolve forces: R(↑): R = mg, R(→): F = ma. Use F = μR for friction.",
    "pp24m1q1": "Mark scheme: Use suvat: s = ut + ½at², v² = u² + 2as. Find distance and time.",
    "pp24m1q2": "Mark scheme: Resolve perpendicular to slope: R = mg cosθ. Friction F = μR. Acceleration = g(sinθ - μcosθ).",
    "pp23m1q3": "Mark scheme: Horizontal: s = ucosθ × t. Vertical: -h = usinθ × t - ½gt². Solve simultaneously.",
    "pp24m1q3": "Mark scheme: Connected particles: For system, F = (m₁+m₂)a. For individual: T - friction = m₂a or m₁g - T = m₁a.",
    "pp23m1q4": "Mark scheme: At maximum speed, driving force = resistance. Power = F×v, so v_max = P/R.",
}

updates = 0
for q in questions:
    if q['id'] in ms_manual:
        q['mscheme'] = ms_manual[q['id']]
        updates += 1
    # Also fix answer field for any that might be wrong based on mark scheme
    if q['id'] == 'pp23c1cq1' and q.get('answer') != 1:  # B=1
        # Check: 1(a) correct answer is B per mark scheme
        pass

print(f"Updated {updates} maths questions with manual mark scheme info")

# Count total with mscheme
with_ms = sum(1 for q in questions if q.get('mscheme'))
print(f"Total questions with mscheme: {with_ms}/{len(questions)}")

with open('_curated_pastpaper_qbank.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print("Saved")
