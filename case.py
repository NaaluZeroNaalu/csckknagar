import streamlit as st
from datetime import date

st.header("LOVE LEVELS")

Name = st.text_input("what is your lover name?")

age = st.text_input("Enter your lover age?")

Selected_date = st.date_input("what is your lover date of birth?",value=date(2000, 1, 1),
min_value=date(2000, 1, 1),max_value=date.today())

meet = st.selectbox("when did you first meet your lover?",["school","college","work place",
"social media","public place","other"],index=None)

food = st.multiselect("what are your lover favorite food?",
["veg","Non-veg","Fast food","Desserts","Snacks","other"])

day = st.radio("Does your lover like?",["Sunrise","sunset"])

color = st.radio("What is your lover favouite colour?",["🧡","💙","🖤","🤍","💗","💛"])

about = st.text_area("Tell me about your lover")

season = st.selectbox("What is your lover favourite season?",["🌸 Spring","☀️ Summer",
"🌧️ Rainy","❄️ Winter"])

place = st.multiselect("What is your lover favourite place?",["🏖️ Beach",
"⛰️ Hill Station","🎥 Cinema","🛍️ Shopping Mall"])

if st.button("Submit"):
    st.write("You entered:")
    st.write(about)







