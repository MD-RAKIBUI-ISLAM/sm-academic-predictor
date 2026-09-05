# Social Media Usage & Academic Performance Predictor

A Streamlit web application exploring the relationship between social-media
usage habits and academic performance among School/College and University
students in Bangladesh, based on survey data collected via Google Forms.

Built as part of an undergraduate honors thesis project.

**Live app**: https://edupulse-thesis.streamlit.app/

## What This App Does

- Presents exploratory data analysis (EDA) on how social-media usage, study
  habits, distraction, and sleep relate to GPA/CGPA, including formal
  statistical significance testing of five research hypotheses
- Explains the modeling methodology (feature engineering, model comparison,
  hyperparameter tuning, evaluation, and feature importance analysis)
- Requires account signup/login before generating predictions, as a
  mitigation for verifying that predictions are being requested by genuine
  students (registered accounts get one free trial prediction before full
  verification is required)
- Lets a verified/trial user answer survey-style questions and receive a
  predicted GPA/CGPA performance band, a full confidence breakdown,
  personalized recommendations grounded in feature-importance findings,
  and a peer-comparison view against the original survey respondents
- Provides an admin panel for manually reviewing and verifying/rejecting
  registered accounts
- Shows the underlying model comparison results, feature importances, and
  known limitations

## Project Structure

sm_academic_predictor/
├── app.py # Homepage
├── pages/
│ ├── 0_🔑_Login.py # Signup / login
│ ├── 1_📊_EDA_Insights.py # Live-generated exploratory charts + hypothesis testing
│ ├── 2_🧪_Methodology.py # Summary of the modeling approach
│ ├── 3_🎓_Predict_School.py # Prediction form — School/College model (login required)
│ ├── 4_🏫_Predict_University.py # Prediction form — University model (login required)
│ ├── 5_📈_Model_Performance.py # Model comparison table, feature importance, limitations
│ └── 9_🛡️_Admin.py # Password-protected account verification panel
├── auth_utils.py # Signup/login/session/trial/verification logic
├── model_utils.py # Encoding, prediction, recommendations, result-image export
├── data_utils.py # EDA chart-generation logic, peer-comparison logic
├── style_utils.py # Shared CSS loader
├── navbar_utils.py # Custom top navigation bar
├── final_model_artifacts.pkl # Trained models + encoding metadata
├── eda_data.pkl # Raw survey data for live EDA charts
├── feature_importance_data.pkl # Saved feature importance rankings
├── users.db # SQLite database of registered accounts (not committed to git)
├── requirements.txt
├── .streamlit/
│ ├── config.toml # Theme configuration
│ └── secrets.toml # Admin password (not committed to git)
└── README.md


## Setup & Running Locally

1. Clone this repository.
2. Create and activate a virtual environment:
```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
```
3. Install dependencies:
```bash
   python -m pip install -r requirements.txt
```
4. Create `.streamlit/secrets.toml` with:
```toml
   admin_password = "your-chosen-password"
```
5. Run the app:
```bash
   streamlit run app.py
```
6. Open the local URL shown in the terminal (typically `http://localhost:8501`).

## Deployment

This app is deployed on Streamlit Community Cloud. To deploy your own copy:
1. Push this repository to GitHub (ensure `.gitignore` excludes `venv/`,
   `.streamlit/secrets.toml`, and `users.db`).
2. Create a new app at [share.streamlit.io](https://share.streamlit.io),
   pointing to `app.py`.
3. Add `admin_password` under the app's Settings → Secrets.

**Note**: on Streamlit Community Cloud's free tier, the SQLite user database
(`users.db`) does not persist across app restarts/redeploys. This is
acceptable for demonstration purposes but is documented as a known
limitation for any production use.

## Account & Verification System

Since the original survey was anonymous, there was no way to confirm
respondents were genuine students. The deployed prediction tool addresses
this going forward by requiring account registration (name, institutional
email, registration number) before repeated use:

- New accounts start as **Pending** and receive **one free trial**
  prediction.
- An administrator reviews accounts via the password-protected Admin page
  and marks them **Verified** (unlimited access) or **Rejected** (account
  disabled, logged out).
- This account data is stored separately from, and not linked to, the
  original anonymous survey dataset used for training.

## Modeling Summary

Two separate models were built, since School/College (GPA out of 5) and
University (CGPA out of 4) use different grading scales:

| Dataset | Final Model | Accuracy | F1 (macro) | Mean Ordinal Distance |
|---|---|---|---|---|
| School/College | Logistic Regression (tuned) | 0.333 | 0.300 | 1.091 |
| University | Random Forest (tuned) | 0.454 | 0.396 | 0.714 |

Five algorithms (Logistic Regression, Decision Tree, Random Forest, Gradient
Boosting, XGBoost) were compared for each dataset, alongside a dummy
most-frequent-class baseline, before final selection. All five research
hypotheses (H1–H5) were statistically supported via Spearman rank
correlation (p < 0.05) in both cohorts. See the in-app **EDA Insights** and
**Model Performance** pages for full details.

## Known Limitations

- Small sample sizes, especially for School/College (165 records) and the
  "Below 2.5" performance band in both datasets, limit model reliability
  for minority classes.
- Data is self-reported survey data and may include response bias.
- The original survey could not verify respondent identity; response
  integrity was assessed retrospectively via duplicate/consistency checks
  and a repeated cross-validation sensitivity analysis (see thesis Chapter
  3 for details).
- A probability-weighted numeric GPA/CGPA estimate was tested and rejected
  after validation showed it performed no better than predicting the sample
  average — the app instead reports a predicted band with a confidence
  breakdown, to avoid misleading precision.
- The account-verification system is currently self-attested at signup;
  institutional cross-checking depends on future access to official student
  records.

## Disclaimer

This tool provides a statistical estimate for educational/research purposes
only and is not a diagnostic or predictive guarantee of individual academic
performance.