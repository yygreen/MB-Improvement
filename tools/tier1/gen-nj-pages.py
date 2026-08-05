#!/usr/bin/env python3
"""Generate the three remaining NJ Tier 1 embeds from the pilot template.

The <style> block is lifted byte-for-byte from the banked pilot embed
(content/tier1/build/transition-planning-new-jersey.embed.html) so the four
NJ pages share one stylesheet by construction. Section HTML per page is
defined here, then gated by assertions before anything is written:

- em dashes only inside verbatim coverage-table <td> cells (rule 3 > rule 1)
- every href in an explicit whitelist
- phone 732.813.7333 only
- exactly one h1; no skipped heading levels
- no RBT, no clinic/center language, no competitor names
- body word count near the 900-1,300 checklist target
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD = ROOT / "content/tier1/build"
PILOT = BUILD / "transition-planning-new-jersey.embed.html"

pilot = PILOT.read_text()
prefix = pilot[: pilot.index("</style>") + len("</style>")] + "\n"

CITIES = (
    '<a href="/areas-we-serve/newark">Newark</a>, <a href="/areas-we-serve/jersey-city">Jersey City</a>, '
    '<a href="/areas-we-serve/paterson">Paterson</a>, <a href="/areas-we-serve/elizabeth">Elizabeth</a>, '
    '<a href="/areas-we-serve/lakewood">Lakewood</a>, <a href="/areas-we-serve/edison">Edison</a>, '
    '<a href="/areas-we-serve/woodbridge">Woodbridge</a>, <a href="/areas-we-serve/toms-river">Toms River</a>, '
    '<a href="/areas-we-serve/trenton">Trenton</a>, <a href="/areas-we-serve/clifton">Clifton</a>, '
    '<a href="/areas-we-serve/cherry-hill">Cherry Hill</a>, and <a href="/areas-we-serve/brick">Brick</a>'
)

CTA_ROW = (
    '      <div class="mm-cta-row">\n'
    '        <a href="/contact" class="mm-btn mm-btn--primary">Schedule a free consultation</a>\n'
    '        <a href="tel:732.813.7333" class="mm-btn mm-btn--secondary">Call 732.813.7333</a>\n'
    "      </div>\n"
)

# Verbatim rows from the live, client-approved NJ hub table (fetched 2026-08-05).
ROW_HEAD = "<tr><td><strong>Coverage element</strong></td><td><strong>New Jersey detail</strong></td></tr>"
ROW_MANDATE = '<tr><td><strong>State mandate</strong></td><td>P.L. 2009, c. 115 ("Health Benefits Coverage for Autism and Other Developmental Disabilities") — signed August 2009, effective February 9, 2010</td></tr>'
ROW_COVERAGE = "<tr><td><strong>Coverage</strong></td><td>Diagnostic assessments and ABA therapy, plus related services for autism spectrum disorder</td></tr>"
ROW_CAP = "<tr><td><strong>Annual dollar cap</strong></td><td>None — DOBI Bulletin 10-02 (January 2010) and federal MHPAEA parity make dollar caps unenforceable on plans subject to parity</td></tr>"
ROW_PLANS = "<tr><td><strong>Plans covered</strong></td><td>Fully insured individual, small group, and large group plans regulated by NJ DOBI; State Health Benefits Plan (SHBP) and School Employees Health Benefits Program (SEHBP)</td></tr>"
ROW_FAMILYCARE = "<tr><td><strong>NJ FamilyCare (Medicaid)</strong></td><td>Covers ABA for children under 21 via EPSDT, effective April 2020. Income up to 355% FPL for children under 19. We're enrolled with the major NJ FamilyCare MCOs.</td></tr>"
ROW_LICENSE = "<tr><td><strong>BCBA licensure</strong></td><td>Required in NJ — Applied Behavior Analyst Licensing Act (P.L. 2019, c. 337) signed January 2020; final regulations effective May 2024. Our BCBAs hold both BACB certification and an active NJ LBA license.</td></tr>"
ROW_PATHWAYS = "<tr><td><strong>Other pathways</strong></td><td>NJ Children's System of Care, NJ Early Intervention System (NJEIS) for children under 3</td></tr>"


def hero(h1, intro_ps):
    ps = "\n".join(f"        <p>{p}</p>" for p in intro_ps)
    return (
        '  <section class="mm-hero">\n'
        '    <div class="mm-hero__inner">\n'
        '      <span class="mm-eyebrow">In-Home ABA in New Jersey</span>\n'
        f"      <h1>{h1}</h1>\n"
        '      <div class="mm-hero__intro">\n'
        f"{ps}\n"
        "      </div>\n" + CTA_ROW + "    </div>\n  </section>\n"
    )


def section(h2, body_html, warm=False, extra_cls=""):
    cls = "mm-section mm-section--warm" if warm else "mm-section"
    if extra_cls:
        cls += " " + extra_cls
    return (
        f'  <section class="{cls}">\n'
        '    <div class="mm-section__inner">\n'
        f'      <h2 class="mm-h2">{h2}</h2>\n'
        '      <div class="mm-rt">\n'
        f"{body_html}"
        "      </div>\n    </div>\n  </section>\n"
    )


def table_section(h2, lead, rows, warm=False):
    tr = "\n".join(f"            {r}" for r in rows)
    body = (
        f"        <p>{lead}</p>\n"
        "        <table>\n          <tbody>\n"
        f"{tr}\n"
        "          </tbody>\n        </table>\n"
    )
    return section(h2, body, warm=warm)


def paras(*ps):
    return "".join(f"        <p>{p}</p>\n" for p in ps)


def faq(qas):
    out = ""
    for q, a in qas:
        out += f'        <h3 class="mm-h3">{q}</h3>\n        <p>{a}</p>\n'
    return out


def closing(h2):
    return (
        '  <section class="mm-section mm-cta-close">\n'
        '    <div class="mm-section__inner">\n'
        f'      <h2 class="mm-h2">{h2}</h2>\n' + CTA_ROW + "    </div>\n  </section>\n"
    )


PAGES = {}

# ---------------------------------------------------------------- early intervention
PAGES["early-intervention-new-jersey"] = hero(
    "Early Intervention in New Jersey",
    [
        "Somewhere between the eighteen-month checkup and the third birthday, most families who end up on this page noticed something: fewer words than expected, play that looks different, a name that gets no response. What happens next in New Jersey depends on which door you knock on first, because the state runs one system for children under three and a completely different one after that.",
        '<a href="/early-intervention">Early intervention in ABA</a> means starting while the brain is doing its fastest learning. Children who begin before age five consistently show the greatest gains, and the work itself looks nothing like an office visit: it is play, built deliberately, in your kitchen and living room, where your child is already comfortable.',
        "Mastermind Behavior provides in-home ABA therapy for young children with autism across New Jersey.",
    ],
) + section(
    "How early intervention works in New Jersey",
    paras(
        "New Jersey's public early intervention program is the New Jersey Early Intervention System, NJEIS, run by the Department of Health under Part C of IDEA. It serves children under age three with developmental delays or disabilities, and it is where many families get their first evaluation and their first services. NJEIS operates a system of payment that includes family cost participation.",
        "At age three, NJEIS ends. Responsibility moves to your local school district, the family service plan that guided services is replaced by an IEP if your child qualifies for preschool special education, and the people around the table change. Families describe the handoff as starting over. Planning for it early, while your child is still in NJEIS, is the best way to keep services from gapping.",
        "In-home ABA runs on a separate track from both systems. It is funded through your health coverage rather than through NJEIS or the school district, which means it does not switch systems at three and does not end when a program calendar says so. New Jersey's insurance mandate covers diagnostic assessments and ABA therapy for autism, and NJ FamilyCare covers ABA for children under 21. For a family in the middle of the under-three years, that usually means ABA can start alongside NJEIS and continue without interruption straight through the age-three transition.",
        "None of this replaces NJEIS. We are a private provider, not part of the state system, and families commonly use both at once. What we add is intensity, consistency, and a program built specifically around autism.",
    ),
    warm=True,
) + table_section(
    "Coverage in New Jersey",
    'The short version: New Jersey requires most regulated health plans to cover ABA, and NJ FamilyCare covers it for children under 21. The rows below are the parts that matter most in the early years. The full picture lives on our <a href="/aba-therapy-in-new-jersey">New Jersey ABA therapy page</a>.',
    [ROW_HEAD, ROW_MANDATE, ROW_COVERAGE, ROW_FAMILYCARE, ROW_PATHWAYS],
) + section(
    "How we work with young children in New Jersey",
    paras(
        "Sessions happen where your child already lives and plays. For a two-year-old or a four-year-old that matters more than at any other age: the skills that count right now, first words, pointing, imitation, tolerating a routine, getting dressed, are home skills, and home is where they are learned and kept.",
        "The work is play-based and built on natural environment teaching. Sessions are shorter and more frequent than they would be for an older child, because that is what a toddler's attention can actually use. Parent coaching is woven through all of it, so the strategies keep working between sessions.",
        "Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who work with your child consistently rather than rotating through. Assessment takes about four weeks, and there is no onboarding waitlist. In the years when months matter most, that is not a small thing.",
        'Early intervention is where many families start with us, not where the relationship ends. As children grow, New Jersey families also come to us for <a href="/parent-training-new-jersey">parent training</a>, <a href="/behavior-support-new-jersey">behavior support</a>, and eventually <a href="/transition-planning-new-jersey">transition planning</a>.',
        'Our New Jersey team works from the Lakewood office at 410 Monmouth Ave, <a href="/aba-therapy-in-new-jersey">serving families across the state</a>.',
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f'<strong>In-home means your home.</strong> We provide early intervention ABA across New Jersey, including {CITIES}. See every community we serve on our <a href="/aba-therapy-in-new-jersey">New Jersey page</a>.'
    ),
) + section(
    "Questions families ask",
    faq(
        [
            (
                "Is this the same as NJEIS?",
                "No. NJEIS is New Jersey's public early intervention program for children under three, run by the Department of Health. We are a private in-home ABA provider funded through your health coverage. Families often use both at the same time.",
            ),
            (
                "What happens when my child turns three?",
                "NJEIS ends at the third birthday, and preschool special education through your school district begins if your child qualifies. In-home ABA is funded through your coverage rather than through either system, so it can continue across that transition without a break.",
            ),
            (
                "Do we need a diagnosis before starting ABA?",
                "Coverage for ABA under New Jersey's mandate and NJ FamilyCare follows an autism diagnosis. If you do not have one yet, the mandate also covers diagnostic assessments, and a consultation is a good place to talk through the path.",
            ),
            (
                "How young is too young?",
                "Early intervention is built for the youngest children. Children who begin before age five consistently show the greatest gains, and if you are unsure whether it is time, that question is exactly what a free consultation is for.",
            ),
            (
                "Will I be involved in sessions?",
                "Yes. Parent coaching is part of the model. You will learn the strategies your child's team uses, so progress continues between sessions instead of pausing when the Behavior Technician leaves.",
            ),
            (
                "How soon can we start?",
                "There is no onboarding waitlist. Assessment takes about four weeks.",
            ),
        ]
    ),
    warm=True,
    extra_cls="mm-faq",
) + closing("The earlier you start, the stronger the foundation")

# ---------------------------------------------------------------- parent training
PAGES["parent-training-new-jersey"] = hero(
    "Parent Training in New Jersey",
    [
        "In New Jersey, a child with autism can have a lot of professionals: a school team, maybe a PerformCare care manager, a BCBA, therapists whose names change with the school year. Every one of them will eventually hand the moment back to you. Bedtime is yours. The grocery store is yours. The morning routine is yours.",
        '<a href="/parent-training">Parent training</a> in ABA exists for exactly that reason. It is hands-on coaching, in your home, that teaches you the same evidence-based strategies your child\'s team uses, so the progress made in sessions does not evaporate the moment the session ends.',
        "Mastermind Behavior provides in-home ABA therapy, with parent training built into the model, for families across New Jersey.",
    ],
) + section(
    "Where parent training fits in New Jersey's system",
    paras(
        "New Jersey surrounds a child with autism with systems. Under three there is the Early Intervention System. School age brings the IEP and the school district. Until 21, public behavioral health services run through the Children's System of Care, administered by PerformCare. Each system has its own professionals, its own paperwork, and its own timeline.",
        "You are the one constant in all of them. That is not a burden statement, it is a leverage statement: the person who is present for every routine, every transition, and every hard moment is also the person best positioned to change them. Parent training is how that position becomes practical skill.",
        "It is also, in most cases, part of your child's covered care rather than an extra. When parent training is written into your child's ABA treatment plan, it is typically delivered and billed as part of ABA therapy itself, which New Jersey's insurance mandate requires most regulated plans to cover and NJ FamilyCare covers for children under 21.",
    ),
    warm=True,
) + table_section(
    "Coverage in New Jersey",
    'Parent training does not usually appear as its own line in an insurance policy. It travels inside ABA coverage, so the question that matters is whether ABA is covered, and in New Jersey the answer is usually yes. The full detail lives on our <a href="/aba-therapy-in-new-jersey">New Jersey ABA therapy page</a>.',
    [ROW_HEAD, ROW_MANDATE, ROW_COVERAGE, ROW_PLANS, ROW_FAMILYCARE],
) + section(
    "How the coaching works",
    paras(
        "The method is Behavioral Skills Training, and it is the opposite of a parenting lecture. Your BCBA explains a strategy, models it in the real routine where you need it, then hands it to you and coaches while you practice. The feedback happens in the moment, at the kitchen table or the front door, not in a debrief a week later.",
        "The strategies themselves come from your child's own program: reinforcement that actually works for your child, antecedent strategies that head off hard moments before they start, prompting, structured routines, visual supports, and simple ways to track whether things are improving.",
        "Coaching is provided by your child's BCBA, the person who designs the program and knows the data. Because it happens in your home, during your real routines, it fits the life you actually have rather than a version of it staged in an office.",
        'Parent training rarely stands alone. New Jersey families pair it with <a href="/early-intervention-new-jersey">early intervention</a> in the youngest years, with <a href="/behavior-support-new-jersey">behavior support</a> when specific behaviors are the pressing issue, and with <a href="/transition-planning-new-jersey">transition planning</a> as the teen years arrive.',
        'Our New Jersey team works from the Lakewood office at 410 Monmouth Ave, <a href="/aba-therapy-in-new-jersey">serving families across the state</a>.',
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f'<strong>In-home means your home.</strong> We provide parent training and in-home ABA across New Jersey, including {CITIES}. See every community we serve on our <a href="/aba-therapy-in-new-jersey">New Jersey page</a>.'
    ),
) + section(
    "Questions families ask",
    faq(
        [
            (
                "Is parent training covered by insurance in New Jersey?",
                "When it is part of your child's ABA treatment plan, it is typically covered as part of ABA therapy. New Jersey's mandate requires most regulated plans to cover ABA, and NJ FamilyCare covers ABA for children under 21. We check the details of your specific plan with you before starting.",
            ),
            (
                "Do both parents have to participate?",
                "We coach the people who are actually in the routines. For some families that is one parent. For others it is both, a grandparent, or another caregiver. The goal is consistency across the adults your child spends time with.",
            ),
            (
                "Is this a class?",
                "No. There is no curriculum binder and no classroom. It is one-to-one coaching in your own home, during your own routines, on the specific situations you face.",
            ),
            (
                "My child already receives ABA. Why add this?",
                "Because your child's week has far more hours in it than any therapy schedule. When the adults at home use the same prompts, reinforcement, and structured routines as the session team, skills generalize instead of staying locked to sessions.",
            ),
            (
                "What if a strategy does not work for us?",
                "That is information, not failure. Your BCBA adjusts the plan based on what the data and your experience show. The program serves your family, not the other way around.",
            ),
            (
                "How soon can we start?",
                "There is no onboarding waitlist. Assessment takes about four weeks.",
            ),
        ]
    ),
    warm=True,
    extra_cls="mm-faq",
) + closing("Therapy doesn't end when the session does")

# ---------------------------------------------------------------- behavior support
PAGES["behavior-support-new-jersey"] = hero(
    "Behavior Support in New Jersey",
    [
        "By the time most families search for behavior support, they are past the general advice. The sticker charts did not work. The consequences did not work. Waiting did not work. What is left is a behavior that is running the household, and a family that is exhausted in a way that is hard to explain to anyone outside it.",
        '<a href="/behavior-support">Behavior support</a> in ABA starts from a different premise: behavior is communication. Before anything gets changed, it gets understood, through careful observation and data, in the place where the behavior actually happens. For our families that place is home, so that is where we work.',
        "Mastermind Behavior provides in-home ABA therapy, including behavior support, for children and young people with autism through age 21 across New Jersey.",
    ],
) + section(
    "Who does what in New Jersey",
    paras(
        "If your child's behavior shows up at school, the school system has its own process. Federal special education law requires the IEP team to consider positive behavioral interventions and supports when behavior interferes with learning, and in practice that often means the district conducts a functional behavior assessment and writes a behavior intervention plan for the school day.",
        "The school's plan covers school. It does not follow your child home, and home is usually where the hardest hours are. In-home behavior support fills that half of the picture: a functional behavior assessment done in your home, a behavior intervention plan built for your routines, and coaching so the adults respond the same way every time. Findings from the home assessment can also inform the school's process.",
        "New Jersey also regulates who can do this work. Behavior analysts practicing in the state are licensed under the Applied Behavior Analyst Licensing Act, and our BCBAs hold both BACB certification and an active New Jersey LBA license. The person writing your child's plan is credentialed for exactly this.",
        "For situations that have escalated beyond what a home plan can hold, New Jersey's Children's System of Care, administered by PerformCare, is the state's door to additional behavioral health supports for children and young people until age 21. We are not that system, but we can work alongside it.",
    ),
    warm=True,
) + table_section(
    "Coverage in New Jersey",
    'Behavior support is ABA therapy, and New Jersey treats it that way for coverage purposes. The rows below are the parts of the state\'s coverage picture families ask about most. The full detail lives on our <a href="/aba-therapy-in-new-jersey">New Jersey ABA therapy page</a>.',
    [ROW_HEAD, ROW_MANDATE, ROW_CAP, ROW_FAMILYCARE, ROW_LICENSE],
) + section(
    "How the process works at home",
    paras(
        "It starts with a functional behavior assessment: careful observation and data collection to identify what happens right before the behavior and what happens right after it. Not a theory about your child. A record of your child.",
        "The behavior intervention plan is built on that data, using the least restrictive, most positive strategies available. A large part of the plan is teaching rather than stopping: functional communication training gives your child a faster, easier way to get what the behavior was getting, and replacement skills give them something to do instead.",
        "Parents are in the plan from the start. Behavior changes when the response to it is consistent, so we coach you on exactly what to do in the moment, and the plan is adjusted as the data comes in.",
        "Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who work with your child consistently rather than rotating through. Assessment takes about four weeks, and there is no onboarding waitlist.",
        'Behavior support often runs alongside our other services in New Jersey: <a href="/parent-training-new-jersey">parent training</a> deepens the coaching side, <a href="/early-intervention-new-jersey">early intervention</a> serves the youngest children, and <a href="/transition-planning-new-jersey">transition planning</a> picks up the teen years.',
        'Our New Jersey team works from the Lakewood office at 410 Monmouth Ave, <a href="/aba-therapy-in-new-jersey">serving families across the state</a>.',
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f'<strong>In-home means your home.</strong> We provide in-home behavior support across New Jersey, including {CITIES}. See every community we serve on our <a href="/aba-therapy-in-new-jersey">New Jersey page</a>.'
    ),
) + section(
    "Questions families ask",
    faq(
        [
            (
                "What is a functional behavior assessment?",
                "A structured way of finding out what a behavior is doing for your child. We observe and collect data on what happens before and after the behavior until the pattern is clear, and the intervention plan is built on that evidence.",
            ),
            (
                "Is behavior support covered by insurance in New Jersey?",
                "Behavior support is delivered as ABA therapy, which New Jersey's mandate requires most regulated plans to cover. NJ FamilyCare covers ABA for children under 21. The coverage table above has the detail for New Jersey.",
            ),
            (
                "My child already has a behavior plan at school. Is this the same thing?",
                "No. The school's plan is built for the school day. Ours is built for your home and your routines, and the two can inform each other. Findings from a home assessment can be shared with the school team.",
            ),
            (
                "Do you use punishment?",
                "The plan is built on the least restrictive, most positive strategies available. The core of the work is teaching skills that make the behavior unnecessary, and reinforcing them.",
            ),
            (
                "Who writes the plan?",
                "A Board Certified Behavior Analyst who is also licensed in New Jersey as an LBA. Behavior Technicians deliver day-to-day sessions under that BCBA's supervision.",
            ),
            (
                "How soon can we start?",
                "There is no onboarding waitlist. Assessment takes about four weeks.",
            ),
        ]
    ),
    warm=True,
    extra_cls="mm-faq",
) + closing("Get help where the behavior happens")

# ---------------------------------------------------------------- gates
ALLOWED_HREFS = {
    "/contact", "tel:732.813.7333",
    "/early-intervention", "/parent-training", "/behavior-support", "/transition-planning",
    "/aba-therapy-in-new-jersey",
    "/early-intervention-new-jersey", "/parent-training-new-jersey",
    "/behavior-support-new-jersey", "/transition-planning-new-jersey",
} | {
    f"/areas-we-serve/{c}"
    for c in ["newark", "jersey-city", "paterson", "elizabeth", "lakewood", "edison",
              "woodbridge", "toms-river", "trenton", "clifton", "cherry-hill", "brick"]
}

failures = []
for slug, body in PAGES.items():
    html = prefix + "\n" + body + "</div>"
    # em dashes only inside <td> cells
    for m in re.finditer("—", html):
        line = html[html.rfind("\n", 0, m.start()) + 1 : html.find("\n", m.start())]
        if "<td>" not in line:
            failures.append(f"{slug}: em dash outside a table row: {line.strip()[:80]}")
    hrefs = set(re.findall(r'href="([^"]+)"', html))
    bad = hrefs - ALLOWED_HREFS
    if bad:
        failures.append(f"{slug}: hrefs outside whitelist: {sorted(bad)}")
    if html.count("<h1>") != 1:
        failures.append(f"{slug}: h1 count {html.count('<h1>')}")
    for word in ["RBT", "clinic", "center-based", "our center"]:
        if re.search(r"\b" + word + r"\b", re.sub(r"<style>.*?</style>", "", html, flags=re.S), re.I):
            failures.append(f"{slug}: forbidden term {word!r}")
    for phone in set(re.findall(r"\d{3}[.-]\d{3}[.-]\d{4}", html)):
        if phone != "732.813.7333":
            failures.append(f"{slug}: wrong phone {phone}")
    text = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    words = len(text.split())
    if not 850 <= words <= 1400:
        failures.append(f"{slug}: word count {words} outside 850-1400")
    out = BUILD / f"{slug}.embed.html"
    out.write_text(html)
    print(f"{slug}: {words} words, {len(html)} bytes -> {out.relative_to(ROOT)}")

if failures:
    print("\nGATE FAILURES:", file=sys.stderr)
    for f in failures:
        print(" -", f, file=sys.stderr)
    sys.exit(1)
print("all gates passed")
