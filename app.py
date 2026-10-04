import streamlit as st
from streamlit_calendar import calendar
from google import genai
from google.genai import types
from datetime import date
from pathlib import Path
import base64
import json


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="StudyFlow AI",
    page_icon="📅",
    layout="wide"
)


# =========================================================
# BACKGROUND IMAGE
# =========================================================

def set_background(image_path):

    if not image_path.exists():
        return

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(
            image_file.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        /* =========================================
           FULL PAGE BACKGROUND
           ========================================= */

        .stApp {{
            background-image:
                linear-gradient(
                    rgba(255, 255, 255, 0.20),
                    rgba(255, 255, 255, 0.20)
                ),
                url("data:image/jpeg;base64,{encoded_image}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}


        /* =========================================
           MAIN CONTENT - TRANSPARENT
           ========================================= */

        .block-container {{
            background: transparent !important;
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}


        /* =========================================
           SIDEBAR
           ========================================= */

        [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.78) !important;
        }}


        /* =========================================
           HEADINGS
           ========================================= */

        h1, h2, h3 {{
            text-shadow: 0 1px 2px rgba(255,255,255,0.8);
        }}


        /* =========================================
           INPUT BOXES
           ========================================= */

        div[data-baseweb="input"],
        div[data-baseweb="select"],
        div[data-baseweb="textarea"] {{
            background: rgba(255, 255, 255, 0.82) !important;
            border-radius: 10px;
        }}


        /* =========================================
           FILE UPLOADER
           ========================================= */

        [data-testid="stFileUploader"] {{
            background: rgba(255, 255, 255, 0.78);
            border-radius: 14px;
            padding: 10px;
        }}


        /* =========================================
           CHAT INPUT
           ========================================= */

        [data-testid="stChatInput"] {{
            background: rgba(255, 255, 255, 0.85);
            border-radius: 14px;
        }}


        /* =========================================
           ALERT / INFO BOXES
           ========================================= */

        [data-testid="stAlert"] {{
            background: rgba(255, 255, 255, 0.82);
            border-radius: 12px;
        }}

        /* FIX TEXT VISIBILITY */
.stApp,
.block-container,
[data-testid="stSidebar"] {
    color: #222222 !important;
}

h1, h2, h3, h4, h5, h6,
p,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * {
    color: #222222 !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: #222222 !important;
    background-color: #ffffff !important;
}

div[data-baseweb="select"] {
    background-color: #ffffff !important;
}

div[data-baseweb="select"] * {
    color: #222222 !important;
}

[data-testid="stFileUploader"] * {
    color: #222222 !important;
}

[data-testid="stChatInput"] * {
    color: #222222 !important;
}

[data-testid="stAlert"] * {
    color: #222222 !important;
}
        </style>
        """,
        unsafe_allow_html=True
    )


# Find project folder
BASE_DIR = Path(__file__).resolve().parent

BACKGROUND_IMAGE = (
    BASE_DIR
    / "assets"
    / "study_background.jpg"
)

# Apply background only if image exists
set_background(BACKGROUND_IMAGE)


# =========================================================
# TITLE
# =========================================================

st.title("📅 StudyFlow AI")

st.caption(
    "AI Academic Deadline & Study Planner"
)


# =========================================================
# GEMINI SETUP
# =========================================================

if "GEMINI_API_KEY" not in st.secrets:

    st.error(
        "Gemini API key is missing from Streamlit secrets."
    )

    st.stop()


client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL_NAME = "gemini-3.5-flash"


# =========================================================
# SESSION STATE
# =========================================================

if "profile" not in st.session_state:
    st.session_state.profile = None

if "deadlines" not in st.session_state:
    st.session_state.deadlines = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_mode" not in st.session_state:
    st.session_state.input_mode = None

if "extracted_items" not in st.session_state:
    st.session_state.extracted_items = []


# =========================================================
# STUDENT PROFILE
# =========================================================

if st.session_state.profile is None:

    st.header("👩‍🎓 Student Profile")

    st.write(
        "Tell us a little about yourself so StudyFlow "
        "can personalize your planner."
    )

    name = st.text_input("Name")

    institution = st.selectbox(
        "You are studying in",
        [
            "School",
            "College"
        ]
    )

    if institution == "School":

        standard = st.text_input(
            "Class / Standard"
        )

        semester = ""
        course = ""

    else:

        standard = ""

        semester = st.text_input(
            "Semester"
        )

        course = st.text_input(
            "Course / Branch"
        )

    goal_type = st.selectbox(
        "Academic goal",
        [
            "Target marks / percentage",
            "Target CGPA",
            "Stay on track",
            "No specific target"
        ]
    )

    goal_value = ""

    if goal_type in [
        "Target marks / percentage",
        "Target CGPA"
    ]:

        goal_value = st.text_input(
            "Target value (example: 85% or 8.0)"
        )

    if st.button(
        "🚀 Create My Planner",
        type="primary"
    ):

        if not name.strip():

            st.warning(
                "Please enter your name."
            )

            st.stop()

        st.session_state.profile = {

            "name": name.strip(),

            "institution": institution,

            "standard": standard,

            "semester": semester,

            "course": course,

            "goal_type": goal_type,

            "goal_value": goal_value
        }

        st.rerun()


# =========================================================
# MAIN APPLICATION
# =========================================================

else:

    profile = st.session_state.profile

    st.success(
        f"Welcome, {profile['name']}! 👋"
    )


    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.header("👩‍🎓 My Profile")

        st.write(
            f"**Name:** {profile['name']}"
        )

        st.write(
            f"**Type:** {profile['institution']}"
        )

        if profile["institution"] == "School":

            if profile["standard"]:

                st.write(
                    f"**Class:** {profile['standard']}"
                )

        else:

            if profile["course"]:

                st.write(
                    f"**Course:** {profile['course']}"
                )

            if profile["semester"]:

                st.write(
                    f"**Semester:** {profile['semester']}"
                )

        if profile["goal_type"] != "No specific target":

            st.write(
                f"**Goal:** "
                f"{profile['goal_type']} "
                f"{profile['goal_value']}"
            )

        else:

            st.write(
                "**Goal:** Stay flexible"
            )

        st.divider()

        if st.button("🔄 Reset Profile"):

            st.session_state.profile = None
            st.session_state.deadlines = []
            st.session_state.messages = []
            st.session_state.input_mode = None
            st.session_state.extracted_items = []

            st.rerun()


    # =====================================================
    # ADD ACADEMIC INFORMATION
    # =====================================================

    st.header("➕ Add Academic Information")

    st.write(
        "Add an academic calendar, exam timetable, "
        "assignment notice, or other important academic information."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📸 Add From Image",
            use_container_width=True
        ):

            st.session_state.input_mode = "image"

    with col2:

        if st.button(
            "✍️ Add Manually",
            use_container_width=True
        ):

            st.session_state.input_mode = "manual"


    # =====================================================
    # IMAGE INPUT
    # =====================================================

    if st.session_state.input_mode == "image":

        st.subheader(
            "📸 Upload or Take a Picture"
        )

        image_source = st.radio(
            "Choose image source",
            [
                "📷 Take a Picture",
                "🖼️ Upload from Gallery"
            ],
            horizontal=True
        )

        image = None

        if image_source == "📷 Take a Picture":

            image = st.camera_input(
                "Take a picture of your academic document"
            )

        else:

            image = st.file_uploader(
                "Upload an academic calendar, timetable, notice, etc.",
                type=[
                    "jpg",
                    "jpeg",
                    "png"
                ]
            )

        if image is not None:

            if st.button(
                "🔍 Extract Academic Events",
                type="primary"
            ):

                with st.spinner(
                    "AI is reading your academic document..."
                ):

                    image_bytes = image.getvalue()

                    prompt = """
You are StudyFlow AI, an academic schedule extraction assistant.

Analyze the uploaded academic document carefully.

Extract ONLY academic events that have a clearly identifiable date.

Examples:

- Exams
- Tests
- Assignments
- Project submissions
- Practical exams
- Presentations
- Viva
- Internal assessments
- Important academic sessions
- Classes
- Other academic deadlines

Return ONLY valid JSON.

Use exactly this structure:

[
  {
    "title": "Event or task name",
    "date": "YYYY-MM-DD",
    "time": "",
    "type": "Exam",
    "priority": "High"
  }
]

Rules:

1. Use YYYY-MM-DD for dates.
2. Do not invent dates.
3. If the exact date is unclear, do not include the event.
4. If time is unavailable, use an empty string.
5. Type must be one of:
   Exam, Assignment, Project, Test, Presentation,
   Practical, Class, Deadline, Other
6. Priority must be one of:
   High, Medium, Low
7. Exams and major deadlines should normally be High.
8. Regular classes should normally be Low.
9. Return ONLY the JSON array.
10. Do not include markdown or explanations.
"""

                    try:

                        response = client.models.generate_content(

                            model=MODEL_NAME,

                            contents=[

                                types.Part.from_bytes(
                                    data=image_bytes,
                                    mime_type=image.type
                                ),

                                prompt
                            ]
                        )

                        raw_text = response.text.strip()

                        if raw_text.startswith(
                            "```json"
                        ):

                            raw_text = raw_text[7:]

                        elif raw_text.startswith(
                            "```"
                        ):

                            raw_text = raw_text[3:]

                        if raw_text.endswith("```"):

                            raw_text = raw_text[:-3]

                        raw_text = raw_text.strip()

                        extracted = json.loads(
                            raw_text
                        )

                        if not isinstance(
                            extracted,
                            list
                        ):

                            raise ValueError(
                                "AI did not return a list."
                            )

                        valid_items = []

                        for item in extracted:

                            if not isinstance(
                                item,
                                dict
                            ):

                                continue

                            title = str(
                                item.get(
                                    "title",
                                    ""
                                )
                            ).strip()

                            event_date = str(
                                item.get(
                                    "date",
                                    ""
                                )
                            ).strip()

                            event_time = str(
                                item.get(
                                    "time",
                                    ""
                                )
                            ).strip()

                            event_type = str(
                                item.get(
                                    "type",
                                    "Other"
                                )
                            ).strip()

                            priority = str(
                                item.get(
                                    "priority",
                                    "Medium"
                                )
                            ).strip()

                            if not title:
                                continue

                            if not event_date:
                                continue

                            valid_items.append({

                                "title": title,

                                "date": event_date,

                                "time": event_time,

                                "type": event_type,

                                "priority": priority,

                                "source": "Image"
                            })

                        st.session_state.extracted_items = (
                            valid_items
                        )

                        if not valid_items:

                            st.warning(
                                "No clearly dated academic events "
                                "were found in the image."
                            )

                    except Exception as e:

                        st.error(
                            "Could not extract the academic events."
                        )

                        st.code(str(e))


        # =================================================
        # REVIEW EXTRACTED EVENTS
        # =================================================

        if st.session_state.extracted_items:

            st.subheader(
                "🔎 Review Extracted Events"
            )

            st.info(
                "Review the events before adding them "
                "to your calendar."
            )

            for index, item in enumerate(
                st.session_state.extracted_items
            ):

                with st.container(border=True):

                    st.markdown(
                        f"### {index + 1}. "
                        f"{item['title']}"
                    )

                    st.write(
                        f"📅 **Date:** {item['date']}"
                    )

                    if item["time"]:

                        st.write(
                            f"⏰ **Time:** {item['time']}"
                        )

                    st.write(
                        f"📌 **Type:** {item['type']}"
                    )

                    st.write(
                        f"🚦 **Priority:** {item['priority']}"
                    )

            if st.button(
                "✅ Add All to Planner",
                type="primary"
            ):

                for item in (
                    st.session_state.extracted_items
                ):

                    st.session_state.deadlines.append(
                        item
                    )

                st.session_state.extracted_items = []

                st.success(
                    "All extracted events were added "
                    "to your planner!"
                )

                st.rerun()

            if st.button(
                "❌ Discard Extracted Events"
            ):

                st.session_state.extracted_items = []

                st.rerun()


    # =====================================================
    # MANUAL INPUT
    # =====================================================

    if st.session_state.input_mode == "manual":

        st.subheader(
            "✍️ Add a Task or Event"
        )

        task_name = st.text_input(
            "Task / Event name"
        )

        task_date = st.date_input(
            "Date",
            value=date.today()
        )

        task_time = st.time_input(
            "Time"
        )

        task_type = st.selectbox(
            "Type",
            [
                "Exam",
                "Assignment",
                "Project",
                "Test",
                "Presentation",
                "Practical",
                "Class",
                "Deadline",
                "Personal Academic Task",
                "Other"
            ]
        )

        priority = st.selectbox(
            "Priority",
            [
                "High",
                "Medium",
                "Low"
            ]
        )

        if st.button(
            "➕ Add to Planner",
            type="primary"
        ):

            if not task_name.strip():

                st.warning(
                    "Please enter a task or event name."
                )

            else:

                st.session_state.deadlines.append({

                    "source": "Manual",

                    "title": task_name.strip(),

                    "task": task_name.strip(),

                    "date": str(task_date),

                    "time": str(task_time),

                    "type": task_type,

                    "priority": priority
                })

                st.success(
                    "Task added to your planner!"
                )


    # =====================================================
    # CALENDAR
    # =====================================================

    st.divider()

    st.header(
        "📅 Academic Calendar"
    )

    calendar_events = []

    for item in st.session_state.deadlines:

        if "date" not in item:
            continue

        title = item.get(
            "title",
            item.get(
                "task",
                "Academic Event"
            )
        )

        calendar_events.append({

            "title": title,

            "start": item["date"],

            "allDay": True
        })

    if calendar_events:

        calendar(

            events=calendar_events,

            options={

                "initialView":
                    "dayGridMonth",

                "headerToolbar": {

                    "left":
                        "prev,next today",

                    "center":
                        "title",

                    "right":
                        "dayGridMonth,timeGridWeek"
                },

                "height":
                    600
            }
        )

    else:

        st.info(
            "Add a task or deadline to see it "
            "on your calendar."
        )


    # =====================================================
    # UPCOMING EVENTS
    # =====================================================

    st.divider()

    st.header(
        "⏳ Upcoming Academic Events"
    )

    today = date.today()

    upcoming = []

    for item in st.session_state.deadlines:

        try:

            event_date = date.fromisoformat(
                item["date"]
            )

            if event_date >= today:

                upcoming.append(
                    (
                        event_date,
                        item
                    )
                )

        except Exception:

            continue

    upcoming.sort(
        key=lambda x: x[0]
    )

    if upcoming:

        for event_date, item in upcoming[:5]:

            title = item.get(
                "title",
                item.get(
                    "task",
                    "Academic Event"
                )
            )

            priority = item.get(
                "priority",
                "Medium"
            )

            st.write(
                f"📅 **{event_date.strftime('%d %b %Y')}** — "
                f"{title} ({priority})"
            )

    else:

        st.info(
            "No upcoming events yet."
        )


    # =====================================================
    # SAVED INFORMATION
    # =====================================================

    st.divider()

    st.header(
        "📋 My Academic Information"
    )

    if not st.session_state.deadlines:

        st.info(
            "No deadlines or tasks added yet. "
            "Use Add From Image or Add Manually above."
        )

    else:

        for index, item in enumerate(
            st.session_state.deadlines,
            start=1
        ):

            with st.container(border=True):

                title = item.get(
                    "title",
                    item.get(
                        "task",
                        "Academic Event"
                    )
                )

                st.markdown(
                    f"### {index}. {title}"
                )

                st.write(
                    f"📅 **Date:** "
                    f"{item.get('date', 'Not available')}"
                )

                if item.get("time"):

                    st.write(
                        f"⏰ **Time:** "
                        f"{item['time']}"
                    )

                st.write(
                    f"📌 **Type:** "
                    f"{item.get('type', 'Other')}"
                )

                st.write(
                    f"🚦 **Priority:** "
                    f"{item.get('priority', 'Medium')}"
                )

                st.caption(
                    f"Source: "
                    f"{item.get('source', 'Unknown')}"
                )


    # =====================================================
    # AI CHAT
    # =====================================================

    st.divider()

    st.header(
        "💬 Ask StudyFlow AI"
    )

    st.caption(
        "Ask about your deadlines, priorities, "
        "or what you should work on."
    )

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    user_question = st.chat_input(
        "Example: What should I focus on this week?"
    )

    if user_question:

        st.session_state.messages.append({

            "role": "user",

            "content": user_question
        })

        deadline_context = str(
            st.session_state.deadlines
        )

        chat_prompt = f"""
You are StudyFlow AI, a concise academic planning assistant.

Student profile:
{profile}

Current academic tasks and deadlines:
{deadline_context}

Student question:
{user_question}

Give practical and concise advice.

Rules:
- Do not invent deadlines.
- Prioritize urgent and important tasks.
- Consider the student's academic goal when relevant.
- If there is not enough information, say so.
- Keep the response short and easy to scan.
"""

        with st.spinner(
            "Thinking..."
        ):

            response = client.models.generate_content(

                model=MODEL_NAME,

                contents=chat_prompt
            )

        st.session_state.messages.append({

            "role": "assistant",

            "content": response.text
        })

        st.rerun()