import re
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Caregiver Support (Demo)", page_icon="🤝", layout="centered")

# ----------------------------
# Rule-based knowledge (demo)
# ----------------------------
EMERGENCY_PATTERNS = [
    (r"\b(chest pain|pressure in chest|can't breathe|cannot breathe|shortness of breath)\b", "Breathing/chest symptoms"),
    (r"\b(fainted|passed out|unconscious|not waking)\b", "Loss of consciousness"),
    (r"\b(stroke|face droop|slurred speech|one-sided weakness)\b", "Possible stroke signs"),
    (r"\b(seizure|convulsion)\b", "Seizure"),
    (r"\b(suicide|kill myself|self harm|hurt myself)\b", "Self-harm risk"),
    (r"\b(bleeding won't stop|severe bleeding)\b", "Uncontrolled bleeding"),
]

URGENCY_PATTERNS = [
    (r"\b(high fever|fever over|fever above|very high fever)\b", "High fever"),
    (r"\b(confused|new confusion|delirious|disoriented)\b", "New/worsening confusion"),
    (r"\b(dehydrated|not drinking|not peeing|no urine)\b", "Possible dehydration"),
    (r"\b(fall|fell|hit head|head injury)\b", "Fall or head injury"),
    (r"\b(severe pain|worst pain)\b", "Severe pain"),
    (r"\b(vomiting repeatedly|can't keep fluids down)\b", "Repeated vomiting"),
]

TOPIC_RULES = [
    {
        "name": "Agitation / anxiety",
        "keywords": [r"\b(agitated|anxious|restless|panick|panic|irritable)\b"],
        "what_to_try": [
            "Reduce stimulation: dim lights, lower noise, limit visitors.",
            "Offer reassurance with a calm voice; validate feelings (e.g., “I’m here with you”).",
            "Check basic needs: hunger, thirst, toilet, temperature, pain (without diagnosing).",
            "Try a simple grounding activity: slow breathing together, familiar music, photo album.",
        ],
        "what_to_log": [
            "What was happening right before it started (time, place, people, activity).",
            "Any new changes: routine disruptions, poor sleep, missed meals, stressors.",
            "What helped and what made it worse.",
        ],
    },
    {
        "name": "Sleep trouble",
        "keywords": [r"\b(can't sleep|cannot sleep|insomnia|up all night|sleepy daytime)\b"],
        "what_to_try": [
            "Keep a consistent schedule: same wake time daily.",
            "Daytime light and gentle activity; avoid long late naps.",
            "Create a wind-down routine: warm drink (non-caffeinated), quiet activity, low screens.",
            "Check comfort: room temperature, bedding, noise, bathroom needs.",
        ],
        "what_to_log": [
            "Bedtime/wake time and number of night awakenings.",
            "Caffeine timing, naps, and evening screen time.",
            "Any patterns (worse after certain activities or foods).",
        ],
    },
    {
        "name": "Eating / drinking concerns",
        "keywords": [r"\b(not eating|no appetite|won't eat|not drinking|dehydration|lost weight)\b"],
        "what_to_try": [
            "Offer small frequent snacks; prioritize favorite foods if safe to eat.",
            "Make fluids easy: water bottle nearby, soups, popsicles, scheduled sips.",
            "Reduce distractions during meals; sit together if possible.",
            "Try soft/easy-to-chew options if chewing seems difficult (no diagnosis).",
        ],
        "what_to_log": [
            "Approximate intake (meals, snacks, fluids) and times.",
            "Any coughing/choking or difficulty swallowing (note to discuss with clinician).",
            "What foods/fluids were tolerated best.",
        ],
    },
    {
        "name": "Memory / confusion changes",
        "keywords": [r"\b(confused|forgetting|memory|doesn't recognize|lost|wandering)\b"],
        "what_to_try": [
            "Use simple cues: date/time board, clear labels, consistent routine.",
            "Offer one-step instructions; avoid quizzing or correcting repeatedly.",
            "Ensure safe environment: remove trip hazards, consider door alerts (demo suggestion).",
            "If wandering risk: keep ID info available and notify household members.",
        ],
        "what_to_log": [
            "When confusion is worse (time of day, after naps, after visitors).",
            "Any safety incidents or near-misses.",
            "Triggers and calming strategies that worked.",
        ],
    },
    {
        "name": "Caregiver stress / burnout",
        "keywords": [r"\b(overwhelmed|burnout|exhausted|can't do this|stressed|no support)\b"],
        "what_to_try": [
            "Take a short reset: 2–5 minutes of breathing, stretching, or stepping outside safely.",
            "Ask for specific help: one task, one person, one time (e.g., “Can you sit with them 30 min?”).",
            "Create a mini-rotation: list 3–5 people/resources to contact.",
            "If you feel unsafe or in crisis, seek immediate help (local emergency resources).",
        ],
        "what_to_log": [
            "What tasks feel hardest and when they peak.",
            "Sleep quantity, breaks taken, and support used.",
            "One small doable action for tomorrow.",
        ],
    },
]

GENERAL_TIPS = [
    "Focus on comfort, safety, and routines. Avoid making medical conclusions.",
    "If symptoms are new, severe, or rapidly worsening, contact a licensed clinician or local urgent care guidance.",
    "In an emergency, call your local emergency number immediately."
]

DISCLAIMER = (
    "This demo provides **non-medical**, **non-diagnostic** caregiving support tips using simple rules. "
    "It does **not** give medical diagnoses or medication changes. "
    "If you're worried about safety or serious symptoms, contact a licensed clinician or emergency services."
)

# ----------------------------
# Helpers
# ----------------------------
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

