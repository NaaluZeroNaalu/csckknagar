import streamlit as st
import pandas as pd
import re
import html


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Students Dashboard",
    layout="wide"
)


# ============================================================
# GOOGLE SHEET
# ============================================================

SHEET_ID = "15CwUlQD9dQISXVa4Hn_JuOMzrdF9qPD26Dd_GZneYs0"
SHEET_GID = "0"

GOOGLE_SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f4f7fc;
    }

    h1 {
        color: #2f3140 !important;
        font-size: 48px !important;
        font-weight: 700 !important;
    }

    /* ================= STUDENT CARD ================= */

    .student-card {
        background: white;
        padding: 10px 11px;
        border-radius: 9px;
        box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.20);
        border-left: 4px solid #4CAF50;
        height: 115px;
        min-height: 115px;
        margin-bottom: 8px;
        box-sizing: border-box;
    }

    .student-name {
        color: #0000ee;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .student-info {
        color: #222222;
        font-size: 10px;
        margin-bottom: 3px;
    }

    .balance-due {
        color: red;
        font-size: 11px;
        font-weight: 700;
        margin-top: 4px;
    }

    .balance-paid {
        color: green;
        font-size: 11px;
        font-weight: 700;
        margin-top: 4px;
    }

    /* ================= SEARCH ================= */

    div[data-testid="stTextInput"] input {
        background: #eef1f6;
        border: none;
        border-radius: 10px;
        padding: 14px;
        font-size: 12px;
    }

    /* ================= BUTTON ================= */

    .stButton > button {
        border-radius: 7px;
        padding: 3px 6px;
        height: 27px;
        background: white;
        border: 1px solid #d0d0d0;
        color: #222222;
    }

    .stButton > button:hover {
        border-color: #1565C0;
        color: #1565C0;
    }

    /* ==================================================
       POPUP
       ================================================== */

    div[data-testid="stDialog"] > div {
        width: 750px !important;
        max-width: 750px !important;
    }

    div[data-testid="stDialog"] div[role="dialog"] {
        max-height: 88vh !important;
        overflow-y: auto !important;
    }

    /* ================= POPUP TABLE ================= */

    .student-details-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    .student-details-table th {
        background: #1565C0;
        color: white;
        padding: 7px 10px;
        text-align: left;
        font-size: 13px;
    }

    .student-details-table td {
        padding: 6px 10px;
        border-bottom: 1px solid #dddddd;
        line-height: 1.2;
        font-size: 12px;
    }

    .student-details-table td:first-child {
        width: 35%;
        white-space: nowrap;
    }

    .student-details-table td:last-child {
        width: 65%;
        word-break: break-word;
    }

    /* ================= RESULT COUNT ================= */

    .result-count {
        color: #263238;
        font-size: 14px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 20px;
    }

    /* ================= PAGE INFO ================= */

    .page-info {
        text-align: center;
        color: #666666;
        font-size: 12px;
        margin-top: 8px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD GOOGLE SHEET
# ============================================================

@st.cache_data(ttl=60)
def load_google_sheet():

    try:

        df = pd.read_csv(GOOGLE_SHEET_URL)

        df = df.dropna(how="all")

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace("/", "_", regex=False)
            .str.replace("-", "_", regex=False)
        )

        return df

    except Exception as e:

        st.error("❌ Google Sheet data load panna mudiyala.")

        st.info(
            "Google Sheet → Share → "
            "General Access → "
            "Anyone with the link → Viewer"
        )

        st.code(str(e))

        return pd.DataFrame()


# ============================================================
# GET DATA
# ============================================================

df = load_google_sheet()


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.warning("Google Sheet-la data available illa.")

    st.stop()


# ============================================================
# FIND COLUMN FUNCTION
# ============================================================

def find_column(possible_names):

    for name in possible_names:

        clean_name = (
            name
            .lower()
            .strip()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )

        if clean_name in df.columns:
            return clean_name

    return None


# ============================================================
# FIND IMPORTANT COLUMNS
# ============================================================

name_col = find_column(
    [
        "name",
        "student_name",
        "studentname"
    ]
)

register_col = find_column(
    [
        "register_no",
        "register_number",
        "reg_no",
        "reg",
        "register"
    ]
)

course_col = find_column(
    [
        "course",
        "course_name"
    ]
)

balance_col = find_column(
    [
        "balance",
        "balance_due",
        "balance_due_amount",
        "due",
        "due_amount",
        "remaining"
    ]
)

paid_col = find_column(
    [
        "paid_amount",
        "paid",
        "amount_paid"
    ]
)

total_payable_col = find_column(
    [
        "total_payable",
        "total_payable_amount",
        "payable"
    ]
)


# ============================================================
# AMOUNT CONVERTER
# ============================================================

def convert_amount(value):

    if pd.isna(value):
        return 0

    value = str(value)

    value = re.sub(
        r"[^\d.-]",
        "",
        value
    )

    if value == "":
        return 0

    try:
        return float(value)

    except:
        return 0


