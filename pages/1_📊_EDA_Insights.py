# pages/1_EDA_Insights.py

import streamlit as st
from data_utils import load_eda_data, plot_target_distribution, plot_percentage_crosstab
from style_utils import load_css

st.set_page_config(page_title="EDA Insights", page_icon="📊", layout="wide")
load_css()

from navbar_utils import render_navbar
render_navbar(active="EDA Insights")

st.title("📊 Exploratory Data Analysis")
st.markdown(
    """
    This page presents the key exploratory findings from the survey data,
    showing how social-media usage and related behaviors relate to academic
    performance across both the **School/College** and **University** groups.
    All charts show the percentage of students in each performance band,
    normalized within each category — so patterns reflect true proportions,
    not just how many students fall into each usage group.
    """
)

with st.container(border=True):
    st.markdown(
        """
        **Jump to:**
        [1. GPA/CGPA Distribution](#1-gpa-cgpa-distribution) ·
        [2. Social Media Hours](#2-social-media-usage-hours-vs-performance) ·
        [3. Study Hours](#3-daily-study-hours-vs-performance) ·
        [4. Notification Distraction](#4-notification-distraction-vs-performance) ·
        [5. Loss of Focus](#5-loss-of-focus-vs-performance) ·
        [6. Sleep Disruption](#6-sleep-disruption-vs-performance)
        """
    )

eda_data = load_eda_data()

st.divider()

# --- Target Distribution ---
st.header("1. GPA / CGPA Distribution")
fig1 = plot_target_distribution(eda_data)
st.pyplot(fig1)
st.info(
    "**Key Insight:** The School/College distribution is moderately spread, "
    "while the University distribution skews toward the 3.5–4.0 band "
    "(45% of records). Both groups show a thin *Below 2.5* category — "
    "just 6 students in School/College and ~5% of University records — "
    "which limits how confidently any model can learn that class."
)

st.divider()

# --- Social Media Usage Hours ---
st.header("2. Social Media Usage Hours vs Performance")
fig2 = plot_percentage_crosstab(
    eda_data,
    col_key="sm_hours_col",
    order_key="sm_hours_order",
    title_school="School: SM Hours vs GPA (% within group)",
    title_university="University: SM Hours vs CGPA (% within group)",
    xlabel="Daily Social Media Hours"
)
st.pyplot(fig2)
st.info(
    "**Key Insight:** Higher daily social-media usage is associated with a "
    "lower share of students in the top GPA/CGPA bands, and a growing share "
    "in the bottom bands. In School/College, the top band drops from ~75% "
    "of students at *less than 1 hour* to nearly 0% at *more than 6 hours* — "
    "a clear, consistent pattern across both groups."
)

st.divider()

# --- Study Hours ---
st.header("3. Daily Study Hours vs Performance")
fig3 = plot_percentage_crosstab(
    eda_data,
    col_key="study_hours_col",
    order_key="study_hours_order",
    title_school="School: Study Hours vs GPA (% within group)",
    title_university="University: Study Hours vs CGPA (% within group)",
    xlabel="Daily Study Hours"
)
st.pyplot(fig3)
st.success(
    "**Key Insight:** As expected, more daily study time is associated with "
    "higher performance bands — the mirror image of the social-media pattern "
    "above. This consistency between two independent variables moving in "
    "their expected directions adds confidence in the reliability of the "
    "underlying survey responses."
)

st.divider()

# --- Notification Distraction ---
st.header("4. Notification Distraction vs Performance")
fig4 = plot_percentage_crosstab(
    eda_data,
    col_key="notif_col",
    order_key="likert_order",
    title_school="School: Notification Distraction vs GPA",
    title_university="University: Notification Distraction vs CGPA",
    xlabel="Notification Distraction Frequency"
)
st.pyplot(fig4)
st.info(
    "**Key Insight:** Students who report *Never* or *Rarely* being "
    "distracted by notifications while studying show a larger share in the "
    "top performance bands. As distraction frequency rises toward *Often* "
    "and *Always*, that top-band share shrinks and the lowest bands grow — "
    "a clear gradient in both groups, slightly more pronounced in "
    "School/College."
)

st.divider()

# --- Loss of Focus ---
st.header("5. Loss of Focus vs Performance")
fig5 = plot_percentage_crosstab(
    eda_data,
    col_key="focus_col",
    order_key="likert_order",
    title_school="School: Loss of Focus vs GPA",
    title_university="University: Loss of Focus vs CGPA",
    xlabel="Loss of Focus Frequency"
)
st.pyplot(fig5)
st.info(
    "**Key Insight:** This is one of the sharpest patterns in the dataset, "
    "especially for School/College students: those who *Often* or *Always* "
    "lose focus while studying due to social media show a markedly smaller "
    "top-band share and a much larger share in the lowest bands, compared "
    "to those who *Never* or *Rarely* do. Along with notification "
    "distraction, this is one of the more direct behavioral links between "
    "social-media use and lost study effectiveness."
)

st.divider()

# --- Sleep Effect ---
st.header("6. Sleep Disruption vs Performance")
fig6 = plot_percentage_crosstab(
    eda_data,
    col_key="sleep_effect_col",
    order_key="sleep_effect_order",
    title_school="School: Sleep Effect vs GPA",
    title_university="University: Sleep Effect vs CGPA",
    xlabel="Effect of Social Media on Sleep"
)
st.pyplot(fig6)
st.info(
    "**Key Insight:** The University model shows a fairly clean pattern — "
    "students unaffected by social media sleep the most in top performance "
    "bands, while those sleeping *less than 5 hours* due to social media "
    "show the largest low-band share. The School/College pattern is noisier "
    "(likely due to its smaller sample), but *less than 5 hours* still "
    "clearly shows the worst outcome in both groups."
)

st.divider()

st.subheader("Overall Takeaway")
st.success(
    """
    Across five independent behavioral indicators — social-media hours,
    study hours, notification distraction, loss of focus, and sleep
    disruption — a coherent pattern emerges: **higher social-media
    engagement and its associated consequences (distraction, reduced study
    time, disrupted sleep) are consistently linked to lower academic
    performance bands**, in both the School/College and University groups.

    This is an *association*, not a proven cause — see the
    [Methodology](/Methodology) page for how this shaped the modeling
    approach, and the [Model Performance](/Model_Performance) page for how
    well these patterns actually translate into predictive accuracy.
    """
)