# pages/3_Predict_School.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from model_utils import load_artifacts, predict, load_feature_importance, get_recommendations
from data_utils import load_eda_data
from style_utils import load_css

st.set_page_config(page_title="Predict — School/College", page_icon="🎓", layout="wide")
load_css()

from auth_utils import require_login, current_user
require_login()

user = current_user()
st.caption(f"Logged in as {user['full_name']} ({user['registration_number']})")

from navbar_utils import render_navbar
render_navbar(active="Predict School")

st.title("🎓 GPA Prediction — School / College Students")
st.markdown(
    "Answer the questions below to get an estimated **GPA band**, based on "
    "patterns learned from 165 School/College student survey responses."
)

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("Questions", "20")
    c2.metric("Est. Time", "~2 min")
    c3.metric("Model", "Logistic Regression")

artifacts = load_artifacts()
eda_data = load_eda_data()
col = artifacts["column_names"]
df_school = eda_data["df_school_model"]

likert_options = ["Never", "Rarely", "Sometimes", "Often", "Always"]
yes_no_options = ["No", "Yes"]

with st.form("school_prediction_form"):

    st.subheader("👤 Student Information")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        age = c1.selectbox("Age", ["under 18", "18 - 21", "21 - 25", "25 - 28", "28+"])
        gender = c2.selectbox("Gender", ["Male", "Female"])
        level = c3.selectbox("Level of Study", sorted(df_school[col["level_col"]].dropna().unique().tolist()))

    st.subheader("📱 Social Media Usage")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        sm_hours = c1.selectbox("Daily social media usage hours",
            ["Less than 1 hour", "1 - 2 hours", "3 - 4 hours", "5 - 6 hours", "More than 6 hours"])
        accounts = c2.selectbox("Number of active accounts", ["1", "2 - 3", "4 - 5", "more than 5"])
        purpose = c3.selectbox("Primary purpose", sorted(df_school[col["purpose_col"]].dropna().unique().tolist()))

        c1, c2 = st.columns(2)
        platform = c1.selectbox("Most-used platform", sorted(df_school[col["platform_col"]].dropna().unique().tolist()))
        checking = c2.selectbox("Checking frequency",
            ["Less than 5 times", "5–10 times", "10–20 times", "More than 20 times"],
            help="How many times per day you actively open and check social media")

    st.subheader("📚 Academic Interaction")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        study_related = c1.selectbox("Use social media for study-related purposes?", yes_no_options,
            help="E.g. joining study groups, following educational pages")
        during_study = c2.selectbox("Use social media during study time?", likert_options)

        c1, c2 = st.columns(2)
        notif = c1.selectbox("Distracted by notifications while studying?", likert_options)
        study_hours = c2.selectbox("Daily study hours",
            ["Less than 1 hour", "1 - 2 hours", "3 - 4 hours", "more than 4 hours"])

        c1, c2 = st.columns(2)
        focus = c1.selectbox("Lose focus while studying due to social media?", likert_options)
        assignment = c2.selectbox("Fail to submit assignments on time due to social media?", yes_no_options)

    st.subheader("🧠 Psychological Effects")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        anxiety = c1.selectbox("Anxious or stressed after using social media?", likert_options)
        stopping = c2.selectbox("Difficult to stop using social media once started?", likert_options)
        comparison = c3.selectbox("Compare your life with others on social media?", likert_options)

    st.subheader("😴 Sleep")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        before_sleep = c1.selectbox("Use social media before sleep?", yes_no_options)
        sleep_effect = c2.selectbox("Effect on your sleeping time", [
            "Social media does not affect my sleep time",
            "I sleep 7–8 hours, not affected by social media",
            "I sleep 6–7 hours, slightly affected by social media",
            "I sleep 5–6 hours due to social media",
            "I sleep less than 5 hours due to social media",
        ])
        tired = c3.selectbox("Feel tired in class due to late-night usage?", yes_no_options)

    st.markdown("")
    submitted = st.form_submit_button("🔮 Predict My GPA Band", use_container_width=True)

