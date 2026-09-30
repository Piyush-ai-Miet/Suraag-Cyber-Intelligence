import streamlit as st

if "hist" not in st.session_state:
    st.session_state.hist = []

st.write("History:", st.session_state.hist)

with st.form(key="my_form", clear_on_submit=True):
    val = st.text_input("Enter")
    btn = st.form_submit_button("Send")

if btn and val:
    st.session_state.hist.append(val)
    st.rerun()
