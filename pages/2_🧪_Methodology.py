# pages/2_Methodology.py

import streamlit as st
import pandas as pd
from style_utils import load_css

st.set_page_config(page_title="Methodology", page_icon="🧪", layout="wide")
load_css()

from navbar_utils import render_navbar
render_navbar(active="Methodology")

st.title("🧪 Methodology")
st.markdown(
    """
    This page explains how the underlying models were built — from raw
    survey data to the final prediction tool. It follows the actual workflow
    used in this project, including points where testing led to a change
    from the original plan.
    """
)

with st.container(border=True):
    st.markdown(
        """
        **Jump to:**
        [1. Data Collection & Cleaning](#1-data-collection-cleaning) ·
        [2. Feature Selection](#2-feature-selection) ·
        [3. Encoding](#3-encoding) ·
        [4. Model Comparison](#4-model-comparison) ·
        [5. Handling Class Imbalance](#5-handling-class-imbalance) ·
        [6. Final Model Selection](#6-final-model-selection) ·
        [7. A Tested & Rejected Idea](#7-a-tested-and-rejected-idea-numeric-gpa-estimation)
        """
    )

st.divider()

# --- Workflow overview ---
st.subheader("Project Workflow")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("**1. Data**")
    st.caption("Google Form survey → cleaning → 757 valid responses")
with c2:
    st.markdown("**2. Features**")
    st.caption("20 predictors selected → encoded by type")
with c3:
    st.markdown("**3. Modeling**")
    st.caption("5 algorithms compared → tuned on macro F1")
with c4:
    st.markdown("**4. Deployment**")
    st.caption("Best model per group → this Streamlit app")

st.divider()

# --- 1. Data Collection & Cleaning ---
st.header("1. Data Collection & Cleaning")
st.markdown(
    """
    Data was collected via a Google Form survey covering demographics,
    social-media habits, academic behavior, psychological effects, and
    sleep. After removing invalid or identifying entries, the dataset was
    split into two groups by education level:
    """
)
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("**🎓 School/College Model**")
        st.write("Secondary & Higher Secondary students — GPA out of 5")
        st.metric("Records", "165")
with c2:
    with st.container(border=True):
        st.markdown("**🏫 University Model**")
        st.write("Bachelor & Masters/Above students — CGPA out of 4")
        st.metric("Records", "592")

st.info(
    "**Why two models?** Each group uses a different grading scale and "
    "represents a different life stage, so combining them into a single "
    "model would blur two genuinely different populations."
)

st.divider()

# --- 2. Feature Selection ---
st.header("2. Feature Selection")
st.markdown("20 candidate input features were selected, grouped into five categories:")

feature_table = pd.DataFrame({
    "Category": [
        "👤 Student information",
        "📱 Social-media usage",
        "📚 Academic interaction",
        "🧠 Psychological effects",
        "😴 Sleep",
    ],
    "Features": [
        "Age, Gender, Level of Study",
        "Daily usage hours, Active accounts, Primary purpose, Most-used platform, Checking frequency",
        "Study-related use, Use during study time, Notification distraction, Daily study hours, Loss of focus, Assignment problems",
        "Anxiety/stress, Difficulty stopping, Social comparison",
        "Use before sleep, Effect on sleep time, Tired in class",
    ],
})

st.dataframe(feature_table, use_container_width=True, hide_index=True)
st.caption(
    "Identifiers (name, email, timestamp) and free-text/messy multi-select "
    "fields were excluded from modeling."
)

st.divider()

# --- 3. Encoding ---
st.header("3. Encoding")
st.markdown("Features were encoded according to their nature, not a single blanket method:")

c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown("**Ordinal**")
        st.caption("Age ranges, usage frequency → mapped to ordered integers, preserving sequence")
with c2:
    with st.container(border=True):
        st.markdown("**Binary**")
        st.caption("Yes/No questions → mapped to 0/1")
with c3:
    with st.container(border=True):
        st.markdown("**Nominal**")
        st.caption("Platform, purpose → one-hot encoded")

st.success(
    "**Design choice:** the GPA/CGPA target itself was also treated as an "
    "ordered category (e.g. \"Below 2.5\" < \"2.5–3.0\" < ...), not an "
    "arbitrary label — so evaluation could account for *how far off* a "
    "wrong prediction is, not just whether it was exactly right."
)

st.divider()

# --- 4. Model Comparison ---
st.header("4. Model Comparison")
st.markdown("Rather than jumping directly to a single algorithm, five models were trained and compared for each dataset:")

cols = st.columns(5)
models = ["Logistic\nRegression\n(baseline)", "Decision\nTree", "Random\nForest", "Gradient\nBoosting", "XGBoost"]
for c, m in zip(cols, models):
    with c:
        st.markdown(f"<div style='text-align:center; padding:0.8rem; background:#F1F5F9; border-radius:8px;'>{m}</div>", unsafe_allow_html=True)

st.markdown("")
with st.expander("How were these models evaluated?"):
    st.markdown(
        """
        Each model was scored using:
        - Accuracy, Precision, Recall, F1-score
        - A confusion matrix
        - An **ordinal-aware "average bands off"** metric — since the target
          categories are ordered, this captures how close a wrong prediction
          was, not just whether it was exactly correct.
        """
    )

st.divider()

# --- 5. Handling Class Imbalance ---
st.header("5. Handling Class Imbalance")
st.warning(
    """
    Both datasets showed uneven class sizes — particularly the **"Below 2.5"**
    band, which made up only ~5% of University records and just 6 students
    in the School/College data.
    """
)
st.markdown(
    """
    To address this:
    - `class_weight="balanced"` was used wherever the algorithm supported it
    - Models were tuned using **macro F1**, not raw accuracy — so tuning
      wasn't rewarded for simply ignoring minority classes
    """
)

st.divider()

# --- 6. Final Model Selection ---
st.header("6. Final Model Selection")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("**🏫 University → Random Forest** (tuned)")
        st.caption("Best balance of accuracy and fair treatment of minority classes")
with c2:
    with st.container(border=True):
        st.markdown("**🎓 School/College → Logistic Regression** (tuned)")
        st.caption("Outperformed every tree-based/boosting alternative on this smaller, 132-record training set")

st.info(
    "**Notable finding:** added model complexity only helped on the larger "
    "University dataset. On the smaller School/College dataset, a simpler "
    "linear model won out — a useful reminder that more sophisticated "
    "algorithms aren't automatically better on small data."
)

st.divider()

# --- 7. Tested & Rejected Idea ---
st.header("7. A Tested and Rejected Idea: Numeric GPA Estimation")
st.markdown(
    """
    The original plan included producing a single probability-weighted
    numeric GPA/CGPA estimate (e.g. "3.28"), not just a category. This was
    implemented and tested.
    """
)
st.error(
    "**Result:** it performed no better than simply guessing the average "
    "GPA/CGPA for every student — confirmed by comparing its error against "
    "a naive baseline."
)
st.success(
    "**Decision:** rather than present a misleadingly precise number, this "
    "tool instead shows the **predicted performance band along with the "
    "model's confidence across all bands** — a more honest reflection of "
    "what the model actually knows."
)

st.divider()
st.page_link("pages/5_📈_Model_Performance.py", label="→ See exact performance numbers and confusion matrices")