import streamlit as st

pages = {

    "REPORTS":[
        st.Page("lap.py",title="Send Mail ",icon=":material/view_timeline:"),
        st.Page("Test.py",title="Check",icon=":material/home:"),

    ]
}


st.navigation(pages).run()
