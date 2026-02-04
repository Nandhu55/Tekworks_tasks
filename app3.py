import streamlit as st
from supabase import create_client
import re

st.set_page_config(page_title="Complaint System", page_icon="📣")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


if "admin" not in st.session_state:
    st.session_state.admin = False

def valid_email(email):
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email)

def submit_complaint():

    st.title("📣 Submit Complaint")

    with st.form("complaint_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        category = st.selectbox(
            "Category",
            ["Technical", "Billing", "Service", "Other"]
        )
        desc = st.text_area("Complaint Description")

        submit = st.form_submit_button("Submit Complaint")

        if submit:

            if not name or not email or not desc:
                st.error("All fields required")
                return

            if not valid_email(email):
                st.error("Invalid email format")
                return

            res = supabase.table("complaints").insert({
                "name": name,
                "email": email,
                "category": category,
                "description": desc
            }).execute()

            if res.data:
                st.success("✅ Complaint submitted")
                st.info(f"🆔 Complaint ID: {res.data[0]['id']}")

def search_complaint():

    st.subheader("🔎 Search Complaint")

    cid = st.text_input("Complaint ID")

    if st.button("Search"):
        res = supabase.table("complaints") \
            .select("*") \
            .eq("id", cid) \
            .execute()

        if not res.data:
            st.warning("Not found")
            return

        c = res.data[0]

        with st.expander("Complaint Details", expanded=True):
            st.write("**Name:**", c["name"])
            st.write("**Email:**", c["email"])
            st.write("**Category:**", c["category"])
            st.write("**Status:**", c["status"])
            st.write("**Description:**", c["description"])
            st.write("**Created:**", c["created_at"])


def admin_view():

    st.title("🛠 Admin Complaint Panel")

    res = supabase.table("complaints") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()

    for c in res.data:

        with st.expander(f"📄 {c['id']} — {c['category']}"):

            st.write("Name:", c["name"])
            st.write("Email:", c["email"])
            st.write("Description:", c["description"])
            st.write("Status:", c["status"])

            new_status = st.selectbox(
                "Update Status",
                ["Open", "In Progress", "Closed"],
                key=c["id"]
            )

            if st.button("Update", key="btn"+c["id"]):
                supabase.table("complaints") \
                    .update({"status": new_status}) \
                    .eq("id", c["id"]) \
                    .execute()

                st.success("Updated")
                st.rerun()


def admin_login():

    st.title("🔐 Admin Login")

    user = st.text_input("Admin User")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if user == "admin" and pwd == "1234":
            st.session_state.admin = True
            st.rerun()
        else:
            st.error("Wrong credentials")


st.sidebar.title("📂 Menu")

mode = st.sidebar.radio(
    "Select Mode",
    ["User Portal", "Admin Portal"]
)

if st.session_state.admin:
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin = False
        st.rerun()


def main():
    st.sidebar.title("📂 Menu")

    mode = st.sidebar.radio(
        "Select Mode",
        ["User Portal", "Admin Portal"]
    )

    if st.session_state.admin:
        if st.sidebar.button("🚪 Logout"):
            st.session_state.admin = False
            st.rerun()

    if mode == "User Portal":

        submit_complaint()
        st.divider()
        search_complaint()

    else:

        if not st.session_state.admin:
            admin_login()
        else:
            admin_view()


if __name__ == "__main__":
    main()
