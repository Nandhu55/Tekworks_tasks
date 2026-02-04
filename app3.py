import streamlit as st
from supabase import create_client
import re

st.set_page_config(page_title="Complaint System", page_icon="📣")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


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

    st.title("🔎 Search Complaint")

    cid = st.text_input("Complaint ID")

    if st.button("Search Complaint"):

        res = supabase.table("complaints") \
            .select("*") \
            .eq("id", cid) \
            .execute()

        if not res.data:
            st.warning("Complaint not found")
            return

        c = res.data[0]

        with st.expander("📄 Complaint Details", expanded=True):
            st.write("**Name:**", c["name"])
            st.write("**Email:**", c["email"])
            st.write("**Category:**", c["category"])
            st.write("**Status:**", c["status"])
            st.write("**Description:**", c["description"])
            st.write("**Created:**", c["created_at"])


def manage_complaints():

    st.title("🛠 Manage Complaints")

    res = supabase.table("complaints") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()

    if not res.data:
        st.info("No complaints found")
        return

    for c in res.data:

        with st.expander(f"📄 {c['id']} — {c['category']}"):

            st.write("Name:", c["name"])
            st.write("Email:", c["email"])
            st.write("Description:", c["description"])
            st.write("Current Status:", c["status"])

            new_status = st.selectbox(
                "Update Status",
                ["Open", "In Progress", "Closed"],
                index=["Open","In Progress","Closed"].index(c["status"]),
                key=c["id"]
            )

            if st.button("Update Status", key="btn"+c["id"]):

                supabase.table("complaints") \
                    .update({"status": new_status}) \
                    .eq("id", c["id"]) \
                    .execute()

                st.success("✅ Status Updated")
                st.rerun()

def main():

    st.sidebar.title("📂 Complaint System")

    page = st.sidebar.radio(
        "Navigate",
        [
            "📣 Submit Complaint",
            "🔎 Search Complaint",
            "🛠 Manage Complaints"
        ]
    )

    if page == "📣 Submit Complaint":
        submit_complaint()

    elif page == "🔎 Search Complaint":
        search_complaint()

    elif page == "🛠 Manage Complaints":
        manage_complaints()

if __name__ == "__main__":
    main()
