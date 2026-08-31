import streamlit as st
import pandas as pd
import os
import re


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Full Payment Student Details",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Full Payment Student Details")


# ============================================================
# GOOGLE SHEET DATABASE
# ============================================================

GOOGLE_SHEET_ID = "15CwUlQD9dQISXVa4Hn_JuOMzrdF9qPD26Dd_GZneYs0"
GOOGLE_SHEET_GID = "0"

# Google Sheet CSV URL
GOOGLE_SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{GOOGLE_SHEET_ID}/export?format=csv&gid={GOOGLE_SHEET_GID}"
)


# ============================================================
# LOAD GOOGLE SHEET DATA
# ============================================================

@st.cache_data(ttl=30)
def load_student_data():

    try:

        # Read data directly from Google Sheet
        df = pd.read_csv(GOOGLE_SHEET_URL)

        # Clean empty cells
        df = df.fillna("")

        return df

    except Exception as e:

        st.error(
            "❌ Unable to read data from Google Sheet.\n\n"
            "Please make sure the Google Sheet is shared as "
            "Anyone with the link -> Viewer.\n\n"
            f"Error: {e}"
        )

        return pd.DataFrame()


# ============================================================
# REFRESH GOOGLE SHEET DATA
# ============================================================

refresh_col1, refresh_col2 = st.columns([6, 1])

with refresh_col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ============================================================
# LOAD DATABASE
# ============================================================

df = load_student_data()


if df.empty:

    st.warning("⚠️ No student data found.")

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = [
    str(column).strip()
    for column in df.columns
]


# ============================================================
# FIND STATUS COLUMN
# ============================================================

status_column = None

for column in df.columns:

    clean_column = (
        str(column)
        .strip()
        .lower()
        .replace("_", " ")
    )

    if clean_column == "status":

        status_column = column

        break


if status_column is None:

    st.error(
        "❌ Status column was not found in CSC DB.xlsx"
    )

    st.stop()


# ============================================================
# FULL PAYMENT ONLY
# ============================================================

df = df[
    df[status_column]
    .astype(str)
    .str.strip()
    .str.lower()
    == "fully paid"
].copy()


if df.empty:

    st.warning(
        "⚠️ No Fully Paid students found."
    )

    st.stop()


# ============================================================
# MONTH NAMES
# ============================================================

MONTH_NAMES = {
    1: "january",
    2: "february",
    3: "march",
    4: "april",
    5: "may",
    6: "june",
    7: "july",
    8: "august",
    9: "september",
    10: "october",
    11: "november",
    12: "december"
}


# ============================================================
# NORMALIZE SEARCH TEXT
# ============================================================

def normalize_text(value):

    if value is None:
        return ""

    # Convert to string
    text = str(value)

    # Remove .0 from numbers like 40000.0
    text = re.sub(
        r"(?<=\d)\.0\b",
        "",
        text
    )

    # Lowercase
    text = text.lower()

    # Remove currency symbols
    text = text.replace("₹", "")
    text = text.replace("$", "")
    text = text.replace(",", "")

    # Remove all spaces
    text = re.sub(
        r"\s+",
        "",
        text
    )

    # Remove special characters
    text = re.sub(
        r"[^a-z0-9]",
        "",
        text
    )

    return text


# ============================================================
# CONVERT DATE INTO SEARCHABLE TEXT
# ============================================================

def get_date_search_text(value):

    if value is None:
        return ""

    if str(value).strip() == "":
        return ""

    try:

        date = pd.to_datetime(
            value,
            errors="coerce"
        )

        if pd.notna(date):

            day = str(date.day)

            month = str(date.month)

            month_two_digit = (
                f"{date.month:02d}"
            )

            year = str(date.year)

            month_name = MONTH_NAMES.get(
                date.month,
                ""
            )

            # Examples:
            # 30
            # 07
            # 7
            # 2026
            # July
            # July 2026
            # 30 July 2026

            return " ".join([
                day,
                month,
                month_two_digit,
                year,
                month_name,
                f"{month_name}{year}",
                f"{day}{month_name}{year}",
                f"{day}{month_two_digit}{year}"
            ])

    except Exception:
        pass

    return str(value)


# ============================================================
# CREATE SEARCH TEXT FOR EVERY STUDENT
# ============================================================

def create_search_text(row):

    all_values = []

    for column in df.columns:

        value = row[column]

        # Add original value
        all_values.append(
            str(value)
        )

        # If it is a date, add date variations
        date_text = get_date_search_text(
            value
        )

        if date_text:

            all_values.append(
                date_text
            )

        # Add column name also
        # This allows searches like:
        # payment date
        # fee type
        # academic year
        # etc.

        all_values.append(
            str(column)
        )

    return " ".join(all_values)


