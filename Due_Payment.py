import streamlit as st
import pandas as pd
import requests
from io import StringIO

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Due Payment Student Details",
    layout="wide"
)

st.title("🎓 Due Payment Student Details")


# ============================================================
# GOOGLE SHEET CONFIGURATION
# ============================================================

SHEET_ID = "15CwUlQD9dQISXVa4Hn_JuOMzrdF9qPD26Dd_GZneYs0"

SHEET_GID = "0"

GOOGLE_SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
)


# ============================================================
# LOAD GOOGLE SHEET DATA
# ============================================================

@st.cache_data(ttl=30)
def load_google_sheet():

    try:

        response = requests.get(
            GOOGLE_SHEET_URL,
            timeout=15
        )

        response.raise_for_status()

        df = pd.read_csv(
            StringIO(response.text)
        )

        return df

    except Exception as e:

        st.error(
            "❌ Google Sheet data load ஆகவில்லை."
        )

        st.code(str(e))

        return pd.DataFrame()


df = load_google_sheet()


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.warning("⚠️ No data found in Google Sheet.")

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# ============================================================
# FIND STATUS COLUMN
# ============================================================

status_column = None

for column in df.columns:

    if column.strip().lower() == "status":

        status_column = column
        break


if status_column is None:

    st.error(
        "❌ Google Sheet-ல் 'Status' column கிடைக்கவில்லை."
    )

    st.write("Available columns:")

    st.write(list(df.columns))

    st.stop()


# ============================================================
# SHOW ONLY PAYMENT INCOMPLETE STUDENTS
# ============================================================

df = df[
    df[status_column]
    .astype(str)
    .str.strip()
    .str.lower()
    == "payment incomplete"
].copy()


# ============================================================
# NO PAYMENT INCOMPLETE STUDENTS
# ============================================================

if df.empty:

    st.warning(
        "⚠️ No Payment Incomplete students found."
    )

    st.stop()


# ============================================================
# CONVERT DATAFRAME TO STUDENT LIST
# ============================================================

students = df.fillna("").to_dict(
    orient="records"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_value(student, *possible_names):

    """
    Google Sheet column names slightly different இருந்தாலும்
    value எடுத்துக்கொள்ளும்.
    """

    normalized = {
        str(key).strip().lower(): value
        for key, value in student.items()
    }

    for name in possible_names:

        key = name.strip().lower()

        if key in normalized:

            value = normalized[key]

            if pd.isna(value):

                return ""

            return str(value)

    return ""


# ============================================================
# SEARCH STUDENT
# ============================================================

search = st.text_input(
    "🔍 Search Student",
    placeholder=(
        "Search by Name, Reg No, Course, DOB, "
        "Date, Month, Year, Status..."
    )
)


# ============================================================
# FILTER STUDENTS
# ============================================================

if search.strip() == "":

    filtered = students

else:

    keyword = search.strip().lower()

    filtered = []

    for student in students:

        matched = False

        # --------------------------------------------
        # SEARCH ALL COLUMNS
        # --------------------------------------------

        for value in student.values():

            value_text = str(value).strip().lower()

            if value_text.startswith(keyword):

                matched = True
                break

        # --------------------------------------------
        # SEARCH ANYWHERE IN NAME
        # --------------------------------------------

        if not matched:

            name = get_value(
                student,
                "Name",
                "Student Name",
                "name"
            ).lower()

            if keyword in name:

                matched = True

        # --------------------------------------------
        # SEARCH COURSE
        # --------------------------------------------

        if not matched:

            course = get_value(
                student,
                "Course",
                "course"
            ).lower()

            if keyword in course:

                matched = True

        # --------------------------------------------
        # SEARCH STATUS
        # --------------------------------------------

        if not matched:

            status = get_value(
                student,
                "Status",
                "status"
            ).lower()

            if keyword in status:

                matched = True

        if matched:

            filtered.append(student)


# ============================================================
# NO SEARCH RESULTS
# ============================================================

if len(filtered) == 0:

    st.warning("⚠️ No Student Found")

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:

    st.session_state.page = 0


if "selected" not in st.session_state:

    st.session_state.selected = students[0]


# ============================================================
# CARDS PER PAGE
# ============================================================

cards_per_page = 5


total_pages = max(
    1,
    (len(filtered) - 1) // cards_per_page + 1
)


# Reset page if search result count changes

if st.session_state.page >= total_pages:

    st.session_state.page = 0


# ============================================================
# STUDENT DETAILS POPUP
# ============================================================

@st.dialog("📄 Student Details")
def show_student_details(student):

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    col1, col2 = st.columns([1, 3])

    with col1:

        name = get_value(
            student,
            "Name",
            "Student Name"
        )

        initials = "".join(
            [
                word[0].upper()
                for word in name.split()
            ][:2]
        )

        st.markdown(
            f"""
            <div style="
                width:90px;
                height:90px;
                background:#d4a017;
                border-radius:15px;
                color:white;
                font-size:36px;
                font-weight:bold;
                display:flex;
                justify-content:center;
                align-items:center;
            ">
                {initials}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"### {name}"
        )

        register_number = get_value(
            student,
            "Register No",
            "Register Number",
            "Reg No",
            "reg"
        )

        st.write(register_number)

    st.divider()


    # ========================================================
    # STUDENT INFORMATION
    # ========================================================

    st.markdown("### 👤 Student Information")


    c1, c2 = st.columns(2)


    # --------------------------------------------------------
    # LEFT COLUMN
    # --------------------------------------------------------

    with c1:

        st.markdown("**👤 Student Name**")

        st.write(
            get_value(
                student,
                "Name",
                "Student Name"
            )
        )


        st.markdown("**🆔 Register Number**")

        st.write(
            get_value(
                student,
                "Register No",
                "Register Number",
                "Reg No",
                "reg"
            )
        )


        st.markdown("**🎂 Date of Birth**")

        st.write(
            get_value(
                student,
                "DOB",
                "Date of Birth",
                "dob"
            )
        )


        st.markdown("**📚 Semester**")

        st.write(
            get_value(
                student,
                "Semester",
                "semester"
            )
        )


        st.markdown("**📅 Academic Year**")

        st.write(
            get_value(
                student,
                "Academic Year",
                "academic year"
            )
        )


        st.markdown("**🎓 Qualification**")

        st.write(
            get_value(
                student,
                "Qualification",
                "qualification"
            )
        )


        st.markdown("**📞 Contact**")

        st.write(
            get_value(
                student,
                "Contact",
                "Phone",
                "Mobile",
                "contact"
            )
        )


        st.markdown("**🏠 Address**")

        st.write(
            get_value(
                student,
                "Address",
                "address"
            )
        )


        st.markdown("**📌 Admission Date**")

        st.write(
            get_value(
                student,
                "Admission",
                "Admission Date",
                "admission"
            )
        )


    # --------------------------------------------------------
    # RIGHT COLUMN
    # --------------------------------------------------------

    with c2:

        st.markdown("**🎓 Course**")

        st.write(
            get_value(
                student,
                "Course",
                "course"
            )
        )


        st.markdown("**💳 Fee Type**")

        st.write(
            get_value(
                student,
                "Fee Type",
                "fee type"
            )
        )


        st.markdown("**💰 Total Fee**")

        st.write(
            get_value(
                student,
                "Total Fee",
                "Total Amount",
                "total fee"
            )
        )


        st.markdown("**📌 Previous Due**")

        st.write(
            get_value(
                student,
                "Previous Due",
                "previous due"
            )
        )


        st.markdown("**⚠️ Fine**")

        st.write(
            get_value(
                student,
                "Fine",
                "fine"
            )
        )


        st.markdown("**💵 Total Payable**")

        st.write(
            get_value(
                student,
                "Total Payable",
                "total payable"
            )
        )


        st.markdown("**💸 Paid Amount**")

        st.write(
            get_value(
                student,
                "Paid Amount",
                "Paid",
                "paid amount"
            )
        )


        st.markdown("**🔴 Balance / Due**")

        due_amount = get_value(
            student,
            "Balance/Due",
            "Balance",
            "Due",
            "due"
        )

        st.error(due_amount)


        st.markdown("**📅 Payment Date**")

        st.write(
            get_value(
                student,
                "Payment Date",
                "Date",
                "payment date"
            )
        )


        st.markdown("**💳 Payment Mode**")

        st.write(
            get_value(
                student,
                "Payment Mode",
                "Mode",
                "payment mode"
            )
        )


        st.markdown("**🔢 Transaction ID**")

        st.write(
            get_value(
                student,
                "Transaction ID",
                "Transaction No",
                "Transaction",
                "transaction id"
            )
        )


        st.markdown("**🧾 Receipt No**")

        st.write(
            get_value(
                student,
                "Receipt No",
                "Receipt",
                "receipt no"
            )
        )


        st.markdown("**Status**")

        status = get_value(
            student,
            "Status",
            "status"
        )

        st.error(
            "⚠️ " + status
        )


    # ========================================================
    # CLOSE BUTTON
    # ========================================================

    if st.button(
        "Close",
        use_container_width=True
    ):

        st.rerun()


# ============================================================
# CSS - STUDENT CARDS
# ============================================================

st.markdown(
    """
    <style>

    div[class*="st-key-card_"] button {

        height: 190px;

        width: 100%;

        border-radius: 15px;

        border: 1px solid #ddd;

        box-shadow:
            2px 2px 8px rgba(0,0,0,.1);

        background: white;

        white-space: pre-line;

        display: flex;

        flex-direction: column;

        align-items: center;

        justify-content: center;

        line-height: 1.6;

        cursor: pointer;
    }


    div[class*="st-key-card_"] button p:first-child {

        width: 55px;

        height: 55px;

        border-radius: 50%;

        background: #d4a017;

        color: white;

        font-size: 20px;

        font-weight: bold;

        display: flex;

        align-items: center;

        justify-content: center;

        margin: 0 auto 8px auto;
    }


    div[class*="st-key-card_"] button p:last-child {

        color: #d4a017;

        font-weight: 600;

        font-size: 14px;
    }


    div[class*="st-key-card_"] button p:nth-child(2) {

        color: #1a1a2e;

        font-size: 16px;
    }


    div[class*="st-key-card_"] button:hover {

        border: 1px solid #d4a017;

        box-shadow:
            2px 2px 12px rgba(212,160,23,.3);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PREVIOUS / NEXT
# ============================================================

left, middle, right = st.columns(
    [1, 8, 1]
)


with left:

    if st.button(
        "⬅ Previous",
        use_container_width=True
    ):

        if st.session_state.page > 0:

            st.session_state.page -= 1

            st.rerun()


with right:

    if st.button(
        "Next ➡",
        use_container_width=True
    ):

        if st.session_state.page < total_pages - 1:

            st.session_state.page += 1

            st.rerun()


# ============================================================
# STUDENTS TITLE
# ============================================================

st.markdown(
    "## 👨‍🎓 Payment Incomplete Students"
)


# ============================================================
# PAGE INFORMATION
# ============================================================

st.caption(
    f"Showing page "
    f"{st.session_state.page + 1} "
    f"of {total_pages} "
    f"• {len(filtered)} incomplete payment students"
)


# ============================================================
# HORIZONTAL STUDENT CARDS
# ============================================================

start = (
    st.session_state.page
    * cards_per_page
)

end = min(
    start + cards_per_page,
    len(filtered)
)


cards = st.columns(
    cards_per_page
)


for i, student in enumerate(
    filtered[start:end]
):

    name = get_value(
        student,
        "Name",
        "Student Name"
    )

    reg = get_value(
        student,
        "Register No",
        "Register Number",
        "Reg No",
        "reg"
    )

    initials = "".join(
        [
            word[0].upper()
            for word in name.split()
        ][:2]
    )


    with cards[i]:

        with st.container(
            key=f"card_{reg}"
        ):

            label = (
                f"{initials}\n\n"
                f"**{name}**\n\n"
                f"{reg}"
            )


            if st.button(
                label,
                key=f"btn_{reg}",
                use_container_width=True
            ):

                st.session_state.selected = student

                show_student_details(
                    student
                )