if submitted:
    raw_input = {
        col["age_col"]: age,
        col["gender_col"]: gender,
        col["level_col"]: level,
        col["sm_hours_col"]: sm_hours,
        col["accounts_col"]: accounts,
        col["purpose_col"]: purpose,
        col["platform_col"]: platform,
        col["checking_col"]: checking,
        col["study_related_col"]: study_related,
        col["during_study_col"]: during_study,
        col["notif_col"]: notif,
        col["study_hours_col"]: study_hours,
        col["focus_col"]: focus,
        col["assignment_col"]: assignment,
        col["anxiety_col"]: anxiety,
        col["stopping_col"]: stopping,
        col["comparison_col"]: comparison,
        col["before_sleep_col"]: before_sleep,
        col["sleep_effect_col"]: sleep_effect,
        col["tired_col"]: tired,
    }

    predicted_band, confidence = predict(raw_input, artifacts, model_type="school")

    from auth_utils import current_user, mark_trial_used
    user = current_user()
    if user["verification_status"] == "Pending" and not user["trial_used"]:
        mark_trial_used(user["id"])

    st.divider()
    st.subheader("Your Result")

    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("**Predicted GPA Band**")
            st.markdown(f"## 🎯 {predicted_band}")
            top_confidence = max(confidence.values())
            st.caption(f"Model confidence: {top_confidence:.0%}")
        with c2:
            confidence_series = pd.Series(confidence).reindex(artifacts["school_target_order"])
            fig, ax = plt.subplots(figsize=(7, 3.2))
            colors = ["#2563EB" if band == predicted_band else "#BFDBFE" for band in confidence_series.index]
            ax.bar(confidence_series.index, confidence_series.values, color=colors)
            ax.set_ylabel("Confidence")
            ax.tick_params(axis='x', rotation=45)
            fig.tight_layout()
            st.pyplot(fig)

    from model_utils import generate_result_image
    image_buf = generate_result_image(predicted_band, confidence_series, "Predicted GPA Band", "#2563EB")

    st.download_button(
        label="⬇️ Download My Result",
        data=image_buf,
        file_name="my_gpa_prediction.png",
        mime="image/png",
        use_container_width=True,
    )

    st.subheader("💡 Personalized Suggestions")
    fi_data = load_feature_importance()
    recommendations = get_recommendations(raw_input, artifacts, fi_data, model_type="school")

    if recommendations:
        cards_html = "<div class='rec-list'>"
        for i, (icon, tip) in enumerate(recommendations, start=1):
            cards_html += f"<div class='rec-card'><div class='rec-number'>{i}</div><div class='rec-icon'>{icon}</div><div class='rec-text'>{tip}</div></div>"
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)
    else:
        st.success("Your reported habits don't show any of the strongest risk patterns identified in this study — keep it up!")

    st.divider()

    st.subheader("📊 How You Compare")
    from data_utils import get_percentile_comparisons
    comparisons = get_percentile_comparisons(raw_input, eda_data, model_type="school")

    for comp in comparisons:
        pct = comp["percentile"]
        label = comp["label"]
        answer = comp["user_answer"]

        if comp["higher_is_worse"]:
            caption = f"Higher than **{pct}%** of respondents" if pct >= 50 else f"Lower than **{100 - pct}%** of respondents"
            color = "#EF4444" if pct >= 70 else ("#F59E0B" if pct >= 40 else "#16A34A")
        else:
            caption = f"Higher than **{pct}%** of respondents" if pct >= 50 else f"Lower than **{100 - pct}%** of respondents"
            color = "#16A34A" if pct >= 70 else ("#F59E0B" if pct >= 40 else "#EF4444")

        st.markdown(f"**{label}**: {answer}")
        st.markdown(
            f"<div style='background:#F1F5F9;border-radius:6px;height:10px;margin-bottom:0.3rem;'>"
            f"<div style='background:{color};width:{pct}%;height:10px;border-radius:6px;'></div></div>",
            unsafe_allow_html=True
        )
        st.caption(caption)

    st.divider()

    st.caption(
        "📊 This is a statistical estimate based on survey patterns, not a "
        "guarantee. See the **Model Performance** page for accuracy details."
    )