# ============================================================
# SEARCH MATCH FUNCTION
# ============================================================

def student_matches_search(row, search_query):

    if not search_query:
        return True

    # --------------------------------------------------------
    # SEARCH QUERY
    # --------------------------------------------------------

    query = str(search_query).strip().lower()
    normalized_query = normalize_text(query)

    # Empty search -> show all students
    if normalized_query == "":
        return True

    # ========================================================
    # METHOD 1 - NAME SEARCH
    # ========================================================
    # Single-letter search works anywhere inside the name.
    #
    # A -> Arun, Priya, Subhasree, etc.
    # S -> Subhasree, Sangeetha, etc.
    # sub -> Subhasree
    #
    # This works for every letter A-Z.

    name_value = ""

    for column in row.index:

        clean_column = (
            str(column)
            .strip()
            .lower()
            .replace("_", " ")
        )

        if clean_column in [
            "name",
            "student name"
        ]:

            name_value = str(row[column])
            break

    normalized_name = normalize_text(name_value)

    # Substring matching inside Student Name
    if normalized_query in normalized_name:
        return True

    # ========================================================
    # METHOD 2 - SEARCH ALL DATABASE FIELDS
    # ========================================================
    # Keeps search for Register No, DOB, Semester, Academic
    # Year, Course, Fee, Payment Date, Receipt, Status, etc.

    row_text = create_search_text(row)
    normalized_row = normalize_text(row_text)

    if normalized_query in normalized_row:
        return True

    # ========================================================
    # METHOD 3 - SPACE SEPARATED SEARCH
    # ========================================================

    query_words = re.findall(
        r"[a-zA-Z0-9]+",
        query
    )

    if len(query_words) > 1:

        all_words_found = True

        for word in query_words:

            normalized_word = normalize_text(word)

            if normalized_word == "":
                continue

            if normalized_word not in normalized_row:
                all_words_found = False
                break

        if all_words_found:
            return True

    # ========================================================
    # METHOD 4 - ANY WORD MATCH
    # ========================================================

    for word in query_words:

        normalized_word = normalize_text(word)

        if len(normalized_word) >= 1:

            if normalized_word in normalized_row:
                return True

    return False


# ============================================================
# SEARCH STUDENT
# ============================================================

search = st.text_input(
    "🔍 Search Student",
    placeholder="Search by Name, Reg No, Course, Date, Month, Year...",
    key="student_search"
)


if search.strip() == "":
    filtered_df = df.copy()

else:

    # ----------------------------------------------------
    # GOOGLE-STYLE SEARCH
    # ----------------------------------------------------
    # Uses student_matches_search() defined above, which:
    #   - matches any single letter/word anywhere in Name
    #   - matches any letter/word anywhere in ANY column
    #     (Reg No, Course, Fee, Semester, Status, etc.)
    #   - matches Date columns in many formats
    #     (30, 07, 7, 2026, July, July2026, 30July2026...)
    #   - matches multi-word queries like "July 2026" or
    #     "Subha ECE" even if the words are in different
    #     columns, by checking the whole row's text together
    #   - ignores spaces, commas, currency symbols, ".0"
    #     so numbers like "40,000" / "40000.0" / "₹40000"
    #     all match "40000"
    # ----------------------------------------------------

    match_mask = df.apply(
        lambda row: student_matches_search(row, search),
        axis=1
    )

    filtered_df = df[match_mask].copy()


# ============================================================
# RESULT COUNT
# ============================================================

st.markdown(
    f"""
    ### 🔎 Search Result: {len(filtered_df)} Fully Paid Student(s)
    """
)


# ============================================================
# NO DATA FOUND
# ============================================================

if len(filtered_df) == 0:

    st.warning(
        f"❌ No Student Found for: **{search}**"
    )

    st.stop()


# ============================================================
# GET VALUE FROM ROW
# ============================================================

def get_value(row, possible_names):

    for column in row.index:

        clean_column = (
            str(column)
            .strip()
            .lower()
            .replace("_", " ")
        )

        for name in possible_names:

            clean_name = (
                str(name)
                .strip()
                .lower()
                .replace("_", " ")
            )

            if clean_column == clean_name:

                value = row[column]

                if pd.isna(value):
                    return ""

                return str(value)


    return ""


# ============================================================
# ROW TO STUDENT
# ============================================================

def row_to_student(row):

    return {

        "name": get_value(
            row,
            [
                "Name",
                "Student Name"
            ]
        ),

        "reg": get_value(
            row,
            [
                "Register No",
                "Register Number",
                "Reg No",
                "Registration No"
            ]
        ),

        "dob": get_value(
            row,
            [
                "DOB",
                "Date of Birth"
            ]
        ),

        "semester": get_value(
            row,
            [
                "Semester"
            ]
        ),

        "academic_year": get_value(
            row,
            [
                "Academic Year",
                "AcademicYear"
            ]
        ),

        "qualification": get_value(
            row,
            [
                "Qualification"
            ]
        ),

        "contact": get_value(
            row,
            [
                "Contact",
                "Contact Number",
                "Phone"
            ]
        ),

        "address": get_value(
            row,
            [
                "Address"
            ]
        ),

        "admission": get_value(
            row,
            [
                "Admission",
                "Admission Date"
            ]
        ),

        "fee_type": get_value(
            row,
            [
                "Fee Type",
                "FeeType"
            ]
        ),

        "total_fee": get_value(
            row,
            [
                "Total Fee",
                "TotalFee"
            ]
        ),

        "previous_due": get_value(
            row,
            [
                "Previous Due",
                "PreviousDue"
            ]
        ),

        "fine": get_value(
            row,
            [
                "Fine"
            ]
        ),

        "total_payable": get_value(
            row,
            [
                "Total Payable",
                "TotalPayable"
            ]
        ),

        "paid": get_value(
            row,
            [
                "Paid Amount",
                "PaidAmount",
                "Paid"
            ]
        ),

        "balance": get_value(
            row,
            [
                "Balance/Due",
                "Balance / Due",
                "Balance Due",
                "Balance"
            ]
        ),

        "payment_date": get_value(
            row,
            [
                "Payment Date",
                "PaymentDate"
            ]
        ),

        "mode": get_value(
            row,
            [
                "Payment Mode",
                "PaymentMode",
                "Mode"
            ]
        ),

        "transaction": get_value(
            row,
            [
                "Transaction ID",
                "TransactionID",
                "Transaction"
            ]
        ),

        "receipt": get_value(
            row,
            [
                "Receipt No",
                "Receipt Number",
                "ReceiptNo"
            ]
        ),

        "status": get_value(
            row,
            [
                "Status"
            ]
        )
    }


# ============================================================
# STUDENT LIST
# ============================================================

students = [

    row_to_student(row)

    for _, row in filtered_df.iterrows()

]


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:

    st.session_state.page = 0


if "previous_search" not in st.session_state:

    st.session_state.previous_search = ""


# ============================================================
# RESET PAGE WHEN SEARCH CHANGES
# ============================================================

if (
    st.session_state.previous_search
    != search
):

    st.session_state.page = 0

    st.session_state.previous_search = search


# ============================================================
# PAGINATION
# ============================================================

cards_per_page = 5


total_pages = max(

    1,

    (len(students) - 1)
    // cards_per_page
    + 1

)


if st.session_state.page >= total_pages:

    st.session_state.page = 0


# ============================================================
# STUDENT DETAILS POPUP
# ============================================================

@st.dialog("📄 Student Details")
def show_student_details(student):

    # ========================================================
    # HEADER
    # ========================================================

    col1, col2 = st.columns(
        [1, 3]
    )


    # ========================================================
    # INITIALS
    # ========================================================

    with col1:

        initials = "".join(

            [
                x[0]
                for x in student["name"].split()
            ][:2]

        ).upper()


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


    # ========================================================
    # NAME
    # ========================================================

    with col2:

        st.markdown(
            f"### {student['name']}"
        )

        st.write(
            f"Register No: **{student['reg']}**"
        )


    st.divider()


    # ========================================================
    # STUDENT INFORMATION
    # ========================================================

    st.markdown(
        "## 👤 Student Information"
    )


    c1, c2 = st.columns(2)


    # ========================================================
    # LEFT
    # ========================================================

    with c1:

        st.markdown(
            "**👤 Student Name**"
        )

        st.write(
            student["name"]
        )


        st.markdown(
            "**🆔 Register Number**"
        )

        st.write(
            student["reg"]
        )


        st.markdown(
            "**🎂 Date of Birth**"
        )

        st.write(
            student["dob"]
        )


        st.markdown(
            "**📚 Semester**"
        )

        st.write(
            student["semester"]
        )


        st.markdown(
            "**📅 Academic Year**"
        )

        st.write(
            student["academic_year"]
        )


        st.markdown(
            "**🎓 Qualification**"
        )

        st.write(
            student["qualification"]
        )


        st.markdown(
            "**📱 Contact**"
        )

        st.write(
            student["contact"]
        )


        st.markdown(
            "**🏠 Address**"
        )

        st.write(
            student["address"]
        )


        st.markdown(
            "**📝 Admission Date**"
        )

        st.write(
            student["admission"]
        )


    # ========================================================
    # RIGHT
    # ========================================================

    with c2:

        st.markdown(
            "**💳 Fee Type**"
        )

        st.write(
            student["fee_type"]
        )


        st.markdown(
            "**💰 Total Fee**"
        )

        st.write(
            student["total_fee"]
        )


        st.markdown(
            "**⚠️ Previous Due**"
        )

        st.write(
            student["previous_due"]
        )


        st.markdown(
            "**➕ Fine**"
        )

        st.write(
            student["fine"]
        )


        st.markdown(
            "**💰 Total Payable**"
        )

        st.write(
            student["total_payable"]
        )


        st.markdown(
            "**💵 Paid Amount**"
        )

        st.success(
            student["paid"]
        )


        st.markdown(
            "**💳 Balance / Due**"
        )

        st.success(
            student["balance"]
        )


        st.markdown(
            "**📅 Payment Date**"
        )

        st.write(
            student["payment_date"]
        )


        st.markdown(
            "**💳 Payment Mode**"
        )

        st.write(
            student["mode"]
        )


        st.markdown(
            "**🔢 Transaction ID**"
        )

        st.write(
            student["transaction"]
        )


        st.markdown(
            "**🧾 Receipt No**"
        )

        st.write(
            student["receipt"]
        )


    # ========================================================
    # STATUS
    # ========================================================

    st.divider()


    st.markdown(
        "### 📌 Payment Status"
    )


    st.success(
        "✅ " + student["status"]
    )


    # ========================================================
    # CLOSE
    # ========================================================

    if st.button(
        "Close",
        use_container_width=True
    ):

        st.rerun()


# ============================================================
# CSS
# ============================================================

st.markdown(

    """
    <style>

    /* =====================================================
       STUDENT CARD
       ===================================================== */

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


    /* =====================================================
       INITIALS
       ===================================================== */

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


    /* =====================================================
       NAME
       ===================================================== */

    div[class*="st-key-card_"] button p:nth-child(2) {

        color: #1a1a2e;

        font-size: 16px;

        font-weight: 600;

    }


    /* =====================================================
       REGISTER NUMBER
       ===================================================== */

    div[class*="st-key-card_"] button p:last-child {

        color: #d4a017;

        font-weight: 600;

        font-size: 14px;

    }


    /* =====================================================
       HOVER
       ===================================================== */

    div[class*="st-key-card_"] button:hover {

        border: 1px solid #d4a017;

        box-shadow:
            2px 2px 12px rgba(212,160,23,.3);

    }


    /* =====================================================
       SEARCH BOX
       ===================================================== */

    div[data-testid="stTextInput"] input {

        border-radius: 10px;

        padding: 12px;

        font-size: 16px;

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


# ============================================================
# PREVIOUS
# ============================================================

with left:

    if st.button(
        "⬅ Previous",
        use_container_width=True
    ):

        if st.session_state.page > 0:

            st.session_state.page -= 1

            st.rerun()


# ============================================================
# PAGE NUMBER
# ============================================================

with middle:

    st.markdown(

        f"""
        <div style="
            text-align:center;
            padding-top:8px;
            font-weight:600;
        ">
            Page {st.session_state.page + 1}
            of
            {total_pages}
        </div>
        """,

        unsafe_allow_html=True

    )


# ============================================================
# NEXT
# ============================================================

with right:

    if st.button(
        "Next ➡",
        use_container_width=True
    ):

        if (
            st.session_state.page
            < total_pages - 1
        ):

            st.session_state.page += 1

            st.rerun()


# ============================================================
# STUDENTS
# ============================================================

st.markdown(
    "## 👨‍🎓 Full Payment Students"
)


# ============================================================
# CURRENT PAGE
# ============================================================

start = (

    st.session_state.page
    * cards_per_page

)


end = min(

    start + cards_per_page,

    len(students)

)


current_students = students[
    start:end
]


# ============================================================
# CARDS
# ============================================================

cards = st.columns(
    cards_per_page
)


for i, student in enumerate(
    current_students
):

    initials = "".join(

        [
            x[0]
            for x in student["name"].split()
        ][:2]

    ).upper()


    with cards[i]:

        with st.container(
            key=f"card_{student['reg']}"
        ):

            label = (

                f"{initials}\n\n"

                f"{student['name']}\n\n"

                f"{student['reg']}"

            )


            if st.button(

                label,

                key=f"btn_{student['reg']}",

                use_container_width=True

            ):

                show_student_details(
                    student
                )