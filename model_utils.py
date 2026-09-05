# model_utils.py

import io
import matplotlib.pyplot as plt
import pickle
import pandas as pd
import numpy as np

ARTIFACTS_PATH = "final_model_artifacts.pkl"


def load_artifacts():
    """Load trained models and all encoding metadata."""
    with open(ARTIFACTS_PATH, "rb") as f:
        artifacts = pickle.load(f)
    return artifacts


def encode_single_input(raw_input: dict, artifacts: dict, model_type: str):
    """
    Convert a single user's raw survey answers (as a dict of
    column_name -> answer_string) into an encoded row matching
    the model's expected input format.

    model_type: "school" or "university" — determines which
    one-hot column set to align to.
    """
    ordinal_mappings = artifacts["ordinal_mappings"]
    binary_mappings = artifacts["binary_mappings"]
    nominal_features = artifacts["nominal_features"]

    df = pd.DataFrame([raw_input])

    # Ordinal encoding
    for col, order in ordinal_mappings.items():
        mapping = {category: rank for rank, category in enumerate(order)}
        df[col] = df[col].map(mapping)

    # Binary encoding
    for col, mapping in binary_mappings.items():
        df[col] = df[col].map(mapping)

    # One-hot encoding
    df = pd.get_dummies(df, columns=nominal_features)

    # Align columns exactly to what the model was trained on
    expected_columns = (
        artifacts["X_school_columns"] if model_type == "school"
        else artifacts["X_university_columns"]
    )
    df = df.reindex(columns=expected_columns, fill_value=0)

    return df


def predict(raw_input: dict, artifacts: dict, model_type: str):
    """Run the appropriate model and return predicted band + confidence breakdown."""
    model = artifacts["model_school"] if model_type == "school" else artifacts["model_university"]
    target_order = (
        artifacts["school_target_order"] if model_type == "school"
        else artifacts["university_target_order"]
    )

    X_encoded = encode_single_input(raw_input, artifacts, model_type)
    probs = model.predict_proba(X_encoded)[0]
    predicted_band = target_order[np.argmax(probs)]

    confidence_breakdown = dict(zip(target_order, probs))
    return predicted_band, confidence_breakdown

    

def load_feature_importance(path="feature_importance_data.pkl"):
    """Load saved feature importance rankings."""
    with open(path, "rb") as f:
        return pickle.load(f)


# Each entry: semantic_key -> (rule_type, tip_text)
# rule_type: "ordinal_high" (risky = one of the 2 most severe options),
#            "ordinal_low" (risky = one of the 2 least-favorable options, e.g. very low study hours),
#            "binary_yes" (risky = answered "Yes")
# Each entry: semantic_key -> (rule_type, icon, tip_text)
RECOMMENDATION_RULES = {
    "sm_hours_col": ("ordinal_high", "📱", "Your daily social-media usage is on the higher end. Usage hours was the strongest single predictor of academic performance in this study — even a modest reduction may help."),
    "study_hours_col": ("ordinal_low", "📚", "Increasing your daily dedicated study time was one of the most consistent factors linked to higher performance bands."),
    "during_study_col": ("ordinal_high", "🚫", "Using social media during study sessions was linked to lower performance bands. Try keeping your phone in another room during focused study blocks."),
    "notif_col": ("ordinal_high", "🔔", "Frequent notification distraction while studying was associated with lower performance — consider silencing notifications during study time."),
    "focus_col": ("ordinal_high", "🎯", "Frequently losing focus due to social media while studying was one of the stronger predictors of lower performance bands."),
    "sleep_effect_col": ("ordinal_high", "😴", "Social media affecting your sleep time was linked to lower performance — protecting sleep, especially before exams, may help."),
    "stopping_col": ("ordinal_high", "⏱️", "Finding it difficult to stop using social media once started was associated with lower performance bands. Consider setting app time-limits."),
    "comparison_col": ("ordinal_high", "🪞", "Frequently comparing your life to others on social media was associated with lower performance bands."),
    "checking_col": ("ordinal_high", "🔄", "Checking social media very frequently throughout the day was associated with lower performance."),
    "assignment_col": ("binary_yes", "📝", "Missing assignment deadlines due to social media use was associated with lower performance — consider an app-blocker during deadline periods."),
    "before_sleep_col": ("binary_yes", "🌙", "Using social media right before sleep was associated with lower performance bands."),
    "tired_col": ("binary_yes", "☕", "Feeling tired in class due to late-night usage was associated with lower performance."),
    "anxiety_col": ("ordinal_high", "😟", "Feeling anxious or stressed after social media use was reported more by students in lower performance bands."),
    "accounts_col": ("ordinal_high", "🗂️", "Managing many active social-media accounts can add to daily distraction — consider consolidating to fewer platforms."),
}


def get_recommendations(raw_input: dict, artifacts: dict, fi_data: dict, model_type: str, top_n: int = 5):
    """Score every rule by (importance x how risky the user's answer is),
    and return the top_n highest-scoring tips — graded, not just binary,
    so we reliably surface enough tips even when no answer is at the extreme."""
    importance_series = (
        fi_data["university_rf_importances"] if model_type == "university"
        else fi_data["school_logreg_importances"]
    )
    ordinal_mappings = artifacts["ordinal_mappings"]
    col = artifacts["column_names"]

    scored = []
    for key, (kind, icon, tip) in RECOMMENDATION_RULES.items():
        col_text = col.get(key)
        if col_text is None or col_text not in importance_series.index:
            continue

        importance_score = importance_series[col_text]
        user_val = raw_input.get(col_text)
        risk_fraction = 0.0

        if kind in ("ordinal_high", "ordinal_low"):
            order = ordinal_mappings.get(col_text)
            if order and user_val in order:
                rank = order.index(user_val)
                n = len(order) - 1
                risk_fraction = (rank / n) if kind == "ordinal_high" else (1 - rank / n)
        elif kind == "binary_yes":
            risk_fraction = 1.0 if user_val == "Yes" else 0.0

        if risk_fraction > 0:
            scored.append((importance_score * risk_fraction, icon, tip))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [(icon, tip) for _, icon, tip in scored[:top_n]]



def generate_result_image(predicted_band, confidence_series, title, color):
    """Build a single shareable summary image: predicted band + confidence bars."""
    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor("white")

    bars_color = [color if band == predicted_band else "#E5E7EB" for band in confidence_series.index]
    ax.bar(confidence_series.index, confidence_series.values, color=bars_color)
    ax.set_ylabel("Confidence")
    ax.tick_params(axis='x', rotation=45)

    fig.suptitle(f"{title}: {predicted_band}", fontsize=15, fontweight="bold", y=1.02)
    fig.text(0.5, -0.02, "Generated by the Social Media & Academic Performance tool — statistical estimate, not a guarantee.",
              ha="center", fontsize=8, color="#6B7280")

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf