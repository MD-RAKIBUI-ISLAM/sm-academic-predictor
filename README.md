
## Setup & Running Locally

1. Clone or download this folder.
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
4. Run the app:
```bash
   streamlit run app.py
```
5. Open the local URL shown in the terminal (typically `http://localhost:8501`).

## Modeling Summary

Two separate models were built, since School/College (GPA out of 5) and
University (CGPA out of 4) use different grading scales:

| Dataset | Final Model | Accuracy | F1 (macro) | Mean Ordinal Distance |
|---|---|---|---|---|
| School/College | Logistic Regression (tuned) | 0.333 | 0.300 | 1.091 |
| University | Random Forest (tuned) | 0.454 | 0.396 | 0.714 |

Five algorithms (Logistic Regression, Decision Tree, Random Forest, Gradient
Boosting, XGBoost) were compared for each dataset before final selection.
See the in-app **Model Performance** page for full comparison details.

## Known Limitations

- Small sample sizes, especially for School/College (165 records) and the
  "Below 2.5" performance band in both datasets, limit model reliability
  for minority classes.
- Data is self-reported survey data and may include response bias.
- A probability-weighted numeric GPA/CGPA estimate was tested and rejected
  after validation showed it performed no better than predicting the sample
  average — the app instead reports a predicted band with a confidence
  breakdown, to avoid misleading precision.
- Models were trained under scikit-learn 1.7.1 and are run under 1.9.0 in
  this deployed environment; predictions were manually spot-checked for
  consistency across this version difference.

## Disclaimer

This tool provides a statistical estimate for educational/research purposes
only and is not a diagnostic or predictive guarantee of individual academic
performance.