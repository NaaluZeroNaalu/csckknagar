import streamlit as st

pages = {

    "REPORTS":[
        st.Page("pro.py",title="Send Mail ",icon=":material/view_timeline:"),
        st.Page("test.py",title="Check",icon=":material/home:"),

    ]
}


st.navigation(pages).run()