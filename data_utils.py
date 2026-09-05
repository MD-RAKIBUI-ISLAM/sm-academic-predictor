# data_utils.py

import pickle
import pandas as pd
import matplotlib.pyplot as plt

EDA_DATA_PATH = "eda_data.pkl"


def load_eda_data():
    """Load raw survey data and metadata needed for live chart generation."""
    with open(EDA_DATA_PATH, "rb") as f:
        eda_data = pickle.load(f)
    return eda_data


def plot_target_distribution(eda_data):
    """Bar charts: GPA/CGPA distribution for both models."""
    df_school = eda_data["df_school_model"]
    df_university = eda_data["df_university_model"]
    y_school = eda_data["y_school"]
    y_university = eda_data["y_university"]
    school_order = eda_data["school_target_order"]
    university_order = eda_data["university_target_order"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    y_school.value_counts().reindex(school_order).plot(kind="bar", ax=axes[0], color="steelblue")
    axes[0].set_title("School/College GPA Distribution")
    axes[0].set_xlabel("GPA Range")
    axes[0].set_ylabel("Count")
    axes[0].tick_params(axis='x', rotation=45)

    y_university.value_counts().reindex(university_order).plot(kind="bar", ax=axes[1], color="darkorange")
    axes[1].set_title("University CGPA Distribution")
    axes[1].set_xlabel("CGPA Range")
    axes[1].set_ylabel("Count")
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    return fig


def plot_percentage_crosstab(eda_data, col_key, order_key, title_school, title_university, xlabel):
    """
    Generic normalized (%-within-group) stacked bar chart, reusable for
    SM hours, study hours, distraction, focus, and sleep variables.
    """
    df_school = eda_data["df_school_model"]
    df_university = eda_data["df_university_model"]
    y_school = eda_data["y_school"]
    y_university = eda_data["y_university"]
    school_order = eda_data["school_target_order"]
    university_order = eda_data["university_target_order"]
    col = eda_data["column_names"][col_key]
    order = eda_data["orderings"][order_key]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    school_pct = pd.crosstab(df_school[col], y_school, normalize="index") * 100
    school_pct = school_pct.reindex(index=order, columns=school_order)
    school_pct.plot(kind="bar", stacked=True, ax=axes[0], colormap="RdYlGn", legend=False)
    axes[0].set_title(title_school)
    axes[0].set_xlabel(xlabel)
    axes[0].set_ylabel("Percentage")
    axes[0].tick_params(axis='x', rotation=45)

    university_pct = pd.crosstab(df_university[col], y_university, normalize="index") * 100
    university_pct = university_pct.reindex(index=order, columns=university_order)
    university_pct.plot(kind="bar", stacked=True, ax=axes[1], colormap="RdYlGn", legend=False)
    axes[1].set_title(title_university)
    axes[1].set_xlabel(xlabel)
    axes[1].set_ylabel("Percentage")
    axes[1].tick_params(axis='x', rotation=45)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title="GPA/CGPA Range", bbox_to_anchor=(1.05, 0.5), loc='center left')

    plt.tight_layout()
    return fig


def get_percentile_comparisons(raw_input: dict, eda_data: dict, model_type: str):
    """
    For each of a few key ordinal variables, compute what percentile the
    user's own answer falls at relative to the real survey respondents in
    their cohort. Returns a list of (label, user_answer, percentile, higher_is_worse).
    """
    df_model = eda_data["df_school_model"] if model_type == "school" else eda_data["df_university_model"]
    col = eda_data["column_names"]
    orderings = eda_data["orderings"]

    compare_specs = [
        ("Daily Social Media Usage", "sm_hours_col", "sm_hours_order", True),
        ("Daily Study Hours", "study_hours_col", "study_hours_order", False),
        ("Notification Distraction", "notif_col", "likert_order", True),
        ("Loss of Focus", "focus_col", "likert_order", True),
    ]

    results = []
    for label, col_key, order_key, higher_is_worse in compare_specs:
        col_text = col[col_key]
        order = orderings[order_key]
        rank_map = {cat: rank for rank, cat in enumerate(order)}

        user_answer = raw_input.get(col_text)
        if user_answer not in rank_map:
            continue
        user_rank = rank_map[user_answer]

        cohort_ranks = df_model[col_text].map(rank_map).dropna()
        percentile = (cohort_ranks <= user_rank).mean() * 100

        results.append({
            "label": label,
            "user_answer": user_answer,
            "percentile": round(percentile),
            "higher_is_worse": higher_is_worse,
        })

    return results