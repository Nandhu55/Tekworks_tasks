import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date


st.set_page_config(page_title="Inventory & Billing", page_icon="🧾")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "cart" not in st.session_state:
    st.session_state.cart = []


def add_product():

    st.subheader("➕ Add Product")

    with st.form("add_product"):
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0.0)
        stock = st.number_input("Stock", min_value=0)

        if st.form_submit_button("Add"):
            if not name or price <= 0:
                st.error("Invalid data")
                return

            supabase.table("products").insert({
                "name": name,
                "price": price,
                "stock": int(stock)
            }).execute()

            st.success("Product added")

def view_products():

    st.subheader("📦 Product List")

    res = supabase.table("products").select("*").execute()

    if res.data:
        st.dataframe(res.data)
    else:
        st.info("No products found")


def billing():

    st.subheader("🧾 Create Bill")

    res = supabase.table("products").select("*").execute()

    if not res.data:
        st.warning("No products available")
        return

    df = pd.DataFrame(res.data)

    col1, col2 = st.columns(2)

    with col1:
        pname = st.selectbox("Product", df["name"])
    with col2:
        qty = st.number_input("Quantity", 1, 100)

    if st.button("Add to Cart"):

        prod = df[df["name"] == pname].iloc[0]

        if prod["stock"] < qty:
            st.error("Not enough stock")
            return

        st.session_state.cart.append({
            "id": prod["id"],
            "name": pname,
            "price": prod["price"],
            "qty": qty,
            "total": prod["price"] * qty
        })

        st.success("Added to cart")

    if st.session_state.cart:

        st.divider()
        st.write("### 🛒 Cart")

        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df)

        grand_total = sum(i["total"] for i in st.session_state.cart)
        st.metric("Total Amount", grand_total)

        if st.button("✅ Generate Bill"):
            generate_bill(grand_total)

def generate_bill(total):

    bill = supabase.table("bills").insert({
        "total_amount": total
    }).execute()

    bill_id = bill.data[0]["id"]

    for item in st.session_state.cart:

        supabase.table("bill_items").insert({
            "bill_id": bill_id,
            "product_id": item["id"],
            "quantity": item["qty"]
        }).execute()

        supabase.rpc("decrement_stock", {
            "pid": item["id"],
            "qty": item["qty"]
        }).execute()

    text = "\n".join(
        f"{i['name']} x{i['qty']} = {i['total']}"
        for i in st.session_state.cart
    )

    st.download_button(
        "⬇ Download Bill",
        data=text,
        file_name=f"bill_{bill_id}.txt"
    )

    st.success("Bill generated")
    st.session_state.cart = []

def daily_sales():

    st.subheader("📊 Today Sales")

    today = str(date.today())

    res = supabase.table("bills") \
        .select("total_amount,bill_date") \
        .gte("bill_date", today) \
        .execute()

    if not res.data:
        st.info("No sales today")
        return

    df = pd.DataFrame(res.data)

    total = df["total_amount"].sum()

    st.metric("Today's Sales", total)
    st.dataframe(df)

def main():

    st.title("🏪 Inventory & Billing Management")

    menu = st.sidebar.radio(
        "📂 Menu",
        [
            "➕ Add Product",
            "📦 View Products",
            "🧾 Billing",
            "📊 Daily Sales"
        ]
    )

    if menu == "➕ Add Product":
        add_product()

    elif menu == "📦 View Products":
        view_products()

    elif menu == "🧾 Billing":
        billing()

    elif menu == "📊 Daily Sales":
        daily_sales()


main()
