import streamlit as st

import app1
import app2
import app3
import app4

st.set_page_config(
    page_title="Unified Management Portal",
    page_icon="🚀"
)

if "logged" not in st.session_state:
    st.session_state.logged = False


def login():

    st.title("🔐 Management Portal Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged = True
            st.rerun()
        else:
            st.error("Invalid credentials")


def main():

    st.title("🚀 Unified Management System")

    module = st.sidebar.selectbox(
        "📂 Select Module",
        [
            "🎓 Student Management",
            "📅 Attendance & Marks",
            "📣 Complaints",
            "🧾 Inventory & Billing"
        ]
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged = False
        st.rerun()

    if module == "🎓 Student Management":
        app1.main()

    elif module == "📣 Complaints":
        app3.main()

    elif module == "📅 Attendance & Marks":
        app2.main()

    elif module == "🧾 Inventory & Billing":
        app4.main()


if not st.session_state.logged:
    login()
else:
    main()
