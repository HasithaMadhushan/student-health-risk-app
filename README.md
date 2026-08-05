# Student Health Risk Prediction App

This project is a Streamlit application developed for the CIS6005
Computational Intelligence module. It uses a trained CatBoost classification
model to place one set of health and lifestyle inputs into one of three
competition categories:

- `fit`
- `at-risk`
- `unhealthy`

The deployed application is available at
[studenthealthrisk.streamlit.app](https://studenthealthrisk.streamlit.app/).

## Features

- A two-step form for entering 12 health and lifestyle values
- Support for unknown or missing values
- A review section before generating a prediction
- A predicted category with optional model confidence scores
- A reset option for starting a new prediction
- Local validation of inputs before they are sent to the model

The application does not ask for names, email addresses, student numbers or
other contact details. Entered values are held temporarily in Streamlit session
state and are not saved by this project.

## Technologies used

- Python
- Streamlit for the user interface
- CatBoost for classification
- pandas and NumPy for preparing model inputs
- pytest and Streamlit AppTest for automated tests

## Installation

Python 3.11 or a compatible Python 3 version is recommended. From the project
folder, create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
```

Run the tests with:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
```

Start the application with:

```powershell
& '.\.venv\Scripts\streamlit.exe' run app\streamlit_app.py
```

Streamlit will normally open the application at `http://localhost:8501`.

## How prediction works

1. The application loads the saved feature schema and CatBoost model.
2. The model file is checked against the expected SHA-256 hash.
3. The user completes the two input steps and can review the entered values.
4. The inputs are validated and arranged in the same feature order used by the
   model.
5. CatBoost generates a category and confidence scores.
6. Streamlit displays the result to the user.

The model uses 12 features. The `id` and `gender` columns are not used for
prediction. Numeric missing values are passed as `NaN`, while missing
categorical values use the token expected by the saved model schema.

## Project structure

```text
app/streamlit_app.py   Streamlit interface and navigation
app/presentation.py    Input groups and display labels
app/theme.py           Application styling
src/config.py          Model and schema paths
src/schema.py          Schema loading and checks
src/validation.py      Input validation and DataFrame creation
src/inference.py       Model loading and prediction
tests/                 Automated tests
artifacts/private/     Saved model, schemas and training metadata
```

## Limitations

The model was trained for a Kaggle competition dataset, so its categories and
confidence scores should be interpreted in that context. The confidence scores
are model outputs and are not calibrated medical probabilities. This
application is an educational demonstration and does not provide a medical
diagnosis or replace advice from a qualified healthcare professional.
