import streamlit as st
import streamlit.components.v1 as components
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="CSC Computer Education",
    page_icon="💻",
    layout="wide"
)

# --------------------------------------------------
# LOCAL CSS
# --------------------------------------------------

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        pass


local_css("style.css")


# --------------------------------------------------
# GOOGLE SHEET CONNECTION
# --------------------------------------------------

GOOGLE_SHEET_ID = "1Wigip0xgLX4knr64GqPu75qe0mXNnniFmDBJjZwdbkQ"

# gid=0 means first sheet/tab
GOOGLE_SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
)

@st.cache_data(ttl=5)
def load_courses_from_google_sheet():

    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)

        # Remove unwanted spaces from column names
        df.columns = df.columns.str.strip()

        # Remove empty rows
        df = df.dropna(how="all")

        # Convert important columns to string
        for column in [
            "Course Name",
            "Course Code",
            "Duration",
            "Fees",
            "Course Level",
            "Mode",
            "Syllabus",
            "Mini Project",
            "Certificate",
            "Placement Assistance",
            "Status"
        ]:
            if column in df.columns:
                df[column] = df[column].fillna("").astype(str)

        return df

    except Exception as e:
        st.error("❌ Unable to connect to Google Sheet.")
        st.error(f"Error: {e}")

        return pd.DataFrame()


# Load Google Sheet data
course_df = load_courses_from_google_sheet()


# --------------------------------------------------
# CHECK GOOGLE SHEET
# --------------------------------------------------

if course_df.empty:

    st.warning(
        "⚠️ No course data found. "
        "Please check your Google Sheet sharing settings and columns."
    )

    st.stop()


# Only show Active courses
if "Status" in course_df.columns:

    active_courses = course_df[
        course_df["Status"].str.strip().str.lower() == "active"
    ].copy()

else:

    active_courses = course_df.copy()


# --------------------------------------------------
# COURSE DATA
# --------------------------------------------------

courses = active_courses["Course Name"].dropna().tolist()


# --------------------------------------------------
# COURSE ICONS
# --------------------------------------------------

course_icons = {
    "Python Programming": "🐍",
    "Java Programming": "☕",
    "C Programming": "💻",
    "C++ Programming": "➕",
    "Web Development": "🌐",
    "Artificial Intelligence": "🤖"
}

default_icons = [
    "📚",
    "💻",
    "🌐",
    "🤖",
    "🎓",
    "📖"
]


# --------------------------------------------------
# COURSE POPUP
# --------------------------------------------------

@st.dialog("📚 Course Details")
def course_popup(course):

    course_name = course.get("Course Name", "")
    course_code = course.get("Course Code", "")
    duration = course.get("Duration", "")
    fees = course.get("Fees", "")
    level = course.get("Course Level", "")
    mode = course.get("Mode", "")
    syllabus = course.get("Syllabus", "")
    mini_project = course.get("Mini Project", "")
    certificate = course.get("Certificate", "")
    placement = course.get("Placement Assistance", "")

    st.markdown(f"### {course_icons.get(course_name, '📚')} {course_name}")

    if course_code:
        st.write(f"🏷️ **Course Code:** {course_code}")

    if duration:
        st.write(f"📅 **Duration:** {duration}")

    if fees:
        st.write(f"💰 **Fees:** {fees}")

    if level:
        st.write(f"📊 **Course Level:** {level}")

    if mode:
        st.write(f"🏫 **Mode:** {mode}")

    st.markdown("### 📖 Syllabus")

    if syllabus:

        # Supports comma-separated syllabus
        syllabus_items = [
            item.strip()
            for item in syllabus.split(",")
            if item.strip()
        ]

        for item in syllabus_items:
            st.write(f"✅ {item}")

    if mini_project:
        st.write(f"🛠️ **Mini Project:** {mini_project}")

    if certificate:
        st.write(f"🎓 **Certificate:** {certificate}")

    if placement:
        st.write(
            f"💼 **Placement Assistance:** {placement}"
        )


# --------------------------------------------------
# AI COURSE SEARCH
# --------------------------------------------------

@st.cache_resource
def load_model():

    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


model = load_model()


search = st.text_input(
    "🔍 Search Course",
    placeholder="Example: Python, Web Development, AI..."
)


if search and courses:

    query_embedding = model.encode(
        [search]
    )

    course_embeddings = model.encode(
        courses
    )

    similarity = cosine_similarity(
        query_embedding,
        course_embeddings
    )[0]

    index = similarity.argmax()

    best_match = courses[index]

    st.success(
        f"🎯 Best Match : {best_match}"
    )


# --------------------------------------------------
# SIDEBAR MENU
# --------------------------------------------------

menu = st.sidebar.selectbox(
    "📌 Menu",
    [
        "Home",
        "About",
        "Courses",
        "Admission",
        "Address",
        "Reviews",
        "Contact"
    ]
)


# --------------------------------------------------
# MAIN TITLE
# --------------------------------------------------

st.title("💻 CSC Computer Education")


# ==================================================
# HOME
# ==================================================