def match_any(patterns, text):
    hits = []
    for pat, label in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append(label)
    return hits

def pick_topics(text):
    matched = []
    for rule in TOPIC_RULES:
        for kw in rule["keywords"]:
            if re.search(kw, text, flags=re.IGNORECASE):
                matched.append(rule)
                break
    return matched

def structured_plan(user_text: str):
    t = normalize(user_text)

    emergency_hits = match_any(EMERGENCY_PATTERNS, t)
    urgent_hits = match_any(URGENCY_PATTERNS, t)

    topics = pick_topics(t)

    # Priority logic: emergency > urgent > routine
    if emergency_hits:
        level = "EMERGENCY"
        headline = "Possible emergency signs detected"
        actions_now = [
            "Call your local emergency number now (or seek immediate emergency care).",
            "If safe, stay with the person and keep them comfortable while help is on the way.",
            "Do not delay care to use this demo."
        ]
        reasons = emergency_hits
    elif urgent_hits:
        level = "URGENT"
        headline = "Concerning signs detected"
        actions_now = [
            "Consider contacting a licensed clinician, nurse line, or urgent care guidance today.",
            "Monitor closely and escalate if symptoms worsen or safety concerns arise.",
            "Keep notes to share (time, triggers, what you observed)."
        ]
        reasons = urgent_hits
    else:
        level = "ROUTINE"
        headline = "Supportive caregiving suggestions"
        actions_now = [
            "Try one or two practical steps below and observe what helps.",
            "Track patterns (time of day, triggers, what worked).",
            "Reach out to a clinician if issues persist or you’re unsure."
        ]
        reasons = ["No urgent keywords found"]

    # If no topics matched, provide a generic structure
    if not topics:
        topics_section = [{
            "name": "General support",
            "what_to_try": [
                "Check immediate comfort: hydration, snack, restroom, temperature, pain/discomfort signs.",
                "Reduce stimulation and provide reassurance.",
                "Use simple choices (yes/no) and one-step prompts."
            ],
            "what_to_log": [
                "What happened, when, and any triggers you noticed.",
                "What you tried and the result."
            ]
        }]
    else:
        topics_section = topics

    return {
        "level": level,
        "headline": headline,
        "reasons": reasons,
        "actions_now": actions_now,
        "topics": topics_section,
        "general_tips": GENERAL_TIPS
    }

def make_notes_template():
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "situation": "",
        "observations": "",
        "what_helped": "",
        "what_didnt_help": "",
        "questions_for_clinician": ""
    }

# ----------------------------
# UI
# ----------------------------
st.title("🤝 Caregiver Support (Demo, No API Keys)")
st.caption("Rule-based tips • Structured output • Non-diagnostic")

with st.expander("Important note", expanded=True):
    st.markdown(DISCLAIMER)

st.markdown("### Describe what’s going on")
user_text = st.text_area(
    "Write a short description (e.g., behaviors, timing, what you observed).",
    height=140,
    placeholder="Example: They seem restless in the evening and won’t eat much. I’m feeling overwhelmed."
)

col1, col2 = st.columns(2)
with col1:
    generate = st.button("Generate support plan", type="primary")
with col2:
    clear = st.button("Clear")

if clear:
    st.session_state.pop("last_plan", None)
    st.session_state.pop("last_notes", None)
    st.rerun()

if generate:
    plan = structured_plan(user_text)
    st.session_state["last_plan"] = plan
    st.session_state["last_notes"] = make_notes_template()

if "last_plan" in st.session_state:
    plan = st.session_state["last_plan"]
    st.markdown("---")
    st.markdown(f"## Result: {plan['level']}")
    st.markdown(f"**{plan['headline']}**")

    st.markdown("### Why this level?")
    st.write(", ".join(plan["reasons"]))

    st.markdown("### Actions to consider now")
    for a in plan["actions_now"]:
        st.write(f"- {a}")

    st.markdown("### Practical ideas (rule-based)")
    for topic in plan["topics"]:
        st.markdown(f"#### {topic['name']}")
        st.markdown("**Try:**")
        for w in topic["what_to_try"]:
            st.write(f"- {w}")
        st.markdown("**Log/track:**")
        for l in topic["what_to_log"]:
            st.write(f"- {l}")

    st.markdown("### General tips")
    for tip in plan["general_tips"]:
        st.write(f"- {tip}")

    st.markdown("---")
    st.markdown("## Notes template (copy/paste)")
    notes = st.session_state.get("last_notes", make_notes_template())

    # Editable notes
    notes["situation"] = st.text_input("Situation (1 sentence)", value=notes.get("situation", ""))
    notes["observations"] = st.text_area("Observations (what you saw/heard)", value=notes.get("observations", ""), height=90)
    notes["what_helped"] = st.text_area("What helped", value=notes.get("what_helped", ""), height=70)
    notes["what_didnt_help"] = st.text_area("What didn’t help", value=notes.get("what_didnt_help", ""), height=70)
    notes["questions_for_clinician"] = st.text_area("Questions for clinician", value=notes.get("questions_for_clinician", ""), height=70)

    st.session_state["last_notes"] = notes

    notes_md = (
        f"- Date: {notes['date']}\n"
        f"- Time: {notes['time']}\n"
        f"- Situation: {notes['situation']}\n"
        f"- Observations: {notes['observations']}\n"
        f"- What helped: {notes['what_helped']}\n"
        f"- What didn’t help: {notes['what_didnt_help']}\n"
        f"- Questions for clinician: {notes['questions_for_clinician']}\n"
    )

    st.code(notes_md, language="markdown")

st.markdown("---")
st.caption("Demo-only. No diagnosis. No medication guidance. Seek professional help for medical concerns.")
