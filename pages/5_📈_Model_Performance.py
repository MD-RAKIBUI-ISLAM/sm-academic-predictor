# pages/5_Model_Performance.py

import streamlit as st
import pandas as pd
from style_utils import load_css

st.set_page_config(page_title="Model Performance", page_icon="📈", layout="wide")
load_css()

from navbar_utils import render_navbar
render_navbar(active="Model Performance")

st.title("📈 Model Performance & Comparison")
st.markdown(
    """
    Five algorithms were trained and compared for each dataset before
    selecting a final model. Scores below are from a **held-out test set**
    (20% of each dataset, never seen during training).
    """
)

with st.expander("📖 What do these metrics mean?"):
    st.markdown(
        """
        - **Accuracy** — % of predictions that exactly matched the true band
        - **Precision (macro)** — when the model predicts a band, how often it's right, averaged equally across all bands
        - **Recall (macro)** — of all students actually in a band, how many the model correctly caught, averaged equally across all bands
        - **F1 (macro)** — the balance of precision and recall; the primary metric used for model selection here, since it doesn't get inflated by ignoring rare classes
        - **Mean Ordinal Distance** — average number of GPA/CGPA bands a wrong prediction was off by (lower is better) — meaningful because the bands are ordered, not arbitrary labels
        """
    )

st.divider()

# --- Headline final models ---
st.subheader("🏆 Final Models Selected")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("**🎓 School/College**")
        st.markdown("#### Logistic Regression (Tuned)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Accuracy", "33.3%")
        m2.metric("F1 (macro)", "0.300")
        m3.metric("Avg. Bands Off", "1.09")
with c2:
    with st.container(border=True):
        st.markdown("**🏫 University**")
        st.markdown("#### Random Forest (Tuned)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Accuracy", "45.4%")
        m2.metric("F1 (macro)", "0.396")
        m3.metric("Avg. Bands Off", "0.71")

st.divider()

# --- Full comparison tables, split by dataset ---
st.subheader("Full Model Comparison")

school_results = [
    ["Logistic Regression", 0.303, 0.236, 0.231, 0.224, 1.121, ""],
    ["Decision Tree", 0.242, 0.199, 0.196, 0.188, 1.273, ""],
    ["Random Forest", 0.303, 0.173, 0.224, 0.190, 1.212, ""],
    ["Gradient Boosting", 0.242, 0.169, 0.171, 0.164, 1.303, ""],
    ["XGBoost", 0.182, 0.131, 0.132, 0.124, 1.424, ""],
    ["Logistic Regression (Tuned)", 0.333, 0.313, 0.298, 0.300, 1.091, "🏆 Final"],
]
university_results = [
    ["Logistic Regression", 0.471, 0.525, 0.333, 0.347, 0.639, ""],
    ["Decision Tree", 0.420, 0.251, 0.268, 0.258, 0.748, ""],
    ["Random Forest", 0.504, 0.547, 0.356, 0.372, 0.613, ""],
    ["Gradient Boosting", 0.445, 0.400, 0.322, 0.334, 0.681, ""],
    ["XGBoost", 0.412, 0.321, 0.307, 0.312, 0.756, ""],
    ["Random Forest (Tuned)", 0.454, 0.418, 0.400, 0.396, 0.714, "🏆 Final"],
]
columns = ["Model", "Accuracy", "Precision (macro)", "Recall (macro)", "F1 (macro)", "Mean Ordinal Distance", ""]

tab1, tab2 = st.tabs(["🎓 School/College", "🏫 University"])

with tab1:
    df_school_results = pd.DataFrame(school_results, columns=columns)
    st.dataframe(df_school_results, use_container_width=True, hide_index=True)
    st.bar_chart(df_school_results.set_index("Model")[["Accuracy", "F1 (macro)"]])
    st.caption(
        "Logistic Regression (tuned) outperformed every tree-based and "
        "boosting alternative — likely due to the small training set "
        "(132 records), where added model complexity didn't help."
    )

with tab2:
    df_university_results = pd.DataFrame(university_results, columns=columns)
    st.dataframe(df_university_results, use_container_width=True, hide_index=True)
    st.bar_chart(df_university_results.set_index("Model")[["Accuracy", "F1 (macro)"]])
    st.caption(
        "Random Forest (tuned) gave the strongest overall balance of "
        "accuracy and fair treatment of minority classes, aided by "
        "`class_weight=\"balanced\"` and macro-F1-based tuning."
    )

st.divider()

# --- Limitations ---
st.subheader("⚠️ Known Limitations")
st.warning(
    """
    - **Class imbalance** — the *"Below 2.5"* category was rare in both
      datasets (~5% of University records, only 6 in School/College),
      making it the hardest category for any model to learn reliably.
    - **Small School/College sample size** (165 records total) limits how
      confidently these results generalize.
    - **Self-reported survey data** may include response bias (e.g.
      students under- or over-reporting usage hours).
    - A probability-weighted **numeric GPA/CGPA estimate** was tested and
      found to perform no better than simply predicting the average for
      every student — so this tool reports a **band + confidence** instead
      of a single number, avoiding false precision.
    """
)

st.divider()

# --- Feature Importance ---
st.subheader("🔍 What Matters Most?")
st.markdown(
    "Beyond overall accuracy, it's useful to know *which* factors most "
    "influenced each model's predictions."
)

import pickle

with open("feature_importance_data.pkl", "rb") as f:
    fi_data = pickle.load(f)

# Clean up the long bilingual column names into short readable labels for the chart
def shorten_label(name):
    return name.split("\n")[0].split("?")[0][:45]

tab1, tab2 = st.tabs(["🏫 University (Random Forest)", "🎓 School/College (Logistic Regression)"])

with tab1:
    uni_top10 = fi_data["university_rf_importances"].head(10)
    uni_top10.index = [shorten_label(i) for i in uni_top10.index]
    st.bar_chart(uni_top10)
    st.caption(
        "Daily social-media usage hours is the single strongest predictor "
        "for University students, followed by using social media during "
        "study time and daily study hours."
    )

with tab2:
    school_top10 = fi_data["school_logreg_importances"].head(10)
    school_top10.index = [shorten_label(i) for i in school_top10.index]
    st.bar_chart(school_top10)
    st.caption(
        "Social-media usage hours is again the top predictor for "
        "School/College students. Note: with a smaller training sample, "
        "some platform-specific coefficients here should be interpreted "
        "cautiously."
    )

st.page_link("pages/2_🧪_Methodology.py", label="← Back to Methodology for full modeling details")

