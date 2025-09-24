import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Apartment Hunter", layout="centered")

# ===== CONFIG =====
DEFAULT_CRITERIA = [
    "Price", "Bang for the buck", "Location", "Good Kitchen", "In Unit Laundry",
    "Good Layout", "Natural Light", "Balcony/Patio", "Closet Space",
    "Bathroom Storage", "Updated Appliances", "Community",
    "General cuteness/ vibes", "Parking", "Amenities"
]

# Hardcoded weights (importance)
WEIGHTS = {
    "Price": 5,
    "Bang for the buck": 4,
    "Location": 5,
    "Good Kitchen": 4,
    "In Unit Laundry": 4,
    "Good Layout": 3,
    "Natural Light": 3,
    "Balcony/Patio": 2,
    "Closet Space": 2,
    "Bathroom Storage": 2,
    "Updated Appliances": 3,
    "Community": 2,
    "General cuteness/ vibes": 3,
    "Parking": 3,
    "Amenities": 2
}

# ===== LOAD EXISTING =====
if "apartments" not in st.session_state:
    st.session_state.apartments = []

# ===== MAIN APP =====
st.title("🏠 Apartment Hunter — Mobile Scorer")
st.markdown("Rate each apartment (0–10). ")

with st.form("apartment_form", clear_on_submit=True):
    name = st.text_input("Apartment name / address", "")
    cols = st.columns(2)
    ratings = {}
    for i, c in enumerate(DEFAULT_CRITERIA):
        col = cols[i % 2]
        ratings[c] = col.slider(c, 0, 10, 5)

    notes = st.text_area("Notes / impressions")
    photo = st.text_input("Photo URL (optional)")
    submitted = st.form_submit_button("Save apartment")

    if submitted:
        total_weight = sum(WEIGHTS.values()) or 1
        weighted_sum = sum(ratings[c] * WEIGHTS[c] for c in DEFAULT_CRITERIA)
        normalized_score = weighted_sum / (10 * total_weight) * 100

        entry = {"Name": name or "Unnamed", "Score": round(normalized_score, 1), "Notes": notes}
        entry.update(ratings)
        if photo:
            entry["Photo"] = photo

        st.session_state.apartments.append(entry)
        st.success(f"Saved '{entry['Name']}' — Score: {entry['Score']}")

# ===== SHOW RESULTS =====
if st.session_state.apartments:
    df = pd.DataFrame(st.session_state.apartments)
    df_display = df[["Name", "Score"] + DEFAULT_CRITERIA + ["Notes"]]
    st.subheader("Saved Apartments")
    st.dataframe(df_display.sort_values("Score", ascending=False), use_container_width=True)

    st.download_button("Download CSV", df_display.to_csv(index=False).encode("utf-8"), "apartments.csv")

    selected = st.selectbox("View details for:", options=df["Name"])
    if selected:
        row = df[df["Name"] == selected].iloc[0]
        st.markdown(f"**{row['Name']}** — Score: {row['Score']}")
        st.markdown("**Notes:**")
        st.write(row.get("Notes", ""))
        photo_url = row.get("Photo", "")
        if photo_url.strip():
            try:
                st.image(photo_url, use_column_width=True)
            except:
                st.write("Unable to load photo.")
else:
    st.info("No apartments saved yet — fill out the form above.")
