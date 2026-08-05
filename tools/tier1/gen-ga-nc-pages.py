#!/usr/bin/env python3
"""Generate the Georgia and North Carolina Tier 1 embeds (8 pages).

Same construction discipline as gen-nj-pages.py: the <style> block is lifted
byte-for-byte from the banked pilot embed, and coverage-table rows are read
verbatim from tools/tier1/{georgia,north-carolina}-hub-rows.txt, which were
extracted programmatically from the live client-approved state hubs
(2026-08-05). Fresh copy is gated: em dashes only in verbatim <td> cells,
href whitelists, phone, single h1, forbidden terms, word count.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD = ROOT / "content/tier1/build"
PILOT = BUILD / "transition-planning-new-jersey.embed.html"

pilot = PILOT.read_text()
prefix = pilot[: pilot.index("</style>") + len("</style>")] + "\n"


def load_rows(fname):
    txt = (ROOT / "tools/tier1" / fname).read_text()
    rows = {}
    for r in [x.strip() for x in txt.split("=====") if x.strip()]:
        label = re.search(r"<strong>(.*?)</strong>", r).group(1)
        rows[label] = r
    return rows


GA = load_rows("georgia-hub-rows.txt")
NC = load_rows("north-carolina-hub-rows.txt")

GA_CITIES = [("macon", "Macon"), ("savannah", "Savannah"), ("warner-robins", "Warner Robins"),
             ("perry", "Perry"), ("milledgeville", "Milledgeville"), ("dublin", "Dublin"),
             ("brunswick", "Brunswick"), ("thomasville", "Thomasville"), ("tifton", "Tifton"),
             ("buford", "Buford"), ("snellville", "Snellville"), ("norcross", "Norcross")]
NC_CITIES = [("charlotte", "Charlotte"), ("raleigh", "Raleigh"), ("greensboro-nc", "Greensboro"),
             ("durham", "Durham"), ("winston-salem", "Winston-Salem"), ("fayetteville-nc", "Fayetteville"),
             ("cary", "Cary"), ("wilmington", "Wilmington"), ("concord", "Concord"),
             ("jacksonville", "Jacksonville"), ("asheville", "Asheville"), ("gastonia", "Gastonia")]


def city_links(cities):
    parts = [f'<a href="/areas-we-serve/{slug}">{name}</a>' for slug, name in cities]
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


CTA_ROW = (
    '      <div class="mm-cta-row">\n'
    '        <a href="/contact" class="mm-btn mm-btn--primary">Schedule a free consultation</a>\n'
    '        <a href="tel:732.813.7333" class="mm-btn mm-btn--secondary">Call 732.813.7333</a>\n'
    "      </div>\n"
)


def hero(eyebrow, h1, intro_ps):
    ps = "\n".join(f"        <p>{p}</p>" for p in intro_ps)
    return (
        '  <section class="mm-hero">\n'
        '    <div class="mm-hero__inner">\n'
        f'      <span class="mm-eyebrow">{eyebrow}</span>\n'
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


def table_section(h2, lead, rows):
    tr = "\n".join(f"            {r}" for r in rows)
    body = (
        f"        <p>{lead}</p>\n"
        "        <table>\n          <tbody>\n"
        f"{tr}\n"
        "          </tbody>\n        </table>\n"
    )
    return section(h2, body)


def paras(*ps):
    return "".join(f"        <p>{p}</p>\n" for p in ps)


def faq(qas):
    return "".join(
        f'        <h3 class="mm-h3">{q}</h3>\n        <p>{a}</p>\n' for q, a in qas
    )


def closing(h2):
    return (
        '  <section class="mm-section mm-cta-close">\n'
        '    <div class="mm-section__inner">\n'
        f'      <h2 class="mm-h2">{h2}</h2>\n' + CTA_ROW + "    </div>\n  </section>\n"
    )


GA_OFFICE = 'Our Georgia team works from the Macon office at 4658 Presidential Pkwy, <a href="/aba-therapy-in-georgia">serving families across the state</a>.'
NC_REACH = 'We serve families across North Carolina; our <a href="/aba-therapy-in-north-carolina">North Carolina page</a> lists every community.'

PAGES = {}

# ================================================================ GEORGIA
GA_EYEBROW = "In-Home ABA in Georgia"

PAGES["transition-planning-georgia"] = hero(
    GA_EYEBROW,
    "Transition Planning in Georgia",
    [
        """In Georgia, the systems that support a child with autism mostly wind down in the early twenties. Special education ends at graduation or aging out. The insurance mandate covers through age 20. Medicaid ABA coverage runs to 21. What comes after is a set of adult supports your family applies to, waits for, and navigates, and the families who do best are the ones who started preparing years before the deadline.""",
        """<a href="/transition-planning">Transition planning in ABA</a> means teaching the skills adult life will ask for while there is still time to teach them: self-advocacy, daily living routines, handling unstructured time, communicating with people who do not already know your child. We work on them in your home and in your community, where they will actually be used.""",
        """Mastermind Behavior provides in-home ABA therapy for children and young people with autism through age 21, across Georgia.""",
    ],
) + section(
    "What Georgia requires, and when",
    paras(
        """On the school side, Georgia follows the federal timeline. Under IDEA, transition services must be in place in the IEP by the time your child turns 16, and your child must be invited to IEP meetings where transition is discussed. Many teams begin earlier, and nothing stops you from asking for that.""",
        """On the adult side, the agency that matters is the Department of Behavioral Health and Developmental Disabilities, DBHDD. Georgia's home and community based supports for adults with developmental disabilities run through two Medicaid waivers, the New Options Waiver and the Comprehensive Supports Waiver, and DBHDD manages the day-to-day operation of both.""",
        """Here is the part worth writing down: waiver slots are limited, demand runs ahead of supply, and waits are commonly measured in years. The application is not something to hold until the last year of school. Families who apply early, keep documentation current, and stay in contact with their DBHDD regional field office give themselves options that late applicants do not have.""",
        """Meanwhile the funding that pays for ABA itself has its own clock. Ava's Law coverage is mandated through age 20. Georgia Medicaid covers ABA to 21 under EPSDT. Special education continues until your child graduates or ages out. All of these end within a short span, which is exactly why the skills work belongs in the years before the deadline, not the year of it.""",
    ),
    warm=True,
) + table_section(
    "Coverage in Georgia",
    """Coverage in the transition years is a countdown, and the rows below are the clocks that matter most. The full Georgia picture lives on our <a href="/aba-therapy-in-georgia">Georgia ABA therapy page</a>.""",
    [GA["Coverage element"], GA["State mandate"], GA["Age limit"], GA["Medicaid"], GA["Other programs"]],
) + section(
    "How we work with teens in Georgia",
    paras(
        """Everything we do happens in your home and in the places your child already goes, and for a teenager that increasingly means the places adult life will happen: the kitchen, the store, the job application, the bus ride, the plan that changes at the last minute.""",
        """Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who work with your child consistently rather than rotating through. Assessment takes about four weeks, and there is no onboarding waitlist, which matters most in the years when time is the scarcest resource.""",
        """Your BCBA can contribute to the IEP process.""",
        """Transition planning connects to our other Georgia services: <a href="/behavior-support-georgia">behavior support</a> when specific behaviors stand in the way, <a href="/parent-training-georgia">parent training</a> so the skills hold at home, and <a href="/early-intervention-georgia">early intervention</a> for the youngest children.""",
        GA_OFFICE,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide transition-focused ABA across Georgia, including {city_links(GA_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-georgia">Georgia page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("When does transition planning start in Georgia?",
         """Federal law requires transition services to be in the IEP by age 16. Teams can address it earlier when appropriate, and asking for that is reasonable."""),
        ("What is DBHDD and when should we apply?",
         """The Department of Behavioral Health and Developmental Disabilities runs Georgia's adult developmental disability supports, including the NOW and COMP Medicaid waivers. Because waits for waiver slots are commonly measured in years, applying early in the transition years is the safer path."""),
        ("What happens when my child turns 21?",
         """The insurance mandate covers through age 20, Georgia Medicaid covers ABA to 21, and special education ends at graduation or aging out. After that, support runs through adult systems that require their own applications and eligibility determinations."""),
        ("What is the Katie Beckett waiver?",
         """A Medicaid pathway for children with disabilities whose family income exceeds standard Medicaid limits. It is one of the alternative routes listed in the coverage table above."""),
        ("Can ABA therapy continue through the transition years?",
         """We work with children and young people through age 21. Whether it continues uninterrupted depends on your coverage, which is covered above."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("Start while there is still time to teach")

PAGES["early-intervention-georgia"] = hero(
    GA_EYEBROW,
    "Early Intervention in Georgia",
    [
        """It usually starts with a feeling before it starts with a form: fewer words than the checklist says, play that looks different, a name that gets no response. What happens next in Georgia depends on which door you knock on first, because the state runs one system for children under three and a different one after that.""",
        """<a href="/early-intervention">Early intervention in ABA</a> means starting while the brain is doing its fastest learning. Children who begin before age five consistently show the greatest gains, and the work looks nothing like an office visit: it is deliberate, play-based teaching in your kitchen and living room, where your child is already comfortable.""",
        """Mastermind Behavior provides in-home ABA therapy for young children with autism across Georgia.""",
    ],
) + section(
    "How early intervention works in Georgia",
    paras(
        """Georgia's public early intervention program is Babies Can't Wait, run by the Department of Public Health under Part C of IDEA. It serves infants and toddlers with special needs from birth to three, and referrals can be made by phone, email, fax, letter, or in person. For many families it is the first evaluation and the first services their child receives.""",
        """At age three, Babies Can't Wait ends and responsibility moves to your local school district, where your child may qualify for preschool special education under an IEP. The program publishes its own transition-at-three materials because the handoff takes planning. Starting that planning early is the best way to keep services from gapping.""",
        """In-home ABA runs on a separate track from both systems. It is funded through your health coverage rather than a program calendar, so it does not switch systems at three. Ava's Law requires most state-regulated plans to cover diagnostic assessments and ABA therapy, and Georgia Medicaid covers ABA for individuals under 21, at up to 40 hours per week for children under six. For a family in the under-three years, ABA can usually start alongside Babies Can't Wait and continue straight through the age-three transition.""",
        """None of this replaces Babies Can't Wait. We are a private provider, not part of the state system, and families commonly use both at once. What we add is intensity, consistency, and a program built specifically around autism.""",
    ),
    warm=True,
) + table_section(
    "Coverage in Georgia",
    """The short version: most state-regulated Georgia plans must cover ABA, and Georgia Medicaid covers it for individuals under 21, with its highest weekly-hours allowance in the under-six years. The full picture lives on our <a href="/aba-therapy-in-georgia">Georgia ABA therapy page</a>.""",
    [GA["Coverage element"], GA["State mandate"], GA["Coverage"], GA["Medicaid"], GA["Other programs"]],
) + section(
    "How we work with young children in Georgia",
    paras(
        """For a two-year-old, the skills that matter are home skills: first words, pointing, imitation, tolerating a routine, getting dressed. So that is where we teach them, in the rooms where they will be used, woven into play your child actually wants to be part of.""",
        """Sessions are shorter and more frequent than they would be for an older child, matched to a toddler's attention. The teaching leans on natural environment methods, and parent coaching runs through all of it so progress keeps moving between sessions.""",
        """Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who stay with your child consistently. Assessment takes about four weeks, and there is no onboarding waitlist. In the years when months matter most, that is not a small thing.""",
        """As children grow, Georgia families also come to us for <a href="/parent-training-georgia">parent training</a>, <a href="/behavior-support-georgia">behavior support</a>, and eventually <a href="/transition-planning-georgia">transition planning</a>.""",
        GA_OFFICE,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide early intervention ABA across Georgia, including {city_links(GA_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-georgia">Georgia page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("Is this the same as Babies Can't Wait?",
         """No. Babies Can't Wait is Georgia's public early intervention program for children from birth to three, run by the Department of Public Health. We are a private in-home ABA provider funded through your health coverage. Families often use both at the same time."""),
        ("What happens when my child turns three?",
         """Babies Can't Wait ends at the third birthday, and preschool special education through your school district begins if your child qualifies. In-home ABA is funded through your coverage rather than through either system, so it can continue across that transition without a break."""),
        ("Do we need a diagnosis before starting ABA?",
         """Coverage follows an autism diagnosis. Ava's Law also covers diagnostic assessments, and Georgia Medicaid requires a DSM-5 autism diagnosis from a licensed professional with prior authorization through your Care Management Organization. A consultation is a good place to talk through the path."""),
        ("How young is too young?",
         """Early intervention is built for the youngest children. Children who begin before age five consistently show the greatest gains, and if you are unsure whether it is time, that question is exactly what a free consultation is for."""),
        ("Will I be involved in sessions?",
         """Yes. Parent coaching is part of the model. You will learn the strategies your child's team uses, so progress continues between sessions instead of pausing when the Behavior Technician leaves."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("The earlier you start, the stronger the foundation")

PAGES["parent-training-georgia"] = hero(
    GA_EYEBROW,
    "Parent Training in Georgia",
    [
        """A child with autism in Georgia can have a long list of professionals: a Babies Can't Wait coordinator in the early years, a school team, a BCBA, a care manager at a Medicaid CMO. Every one of them eventually hands the moment back to you. Bedtime is yours. The grocery store is yours. The morning routine is yours.""",
        """<a href="/parent-training">Parent training</a> in ABA exists for exactly that reason. It is hands-on coaching, in your home, that teaches you the same evidence-based strategies your child's team uses, so progress made in sessions does not evaporate when the session ends.""",
        """Mastermind Behavior provides in-home ABA therapy, with parent training built into the model, for families across Georgia.""",
    ],
) + section(
    "Where parent training fits in Georgia's system",
    paras(
        """Georgia surrounds a child with autism with systems: Babies Can't Wait before three, the school district and IEP after, a Care Management Organization if your child's ABA runs through Medicaid, and pathways like Katie Beckett for families whose income sits above standard Medicaid limits. Each has its own professionals, paperwork, and timeline.""",
        """You are the one constant in all of them, and that is leverage, not just load: the person present for every routine, every transition, and every hard moment is also the person best positioned to change them. Parent training turns that position into practical skill.""",
        """It is also, in most cases, part of your child's covered care rather than an extra. When parent training is written into your child's ABA treatment plan, it is typically delivered and billed as part of ABA therapy itself, which Ava's Law requires most state-regulated plans to cover and Georgia Medicaid covers for individuals under 21.""",
    ),
    warm=True,
) + table_section(
    "Coverage in Georgia",
    """Parent training rarely appears as its own line in a policy. It travels inside ABA coverage, so the question that matters is whether ABA is covered, and in Georgia the answer is usually yes. The full detail lives on our <a href="/aba-therapy-in-georgia">Georgia ABA therapy page</a>.""",
    [GA["Coverage element"], GA["State mandate"], GA["Coverage"], GA["Plans covered"], GA["Medicaid"]],
) + section(
    "How the coaching works",
    paras(
        """The method is Behavioral Skills Training, which is the opposite of a parenting lecture. Your BCBA explains a strategy, models it inside the routine where you need it, then coaches while you practice it yourself. Feedback lands in the moment, at the kitchen table or the front door, not in a debrief a week later.""",
        """The strategies come from your child's own program: reinforcement that actually works for your child, antecedent strategies that head off hard moments, prompting, structured routines, visual supports, and simple ways to track whether things are improving.""",
        """Coaching is provided by your child's BCBA, the person who designs the program and knows the data, and it happens during your real routines rather than a staged version of them.""",
        """Parent training rarely stands alone. Georgia families pair it with <a href="/early-intervention-georgia">early intervention</a> in the youngest years, <a href="/behavior-support-georgia">behavior support</a> when specific behaviors press hardest, and <a href="/transition-planning-georgia">transition planning</a> as the teen years arrive.""",
        GA_OFFICE,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide parent training and in-home ABA across Georgia, including {city_links(GA_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-georgia">Georgia page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("Is parent training covered by insurance in Georgia?",
         """When it is part of your child's ABA treatment plan, it is typically covered as part of ABA therapy. Ava's Law requires most state-regulated plans to cover ABA, and Georgia Medicaid covers ABA for individuals under 21. We check your specific plan with you before starting."""),
        ("Do both parents have to participate?",
         """We coach the people who are actually in the routines. For some families that is one parent. For others it is both, a grandparent, or another caregiver. The goal is consistency across the adults your child spends time with."""),
        ("Is this a class?",
         """No. There is no curriculum binder and no classroom. It is one-to-one coaching in your own home, during your own routines, on the specific situations you face."""),
        ("My child already receives ABA. Why add this?",
         """Because your child's week has far more hours in it than any therapy schedule. When the adults at home use the same prompts, reinforcement, and structured routines as the session team, skills generalize instead of staying locked to sessions."""),
        ("What if a strategy does not work for us?",
         """That is information, not failure. Your BCBA adjusts the plan based on what the data and your experience show. The program serves your family, not the other way around."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("Therapy doesn't end when the session does")

PAGES["behavior-support-georgia"] = hero(
    GA_EYEBROW,
    "Behavior Support in Georgia",
    [
        """Most families who search for behavior support are past the general advice. The sticker charts did not work. The consequences did not work. Waiting did not work. What is left is a behavior that is running the household, and a family that is exhausted in a way that is hard to explain to anyone outside it.""",
        """<a href="/behavior-support">Behavior support</a> in ABA starts from a different premise: behavior is communication. Before anything gets changed, it gets understood, through careful observation and data, in the place where the behavior actually happens. For our families that place is home, so that is where we work.""",
        """Mastermind Behavior provides in-home ABA therapy, including behavior support, for children and young people with autism through age 21 across Georgia.""",
    ],
) + section(
    "Who does what in Georgia",
    paras(
        """If the behavior shows up at school, the school system has its own process. Federal special education law requires the IEP team to consider positive behavioral interventions and supports when behavior interferes with learning, which in practice often means the district conducts a functional behavior assessment and writes a behavior intervention plan for the school day.""",
        """The school's plan covers school. It does not follow your child home, and home is usually where the hardest hours are. In-home behavior support fills that half of the picture: a functional behavior assessment done in your home, a behavior intervention plan built for your routines, and coaching so the adults respond the same way every time. Findings from the home assessment can also inform the school's process.""",
        """Georgia also regulates who can do this work. Behavior analysts are required to be state-licensed, and our BCBAs serving Georgia families hold both BACB certification and a current Georgia license. The person writing your child's plan is credentialed for exactly this.""",
        """For situations that have grown beyond what a home plan can hold, Georgia's Department of Behavioral Health and Developmental Disabilities is the state's door to additional developmental disability supports. We are not that system, but we can work alongside it.""",
    ),
    warm=True,
) + table_section(
    "Coverage in Georgia",
    """Behavior support is ABA therapy, and Georgia treats it that way for coverage purposes. The rows below are the parts of the state's picture families ask about most. The full detail lives on our <a href="/aba-therapy-in-georgia">Georgia ABA therapy page</a>.""",
    [GA["Coverage element"], GA["State mandate"], GA["Annual dollar cap"], GA["Medicaid"], GA["BCBA licensure"]],
) + section(
    "How the process works at home",
    paras(
        """It starts with a functional behavior assessment: careful observation and data collection to identify what happens right before the behavior and what happens right after it. Not a theory about your child. A record of your child.""",
        """The behavior intervention plan is built on that data, using the least restrictive, most positive strategies available. A large part of the plan is teaching rather than stopping: functional communication training gives your child a faster, easier way to get what the behavior was getting, and replacement skills give them something to do instead.""",
        """Parents are in the plan from the start. Behavior changes when the response to it is consistent, so we coach you on exactly what to do in the moment, and the plan is adjusted as the data comes in.""",
        """Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who work with your child consistently rather than rotating through. Assessment takes about four weeks, and there is no onboarding waitlist.""",
        """Behavior support often runs alongside our other Georgia services: <a href="/parent-training-georgia">parent training</a> deepens the coaching side, <a href="/early-intervention-georgia">early intervention</a> serves the youngest children, and <a href="/transition-planning-georgia">transition planning</a> picks up the teen years.""",
        GA_OFFICE,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide in-home behavior support across Georgia, including {city_links(GA_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-georgia">Georgia page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("What is a functional behavior assessment?",
         """A structured way of finding out what a behavior is doing for your child. We observe and collect data on what happens before and after the behavior until the pattern is clear, and the intervention plan is built on that evidence."""),
        ("Is behavior support covered by insurance in Georgia?",
         """Behavior support is delivered as ABA therapy, which Ava's Law requires most state-regulated plans to cover. Georgia Medicaid covers ABA for individuals under 21. The coverage table above has the detail."""),
        ("My child already has a behavior plan at school. Is this the same thing?",
         """No. The school's plan is built for the school day. Ours is built for your home and your routines, and the two can inform each other. Findings from a home assessment can be shared with the school team."""),
        ("Do you use punishment?",
         """The plan is built on the least restrictive, most positive strategies available. The core of the work is teaching skills that make the behavior unnecessary, and reinforcing them."""),
        ("Who writes the plan?",
         """A Board Certified Behavior Analyst who also holds a current Georgia behavior analyst license. Behavior Technicians deliver day-to-day sessions under that BCBA's supervision."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("Get help where the behavior happens")

# ================================================================ NORTH CAROLINA
NC_EYEBROW = "In-Home ABA in North Carolina"

PAGES["transition-planning-north-carolina"] = hero(
    NC_EYEBROW,
    "Transition Planning in North Carolina",
    [
        """North Carolina's transition story has a twist most states do not have: Medicaid here covers ABA for adults over 21. That does not make transition planning optional. School still ends. The children's coverage rules still change. But it changes what the years after 21 can look like, and it makes the planning years count double.""",
        """<a href="/transition-planning">Transition planning in ABA</a> means teaching the skills adult life will ask for while there is still time to teach them: self-advocacy, daily living routines, handling unstructured time, communicating with people who do not already know your child. We work on them in your home and in your community, where they will actually be used.""",
        """Mastermind Behavior provides in-home ABA therapy for children and young people with autism through age 21, across North Carolina.""",
    ],
) + section(
    "What North Carolina requires, and when",
    paras(
        """On the school side, North Carolina follows the federal timeline. Under IDEA, transition services must be in place in the IEP by the time your child turns 16, and your child must be invited to IEP meetings where transition is discussed. Many teams begin earlier, and nothing stops you from asking for that.""",
        """On the adult services side, long-term developmental disability supports run through the NC Innovations Waiver, administered through your regional LME/MCO. Demand for waiver slots runs far ahead of supply and waits are long, which is why families are urged to get on the list years before adulthood rather than at the end of school.""",
        """Now the twist. On the coverage side, the private-plan mandate runs to age 19, and NC Medicaid covers ABA for children under 21 through EPSDT. But North Carolina is one of the few states where Medicaid also covers ABA for adults over 21, approved by CMS effective July 1, 2021. For families whose child is on Medicaid, turning 21 is a change in process, not automatically the end of ABA coverage.""",
        """The IEP still ends when school does, and whatever your child can do independently by then is what they carry forward. That is the case for starting the skills work early, with the adult-services paperwork moving in parallel rather than after.""",
    ),
    warm=True,
) + table_section(
    "Coverage in North Carolina",
    """The rows below are the clocks that matter most in the transition years, including the one that keeps running. The full North Carolina picture lives on our <a href="/aba-therapy-in-north-carolina">North Carolina ABA therapy page</a>.""",
    [NC["Coverage element"], NC["State mandate"], NC["Age limit"], NC["NC Medicaid (children)"], NC["NC Medicaid (adults 21+)"]],
) + section(
    "How we work with teens in North Carolina",
    paras(
        """Everything we do happens in your home and in the places your child already goes, and for a teenager that increasingly means the places adult life will happen: the kitchen, the store, the bus ride, the plan that changes at the last minute.""",
        """Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who work with your child consistently rather than rotating through. Assessment takes about four weeks, and there is no onboarding waitlist, which matters most in the years when time is the scarcest resource.""",
        """Your BCBA can contribute to the IEP process.""",
        """Transition planning connects to our other North Carolina services: <a href="/behavior-support-north-carolina">behavior support</a> when specific behaviors stand in the way, <a href="/parent-training-north-carolina">parent training</a> so the skills hold at home, and <a href="/early-intervention-north-carolina">early intervention</a> for the youngest children.""",
        NC_REACH,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide transition-focused ABA across North Carolina, including {city_links(NC_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-north-carolina">North Carolina page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("When does transition planning start in North Carolina?",
         """Federal law requires transition services to be in the IEP by age 16. Teams can address it earlier when appropriate, and asking for that is reasonable."""),
        ("What is the Innovations Waiver and when should we apply?",
         """It is North Carolina's Medicaid waiver for long-term developmental disability supports, administered through your regional LME/MCO. Waits are long, so getting on the list early in the transition years is the safer path."""),
        ("What happens when my child turns 21?",
         """School services end at graduation or aging out, and children's Medicaid coverage rules change. North Carolina is one of the few states where Medicaid covers ABA for adults over 21, so continued therapy can be possible depending on your coverage. Talk to us about what continuity can look like for your family."""),
        ("Does the insurance mandate cover my teenager?",
         """The state mandate applies to individuals under 19 on state-regulated plans. Medicaid coverage runs broader, as the table above shows."""),
        ("Can ABA therapy continue through the transition years?",
         """We work with children and young people through age 21. Whether it continues uninterrupted depends on your coverage, which is covered above."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("Start while there is still time to teach")

PAGES["early-intervention-north-carolina"] = hero(
    NC_EYEBROW,
    "Early Intervention in North Carolina",
    [
        """It usually starts with a feeling before it starts with a form: fewer words than the checklist says, play that looks different, a name that gets no response. What happens next in North Carolina depends on which door you knock on first, because the state runs one system for children under three and a different one after that.""",
        """<a href="/early-intervention">Early intervention in ABA</a> means starting while the brain is doing its fastest learning. Children who begin before age five consistently show the greatest gains, and the work looks nothing like an office visit: it is deliberate, play-based teaching in your kitchen and living room, where your child is already comfortable.""",
        """Mastermind Behavior provides in-home ABA therapy for young children with autism across North Carolina.""",
    ],
) + section(
    "How early intervention works in North Carolina",
    paras(
        """North Carolina's public early intervention program is the NC Infant-Toddler Program, run by the Early Intervention Section of the Division of Child and Family Well-Being under Part C of IDEA. It serves children younger than three who have a developmental delay or an established condition, with services delivered through sixteen local Children's Developmental Services Agencies, CDSAs. Referrals can be made by phone, fax, letter, in person, or with the program's referral form.""",
        """At age three, the Infant-Toddler Program ends and responsibility moves to your local school district, where your child may qualify for preschool special education under an IEP. The handoff takes planning, and starting that planning early is the best way to keep services from gapping.""",
        """In-home ABA runs on a separate track from both systems. It is funded through your health coverage rather than a program calendar, so it does not switch systems at three. North Carolina's mandate requires state-regulated plans to cover adaptive behavior treatment for autism, and NC Medicaid covers ABA for children under 21 through EPSDT. For a family in the under-three years, ABA can usually start alongside the Infant-Toddler Program and continue straight through the age-three transition.""",
        """None of this replaces the Infant-Toddler Program. We are a private provider, not part of the state system, and families commonly use both at once. What we add is intensity, consistency, and a program built specifically around autism.""",
    ),
    warm=True,
) + table_section(
    "Coverage in North Carolina",
    """The short version: state-regulated North Carolina plans must cover adaptive behavior treatment for autism, and NC Medicaid covers ABA for children under 21. The full picture lives on our <a href="/aba-therapy-in-north-carolina">North Carolina ABA therapy page</a>.""",
    [NC["Coverage element"], NC["State mandate"], NC["Coverage"], NC["Age limit"], NC["NC Medicaid (children)"]],
) + section(
    "How we work with young children in North Carolina",
    paras(
        """For a two-year-old, the skills that matter are home skills: first words, pointing, imitation, tolerating a routine, getting dressed. So that is where we teach them, in the rooms where they will be used, woven into play your child actually wants to be part of.""",
        """Sessions are shorter and more frequent than they would be for an older child, matched to a toddler's attention. The teaching leans on natural environment methods, and parent coaching runs through all of it so progress keeps moving between sessions.""",
        """Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who stay with your child consistently. Assessment takes about four weeks, and there is no onboarding waitlist. In the years when months matter most, that is not a small thing.""",
        """As children grow, North Carolina families also come to us for <a href="/parent-training-north-carolina">parent training</a>, <a href="/behavior-support-north-carolina">behavior support</a>, and eventually <a href="/transition-planning-north-carolina">transition planning</a>.""",
        NC_REACH,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide early intervention ABA across North Carolina, including {city_links(NC_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-north-carolina">North Carolina page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("Is this the same as the Infant-Toddler Program?",
         """No. The NC Infant-Toddler Program is the state's public early intervention program for children under three, delivered through your local CDSA. We are a private in-home ABA provider funded through your health coverage. Families often use both at the same time."""),
        ("What happens when my child turns three?",
         """The Infant-Toddler Program ends at the third birthday, and preschool special education through your school district begins if your child qualifies. In-home ABA is funded through your coverage rather than through either system, so it can continue across that transition without a break."""),
        ("Do we need a diagnosis before starting ABA?",
         """Coverage follows an autism diagnosis. If you do not have one yet, a consultation is a good place to talk through the path, including how evaluations work under your plan."""),
        ("How young is too young?",
         """Early intervention is built for the youngest children. Children who begin before age five consistently show the greatest gains, and if you are unsure whether it is time, that question is exactly what a free consultation is for."""),
        ("Will I be involved in sessions?",
         """Yes. Parent coaching is part of the model. You will learn the strategies your child's team uses, so progress continues between sessions instead of pausing when the Behavior Technician leaves."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("The earlier you start, the stronger the foundation")

PAGES["parent-training-north-carolina"] = hero(
    NC_EYEBROW,
    "Parent Training in North Carolina",
    [
        """A child with autism in North Carolina can have a long list of professionals: a CDSA service coordinator in the early years, a school team, a BCBA, a care manager at your health plan. Every one of them eventually hands the moment back to you. Bedtime is yours. The grocery store is yours. The morning routine is yours.""",
        """<a href="/parent-training">Parent training</a> in ABA exists for exactly that reason. It is hands-on coaching, in your home, that teaches you the same evidence-based strategies your child's team uses, so progress made in sessions does not evaporate when the session ends.""",
        """Mastermind Behavior provides in-home ABA therapy, with parent training built into the model, for families across North Carolina.""",
    ],
) + section(
    "Where parent training fits in North Carolina's system",
    paras(
        """North Carolina surrounds a child with autism with systems: the Infant-Toddler Program before three, the school district and IEP after, and Medicaid plans managed through LME/MCOs, Tailored Plans, or Standard Plans. Each has its own professionals, paperwork, and timeline.""",
        """You are the one constant in all of them, and that is leverage, not just load: the person present for every routine, every transition, and every hard moment is also the person best positioned to change them. Parent training turns that position into practical skill.""",
        """It is also, in most cases, part of your child's covered care rather than an extra. When parent training is written into your child's ABA treatment plan, it is typically delivered and billed as part of ABA therapy itself, which North Carolina's mandate requires state-regulated plans to cover and NC Medicaid covers for children under 21.""",
    ),
    warm=True,
) + table_section(
    "Coverage in North Carolina",
    """Parent training rarely appears as its own line in a policy. It travels inside ABA coverage, so the question that matters is whether ABA is covered, and in North Carolina the answer is usually yes. The full detail lives on our <a href="/aba-therapy-in-north-carolina">North Carolina ABA therapy page</a>.""",
    [NC["Coverage element"], NC["State mandate"], NC["Coverage"], NC["NC Medicaid (children)"], NC["LME/MCOs"]],
) + section(
    "How the coaching works",
    paras(
        """The method is Behavioral Skills Training, which is the opposite of a parenting lecture. Your BCBA explains a strategy, models it inside the routine where you need it, then coaches while you practice it yourself. Feedback lands in the moment, at the kitchen table or the front door, not in a debrief a week later.""",
        """The strategies come from your child's own program: reinforcement that actually works for your child, antecedent strategies that head off hard moments, prompting, structured routines, visual supports, and simple ways to track whether things are improving.""",
        """Coaching is provided by your child's BCBA, the person who designs the program and knows the data, and it happens during your real routines rather than a staged version of them.""",
        """Parent training rarely stands alone. North Carolina families pair it with <a href="/early-intervention-north-carolina">early intervention</a> in the youngest years, <a href="/behavior-support-north-carolina">behavior support</a> when specific behaviors press hardest, and <a href="/transition-planning-north-carolina">transition planning</a> as the teen years arrive.""",
        NC_REACH,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide parent training and in-home ABA across North Carolina, including {city_links(NC_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-north-carolina">North Carolina page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("Is parent training covered by insurance in North Carolina?",
         """When it is part of your child's ABA treatment plan, it is typically covered as part of ABA therapy. North Carolina's mandate requires state-regulated plans to cover adaptive behavior treatment, and NC Medicaid covers ABA for children under 21. We check your specific plan with you before starting."""),
        ("Do both parents have to participate?",
         """We coach the people who are actually in the routines. For some families that is one parent. For others it is both, a grandparent, or another caregiver. The goal is consistency across the adults your child spends time with."""),
        ("Is this a class?",
         """No. There is no curriculum binder and no classroom. It is one-to-one coaching in your own home, during your own routines, on the specific situations you face."""),
        ("My child already receives ABA. Why add this?",
         """Because your child's week has far more hours in it than any therapy schedule. When the adults at home use the same prompts, reinforcement, and structured routines as the session team, skills generalize instead of staying locked to sessions."""),
        ("What if a strategy does not work for us?",
         """That is information, not failure. Your BCBA adjusts the plan based on what the data and your experience show. The program serves your family, not the other way around."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("Therapy doesn't end when the session does")

PAGES["behavior-support-north-carolina"] = hero(
    NC_EYEBROW,
    "Behavior Support in North Carolina",
    [
        """Most families who search for behavior support are past the general advice. The sticker charts did not work. The consequences did not work. Waiting did not work. What is left is a behavior that is running the household, and a family that is exhausted in a way that is hard to explain to anyone outside it.""",
        """<a href="/behavior-support">Behavior support</a> in ABA starts from a different premise: behavior is communication. Before anything gets changed, it gets understood, through careful observation and data, in the place where the behavior actually happens. For our families that place is home, so that is where we work.""",
        """Mastermind Behavior provides in-home ABA therapy, including behavior support, for children and young people with autism through age 21 across North Carolina.""",
    ],
) + section(
    "Who does what in North Carolina",
    paras(
        """If the behavior shows up at school, the school system has its own process. Federal special education law requires the IEP team to consider positive behavioral interventions and supports when behavior interferes with learning, which in practice often means the district conducts a functional behavior assessment and writes a behavior intervention plan for the school day.""",
        """The school's plan covers school. It does not follow your child home, and home is usually where the hardest hours are. In-home behavior support fills that half of the picture: a functional behavior assessment done in your home, a behavior intervention plan built for your routines, and coaching so the adults respond the same way every time. Findings from the home assessment can also inform the school's process.""",
        """North Carolina also regulates who can do this work. Behavior analyst licensure is required in the state, and our BCBAs hold both BACB certification and an active North Carolina behavior analyst license. The person writing your child's plan is credentialed for exactly this.""",
        """For situations that have grown beyond what a home plan can hold, North Carolina's public behavioral health system runs through regional LME/MCOs. We are not that system, but we can work alongside it.""",
    ),
    warm=True,
) + table_section(
    "Coverage in North Carolina",
    """Behavior support is ABA therapy, and North Carolina treats it that way for coverage purposes. The rows below are the parts of the state's picture families ask about most. The full detail lives on our <a href="/aba-therapy-in-north-carolina">North Carolina ABA therapy page</a>.""",
    [NC["Coverage element"], NC["State mandate"], NC["Annual dollar cap"], NC["NC Medicaid (children)"], NC["BCBA licensure"]],
) + section(
    "How the process works at home",
    paras(
        """It starts with a functional behavior assessment: careful observation and data collection to identify what happens right before the behavior and what happens right after it. Not a theory about your child. A record of your child.""",
        """The behavior intervention plan is built on that data, using the least restrictive, most positive strategies available. A large part of the plan is teaching rather than stopping: functional communication training gives your child a faster, easier way to get what the behavior was getting, and replacement skills give them something to do instead.""",
        """Parents are in the plan from the start. Behavior changes when the response to it is consistent, so we coach you on exactly what to do in the moment, and the plan is adjusted as the data comes in.""",
        """Programs are designed and supervised by a BCBA and delivered by Behavior Technicians who work with your child consistently rather than rotating through. Assessment takes about four weeks, and there is no onboarding waitlist.""",
        """Behavior support often runs alongside our other North Carolina services: <a href="/parent-training-north-carolina">parent training</a> deepens the coaching side, <a href="/early-intervention-north-carolina">early intervention</a> serves the youngest children, and <a href="/transition-planning-north-carolina">transition planning</a> picks up the teen years.""",
        NC_REACH,
    ),
    warm=True,
) + section(
    "Where we serve",
    paras(
        f"""<strong>In-home means your home.</strong> We provide in-home behavior support across North Carolina, including {city_links(NC_CITIES)}. See every community we serve on our <a href="/aba-therapy-in-north-carolina">North Carolina page</a>."""
    ),
) + section(
    "Questions families ask",
    faq([
        ("What is a functional behavior assessment?",
         """A structured way of finding out what a behavior is doing for your child. We observe and collect data on what happens before and after the behavior until the pattern is clear, and the intervention plan is built on that evidence."""),
        ("Is behavior support covered by insurance in North Carolina?",
         """Behavior support is delivered as ABA therapy. North Carolina's mandate requires state-regulated plans to cover adaptive behavior treatment for autism, and NC Medicaid covers ABA for children under 21. The coverage table above has the detail."""),
        ("My child already has a behavior plan at school. Is this the same thing?",
         """No. The school's plan is built for the school day. Ours is built for your home and your routines, and the two can inform each other. Findings from a home assessment can be shared with the school team."""),
        ("Do you use punishment?",
         """The plan is built on the least restrictive, most positive strategies available. The core of the work is teaching skills that make the behavior unnecessary, and reinforcing them."""),
        ("Who writes the plan?",
         """A Board Certified Behavior Analyst who also holds an active North Carolina behavior analyst license. Behavior Technicians deliver day-to-day sessions under that BCBA's supervision."""),
        ("How soon can we start?",
         """There is no onboarding waitlist. Assessment takes about four weeks."""),
    ]),
    warm=True,
    extra_cls="mm-faq",
) + closing("Get help where the behavior happens")

# ================================================================ gates
GENERIC = {"/contact", "tel:732.813.7333", "/early-intervention", "/parent-training",
           "/behavior-support", "/transition-planning"}
GA_ALLOWED = GENERIC | {"/aba-therapy-in-georgia"} | {
    f"/{s}-georgia" for s in ["early-intervention", "parent-training", "behavior-support", "transition-planning"]
} | {f"/areas-we-serve/{slug}" for slug, _ in GA_CITIES}
NC_ALLOWED = GENERIC | {"/aba-therapy-in-north-carolina"} | {
    f"/{s}-north-carolina" for s in ["early-intervention", "parent-training", "behavior-support", "transition-planning"]
} | {f"/areas-we-serve/{slug}" for slug, _ in NC_CITIES}

failures = []
for slug, body in PAGES.items():
    allowed = GA_ALLOWED if slug.endswith("-georgia") else NC_ALLOWED
    html = prefix + "\n" + body + "</div>"
    for m in re.finditer("—", html):
        line = html[html.rfind("\n", 0, m.start()) + 1 : html.find("\n", m.start())]
        if "<td>" not in line:
            failures.append(f"{slug}: em dash outside a table row: {line.strip()[:80]}")
    bad = set(re.findall(r'href="([^"]+)"', html)) - allowed
    if bad:
        failures.append(f"{slug}: hrefs outside whitelist: {sorted(bad)}")
    if html.count("<h1>") != 1:
        failures.append(f"{slug}: h1 count {html.count('<h1>')}")
    stripped = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
    for word in ["RBT", "clinic", "center-based", "our center"]:
        if re.search(r"\b" + word + r"\b", stripped, re.I):
            failures.append(f"{slug}: forbidden term {word!r}")
    for phone in set(re.findall(r"\d{3}[.-]\d{3}[.-]\d{4}", html)):
        if phone != "732.813.7333":
            failures.append(f"{slug}: wrong phone {phone}")
    words = len(re.sub(r"<[^>]+>", " ", stripped).split())
    if not 850 <= words <= 1400:
        failures.append(f"{slug}: word count {words} outside 850-1400")
    out = BUILD / f"{slug}.embed.html"
    out.write_text(html)
    print(f"{slug}: {words} words, {len(html)} bytes")

if failures:
    print("\nGATE FAILURES:", file=sys.stderr)
    for f in failures:
        print(" -", f, file=sys.stderr)
    sys.exit(1)
print("all gates passed")
