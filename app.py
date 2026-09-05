# app.py

import streamlit as st
from style_utils import load_css

st.set_page_config(page_title="Social Media & Academic Performance", page_icon="🎓", layout="wide")
load_css()

from navbar_utils import render_navbar
render_navbar(active="Home")

# --- Hero ---
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-badge">
            🎓 Academic Insight Project
        </div>
        <h1 class="hero-title">
            Understanding How Screen Time Shapes Student Success
        </h1>
        <p class="hero-subtitle">
            A data-driven look at how social-media habits — usage hours, distraction, sleep, and study behavior — relate to academic performance, built from a survey of <b>757 School/College and University students</b> in Bangladesh. Explore the findings or predict your performance band.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)
with c1:
    st.page_link(
        "pages/3_🎒_School_GPA_Predictor.py",
        label="🎓 School GPA Predictor",
        use_container_width=True,
    )
with c2:
    st.page_link(
        "pages/4_🏛️_University_CGPA_Predictor.py",
        label="🏫 University CGPA Predictor",
        use_container_width=True,
    )


st.divider()

# --- Key stats ---
st.subheader("The Data, at a Glance")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Respondents", "757")
c2.metric("School / College", "165 students")
c3.metric("University", "592 students")
c4.metric("Models Compared", "5 algorithms")

st.divider()

# --- What you can do here ---
st.subheader("Explore the Project")

c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("#### 📊 EDA Insights")
        st.write(
            "See how social-media hours, study time, distraction, and sleep "
            "each relate to GPA/CGPA — with live charts from the real survey "
            "data."
        )
        st.page_link("pages/1_📊_EDA_Insights.py", label="View Insights →")

with c2:
    with st.container(border=True):
        st.markdown("#### 🧪 Methodology")
        st.write(
            "How the data was cleaned, encoded, and modeled — including the "
            "algorithms compared and a tested idea that didn't make the cut."
        )
        st.page_link("pages/2_🧪_Methodology.py", label="Read the Approach →")

with c3:
    with st.container(border=True):
        st.markdown("#### 📈 Model Performance")
        st.write(
            "Full comparison table across all five models, plus an honest "
            "look at the limitations of this approach."
        )
        st.page_link("pages/5_📈_Model_Performance.py", label="See the Results →")

st.divider()

# --- Key findings ---
st.subheader("Key Findings")
st.markdown(
    """
    Across both student groups, five independent behavioral indicators told
    a consistent story:

    - 📱 **More social-media hours** → lower share of students in top GPA/CGPA bands
    - 📚 **More daily study hours** → higher share of students in top bands
    - 🔔 **Frequent notification distraction** → lower performance bands
    - 🎯 **Frequent loss of focus** while studying → lower performance bands
    - 😴 **Greater sleep disruption** from social media → lower performance bands
    """
)
st.page_link("pages/1_📊_EDA_Insights.py", label="See the full charts and analysis →")

st.divider()

# --- How it works ---
st.subheader("How the Prediction Works")

st.markdown(
    """
    <div class="steps-grid">
        <div class="step-card">
            <div class="step-number">01</div>
            <div class="step-title">Answer Questions</div>
            <p class="step-desc">Provide details about your daily habits — social media usage, study hours, notifications, and sleep.</p>
        </div>
        <div class="step-card">
            <div class="step-number">02</div>
            <div class="step-title">Model Runs</div>
            <p class="step-desc">A trained Machine Learning classifier processes your input and estimates your performance band.</p>
        </div>
        <div class="step-card">
            <div class="step-number">03</div>
            <div class="step-title">See Your Result</div>
            <p class="step-desc">Get your predicted GPA/CGPA band along with a transparent confidence score breakdown.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "💡 This tool provides a statistical estimate for educational/research "
    "purposes only — not a diagnostic or guaranteed prediction of individual "
    "academic performance."
)