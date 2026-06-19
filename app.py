import os
import streamlit as st
import pandas as pd
import plotly.express as px
from database import engine

import setup_database

# Page Configuration
st.set_page_config(
    page_title="Local Food Wastage Management System",
    layout="wide"
)

st.title("🍲 Local Food Wastage Management System")

# Sidebar Navigation
page = st.sidebar.selectbox(
    "Choose Page",
    [
    "Dashboard",
    "Food Listings",
    "Providers",
    "Claims",
    "Analytics",
    "SQL Queries",
    "Manage Food",
    "Contact Details"
]
)

# ======================
# DASHBOARD
# ======================
if page == "Dashboard":

    st.header("📊 Dashboard")

    providers = pd.read_sql(
        "SELECT COUNT(*) AS count FROM providers",
        engine
    )

    receivers = pd.read_sql(
        "SELECT COUNT(*) AS count FROM receivers",
        engine
    )

    food = pd.read_sql(
        "SELECT COUNT(*) AS count FROM food_listings",
        engine
    )

    claims = pd.read_sql(
        "SELECT COUNT(*) AS count FROM claims",
        engine
    )

    quantity = pd.read_sql(
        "SELECT SUM(quantity) AS total FROM food_listings",
        engine
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Providers", int(providers["count"][0]))
    col2.metric("Receivers", int(receivers["count"][0]))
    col3.metric("Food Listings", int(food["count"][0]))
    col4.metric("Claims", int(claims["count"][0]))
    col5.metric("Total Quantity", int(quantity["total"][0]))

# ======================
# FOOD LISTINGS
# ======================
elif page == "Food Listings":

    st.header("🍱 Food Listings")

    df = pd.read_sql(
        "SELECT * FROM food_listings",
        engine
    )

    col1, col2, col3, col4 = st.columns(4)

    city = col1.selectbox(
        "Select City",
        ["All"] + sorted(df["location"].dropna().unique().tolist())
    )

    provider_type = col2.selectbox(
        "Select Provider Type",
        ["All"] + sorted(df["provider_type"].dropna().unique().tolist())
    )

    food_type = col3.selectbox(
        "Select Food Type",
        ["All"] + sorted(df["food_type"].dropna().unique().tolist())
    )

    meal_type = col4.selectbox(
        "Select Meal Type",
        ["All"] + sorted(df["meal_type"].dropna().unique().tolist())
    )

    if city != "All":
        df = df[df["location"] == city]

    if provider_type != "All":
        df = df[df["provider_type"] == provider_type]

    if food_type != "All":
        df = df[df["food_type"] == food_type]

    if meal_type != "All":
        df = df[df["meal_type"] == meal_type]

    st.write("Total Records:", len(df))
    st.dataframe(df, use_container_width=True)
elif page == "Providers":

    st.header("🏪 Providers")

    providers_df = pd.read_sql(
        """
        SELECT provider_id,
               name,
               type,
               city,
               contact
        FROM providers
        ORDER BY provider_id
        """,
        engine
    )

    st.dataframe(providers_df, use_container_width=True)

# ======================
# CLAIMS
# ======================
elif page == "Claims":

    st.header("📦 Claims")

    claims_df = pd.read_sql(
        """
        SELECT *
        FROM claims
        ORDER BY claim_id
        """,
        engine
    )

    st.dataframe(claims_df, use_container_width=True)

# ======================
# ANALYTICS
# ======================
elif page == "Analytics":

    st.header("📈 Analytics")

    # Food Type Distribution
    food_type_df = pd.read_sql(
        """
        SELECT food_type,
               COUNT(*) AS total
        FROM food_listings
        GROUP BY food_type
        """,
        engine
    )

    fig1 = px.pie(
        food_type_df,
        names="food_type",
        values="total",
        title="Food Type Distribution"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Meal Type Distribution
    meal_df = pd.read_sql(
        """
        SELECT meal_type,
               COUNT(*) AS total
        FROM food_listings
        GROUP BY meal_type
        """,
        engine
    )

    fig2 = px.bar(
        meal_df,
        x="meal_type",
        y="total",
        title="Meal Type Distribution"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Claim Status Distribution
    status_df = pd.read_sql(
        """
        SELECT status,
               COUNT(*) AS total
        FROM claims
        GROUP BY status
        """,
        engine
    )

    fig3 = px.pie(
        status_df,
        names="status",
        values="total",
        title="Claim Status Distribution"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # Top Cities
    city_df = pd.read_sql(
        """
        SELECT location,
               COUNT(*) AS total
        FROM food_listings
        GROUP BY location
        ORDER BY total DESC
        LIMIT 10
        """,
        engine
    )

    fig4 = px.bar(
        city_df,
        x="location",
        y="total",
        title="Top 10 Cities by Food Listings"
    )

    st.plotly_chart(fig4, use_container_width=True)
elif page == "Manage Food":

    st.header("🍱 Manage Food Listings")

    operation = st.radio(
        "Select Operation",
        ["Add Food", "Delete Food"]
    )

    if operation == "Add Food":

        food_id = st.number_input("Food ID", min_value=1)
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", min_value=1)
        provider_id = st.number_input("Provider ID", min_value=1)
        location = st.text_input("Location")
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")
        expiry_date = st.date_input("Expiry Date")

        if st.button("Add Food"):

            query = f"""
            INSERT INTO food_listings
            (food_id, food_name, quantity, expiry_date,
             provider_id, provider_type,
             location, food_type, meal_type)

            VALUES
            ({food_id},
             '{food_name}',
             {quantity},
             '{expiry_date}',
             {provider_id},
             'Restaurant',
             '{location}',
             '{food_type}',
             '{meal_type}')
            """

            with engine.connect() as conn:
                conn.execute(query)
                conn.commit()

            st.success("Food Added Successfully!")

    elif operation == "Delete Food":

        food_id = st.number_input(
            "Enter Food ID to Delete",
            min_value=1
        )

        if st.button("Delete Food"):

            query = f"""
            DELETE FROM food_listings
            WHERE food_id={food_id}
            """

            with engine.connect() as conn:
                conn.execute(query)
                conn.commit()

            st.success("Food Deleted Successfully!")
elif page == "SQL Queries":

    st.header("🧾 SQL Queries and Outputs")

    queries = {
        "1. Food providers count by city": """
            SELECT city, COUNT(*) AS total_providers
            FROM providers
            GROUP BY city
            ORDER BY total_providers DESC;
        """,

        "2. Receivers count by city": """
            SELECT city, COUNT(*) AS total_receivers
            FROM receivers
            GROUP BY city
            ORDER BY total_receivers DESC;
        """,

        "3. Provider type contributing most food": """
            SELECT provider_type, SUM(quantity) AS total_quantity
            FROM food_listings
            GROUP BY provider_type
            ORDER BY total_quantity DESC;
        """,

        "4. Contact information of providers": """
            SELECT name, type, city, contact
            FROM providers
            ORDER BY city;
        """,

        "5. Receivers who claimed most food": """
            SELECT r.name, COUNT(c.claim_id) AS total_claims
            FROM claims c
            JOIN receivers r ON c.receiver_id = r.receiver_id
            GROUP BY r.name
            ORDER BY total_claims DESC
            LIMIT 10;
        """
,
"6. Total quantity of food available": """
    SELECT SUM(quantity) AS total_food_quantity
    FROM food_listings;
""",

"7. City with highest food listings": """
    SELECT location, COUNT(*) AS total_listings
    FROM food_listings
    GROUP BY location
    ORDER BY total_listings DESC;
""",

"8. Most commonly available food types": """
    SELECT food_type, COUNT(*) AS total
    FROM food_listings
    GROUP BY food_type
    ORDER BY total DESC;
""",

"9. Claims made for each food item": """
    SELECT f.food_name, COUNT(c.claim_id) AS total_claims
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    GROUP BY f.food_name
    ORDER BY total_claims DESC;
""",

"10. Provider with highest successful claims": """
    SELECT p.name, COUNT(c.claim_id) AS successful_claims
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    JOIN providers p ON f.provider_id = p.provider_id
    WHERE c.status = 'Completed'
    GROUP BY p.name
    ORDER BY successful_claims DESC
    LIMIT 10;
""",

"11. Claim status percentage": """
    SELECT status,
           COUNT(*) AS total,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS percentage
    FROM claims
    GROUP BY status;
""",

"12. Average quantity claimed per receiver": """
    SELECT r.name, ROUND(AVG(f.quantity), 2) AS avg_quantity
    FROM claims c
    JOIN receivers r ON c.receiver_id = r.receiver_id
    JOIN food_listings f ON c.food_id = f.food_id
    GROUP BY r.name
    ORDER BY avg_quantity DESC
    LIMIT 10;
""",

"13. Meal type claimed most": """
    SELECT f.meal_type, COUNT(c.claim_id) AS total_claims
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    GROUP BY f.meal_type
    ORDER BY total_claims DESC;
""",

"14. Total quantity donated by each provider": """
    SELECT p.name, SUM(f.quantity) AS total_quantity
    FROM food_listings f
    JOIN providers p ON f.provider_id = p.provider_id
    GROUP BY p.name
    ORDER BY total_quantity DESC
    LIMIT 10;
""",

"15. Expired food listings": """
    SELECT food_name, quantity, expiry_date, location
    FROM food_listings
    WHERE expiry_date < CURRENT_DATE
    ORDER BY expiry_date;
"""
    }

    for title, query in queries.items():
        st.subheader(title)
        df = pd.read_sql(query, engine)
        st.dataframe(df, use_container_width=True)

elif page == "Manage Food":

    st.header("🍱 Manage Food Listings")

    operation = st.selectbox(
        "Select Operation",
        ["Add Food", "Update Food", "Delete Food"]
    )

    st.write("Selected operation:", operation)

    if operation == "Add Food":
        st.subheader("Add Food")
        st.text_input("Food Name")
        st.number_input("Quantity", min_value=1)

    elif operation == "Update Food":
        st.subheader("✅ Update Food Section")
        st.number_input("Food ID to Update", min_value=1)
        st.number_input("New Quantity", min_value=1)
        st.text_input("New Location")

    elif operation == "Delete Food":
        st.subheader("Delete Food")
        st.number_input("Food ID to Delete", min_value=1)
elif page == "Contact Details":

    st.header("📞 Provider Contact Details")

    df = pd.read_sql(
        """
        SELECT provider_id, name, type, address, city, contact
        FROM providers
        ORDER BY city
        """,
        engine
    )

    city = st.selectbox(
        "Select City",
        ["All"] + sorted(df["city"].dropna().unique().tolist())
    )

    if city != "All":
        df = df[df["city"] == city]

    st.write("Total Providers:", len(df))
    st.dataframe(df, use_container_width=True)
