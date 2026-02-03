import streamlit as st
from supabase import create_client
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt


supabase=create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.set_page_config(page_title="Student Performance Management System", page_icon="🎓")



def insert():
    st.subheader("➕ Add Student")

    with st.form("student_form"):
        name=st.text_input("name")
        age= st.number_input("age")
        subject=st.text_input("subject")
        marks= st.number_input("marks")
        submit = st.form_submit_button("Insert")

        if submit:
            if not name or not age or not subject or not marks:
                st.warning("All fields are required")
            else:
                try:
                    supabase.table("students").insert({
                        "name": name,
                        "age": int(age),
                        "subject": subject,
                        "marks": int(marks)
                    }).execute()

                    st.success("✅ User added successfully")

                except Exception as e:
                    st.error("insert failed")
                    st.write(e)


def tableview():
    st.subheader("👀 All Students")

    if st.button("show students data"):
        try:
            res=supabase.table("students").select("*").execute()
            data=res.data

            if data:
                df=pd.DataFrame(data)
                st.dataframe(df,use_container_width=True)
            else:
                st.info("no student records are found")

        except Exception as e:
            st.error("failed to fetch data")
            st.write(e)


def update():
    st.subheader("✏️ Update Student")

    st_id=st.number_input("id")
    age= st.number_input("age")
    marks= st.number_input("marks")

    if st.button("update"):
        if not st_id or not age or not marks:
            st.warning("All fields are required")
        else:
            try:
                res=supabase.table("students").update({
                    "age": int(age),
                    "marks": int(marks)
                }).eq("id",int(st_id)).execute()

                if res.data:
                    st.success("✅ Updated successfully")
                else:
                    st.warning("⚠️ No student found")

            except Exception as e:
                st.error("failed to update")
                st.write(e)


def delete_data():
    st.subheader("🗑️ Delete Student")

    st_id=st.number_input("id")

    if st.button("delete"):
        if st_id == 0:
            st.warning("enter id no")
            return

        try:
            res=supabase.table("students").delete()\
                .eq("id",int(st_id)).execute()

            if res.data:
                st.success("✅ deleted successfully")
            else:
                st.warning("⚠️ No student found")

        except Exception as e:
            st.error("failed to delete")
            st.write(e)


def pass_fail():
    st.subheader("📌 Pass / Fail Status")

    if st.button("Show Status"):
        res=supabase.table("students").select("*").execute()
        data=res.data

        for r in data:
            r["status"] = "PASS" if r["marks"] >= 50 else "FAIL"

        st.dataframe(data)


def show_avg_marks():
    st.subheader("📚 Average Marks Per Subject")

    if st.button("Show Averages"):
        res=supabase.rpc("avg_marks_per_subject").execute()
        st.dataframe(res.data)


def cal():
    st.subheader("🧮 Analytics")

    if st.button("Calculate"):
        res=supabase.table("students").select("*").execute()
        students=res.data

        marks=[s["marks"] for s in students]

        avg=sum(marks)/len(marks)
        pass_pct=sum(m>=50 for m in marks)/len(marks)*100
        top=max(students,key=lambda x:x["marks"])

        c1,c2,c3=st.columns(3)
        c1.metric("Average",round(avg,2))
        c2.metric("Pass %",round(pass_pct,2))
        c3.metric("Top",top["marks"])

        st.success(f"🏆 {top['name']}")


def charts():
    st.subheader("📊 Charts")

    res=supabase.table("students").select("subject,marks").execute()
    data=res.data

    subject_marks=defaultdict(list)
    for r in data:
        subject_marks[r["subject"]].append(r["marks"])

    subject_avg={s:sum(m)/len(m) for s,m in subject_marks.items()}
    st.bar_chart(subject_avg)

    pass_c=sum(r["marks"]>=50 for r in data)
    fail_c=len(data)-pass_c

    fig,ax=plt.subplots()
    ax.pie([pass_c,fail_c],labels=["Pass","Fail"],autopct="%1.1f%%")
    st.pyplot(fig)


def main():

    st.title("🎓 Student Performance Management System")

    st.sidebar.title("📌 Menu")

    choice = st.sidebar.radio(
        "Navigate",
        [
            "➕ Add Student",
            "👀 View Students",
            "✏️ Update Student",
            "🗑️ Delete Student",
            "📌 Pass/Fail",
            "📚 Subject Avg",
            "🧮 Analytics",
            "📊 Charts"
        ]
    )

    if choice == "➕ Add Student":
        insert()

    elif choice == "👀 View Students":
        tableview()

    elif choice == "✏️ Update Student":
        update()

    elif choice == "🗑️ Delete Student":
        delete_data()

    elif choice == "📌 Pass/Fail":
        pass_fail()

    elif choice == "📚 Subject Avg":
        show_avg_marks()

    elif choice == "🧮 Analytics":
        cal()

    elif choice == "📊 Charts":
        charts()


if __name__ == "__main__":
    main()
