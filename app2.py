import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date


st.set_page_config(page_title="Attendance & Marks Portal", page_icon="📘")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "logged" not in st.session_state:
    st.session_state.logged = False

def login():
    st.title("🔐 Login Student Attendance & Marks Portal")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == "admin" and p == "123":
            st.session_state.logged = True
            st.rerun()
        else:
            st.error("Invalid login")


def add_student():
    st.subheader("➕ Add Student")

    with st.form("student_form"):
        roll = st.text_input("Roll No")
        name = st.text_input("Name")
        cls = st.selectbox("Class", ["10th","9th","8th","7th","6th"])
        submit = st.form_submit_button("Add")

        if submit:
            supabase.table("students").insert({
                "roll_no": roll,
                "name": name,
                "class": cls
            }).execute()

            st.success("Student added")

def get_students():
    res = supabase.table("students").select("*").execute()
    return res.data


def mark_attendance():
    st.subheader("📅 Mark Attendance")

    students = get_students()
    names = {s["name"]: s["id"] for s in students}

    student = st.selectbox("Student", names.keys())
    status = st.radio("Status", ["Present","Absent"])

    if st.button("Save Attendance"):
        supabase.table("attendance").insert({
            "student_id": names[student],
            "date": str(date.today()),
            "status": status
        }).execute()

        st.success("Attendance saved")

def add_marks():
    st.subheader("📝 Add Marks")

    students = get_students()
    names = {s["name"]: s["id"] for s in students}

    student = st.selectbox("Student", names.keys(), key="marks_st")
    subject = st.selectbox("Subject", ["Math","Science","English"])
    marks = st.number_input("Marks", 0, 100)

    if st.button("Save Marks"):
        supabase.table("marks").insert({
            "student_id": names[student],
            "subject": subject,
            "marks": marks
        }).execute()

        st.success("Marks saved")

def attendance_history():
    st.subheader("📖 Attendance History")

    res = supabase.table("attendance") \
        .select("date,status,students(name,roll_no)") \
        .execute()

    st.dataframe(res.data)

def attendance_percent():
    st.subheader("📊 Attendance %")

    students = get_students()
    names = {s["name"]: s["id"] for s in students}
    student = st.selectbox("Student", names.keys(), key="att_pct")

    sid = names[student]

    res = supabase.table("attendance") \
        .select("status") \
        .eq("student_id", sid) \
        .execute()

    rows = res.data
    if not rows:
        st.warning("No records")
        return

    present = sum(r["status"] == "Present" for r in rows)
    pct = present / len(rows) * 100

    st.success(f"Attendance = {pct:.1f}%")

def pass_fail():
    st.subheader("✅ Pass / Fail")

    res = supabase.table("marks") \
        .select("marks,subject,students(name)") \
        .execute()

    data = res.data

    for r in data:
        r["status"] = "PASS" if r["marks"] >= 40 else "FAIL"

    st.dataframe(data)

def dashboard():

    st.title("📘 Student Attendance & Marks Portal")

    menu = st.sidebar.radio(
        "Menu",
        [
            "➕ Add Student",
            "📅 Mark Attendance",
            "📝 Add Marks",
            "📖 Attendance History",
            "📊 Attendance %",
            "✅ Pass/Fail"
        ]
    )
    

    if menu == "➕ Add Student":
        add_student()

    elif menu == "📅 Mark Attendance":
        mark_attendance()

    elif menu == "📝 Add Marks":
        add_marks()

    elif menu == "📖 Attendance History":
        attendance_history()

    elif menu == "📊 Attendance %":
        attendance_percent()

    elif menu == "✅ Pass/Fail":
        pass_fail()


if not st.session_state.logged:
    login()
else:
    dashboard()