# ============================================================
# CALCULATE BALANCE
# ============================================================

if balance_col:

    df["_balance_numeric"] = (
        df[balance_col]
        .apply(convert_amount)
    )

elif total_payable_col and paid_col:

    df["_balance_numeric"] = (
        df[total_payable_col]
        .apply(convert_amount)
        -
        df[paid_col]
        .apply(convert_amount)
    )

else:

    df["_balance_numeric"] = 0


# ============================================================
# TITLE
# ============================================================

st.title("🎓 Student Dashboard")


# ============================================================
# METRICS
# ============================================================

total_students = len(df)

total_balance = (
    df["_balance_numeric"]
    .sum()
)

students_with_due = (
    df["_balance_numeric"] > 0
).sum()


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total students",
        total_students
    )

with col2:

    st.metric(
        "Total Balance Due",
        f"₹{total_balance:,.0f}"
    )

with col3:

    st.metric(
        "Students with balance Due",
        students_with_due
    )


# ============================================================
# SEARCH
# ============================================================

search = st.text_input(
    "",
    placeholder="🔍 Search by Name"
)


# ============================================================
# SEARCH FILTER
# ============================================================

if search.strip() == "":

    filtered_df = df.copy()

else:

    keyword = (
        search
        .strip()
        .lower()
    )

    search_mask = (
        df.astype(str)
        .apply(
            lambda column:
            column
            .str
            .lower()
            .str
            .contains(
                keyword,
                na=False,
                regex=False
            )
        )
        .any(axis=1)
    )

    filtered_df = df[
        search_mask
    ].copy()


# ============================================================
# RESET PAGE WHEN SEARCH CHANGES
# ============================================================

if "last_search" not in st.session_state:

    st.session_state.last_search = search

elif st.session_state.last_search != search:

    st.session_state.current_page = 1

    st.session_state.last_search = search


# ============================================================
# STUDENTS FOUND
# ============================================================