if menu == "Home":

    st.markdown(
        """
        <div class="course-title">
            <span>📚</span>
            <h1>Our Courses</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        "Choose a course to view complete course details."
    )

    st.markdown("---")

    # Dynamic course buttons
    # 3 courses per row

    for row_start in range(
        0,
        len(active_courses),
        3
    ):

        row_courses = active_courses.iloc[
            row_start:row_start + 3
        ]

        cols = st.columns(3)

        for col_index, (_, course) in enumerate(
            row_courses.iterrows()
        ):

            with cols[col_index]:

                course_name = course[
                    "Course Name"
                ]

                icon = course_icons.get(
                    course_name,
                    default_icons[
                        (row_start + col_index)
                        % len(default_icons)
                    ]
                )

                if st.button(
                    f"{icon}\n{course_name}",
                    key=f"home_course_{row_start}_{col_index}",
                    use_container_width=True
                ):

                    course_popup(
                        course.to_dict()
                    )

        st.write("")


# ==================================================
# ABOUT
# ==================================================

elif menu == "About":

    st.markdown(
        "## 💻 About CSC Computer Education"
    )

    st.write(
        "CSC Computer Education is a computer training "
        "institute focused on providing quality and "
        "practical computer education for students "
        "and professionals."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🎯 Our Mission")

        st.write(
            "Our mission is to provide practical and "
            "industry-oriented computer education that "
            "helps students build strong technical skills "
            "and achieve their career goals."
        )

    with col2:

        st.subheader("🌟 Why Choose Us?")

        st.write("✅ Experienced Trainers")
        st.write("✅ Practical Training")
        st.write("✅ Affordable Course Fees")
        st.write("✅ Project-Based Learning")
        st.write("✅ Placement Assistance")
        st.write("✅ Course Completion Certificate")

    st.markdown("---")

    st.subheader("📚 What We Offer")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🐍 Programming Courses\n\n"
            "Python, Java, C and C++"
        )

    with col2:

        st.info(
            "🌐 Web Development\n\n"
            "HTML, CSS and JavaScript"
        )

    with col3:

        st.info(
            "🤖 Advanced Technologies\n\n"
            "Artificial Intelligence and Machine Learning"
        )


# ==================================================
# COURSES
# ==================================================

elif menu == "Courses":

    st.markdown("## 📚 Our Courses")

    st.write(
        "Explore our professional computer courses "
        "designed to develop practical and "
        "industry-ready skills."
    )

    st.markdown("---")

    # Dynamic course cards
    for row_start in range(
        0,
        len(active_courses),
        3
    ):

        row_courses = active_courses.iloc[
            row_start:row_start + 3
        ]

        cols = st.columns(3)

        for col_index, (_, course) in enumerate(
            row_courses.iterrows()
        ):

            with cols[col_index]:

                course_name = course[
                    "Course Name"
                ]

                icon = course_icons.get(
                    course_name,
                    default_icons[
                        (row_start + col_index)
                        % len(default_icons)
                    ]
                )

                duration = course.get(
                    "Duration",
                    ""
                )

                fees = course.get(
                    "Fees",
                    ""
                )

                syllabus = course.get(
                    "Syllabus",
                    ""
                )

                syllabus_items = [
                    item.strip()
                    for item in syllabus.split(",")
                    if item.strip()
                ]

                syllabus_text = "\n".join(
                    [
                        f"• {item}"
                        for item in syllabus_items
                    ]
                )

                st.info(
                    f"""
{icon} **{course_name}**

📅 Duration: {duration}

💰 Fees: {fees}

📖 Syllabus:

{syllabus_text}
"""
                )

        st.write("")


# ==================================================
# ADMISSION
# ==================================================

elif menu == "Admission":

    st.header("📝 Admission Form")

    name = st.text_input(
        "Student Name"
    )

    phone = st.text_input(
        "Phone Number"
    )

    course_names = [
        course
        for course in courses
    ]

    course = st.selectbox(
        "Select Course",
        course_names
    )

    st.markdown(
        '<div class="submit-btn">',
        unsafe_allow_html=True
    )

    if st.button(
        "Submit",
        key="admission_submit"
    ):

        if not name.strip():

            st.error(
                "Please enter student name."
            )

        elif not phone.strip():

            st.error(
                "Please enter phone number."
            )

        else:

            st.success(
                "🎉 Admission Submitted Successfully!"
            )

            st.write(
                f"👤 **Student:** {name}"
            )

            st.write(
                f"📞 **Phone:** {phone}"
            )

            st.write(
                f"📚 **Course:** {course}"
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ==================================================
# ADDRESS
# ==================================================

elif menu == "Address":

    st.header("📍 Address")

    st.write(
        """
CSC Computer Education

No.25, Gandhi Road

Chennai - 600001

Phone : 9876543210
"""
    )

    st.subheader("📍 Our Location")

    components.iframe(
        "https://www.google.com/maps"
        "?q=CSC+Computer+Education+Chennai"
        "&output=embed",
        height=350
    )


# ==================================================
# REVIEWS
# ==================================================

elif menu == "Reviews":

    st.header("⭐ Student Reviews")

    st.info(
        "⭐⭐⭐⭐⭐  "
        "'Excellent teaching and friendly trainers.' "
        "- Rahul"
    )

    st.info(
        "⭐⭐⭐⭐⭐  "
        "'Best place to learn Python and Java.' "
        "- Priya"
    )

    st.info(
        "⭐⭐⭐⭐⭐  "
        "'Affordable fees with placement support.' "
        "- Karthik"
    )

    st.markdown("---")

    st.header(
        "🎓 Placement Assistance"
    )

    st.success(
        """
✔ Resume Preparation

✔ Mock Interviews

✔ Internship Support

✔ Placement Guidance

✔ Certificate after Course Completion
"""
    )


# ==================================================
# CONTACT
# ==================================================

elif menu == "Contact":

    st.header("📞 Contact Us")

    st.write(
        "Email : info@csc.com"
    )

    st.write(
        "Phone : 9876543210"
    )

    st.markdown("---")

    st.markdown(
        """
        <center>
        © 2026 CSC Computer Education |
        All Rights Reserved
        </center>
        """,
        unsafe_allow_html=True
    )