st.markdown(
    f"""
    <div class="result-count">
        Students Found: {len(filtered_df)}
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STUDENT DETAILS POPUP
# ============================================================

@st.dialog(
    "Student Details",
    width="large"
)
def student_popup(row):

    table_rows = ""

    # Loop through all Google Sheet columns
    for column in df.columns:

        if column == "_balance_numeric":
            continue

        value = row[column]

        if pd.isna(value):
            value = "-"

        display_name = (
            column
            .replace("_", " ")
            .title()
        )

        safe_name = html.escape(
            str(display_name)
        )

        safe_value = html.escape(
            str(value)
        )

        # ---------------- BALANCE ----------------

        if column == balance_col:

            amount = convert_amount(value)

            if amount > 0:

                safe_value = (
                    f'<span style="'
                    f'color:red;'
                    f'font-weight:bold;">'
                    f'₹{amount:,.0f}'
                    f'</span>'
                )

            else:

                safe_value = (
                    f'<span style="'
                    f'color:green;'
                    f'font-weight:bold;">'
                    f'₹{amount:,.0f}'
                    f'</span>'
                )

        table_rows += (
            "<tr>"
            f"<td><b>{safe_name}</b></td>"
            f"<td>{safe_value}</td>"
            "</tr>"
        )

    popup_html = (
        '<table class="student-details-table">'
        '<tr>'
        '<th>Field</th>'
        '<th>Details</th>'
        '</tr>'
        f'{table_rows}'
        '</table>'
    )

    st.markdown(
        popup_html,
        unsafe_allow_html=True
    )


# ============================================================
# STUDENT CARD FUNCTION
# ============================================================

def show_student_card(row, index):

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if name_col:

        student_name = row[name_col]

    else:

        student_name = f"Student {index + 1}"


    # --------------------------------------------------------
    # REGISTER NUMBER
    # --------------------------------------------------------

    if register_col:

        register_no = row[register_col]

    else:

        register_no = "-"


    # --------------------------------------------------------
    # COURSE
    # --------------------------------------------------------

    if course_col:

        course = row[course_col]

    else:

        course = "-"


    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    balance = float(
        row["_balance_numeric"]
    )


    # --------------------------------------------------------
    # ESCAPE VALUES
    # --------------------------------------------------------

    student_name = html.escape(
        str(student_name)
    )

    register_no = html.escape(
        str(register_no)
    )

    course = html.escape(
        str(course)
    )


    # --------------------------------------------------------
    # BALANCE TEXT
    # --------------------------------------------------------

    if balance > 0:

        balance_text = (
            f'<div class="balance-due">'
            f'Balance ₹{balance:,.0f}'
            f'</div>'
        )

    else:

        balance_text = (
            '<div class="balance-paid">'
            'Paid / No Due'
            '</div>'
        )


    # ========================================================
    # CARD
    # ========================================================

    card_html = (
        '<div class="student-card">'
        f'<div class="student-name">'
        f'🎓 {student_name}'
        f'</div>'
        f'<div class="student-info">'
        f'<b>{register_no}</b> | {course}'
        f'</div>'
        f'{balance_text}'
        '</div>'
    )


    st.markdown(
        card_html,
        unsafe_allow_html=True
    )


    # ========================================================
    # VIEW DETAILS
    # ========================================================

    if st.button(
        "View Details",
        key=f"view_{index}"
    ):

        student_popup(row)


# ============================================================
# PAGINATION SETTINGS
# ============================================================

STUDENTS_PER_PAGE = 10

if "current_page" not in st.session_state:

    st.session_state.current_page = 1


# ============================================================
# DISPLAY STUDENTS
# ============================================================

if filtered_df.empty:

    st.warning("🔍 No student found.")

else:

    students = (
        filtered_df
        .reset_index(drop=True)
    )


    # --------------------------------------------------------
    # TOTAL PAGES
    # --------------------------------------------------------

    total_students_found = len(students)

    total_pages = (
        total_students_found
        + STUDENTS_PER_PAGE
        - 1
    ) // STUDENTS_PER_PAGE


    # --------------------------------------------------------
    # PAGE PROTECTION
    # --------------------------------------------------------

    if st.session_state.current_page > total_pages:

        st.session_state.current_page = total_pages


    # --------------------------------------------------------
    # START / END INDEX
    # --------------------------------------------------------

    start_index = (
        (st.session_state.current_page - 1)
        * STUDENTS_PER_PAGE
    )

    end_index = (
        start_index
        + STUDENTS_PER_PAGE
    )


    # --------------------------------------------------------
    # CURRENT PAGE STUDENTS
    # --------------------------------------------------------

    page_students = students.iloc[
        start_index:end_index
    ]


    # ========================================================
    # FIVE CARDS PER ROW
    # ========================================================

    for i in range(
        0,
        len(page_students),
        5
    ):

        cols = st.columns(
            5,
            gap="small"
        )

        for position, col in enumerate(cols):

            student_index = (
                i + position
            )

            if student_index < len(page_students):

                with col:

                    row = page_students.iloc[
                        student_index
                    ]

                    actual_index = (
                        start_index
                        + student_index
                    )

                    show_student_card(
                        row,
                        actual_index
                    )


    # ========================================================
    # PAGINATION
    # ========================================================

    if total_pages > 1:

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # PREVIOUS / PAGES / NEXT
        # ----------------------------------------------------

        prev_col, pages_col, next_col = st.columns(
            [1, 5, 1]
        )


        # ====================================================
        # PREVIOUS
        # ====================================================

        with prev_col:

            if st.button(
                "← Previous",
                disabled=(
                    st.session_state.current_page == 1
                ),
                use_container_width=True,
                key="previous_page"
            ):

                st.session_state.current_page -= 1

                st.rerun()


        # ====================================================
        # PAGE NUMBERS
        # ====================================================

        with pages_col:

            visible_pages = min(
                total_pages,
                7
            )

            page_columns = st.columns(
                visible_pages
            )


            if total_pages <= 7:

                pages_to_show = list(
                    range(
                        1,
                        total_pages + 1
                    )
                )

            else:

                current_page = (
                    st.session_state.current_page
                )

                if current_page <= 4:

                    pages_to_show = [
                        1, 2, 3, 4, 5, 6, 7
                    ]

                elif current_page >= total_pages - 3:

                    pages_to_show = list(
                        range(
                            total_pages - 6,
                            total_pages + 1
                        )
                    )

                else:

                    pages_to_show = [
                        current_page - 3,
                        current_page - 2,
                        current_page - 1,
                        current_page,
                        current_page + 1,
                        current_page + 2,
                        current_page + 3
                    ]


            for button_index, page_number in enumerate(
                pages_to_show
            ):

                with page_columns[
                    button_index
                ]:

                    if st.button(
                        str(page_number),
                        key=f"page_{page_number}",
                        use_container_width=True
                    ):

                        st.session_state.current_page = (
                            page_number
                        )

                        st.rerun()


        # ====================================================
        # NEXT
        # ====================================================

        with next_col:

            if st.button(
                "Next →",
                disabled=(
                    st.session_state.current_page
                    == total_pages
                ),
                use_container_width=True,
                key="next_page"
            ):

                st.session_state.current_page += 1

                st.rerun()


        # ====================================================
        # PAGE INFO
        # ====================================================

        showing_start = (
            start_index + 1
        )

        showing_end = min(
            end_index,
            total_students_found
        )

        st.markdown(
            f"""
            <div class="page-info">
                Page {st.session_state.current_page}
                of {total_pages}
                &nbsp; | &nbsp;
                Showing {showing_start}
                -
                {showing_end}
                of {total_students_found} students
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# COMPLETE DATABASE
# ============================================================

st.markdown("---")

with st.expander(
    "📊 View Complete Student Database"
):

    display_df = (
        filtered_df
        .drop(
            columns=[
                "_balance_numeric"
            ],
            errors="ignore"
        )
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )