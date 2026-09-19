import io
import hashlib
import hmac
import json
import os
import random
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client

APP_TIMEZONE = ZoneInfo("Asia/Kolkata")

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="B.Tech ML Coding Portal", layout="wide", page_icon="⚡"
)

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].removesuffix("/rest/v1/").rstrip("/")
    SUPABASE_SERVICE_ROLE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
except Exception:
    SUPABASE_URL = ""
    SUPABASE_SERVICE_ROLE_KEY = "local-development-key"
    supabase = None
APP_STATE_ID = "main"
AUTH_SIGNING_KEY = SUPABASE_SERVICE_ROLE_KEY.encode("utf-8")
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")

def _auth_token(username):
    signature = hmac.new(AUTH_SIGNING_KEY, username.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{username}:{signature}"

def _restore_authenticated_user(users):
    token = st.query_params.get("auth")
    if not token or ":" not in token:
        return None
    username, signature = token.rsplit(":", 1)
    if username in users and hmac.compare_digest(signature, _auth_token(username).rsplit(":", 1)[1]):
        return username
    return None

# ==========================================
# 1. DATABASE SAVE & LOAD HELPERS
# ==========================================
DEFAULT_QUESTIONS = {
    # --- LEVEL 1: BASIC PYTHON ---
    "Q01. Print a Welcome Message": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Write a Python program to print:\n`Welcome to Machine Learning`",
        "inputs": [""],
        "expected_outputs": ["Welcome to Machine Learning"],
        "starter_code": "# Print welcome message\n",
    },
    "Q02. Add Two Numbers": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Write a program to input two numbers (one per line) and print their sum.",
        "inputs": ["10\n20", "5\n15"],
        "expected_outputs": ["30", "20"],
        "starter_code": "num1 = int(input())\nnum2 = int(input())\n# Print their sum\n",
    },
    "Q03. Find the Larger Number": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Input two numbers (one per line) and print the larger one.",
        "inputs": ["15\n28", "100\n45"],
        "expected_outputs": ["28", "100"],
        "starter_code": "a = int(input())\nb = int(input())\n# Write logic here\n",
    },
    "Q04. Even or Odd": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Input a number and determine whether it is `Even` or `Odd`.",
        "inputs": ["18", "7"],
        "expected_outputs": ["Even", "Odd"],
        "starter_code": "num = int(input())\n# Print Even or Odd\n",
    },
    "Q05. Positive, Negative or Zero": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Input a number and print `Positive`, `Negative`, or `Zero`.",
        "inputs": ["10", "-5", "0"],
        "expected_outputs": ["Positive", "Negative", "Zero"],
        "starter_code": "num = int(input())\n# Print Positive, Negative, or Zero\n",
    },
    "Q06. Calculate Average": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Input marks of 5 students (one per line) and calculate the average. Print in format: `Average = 80`.",
        "inputs": ["80\n70\n90\n60\n100"],
        "expected_outputs": ["Average = 80"],
        "starter_code": "# Read 5 numbers and compute average\n",
    },
    "Q07. Celsius to Fahrenheit": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Convert Celsius to Fahrenheit using formula: F = (C * 9/5) + 32. Print result.",
        "inputs": ["25", "0"],
        "expected_outputs": ["77", "32"],
        "starter_code": "celsius = float(input())\n# Calculate fahrenheit and print\n",
    },
    "Q08. Square of a Number": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Input a number and print its square.",
        "inputs": ["9", "4"],
        "expected_outputs": ["81", "16"],
        "starter_code": "num = int(input())\n# Print square\n",
    },
    "Q09. Swap Two Numbers": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Input two numbers (one per line) and swap them without using a third variable. Print each number on a new line.",
        "inputs": ["10\n20"],
        "expected_outputs": ["20\n10"],
        "starter_code": "a = int(input())\nb = int(input())\n# Swap without third variable\n",
    },
    "Q10. Area of Rectangle": {
        "topic": "Level 1 - Basic Python",
        "points": 10,
        "description": "Input Length and Width (one per line). Print Area (Length * Width).",
        "inputs": ["10\n5"],
        "expected_outputs": ["50"],
        "starter_code": "length = int(input())\nwidth = int(input())\n# Compute area\n",
    },
    # --- LEVEL 2: DECISION MAKING & LOOPS ---
    "Q11. Grade Calculator": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input marks and print grade:\n- 90-100 -> A\n- 80-89 -> B\n- 70-79 -> C\n- Below 70 -> Fail",
        "inputs": ["95", "82", "75", "60"],
        "expected_outputs": ["A", "B", "C", "Fail"],
        "starter_code": "marks = int(input())\n# Print grade\n",
    },
    "Q12. Print Numbers 1 to 20": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Print numbers from 1 to 20, each on a new line.",
        "inputs": [""],
        "expected_outputs": ["\n".join(str(i) for i in range(1, 21))],
        "starter_code": "# Print 1 to 20 using loop\n",
    },
    "Q13. Print Even Numbers": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Print all even numbers between 1 and 100 inclusive, each on a new line.",
        "inputs": [""],
        "expected_outputs": ["\n".join(str(i) for i in range(2, 101, 2))],
        "starter_code": "# Print even numbers from 2 to 100\n",
    },
    "Q14. Multiplication Table": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input N and print its multiplication table from 1 to 10 in format: `N x 1 = Result`",
        "inputs": ["7"],
        "expected_outputs": ["\n".join(f"7 x {i} = {7*i}" for i in range(1, 11))],
        "starter_code": "n = int(input())\n# Print multiplication table\n",
    },
    "Q15. Sum of First N Numbers": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input N and print the sum of first N natural numbers.",
        "inputs": ["5", "10"],
        "expected_outputs": ["15", "55"],
        "starter_code": "n = int(input())\n# Compute sum\n",
    },
    "Q16. Factorial": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input a number and print its factorial.",
        "inputs": ["5", "4"],
        "expected_outputs": ["120", "24"],
        "starter_code": "n = int(input())\n# Compute factorial\n",
    },
    "Q17. Reverse a Number": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input an integer and print its digits in reverse.",
        "inputs": ["1234", "987"],
        "expected_outputs": ["4321", "789"],
        "starter_code": "num = input()\n# Print reverse\n",
    },
    "Q18. Count Digits": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input a number and print total number of digits.",
        "inputs": ["987654", "100"],
        "expected_outputs": ["6", "3"],
        "starter_code": "num = input()\n# Print digit count\n",
    },
    "Q19. Largest of Three Numbers": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input three numbers (one per line) and print the largest one.",
        "inputs": ["10\n50\n20"],
        "expected_outputs": ["50"],
        "starter_code": "a = int(input())\nb = int(input())\nc = int(input())\n# Find largest\n",
    },
    "Q20. Simple Calculator": {
        "topic": "Level 2 - Decision Making & Loops",
        "points": 10,
        "description": "Input choice (1: Add, 2: Subtract, 3: Multiply, 4: Divide) followed by two numbers on new lines. Print calculated result.",
        "inputs": ["1\n10\n20", "3\n5\n4"],
        "expected_outputs": ["30", "20"],
        "starter_code": "choice = int(input())\na = int(input())\nb = int(input())\n# Calculate\n",
    },
    # --- LEVEL 3: LISTS (ML DATA) ---
    "Q21. Find Maximum Value": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given input space-separated integers representing a dataset, find and print maximum value.",
        "inputs": ["25 18 45 67 34"],
        "expected_outputs": ["67"],
        "starter_code": "data = list(map(int, input().split()))\n# Print max\n",
    },
    "Q22. Find Minimum Value": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given input space-separated integers, find and print minimum value.",
        "inputs": ["25 18 45 67 34"],
        "expected_outputs": ["18"],
        "starter_code": "data = list(map(int, input().split()))\n# Print min\n",
    },
    "Q23. Calculate Average of Dataset": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given input space-separated integers, print average.",
        "inputs": ["70 80 90 100 60"],
        "expected_outputs": ["80"],
        "starter_code": "data = list(map(int, input().split()))\n# Compute average\n",
    },
    "Q24. Count Positive Numbers": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given input space-separated numbers, count and print how many are positive (> 0).",
        "inputs": ["-5 8 10 -1 20"],
        "expected_outputs": ["3"],
        "starter_code": "data = list(map(int, input().split()))\n# Count positive\n",
    },
    "Q25. Find Sum of Dataset": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given space-separated integers, compute and print total sum.",
        "inputs": ["5 10 20 30"],
        "expected_outputs": ["65"],
        "starter_code": "data = list(map(int, input().split()))\n# Compute sum\n",
    },
    "Q26. Remove Duplicate Values": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given space-separated integers, remove duplicates preserving order and print as list.",
        "inputs": ["10 20 10 30 20"],
        "expected_outputs": ["[10, 20, 30]"],
        "starter_code": "data = list(map(int, input().split()))\n# Print unique list\n",
    },
    "Q27. Sort Dataset": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given space-separated integers, sort ascending and print list.",
        "inputs": ["45 12 67 5 30"],
        "expected_outputs": ["[5, 12, 30, 45, 67]"],
        "starter_code": "data = list(map(int, input().split()))\n# Sort and print list\n",
    },
    "Q28. Count Occurrences": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Read dataset on line 1, and target on line 2. Print count of target.",
        "inputs": ["1 2 3 2 2 4\n2"],
        "expected_outputs": ["3"],
        "starter_code": "data = list(map(int, input().split()))\ntarget = int(input())\n# Print count\n",
    },
    "Q29. Find Second Largest Number": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given space-separated integers, print second largest number.",
        "inputs": ["12 45 78 25 90"],
        "expected_outputs": ["78"],
        "starter_code": "data = list(map(int, input().split()))\n# Print second largest\n",
    },
    "Q30. Find Average Age of Students": {
        "topic": "Level 3 - Lists (ML Data)",
        "points": 15,
        "description": "Given space-separated ages, print average age.",
        "inputs": ["18 19 20 21 22"],
        "expected_outputs": ["20"],
        "starter_code": "ages = list(map(int, input().split()))\n# Compute average\n",
    },
    # --- BONUS ML-ORIENTED ---
    "Q31. Count Labeled Data": {
        "topic": "Bonus ML-Oriented",
        "points": 20,
        "description": "Given space-separated label strings (e.g. `Cat Dog Dog Cat Cat`), count and print Cat and Dog counts in format:\n`Cat: 3\nDog: 2`",
        "inputs": ["Cat Dog Dog Cat Cat"],
        "expected_outputs": ["Cat: 3\nDog: 2"],
        "starter_code": "labels = input().split()\n# Count labels\n",
    },
    "Q32. Classification Based on Marks": {
        "topic": "Bonus ML-Oriented",
        "points": 20,
        "description": "Given space-separated marks, classify each as `'Pass'` (>= 50) or `'Fail'` (< 50). Print resulting list.",
        "inputs": ["45 60 80 30"],
        "expected_outputs": ["['Fail', 'Pass', 'Pass', 'Fail']"],
        "starter_code": "marks = list(map(int, input().split()))\n# Classify marks and print list\n",
    },
    "Q33. Calculate Mean": {
        "topic": "Bonus ML-Oriented",
        "points": 20,
        "description": "Given space-separated numbers, compute and print mean.",
        "inputs": ["10 15 20 25 30"],
        "expected_outputs": ["20"],
        "starter_code": "data = list(map(int, input().split()))\n# Compute mean\n",
    },
    "Q34. Calculate Absolute Error": {
        "topic": "Bonus ML-Oriented",
        "points": 20,
        "description": "Given actual values on line 1 and predicted on line 2 (space-separated), compute |actual - predicted| for each pair and print list.",
        "inputs": ["100 120 90\n110 118 95"],
        "expected_outputs": ["[10, 2, 5]"],
        "starter_code": "actual = list(map(int, input().split()))\npredicted = list(map(int, input().split()))\n# Calculate absolute error\n",
    },
    "Q35. Find Mean Squared Error (Basic)": {
        "topic": "Bonus ML-Oriented",
        "points": 20,
        "description": "Given actual on line 1 and predicted on line 2, compute MSE = (1/N) * sum((actual - predicted)^2). Print as float.",
        "inputs": ["100 120 90\n110 118 95"],
        "expected_outputs": ["43.0"],
        "starter_code": "actual = list(map(int, input().split()))\npredicted = list(map(int, input().split()))\n# Compute MSE\n",
    },
    "Q36. Complete Machine Learning Workflow (Linear Regression)": {
        "topic": "Bonus ML-Oriented",
        "points": 50,
        "description": "Read the number of training samples N. The next N lines contain two integers: House_Size and House_Price. Read one test house size. Train a simple Linear Regression model using the training data, predict the price for the given test house, and print the predicted price (rounded to 2 decimal places) followed by the Mean Squared Error (MSE) of the model on the training data.",
        "inputs": [
            "5\n1000 200000\n1200 240000\n1500 300000\n1800 360000\n2000 400000\n1600"
        ],
        "expected_outputs": [
            "Predicted Price: 320000.00\nMSE: 0.00"
        ],
        "starter_code": "from sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import mean_squared_error\n\nn = int(input())\nX = []\ny = []\n\nfor _ in range(n):\n    size, price = map(int, input().split())\n    X.append([size])\n    y.append(price)\n\n# Read test house size\ntest_size = int(input())\n\n# Train the model\n\n# Predict the price\n\n# Predict on training data\n\n# Calculate MSE\n\n# Print predicted price and MSE\n"
},
}

QUIZ_QUESTIONS = [
    {
        "question": "Which Python library is primarily used for Data Manipulation?",
        "options": ["Pandas", "PyGame", "Flask", "OpenCV"],
        "answer": "Pandas",
        "explanation": "Pandas provides DataFrames and Series for working with structured data."
    },
    {
        "question": "What is the result of `len([1, 2, 3, 4])`?",
        "options": ["3", "4", "5", "0"],
        "answer": "4",
        "explanation": "The len() function returns the total number of items in a list."
    },
    {
        "question": "Which evaluation metric is used for regression models?",
        "options": ["Accuracy", "Mean Squared Error (MSE)", "Confusion Matrix", "F1 Score"],
        "answer": "Mean Squared Error (MSE)",
        "explanation": "MSE measures the average squared difference between estimated and actual values."
    },
    {
        "question": "What does `input()` function return in Python by default?",
        "options": ["Integer", "Float", "String", "Boolean"],
        "answer": "String",
        "explanation": "input() always reads input as a string type unless explicitly cast."
    },
    {
        "question": "Which operator is used for exponentiation (power) in Python?",
        "options": ["^", "**", "//", "%"],
        "answer": "**",
        "explanation": "** is used for raising a number to a power (e.g., 2**3 = 8)."
    },
  {
    "question": "Which Python library is mainly used for numerical computations?",
    "options": ["NumPy", "Flask", "Tkinter", "Requests"],
    "answer": "NumPy",
    "explanation": "NumPy provides fast array operations and mathematical functions for numerical computing."
  },
  {
    "question": "Which function is used to display output in Python?",
    "options": ["display()", "echo()", "print()", "show()"],
    "answer": "print()",
    "explanation": "The print() function displays output on the console."
  },
  {
    "question": "Which data structure stores key-value pairs in Python?",
    "options": ["List", "Tuple", "Dictionary", "Set"],
    "answer": "Dictionary",
    "explanation": "A dictionary stores data as key-value pairs."
  },
  {
    "question": "Which keyword is used to define a function in Python?",
    "options": ["func", "define", "def", "function"],
    "answer": "def",
    "explanation": "The 'def' keyword is used to create a function in Python."
  },
  {
    "question": "Which machine learning algorithm is commonly used for classification?",
    "options": ["Linear Regression", "Logistic Regression", "K-Means", "PCA"],
    "answer": "Logistic Regression",
    "explanation": "Logistic Regression is used to classify data into categories."
  },
  {
    "question": "What is the output of `5 // 2` in Python?",
    "options": ["2", "2.5", "3", "1"],
    "answer": "2",
    "explanation": "The // operator performs floor division and returns the integer quotient."
  },
  {
    "question": "Which library is commonly used for creating visualizations in Python?",
    "options": ["NumPy", "Pandas", "Matplotlib", "TensorFlow"],
    "answer": "Matplotlib",
    "explanation": "Matplotlib is widely used for plotting graphs and charts."
  },
  {
    "question": "Which of the following is a supervised learning algorithm?",
    "options": ["K-Means", "DBSCAN", "Linear Regression", "Apriori"],
    "answer": "Linear Regression",
    "explanation": "Linear Regression is a supervised learning algorithm used for prediction."
  },
  {
    "question": "Which function converts a string to an integer?",
    "options": ["str()", "float()", "int()", "bool()"],
    "answer": "int()",
    "explanation": "The int() function converts compatible values into integers."
  },
  {
    "question": "What is the correct extension for Python files?",
    "options": [".java", ".py", ".cpp", ".exe"],
    "answer": ".py",
    "explanation": "Python source code files use the .py extension."
  },
  {
    "question": "Which metric is commonly used to evaluate classification models?",
    "options": ["Accuracy", "Mean Absolute Error", "RMSE", "R-Squared"],
    "answer": "Accuracy",
    "explanation": "Accuracy measures the percentage of correct predictions."
  },
  {
    "question": "Which keyword is used for conditional statements in Python?",
    "options": ["switch", "if", "case", "loop"],
    "answer": "if",
    "explanation": "The 'if' keyword is used to make decisions based on conditions."
  },
  {
    "question": "Which function is used to read a CSV file using Pandas?",
    "options": ["pd.load_csv()", "pd.read_csv()", "pd.open_csv()", "pd.import_csv()"],
    "answer": "pd.read_csv()",
    "explanation": "pd.read_csv() reads data from CSV files into a DataFrame."
  },
  {
    "question": "What is the output of `type(3.14)`?",
    "options": ["int", "float", "str", "bool"],
    "answer": "float",
    "explanation": "3.14 is a floating-point number, so its type is float."
  },
  {
    "question": "Which algorithm is commonly used for clustering?",
    "options": ["Decision Tree", "K-Means", "Linear Regression", "Naive Bayes"],
    "answer": "K-Means",
    "explanation": "K-Means is one of the most popular clustering algorithms."
  },
  {
    "question": "Which symbol is used to write comments in Python?",
    "options": ["//", "#", "/*", "--"],
    "answer": "#",
    "explanation": "Single-line comments in Python begin with the # symbol."
  },
  {
    "question": "Which function returns the largest value in a list?",
    "options": ["largest()", "high()", "max()", "top()"],
    "answer": "max()",
    "explanation": "The max() function returns the maximum value from an iterable."
  },
  {
    "question": "Which library is widely used for building deep learning models?",
    "options": ["TensorFlow", "BeautifulSoup", "OpenCV", "PyGame"],
    "answer": "TensorFlow",
    "explanation": "TensorFlow is a popular framework for deep learning and neural networks."
  },
  {
    "question": "What is the output of `bool(0)`?",
    "options": ["True", "False", "0", "None"],
    "answer": "False",
    "explanation": "In Python, the integer value 0 evaluates to False."
  },
  {
    "question": "Which evaluation metric is commonly used for clustering?",
    "options": ["Silhouette Score", "Accuracy", "Precision", "Recall"],
    "answer": "Silhouette Score",
    "explanation": "The Silhouette Score measures how well data points fit within their assigned clusters."
  }
]

DEFAULT_USERS = {
    "Reena_Samuel": {
        "password": "Jenisam@7200.",
        "role": "Industrial Trainer",
        "name": "Trainer",
        "email": "jenisam98896@gamil.com",
    }
}
ADMIN_ROLES = {"Professor", "Industrial Trainer"}
UNIT_NAMES = ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"]


def _mapping_or_default(value, default):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            return parsed
    return default

def _list_or_default(value, default):
    return value if isinstance(value, list) else default

def _question_unit(question, index):
    return question.get("unit") or UNIT_NAMES[index % len(UNIT_NAMES)]

def _student_question_unit(title, question):
    if title in DEFAULT_QUESTIONS:
        return "Unit 1"
    return question.get("unit", "Unit 1")

def _quiz_question_unit(question):
    return question.get("unit", "Unit 1")

def load_db():
    if supabase is None:
        try:
            with open(LOCAL_DB_PATH, "r", encoding="utf-8") as db_file:
                data = json.load(db_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
    else:
        response = (
            supabase.table("app_state")
            .select("data")
            .eq("id", APP_STATE_ID)
            .execute()
        )
        data = _mapping_or_default(response.data[0].get("data"), {}) if response.data else {}

    if not data:
        data = {
            "users": DEFAULT_USERS,
            "student_scores": {},
            "questions": DEFAULT_QUESTIONS,
        }
        save_db_data(data)

    data["users"] = _mapping_or_default(data.get("users"), DEFAULT_USERS)
    data["student_scores"] = _mapping_or_default(data.get("student_scores"), {})
    data["questions"] = _mapping_or_default(data.get("questions"), DEFAULT_QUESTIONS)
    data["quiz_attempts"] = _mapping_or_default(data.get("quiz_attempts"), {})
    data["quiz_completed"] = _mapping_or_default(data.get("quiz_completed"), {})
    data["quiz_completion_times"] = _mapping_or_default(data.get("quiz_completion_times"), {})
    data["quiz_progress"] = _mapping_or_default(data.get("quiz_progress"), {})
    data["assignments"] = _mapping_or_default(data.get("assignments"), {})
    data["quiz_questions"] = _list_or_default(data.get("quiz_questions"), QUIZ_QUESTIONS.copy())

    # Keep code-defined default accounts up to date in the persisted state.
    defaults_changed = False
    for username, default_details in DEFAULT_USERS.items():
        if username in data["users"]:
            updated_details = {**data["users"][username], **default_details}
            if updated_details != data["users"][username]:
                data["users"][username] = updated_details
                defaults_changed = True

    if defaults_changed:
        save_db_data(data)

    for username in data["users"]:
        data["student_scores"].setdefault(username, {})

    units_changed = False
    for index, question in enumerate(data["questions"].values()):
        if "unit" not in question:
            question["unit"] = _question_unit(question, index)
            units_changed = True
    if units_changed:
        save_db_data(data)

    return data

def save_db_data(data):
    if supabase is None:
        with open(LOCAL_DB_PATH, "w", encoding="utf-8") as db_file:
            json.dump(data, db_file, indent=2)
        return
    supabase.table("app_state").upsert(
        {"id": APP_STATE_ID, "data": data}
    ).execute()

def sync_to_disk():
    db = {
        "users": st.session_state.users,
        "student_scores": st.session_state.student_scores,
        "questions": st.session_state.questions,
        "quiz_attempts": st.session_state.get("quiz_attempts", {}),
        "quiz_completed": st.session_state.get("quiz_completed", {}),
        "quiz_completion_times": st.session_state.get("quiz_completion_times", {}),
        "quiz_progress": st.session_state.get("quiz_progress", {}),
        "assignments": st.session_state.get("assignments", {}),
        "quiz_questions": st.session_state.get("quiz_questions", QUIZ_QUESTIONS),
    }
    save_db_data(db)


def render_student_management_panel():
    st.subheader("👥 Student Account Management")

    students = [u for u, data in st.session_state.users.items() if data.get("role") == "Student"]

    if not students:
        st.info("No student accounts are registered yet.")
        return

    selected_student = st.selectbox("Select student to manage:", students, key="student_manage_select")
    student_data = st.session_state.users[selected_student]

    st.markdown("##### 📝 Edit Student Profile")
    with st.form(f"student_edit_form_{selected_student}"):
        new_name = st.text_input("Student Name", value=student_data.get("name", ""))
        new_email = st.text_input("Email", value=student_data.get("email", ""))
        new_student_id = st.text_input("Student ID", value=student_data.get("student_id", ""))
        new_password = st.text_input("Password", type="password", value=student_data.get("password", ""))
        reset_scores = st.checkbox("Reset all scores and attempts for this student", value=False)

        submitted = st.form_submit_button("💾 Save Student Changes")
        if submitted:
            st.session_state.users[selected_student]["name"] = new_name.strip() or student_data.get("name", "")
            st.session_state.users[selected_student]["email"] = new_email.strip() or student_data.get("email", "")
            st.session_state.users[selected_student]["student_id"] = new_student_id.strip()
            st.session_state.users[selected_student]["password"] = new_password.strip() or student_data.get("password", "")

            if reset_scores:
                st.session_state.student_scores[selected_student] = {}

            sync_to_disk()
            st.success(f"Updated student record for {selected_student}.")

    st.markdown("---")
    st.markdown("##### 🧪 Modify Student Attempts")
    scores = st.session_state.student_scores.get(selected_student, {})

    if not scores:
        st.info(f"{student_data.get('name', selected_student)} has no saved attempts yet.")
    else:
        question_to_edit = st.selectbox(
            "Choose question attempt to modify:",
            list(scores.keys()),
            key=f"edit_score_question_{selected_student}",
        )
        current_result = scores.get(question_to_edit, {})

        with st.form(f"score_update_form_{selected_student}_{question_to_edit}"):
            status_options = ["Passed", "Failed", "Not Attempted"]
            current_status = current_result.get("status", "Failed")
            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status) if current_status in status_options else 1,
            )
            new_score = st.number_input(
                "Score",
                min_value=0,
                step=1,
                value=int(current_result.get("score", 0)),
            )

            if st.form_submit_button("Update Attempt"):
                st.session_state.student_scores[selected_student][question_to_edit] = {
                    "status": new_status,
                    "score": int(new_score),
                }
                sync_to_disk()
                st.success(f"Updated attempt for {question_to_edit}.")

    st.markdown("---")
    st.markdown("##### 🗑 Delete Student Record")
    confirm_delete = st.checkbox("I confirm I want to delete this student account", value=False, key=f"confirm_delete_{selected_student}")
    if st.button("Delete Student", key=f"delete_student_{selected_student}", type="secondary"):
        if confirm_delete:
            del st.session_state.users[selected_student]
            st.session_state.student_scores.pop(selected_student, None)
            sync_to_disk()
            st.warning(f"Deleted student account: {selected_student}")
            st.rerun()
        else:
            st.warning("Please confirm deletion before removing the student.")

# Initialize and refresh database-backed session state. Streamlit reruns the
# script for every interaction, so this keeps each session in sync with disk.
db_data = load_db()
st.session_state.users = db_data["users"]
st.session_state.student_scores = db_data["student_scores"]
st.session_state.questions = db_data["questions"]
st.session_state.quiz_attempts = _mapping_or_default(db_data.get("quiz_attempts"), {})
st.session_state.quiz_completed = _mapping_or_default(db_data.get("quiz_completed"), {})
st.session_state.quiz_completion_times = _mapping_or_default(db_data.get("quiz_completion_times"), {})
st.session_state.quiz_progress = _mapping_or_default(db_data.get("quiz_progress"), {})
st.session_state.assignments = _mapping_or_default(db_data.get("assignments"), {})
st.session_state.quiz_questions = _list_or_default(db_data.get("quiz_questions"), QUIZ_QUESTIONS.copy())

def _unit_score_for_student(username, unit_name):
    scores = st.session_state.student_scores.get(username, {})
    return sum(
        st.session_state.questions[title].get("points", 10)
        for title, attempt in scores.items()
        if attempt.get("status") == "Passed"
        and title in st.session_state.questions
        and _student_question_unit(title, st.session_state.questions[title]) == unit_name
    )

def _remove_duplicate_student_emails():
    students_by_email = {}
    for username, user_data in st.session_state.users.items():
        if user_data.get("role") != "Student":
            continue
        email = user_data.get("email", "").strip().casefold()
        if email:
            students_by_email.setdefault(email, []).append(username)

    removed_usernames = []
    for usernames in students_by_email.values():
        if len(usernames) < 2:
            continue
        keeper = max(
            usernames,
            key=lambda username: (
                _unit_score_for_student(username, "Unit 1"),
                len(st.session_state.student_scores.get(username, {})),
            ),
        )
        for username in usernames:
            if username == keeper:
                continue
            removed_usernames.append(username)
            del st.session_state.users[username]
            st.session_state.student_scores.pop(username, None)

    if removed_usernames:
        sync_to_disk()
    return removed_usernames

for username, user_data in st.session_state.users.items():
    user_data.setdefault("department", "")
    user_data.setdefault("student_id", "")

_remove_duplicate_student_emails()

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = _restore_authenticated_user(st.session_state.users)

# Game Quiz State Variables
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_streak" not in st.session_state:
    st.session_state.quiz_streak = 0

def restrict_clipboard(element_id):
        st.markdown(
                f"""
                <script>
                (() => {{
                    const install = () => {{
                        window.parent.document.querySelectorAll('textarea').forEach((area) => {{
                            if (area.dataset.clipboardRestricted) return;
                            area.dataset.clipboardRestricted = 'true';
                            ['copy', 'cut', 'paste', 'drop'].forEach((eventName) =>
                                area.addEventListener(eventName, (event) => event.preventDefault())
                            );
                        }});
                    }};
                    install();
                    new MutationObserver(install).observe(window.parent.document.body, {{childList: true, subtree: true}});
                }})();
                </script>
                """,
                unsafe_allow_html=True,
        )

# ==========================================
# 2. CODE EXECUTION & LEADERBOARD HELPERS
# ==========================================
def evaluate_script(user_code, test_inputs, expected_outputs):
    results = []
    for test_in, expected_out in zip(test_inputs, expected_outputs):
        sys.stdin = io.StringIO(test_in)
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            exec(user_code, {})
            actual_out = captured_output.getvalue().strip()
            if actual_out == str(expected_out).strip():
                results.append((True, test_in, expected_out, actual_out))
            else:
                results.append((False, test_in, expected_out, actual_out))
        except Exception:
            results.append((
                False,
                test_in,
                expected_out,
                f"Runtime Error: {traceback.format_exc()}",
            ))
        finally:
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stdout__
    return results


def assessment_download(title, description, content, filename):
    lines = (title + "\n\n" + description + "\n\nResponse:\n" + content).splitlines()[:55]
    stream_lines = ["BT", "/F1 10 Tf", "50 750 Td"]
    for line in lines:
        escaped = line[:105].replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_lines.append(f"({escaped}) Tj")
        stream_lines.append("0 -14 Td")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("latin-1", "replace")
    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n",
        b"4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
        f"5 0 obj<< /Length {len(stream)} >>stream\n".encode() + stream + b"\nendstream endobj\n",
    ]
    pdf = b"%PDF-1.4\n"; offsets = []
    for obj in objects:
        offsets.append(len(pdf)); pdf += obj
    xref = len(pdf); pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    pdf += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    pdf += f"trailer<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    st.download_button("🖨️ Download / Print PDF", pdf, filename.replace(".html", ".pdf"), "application/pdf")

def build_mcq_response_sheet(unit_name="All Units"):
    question_units = {
        question.get("question", ""): _quiz_question_unit(question)
        for question in st.session_state.quiz_questions
    }
    rows = []
    for username, attempts in st.session_state.get("quiz_attempts", {}).items():
        user_info = st.session_state.users.get(username, {})
        for attempt in attempts:
            question = attempt.get("question", "")
            unit = attempt.get("unit") or question_units.get(question, "Unit 1")
            if unit_name != "All Units" and unit != unit_name:
                continue
            rows.append({
                "Submitted At": _format_mcq_submission_time(attempt.get("answered_at", "")),
                "Student Name": user_info.get("name", username),
                "Student ID": user_info.get("student_id", ""),
                "Email": user_info.get("email", ""),
                "Username": username,
                "Unit": unit,
                "Question": question,
                "Selected Answer": attempt.get("selected_answer", ""),
                "Correct Answer": attempt.get("correct_answer", ""),
                "Correct": "Yes" if attempt.get("correct") else "No",
                "Points": attempt.get("points", 0),
            })
    return pd.DataFrame(rows)

def _mcq_completion_time(username, unit_name, attempts, question_count):
    saved_times = st.session_state.get("quiz_completion_times", {}).get(username, {})
    if isinstance(saved_times, dict):
        completion_time = saved_times.get(unit_name, "")
    else:
        completion_time = saved_times if unit_name == "Unit 1" else ""

    legacy_completion = st.session_state.get("quiz_completed", {}).get(username, "")
    if not completion_time and unit_name == "Unit 1" and isinstance(legacy_completion, str):
        completion_time = legacy_completion

    answered_questions = {
        attempt.get("question")
        for attempt in attempts
        if attempt.get("question") and (
            unit_name == "All Units" or attempt.get("unit", "Unit 1") == unit_name
        )
    }
    if not completion_time and question_count and len(answered_questions) >= question_count:
        answered_times = [
            attempt.get("answered_at", "")
            for attempt in attempts
            if attempt.get("answered_at") and (
                unit_name == "All Units" or attempt.get("unit", "Unit 1") == unit_name
            )
        ]
        completion_time = max(answered_times, default="")
    return completion_time

def _format_mcq_submission_time(timestamp):
    if not timestamp:
        return ""
    try:
        parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed_timestamp.tzinfo is None:
            parsed_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)
        return parsed_timestamp.astimezone(APP_TIMEZONE).strftime("%d/%m/%Y %H:%M:%S")
    except (TypeError, ValueError):
        return str(timestamp)

def build_mcq_leaderboard_data(unit_name="All Units"):
    unit_questions = [
        question for question in st.session_state.quiz_questions
        if unit_name == "All Units" or _quiz_question_unit(question) == unit_name
    ]
    question_count = len(unit_questions)
    maximum_points = sum(int(question.get("points", 0)) for question in unit_questions)
    leaderboard_list = []

    for username, user_data in st.session_state.users.items():
        if user_data.get("role") != "Student":
            continue
        attempts = [
            attempt for attempt in st.session_state.get("quiz_attempts", {}).get(username, [])
            if unit_name == "All Units" or attempt.get("unit", "Unit 1") == unit_name
        ]
        latest_attempts = {}
        for attempt in attempts:
            latest_attempts[attempt.get("question", "")] = attempt
        total_points = sum(int(attempt.get("points", 0)) for attempt in latest_attempts.values())
        completion_time = _mcq_completion_time(username, unit_name, attempts, question_count)
        leaderboard_list.append({
            "Username": username,
            "Student Name": user_data.get("name", username),
            "Student ID": user_data.get("student_id", ""),
            "Email": user_data.get("email", ""),
            "Submitted At": _format_mcq_submission_time(completion_time),
            "Questions Answered": len(latest_attempts),
            "Total Points": total_points,
            "Score": f"{total_points} / {maximum_points}",
            "Completion Time": completion_time or "9999",
            "Completed": bool(completion_time),
        })

    df = pd.DataFrame(leaderboard_list)
    if not df.empty:
        df = df.sort_values(
            by=["Completed", "Completion Time", "Total Points"],
            ascending=[False, True, False],
        ).reset_index(drop=True)
        df["Rank"] = df.index + 1
    return df

def render_mcq_leaderboard_view(unit_name="All Units", include_table=True, include_download=True):
    title_suffix = "" if unit_name == "All Units" else f" - {unit_name}"
    st.title(f"🏆 MCQ Leaderboard{title_suffix}")
    st.caption("MCQ assessment marks ranked by the time each student completed the quiz.")

    df_lb = build_mcq_leaderboard_data(unit_name)
    if df_lb.empty or df_lb["Questions Answered"].sum() == 0:
        st.info(f"No MCQ assessment records are available for {unit_name} yet.")
        return

    st.markdown("### 🥇 Completion Podium")
    podium_columns = st.columns(3)
    podium_classes = ["podium-1", "podium-2", "podium-3"]
    podium_labels = ["1st Place", "2nd Place", "3rd Place"]
    podium_icons = ["👑", "🥈", "🥉"]
    for index, column in enumerate(podium_columns):
        if index >= len(df_lb):
            continue
        row = df_lb.iloc[index]
        completion_label = (
            _format_mcq_submission_time(row["Completion Time"])
            if row["Completed"]
            else "In progress"
        )
        with column:
            st.markdown(
                f'<div class="{podium_classes[index]}">'
                f'<span style="font-size:2.5rem;">{podium_icons[index]}</span>'
                f'<h3 style="margin:0;">{podium_labels[index]}</h3>'
                f'<h4>{row["Student Name"]}</h4>'
                f'<p style="font-weight:bold; font-size:1.2rem;">⭐ {row["Total Points"]} Points</p>'
                f'<small>Completed: {completion_label}</small></div>',
                unsafe_allow_html=True,
            )

    if include_table:
        st.markdown("#### 📋 MCQ Assessment Details")
        st.dataframe(
            df_lb[["Submitted At", "Email", "Score", "Student ID", "Student Name"]],
            use_container_width=True,
            hide_index=True,
        )
    if include_download:
        st.download_button(
            "📥 Export MCQ Leaderboard (CSV)",
            df_lb.to_csv(index=False).encode("utf-8"),
            file_name="mcq_leaderboard.csv",
            mime="text/csv",
            type="primary",
        )

def render_student_mcq_leaderboard_view(username, unit_name="Unit 1"):
    render_mcq_leaderboard_view(unit_name, include_table=False, include_download=False)

    unit_questions = [
        question for question in st.session_state.quiz_questions
        if _quiz_question_unit(question) == unit_name
    ]
    attempts = [
        attempt for attempt in st.session_state.get("quiz_attempts", {}).get(username, [])
        if attempt.get("unit", "Unit 1") == unit_name
    ]
    latest_attempts = {
        attempt.get("question", ""): attempt
        for attempt in attempts
    }
    response_rows = []
    for question_number, question in enumerate(unit_questions, 1):
        question_text = question.get("question", "")
        attempt = latest_attempts.get(question_text, {})
        response_rows.append({
            "Question Number": question_number,
            "Question": question_text,
            "Correct Answer": attempt.get("correct_answer", question.get("answer", "")),
            "Response Answer": attempt.get("selected_answer", "Not Answered"),
            "Correct": "YES" if attempt.get("correct") else "NO",
            "Points": int(attempt.get("points", 0)),
        })

    st.markdown("#### 📋 My MCQ Assessment Details")
    if response_rows:
        st.dataframe(pd.DataFrame(response_rows), use_container_width=True, hide_index=True)
        total_marks = sum(row["Points"] for row in response_rows)
        st.markdown(
            f'<div class="metric-card"><div class="metric-title">Overall MCQ Marks</div>'
            f'<div class="metric-value">{total_marks}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"No MCQ questions are available for {unit_name} yet.")

def build_leaderboard_data(unit_name="All Units"):
    leaderboard_list = []
    for u_name, data in st.session_state.users.items():
        if data["role"] == "Student":
            scores = st.session_state.student_scores.get(u_name, {})
            passed_qs = [
                q
                for q, info in scores.items()
                if info.get("status") == "Passed"
                and q in st.session_state.questions
                and (
                    unit_name == "All Units"
                    or _student_question_unit(q, st.session_state.questions[q]) == unit_name
                )
            ]
            total_pts = sum(
                st.session_state.questions[q].get("points", 10)
                for q in passed_qs
            )
            leaderboard_list.append({
                "Username": u_name,
                "Student Name": data["name"],
                "Student ID": data.get("student_id", ""),
                "Email": data["email"],
                "Questions Solved": len(passed_qs),
                "Total Points": total_pts,
                "Completion Time": min(
                    (
                        info.get("completed_at", "9999")
                        for question, info in scores.items()
                        if info.get("status") == "Passed"
                        and question in st.session_state.questions
                        and (
                            unit_name == "All Units"
                            or _student_question_unit(question, st.session_state.questions[question]) == unit_name
                        )
                    ),
                    default="9999",
                ),
            })

    df = pd.DataFrame(leaderboard_list)
    if not df.empty:
        df = df.sort_values(by=["Total Points", "Completion Time"], ascending=[False, True]).reset_index(drop=True)
        df["Rank"] = df.index + 1
    return df

def render_leaderboard_view(unit_name="All Units"):
    title_suffix = "" if unit_name == "All Units" else f" - {unit_name}"
    st.title(f"🏆 Interactive Leaderboard & Performance Hub{title_suffix}")
    st.caption("Live standings, animated top performers, and export options.")

    df_lb = build_leaderboard_data(unit_name)

    if df_lb.empty:
        st.info("No student activity recorded yet.")
        return
    if unit_name != "All Units" and df_lb["Questions Solved"].sum() == 0:
        st.info(f"No leaderboard records are available for {unit_name} yet.")
        return

    # TOP 3 ANIMATED PODIUM
    st.markdown("### 🥇 Top Performers Podium")
    p_col1, p_col2, p_col3 = st.columns(3)
    top_3 = df_lb.head(3)
    
    with p_col1:
        if len(top_3) >= 1:
            r1 = top_3.iloc[0]
            st.markdown(
                f"""
                <div class="podium-1">
                    <span style="font-size:2.5rem;">👑</span>
                    <h3 style="color:#ffd700 !important; margin:0;">1st Place</h3>
                    <h4>{r1['Student Name']}</h4>
                    <p style="color:#f0f6fc; font-weight:bold; font-size:1.2rem;">⭐ {r1['Total Points']} Points</p>
                    <small>Solved: {r1['Questions Solved']} Problems</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with p_col2:
        if len(top_3) >= 2:
            r2 = top_3.iloc[1]
            st.markdown(
                f"""
                <div class="podium-2">
                    <span style="font-size:2.5rem;">🥈</span>
                    <h3 style="color:#c0c0c0 !important; margin:0;">2nd Place</h3>
                    <h4>{r2['Student Name']}</h4>
                    <p style="color:#f0f6fc; font-weight:bold; font-size:1.2rem;">⭐ {r2['Total Points']} Points</p>
                    <small>Solved: {r2['Questions Solved']} Problems</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with p_col3:
        if len(top_3) >= 3:
            r3 = top_3.iloc[2]
            st.markdown(
                f"""
                <div class="podium-3">
                    <span style="font-size:2.5rem;">🥉</span>
                    <h3 style="color:#cd7f32 !important; margin:0;">3rd Place</h3>
                    <h4>{r3['Student Name']}</h4>
                    <p style="color:#f0f6fc; font-weight:bold; font-size:1.2rem;">⭐ {r3['Total Points']} Points</p>
                    <small>Solved: {r3['Questions Solved']} Problems</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # FILTERS
    st.markdown("#### 🔍 Filter Leaderboard")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        search_name = st.text_input("Search Student Name:", "").strip().lower()
    with f_col2:
        min_pts = st.number_input("Minimum Points Threshold:", min_value=0, value=0, step=10)

    filtered_df = df_lb.copy()
    if search_name:
        filtered_df = filtered_df[filtered_df["Student Name"].str.lower().str.contains(search_name)]
    if min_pts > 0:
        filtered_df = filtered_df[filtered_df["Total Points"] >= min_pts]

    # CHARTS
    st.markdown("#### 📊 Leaderboard Performance Charts")
    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        fig_bar = px.bar(
            filtered_df,
            x="Total Points",
            y="Student Name",
            orientation="h",
            color="Total Points",
            color_continuous_scale="Viridis",
            text="Total Points",
            title="Top Score Standings",
            template="plotly_dark",
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_chart2:
        fig_scatter = px.scatter(
            filtered_df,
            x="Questions Solved",
            y="Total Points",
            size="Total Points",
            color="Student Name",
            hover_data=["Email"],
            title="Accuracy vs Score Distribution",
            template="plotly_dark",
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("#### 📋 Leaderboard Table")
    st.dataframe(
        filtered_df[["Rank", "Student Name", "Student ID", "Email", "Questions Solved", "Total Points"]],
        use_container_width=True,
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Leaderboard Report (CSV)",
        data=csv_data,
        file_name="leaderboard_report.csv",
        mime="text/csv",
        type="primary",
    )

    report_lines = [
        f"{row['Rank']}. {row['Student Name']} | Student ID: {row['Student ID']} | "
        f"Email: {row['Email']} | Solved: {row['Questions Solved']} | Points: {row['Total Points']}"
        for _, row in filtered_df.iterrows()
    ]
    assessment_download(
        f"{unit_name} Leaderboard Report",
        "Student leaderboard details",
        "\n".join(report_lines),
        "leaderboard_report.html",
    )

# ==========================================
# 3. LIGHT BLUE PROFESSIONAL LOGIN SCREEN
# ==========================================
def render_login_screen():
    st.markdown(
        """
        <style>
        /* Light Blue Professional Background Theme */
        .stApp {
            background: linear-gradient(rgba(230, 242, 255, 0.8), rgba(230, 242, 255, 0.9)),
                        url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        /* White Card Container for Login Form */
        [data-testid="stForm"] {
            background-color: #ffffff !important;
            padding: 2.2rem !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 24px rgba(0, 51, 102, 0.15) !important;
            border: 1px solid #b3d9ff !important;
        }

        /* High Contrast Dark Typography for Light Theme */
        .stTextInput label, .stForm p, [data-testid="stMarkdownContainer"] p, h1, h2, h3 {
            color: #002244 !important;
            font-weight: 600 !important;
        }

        /* Login Tab Buttons */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #003366 !important;
            font-weight: bold !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0056b3 !important;
            color: #ffffff !important;
            border-radius: 6px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_login = st.columns([1.6, 1.4])

    with col_login:
        st.markdown(
            "<h2 style='text-align: center; color: #003366 !important;'>⚡ B.Tech ML Assessment Portal</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center; color: #336699 !important; margin-bottom: 20px;'>Interactive Learning, Coding & Performance Platform</p>",
            unsafe_allow_html=True,
        )

        tab_login, tab_register, tab_recovery = st.tabs(["🔐 Sign In", "📝 Create Account", "🔑 Forgot Password"])

        with tab_login:
            with st.form("form_login"):
                username = st.text_input("Username").strip()
                password = st.text_input("Password", type="password").strip()
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if submitted:
                    matched_username = next(
                        (
                            stored_username
                            for stored_username in st.session_state.users
                            if stored_username.casefold() == username.casefold()
                        ),
                        None,
                    )
                    if (
                        matched_username is not None
                        and st.session_state.users[matched_username].get("password") == password
                    ):
                        st.session_state.authenticated_user = matched_username
                        st.query_params["auth"] = _auth_token(matched_username)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_register:
            with st.form("form_register"):
                new_name = st.text_input("Full Name *")
                new_email = st.text_input("Email Address *")
                new_department = st.selectbox("Department", ["AIML-E"])
                new_student_id = st.text_input("Student ID")
                new_username = st.text_input("Choose Username *").strip()
                new_password = st.text_input("Choose Password *", type="password")
                reg_submit = st.form_submit_button("Register Account", type="primary", use_container_width=True)

                if reg_submit:
                    if not (new_name.strip() and new_email.strip() and new_username and new_password and new_department and new_student_id.strip()):
                        st.error("⚠️ All fields marked with * are mandatory!")
                    elif "@" not in new_email:
                        st.error("⚠️ Please enter a valid Email Address!")
                    elif any(
                        stored_username.casefold() == new_username.casefold()
                        for stored_username in st.session_state.users
                    ):
                        st.error("⚠️ Username already taken! Please choose another.")
                    elif any(
                        user.get("email", "").strip().casefold() == new_email.strip().casefold()
                        for user in st.session_state.users.values()
                    ):
                        st.error("⚠️ This email is already registered. One email can have only one account.")
                    else:
                        st.session_state.users[new_username] = {
                            "password": new_password,
                            "role": "Student",
                            "name": new_name.strip(),
                            "email": new_email.strip(),
                            "department": new_department,
                            "student_id": new_student_id.strip(),
                        }
                        st.session_state.student_scores[new_username] = {}
                        sync_to_disk()
                        st.success("🎉 Account created successfully! Switch to 'Sign In' to log in.")
                        st.rerun()

        with tab_recovery:
            st.info("Enter the username and registered email. A temporary password will be shown once.")
            with st.form("form_forgot_password"):
                recovery_username = st.text_input("Username").strip()
                recovery_email = st.text_input("Registered email").strip()
                recover_submit = st.form_submit_button("Generate Temporary Password", type="primary")
                if recover_submit:
                    account = st.session_state.users.get(recovery_username)
                    if account and account.get("email", "").casefold() == recovery_email.casefold():
                        temporary_password = f"Reset-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
                        account["password"] = temporary_password
                        sync_to_disk()
                        st.success(f"Temporary password: {temporary_password}")
                    else:
                        st.error("Username and registered email do not match.")

# Dynamic CSS injection for inner application theme when logged in
# Dynamic CSS injection for inner application theme when logged in
def apply_inner_app_theme():
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #0d1117;
                --sidebar-bg: #161b22;
                --panel-bg: #161b22;
                --panel-soft: #21262d;
                --text-color: #f0f6fc;
                --muted-color: #8b949e;
                --primary-accent: #58a6ff;
                --border-color: #30363d;
                --leaderboard-text: #f0f6fc;
            }

            @media (prefers-color-scheme: light) {
                :root {
                    --app-bg: #f4f9ff;
                    --sidebar-bg: #edf5ff;
                    --panel-bg: #ffffff;
                    --panel-soft: #eef5ff;
                    --text-color: #0f172a;
                    --muted-color: #475569;
                    --primary-accent: #0f6bdb;
                    --border-color: #d4e4ff;
                    --leaderboard-text: #0f172a;
                }
            }

            .stApp {
                background-color: var(--app-bg);
                color: var(--text-color);
            }

            [data-testid="stSidebar"] {
                background-color: var(--sidebar-bg) !important;
                border-right: 1px solid var(--border-color) !important;
            }
            [data-testid="stSidebar"] *, 
            [data-testid="stSidebar"] label, 
            [data-testid="stSidebar"] p, 
            [data-testid="stSidebar"] span, 
            [data-testid="stSidebar"] div,
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {
                color: var(--text-color) !important;
            }

            [data-testid="stRadio"] label, 
            [data-testid="stRadio"] p, 
            [data-testid="stRadio"] span,
            div[role="radiogroup"] label p,
            .stSelectbox label,
            .stTextInput label,
            .stTextArea label,
            .stNumberInput label,
            .stCheckbox label {
                color: var(--text-color) !important;
                font-weight: 500 !important;
            }

            div[data-baseweb="select"] > div {
                background-color: var(--panel-soft) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 8px !important;
            }
            div[data-baseweb="select"] * {
                color: var(--text-color) !important;
            }
            div[data-baseweb="select"] svg {
                fill: var(--text-color) !important;
            }
            ul[role="listbox"] {
                background-color: var(--panel-bg) !important;
                border: 1px solid var(--border-color) !important;
            }
            li[role="option"] {
                color: var(--text-color) !important;
                background-color: var(--panel-bg) !important;
            }
            li[role="option"]:hover, li[aria-selected="true"] {
                background-color: #1f6beb !important;
                color: #ffffff !important;
            }

            [data-testid="stSidebar"] button {
                background-color: var(--panel-soft) !important;
                color: var(--text-color) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 6px !important;
            }
            [data-testid="stSidebar"] button:hover {
                background-color: var(--border-color) !important;
            }

            .metric-card {
                background: var(--panel-bg);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                transition: transform 0.2s ease, border-color 0.2s ease;
            }
            .metric-card:hover {
                transform: translateY(-3px);
                border-color: var(--primary-accent);
            }
            .metric-title {
                font-size: 0.85rem;
                color: var(--muted-color) !important;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .metric-value {
                font-size: 2.2rem;
                font-weight: 800;
                color: var(--primary-accent) !important;
            }
            @keyframes pulseGlow {
                0% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
                50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.6); }
                100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
            }
            .podium-1 {
                background: linear-gradient(145deg, #1f1a00, var(--panel-bg));
                border: 2px solid #ffd700;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                animation: pulseGlow 2.5s infinite;
                color: var(--leaderboard-text);
            }
            .podium-2 {
                background: linear-gradient(145deg, #1a1d24, var(--panel-bg));
                border: 2px solid #c0c0c0;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                color: var(--leaderboard-text);
            }
            .podium-3 {
                background: linear-gradient(145deg, #24160c, var(--panel-bg));
                border: 2px solid #cd7f32;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                color: var(--leaderboard-text);
            }
            .game-card {
                background: var(--panel-bg);
                border: 2px solid #a371f7;
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 8px 24px rgba(163, 113, 247, 0.15);
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px;
                padding: 10px 18px;
                background-color: var(--panel-soft);
                color: var(--text-color) !important;
                border: 1px solid var(--border-color);
            }
            .stTabs [aria-selected="true"] {
                background-color: #1f6beb !important;
                color: #ffffff !important;
                font-weight: bold;
                border-color: #388bfd !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
# ==========================================
# 4. MAIN ENTRYPOINT
# ==========================================
if st.session_state.authenticated_user is None:
    render_login_screen()
else:
    apply_inner_app_theme()
    current_username = st.session_state.authenticated_user
    current_user = st.session_state.users[current_username]

    saved_quiz_progress = st.session_state.quiz_progress.get(current_username, {})
    st.session_state.quiz_score = int(saved_quiz_progress.get("score", 0))
    st.session_state.quiz_streak = int(saved_quiz_progress.get("streak", 0))
    st.session_state.quiz_index = int(saved_quiz_progress.get("index", 0))

    st.sidebar.markdown(f"### 👤 {current_user['name']}")
    st.sidebar.caption(f"📧 {current_user['email']}")
    st.sidebar.caption(f"🛡️ Role: **{current_user['role']}**")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated_user = None
        st.session_state.pop("student_portal_nav", None)
        st.session_state.pop("selected_student_unit", None)
        st.session_state.pop("selected_trainer_unit", None)
        st.session_state.pop("assessment_unit_navigation", None)
        st.query_params.clear()
        st.rerun()

    st.sidebar.markdown("---")

    # -------------------------------------------------------------
    # ROLE A: PROFESSOR ADMIN PANEL
    # -------------------------------------------------------------
    if current_user.get("role") in ADMIN_ROLES:
        selected_trainer_unit = st.session_state.get("selected_trainer_unit")
        if not selected_trainer_unit:
            st.sidebar.markdown("### 🧭 Unit Navigation")
            st.title("👑 Professor Unit Navigation")
            st.caption("Choose a unit to view its students, progress, and content.")

            trainer_unit_columns = st.columns(3)
            for unit_index, unit_name in enumerate(UNIT_NAMES):
                unit_titles = [
                    title
                    for title, question in st.session_state.questions.items()
                    if _student_question_unit(title, question) == unit_name
                ]
                solved_count = sum(
                    1
                    for scores in st.session_state.student_scores.values()
                    for title, attempt in scores.items()
                    if title in unit_titles and attempt.get("status") == "Passed"
                )
                unit_quiz_count = sum(
                    1
                    for question in st.session_state.quiz_questions
                    if _quiz_question_unit(question) == unit_name
                )
                record_label = f"{solved_count} solved" if solved_count else "NO RECORD"
                detail_label = f"Assessment: {len(unit_titles)} questions · MCQ: {unit_quiz_count} questions" if unit_titles or unit_quiz_count else "Assessment: NO RECORD · MCQ: NO RECORD"
                podium_class = ["podium-1", "podium-2", "podium-3"][unit_index % 3]

                with trainer_unit_columns[unit_index % 3]:
                    st.markdown(
                        f'<div class="{podium_class}"><h2>{unit_name}</h2>'
                        f'<p style="font-size:1.35rem; font-weight:800;">{record_label}</p>'
                        f'<small>{detail_label}</small></div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Open {unit_name}", key=f"trainer_open_{unit_name}", use_container_width=True):
                        st.session_state.selected_trainer_unit = unit_name
                        st.rerun()
            st.stop()

        trainer_unit = selected_trainer_unit
        st.sidebar.markdown(f"### 🧭 {trainer_unit} Navigation")
        if st.sidebar.button("← Back to Unit Navigation", use_container_width=True):
            st.session_state.pop("selected_trainer_unit", None)
            st.rerun()
        st.title("👑 Professor Control & Analytics Panel")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["📈 Analytics Dashboard", "🏆 MCQ Leaderboard", "🏆 Class Leaderboard", "➕ Add New Question", "👥 Student Management", "📝 Assignments"]
        )

        with tab1:
            st.subheader("📊 Class Performance & Analytics Dashboard")

            students_list = [u for u, data in st.session_state.users.items() if data["role"] == "Student"]
            filter_student = st.selectbox("🎯 Filter Analytics by Student:", ["All Students"] + students_list)

            unit_questions = {
                title: question
                for title, question in st.session_state.questions.items()
                if _student_question_unit(title, question) == trainer_unit
            }
            total_qs = len(unit_questions)
            total_registered = len(students_list)

            all_passed_count = 0
            all_failed_count = 0
            student_scores_list = []

            for s in students_list:
                scores = st.session_state.student_scores.get(s, {})
                unit_scores = {
                    title: attempt
                    for title, attempt in scores.items()
                    if title in unit_questions
                }
                passed = sum(1 for q in unit_scores.values() if q.get("status") == "Passed")
                failed = sum(1 for q in unit_scores.values() if q.get("status") == "Failed")
                
                if filter_student == "All Students" or filter_student == s:
                    all_passed_count += passed
                    all_failed_count += failed
                    
                student_scores_list.append({
                    "Student": st.session_state.users[s]["name"],
                    "Solved": passed,
                    "Failed": failed,
                    "Total Points": sum(unit_questions[q]["points"] for q, inf in unit_scores.items() if inf.get("status") == "Passed")
                })

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Total Students</div><div class="metric-value">{total_registered}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Total Bank Questions</div><div class="metric-value">{total_qs}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Passed Solutions</div><div class="metric-value" style="color:#3fb950 !important;">{all_passed_count}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Failed Attempts</div><div class="metric-value" style="color:#f85149 !important;">{all_failed_count}</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            chart_col1, chart_col2 = st.columns([1, 1])

            with chart_col1:
                st.markdown("##### 🏆 Leaderboard Points Distribution")
                if student_scores_list:
                    df_chart = pd.DataFrame(student_scores_list)
                    fig_bar = px.bar(
                        df_chart, 
                        x="Student", 
                        y="Total Points", 
                        color="Total Points", 
                        color_continuous_scale="Purples",
                        text="Total Points",
                        template="plotly_dark"
                    )
                    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("No data available yet.")

            with chart_col2:
                st.markdown("##### 🎯 Overall Submission Status Ratio")
                if (all_passed_count + all_failed_count) > 0:
                    fig_pie = px.pie(
                        names=["Passed", "Failed"],
                        values=[all_passed_count, all_failed_count],
                        color=["Passed", "Failed"],
                        color_discrete_map={"Passed": "#2ea043", "Failed": "#da3633"},
                        hole=0.4,
                        template="plotly_dark"
                    )
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No submissions logged yet to plot ratio.")

        with tab2:
            render_mcq_leaderboard_view(trainer_unit)

        with tab3:
            render_leaderboard_view(trainer_unit)

        with tab4:
            st.subheader("Create New Problem")
            visible_questions = {
                title: question
                for title, question in st.session_state.questions.items()
                if _student_question_unit(title, question) == trainer_unit
            }
            st.caption(f"Showing {trainer_unit} question bank")
            with st.form("add_q_form"):
                q_title = st.text_input("Problem Title:")
                q_unit = st.selectbox("Unit:", UNIT_NAMES)
                q_topic = st.selectbox(
                    "Topic / Category:",
                    [
                        "Level 1 - Basic Python",
                        "Level 2 - Decision Making & Loops",
                        "Level 3 - Lists (ML Data)",
                        "Bonus ML-Oriented",
                    ],
                )
                q_points = st.number_input("Points / Score Value:", value=10, step=5)
                q_desc = st.text_area("Problem Description:")
                in1 = st.text_area("Input Test Case 1:")
                out1 = st.text_input("Expected Output Test Case 1:")
                starter = st.text_area("Starter Code:", value="# Write code here\n")

                if st.form_submit_button("➕ Publish Question") and q_title:
                    st.session_state.questions[q_title] = {
                        "unit": q_unit,
                        "topic": q_topic,
                        "points": q_points,
                        "description": q_desc,
                        "inputs": [in1],
                        "expected_outputs": [out1],
                        "starter_code": starter,
                    }
                    sync_to_disk()
                    st.success(f"Added '{q_title}' successfully!")

            st.markdown("#### Existing Coding Questions")
            for question_title, question in visible_questions.items():
                with st.expander(question_title):
                    with st.form(f"edit_coding_question_{question_title}"):
                        edited_title = st.text_input("Problem Title", value=question_title)
                        edited_unit = st.selectbox(
                            "Unit",
                            UNIT_NAMES,
                            index=UNIT_NAMES.index(question.get("unit", trainer_unit))
                            if question.get("unit", trainer_unit) in UNIT_NAMES else 0,
                            key=f"edit_coding_unit_{question_title}",
                        )
                        edited_topic = st.text_input("Topic / Category", value=question.get("topic", ""))
                        edited_points = st.number_input(
                            "Points / Score Value",
                            min_value=0,
                            value=int(question.get("points", 10)),
                            step=1,
                            key=f"edit_coding_points_{question_title}",
                        )
                        edited_description = st.text_area(
                            "Problem Description",
                            value=question.get("description", ""),
                            key=f"edit_coding_description_{question_title}",
                        )
                        edited_input = st.text_area(
                            "Input Test Case 1",
                            value=(question.get("inputs") or [""])[0],
                            key=f"edit_coding_input_{question_title}",
                        )
                        edited_output = st.text_input(
                            "Expected Output Test Case 1",
                            value=(question.get("expected_outputs") or [""])[0],
                            key=f"edit_coding_output_{question_title}",
                        )
                        edited_starter = st.text_area(
                            "Starter Code",
                            value=question.get("starter_code", ""),
                            key=f"edit_coding_starter_{question_title}",
                        )
                        if st.form_submit_button("💾 Save Assessment Changes"):
                            updated_question = {
                                **question,
                                "unit": edited_unit,
                                "topic": edited_topic,
                                "points": int(edited_points),
                                "description": edited_description,
                                "inputs": [edited_input],
                                "expected_outputs": [edited_output],
                                "starter_code": edited_starter,
                            }
                            if edited_title.strip() and edited_title.strip() != question_title:
                                st.session_state.questions.pop(question_title)
                                st.session_state.questions[edited_title.strip()] = updated_question
                            else:
                                st.session_state.questions[question_title] = updated_question
                            sync_to_disk()
                            st.success("Assessment updated successfully.")
                            st.rerun()
                    confirm_delete_assessment = st.checkbox(
                        "Confirm delete this assessment",
                        key=f"confirm_delete_assessment_{question_title}",
                    )
                    if st.button(
                        "🗑 Delete Assessment",
                        key=f"delete_assessment_{question_title}",
                        type="secondary",
                    ):
                        if confirm_delete_assessment:
                            st.session_state.questions.pop(question_title, None)
                            sync_to_disk()
                            st.success("Assessment deleted. Student attempt records were preserved.")
                            st.rerun()
                        else:
                            st.warning("Confirm deletion before removing this assessment.")

            st.markdown("#### Manage MCQ Questions")
            with st.form("add_mcq_form"):
                mcq_question = st.text_area("Question", placeholder="Type the question students should answer")
                mcq_description = st.text_area("Description / help text", placeholder="Optional instructions shown below the question")
                option_values = [
                    st.text_input(f"Option {option_number}", key=f"new_mcq_option_{option_number}")
                    for option_number in range(1, 5)
                ]
                mcq_options = [option.strip() for option in option_values if option.strip()]
                mcq_correct_number = st.selectbox("Correct option number", [1, 2, 3, 4])
                mcq_points = st.number_input("Points", min_value=0, value=10, step=1)
                mcq_required = st.checkbox("Required question", value=True)
                mcq_shuffle = st.checkbox("Shuffle options for each student", value=True)
                mcq_one_response = st.checkbox("Limit students to one response", value=True)
                mcq_explanation = st.text_area("Explanation shown after submission")
                mcq_unit = st.selectbox("Unit:", UNIT_NAMES)
                if st.form_submit_button("➕ Publish MCQ"):
                    normalized_options = [option.casefold() for option in mcq_options]
                    if not mcq_question.strip():
                        st.error("Add a question before publishing.")
                    elif len(mcq_options) < 2:
                        st.error("Add at least two answer choices.")
                    elif mcq_correct_number > len(mcq_options):
                        st.error("Choose a correct option that has text.")
                    elif len(set(normalized_options)) != len(mcq_options):
                        st.error("Answer choices must be unique.")
                    else:
                        st.session_state.quiz_questions.append({
                            "unit": mcq_unit,
                            "question": mcq_question.strip(),
                            "description": mcq_description.strip(),
                            "options": mcq_options,
                            "answer": mcq_options[mcq_correct_number - 1],
                            "points": int(mcq_points),
                            "required": mcq_required,
                            "shuffle_options": mcq_shuffle,
                            "one_response": mcq_one_response,
                            "explanation": mcq_explanation.strip(),
                        })
                        sync_to_disk()
                        st.success("MCQ published successfully.")

            st.markdown("#### Existing MCQ Questions")
            visible_mcqs = [
                (index, mcq)
                for index, mcq in enumerate(st.session_state.quiz_questions)
                if _quiz_question_unit(mcq) == trainer_unit
            ]
            for number, (mcq_index, mcq) in enumerate(visible_mcqs, 1):
                with st.expander(f"{number}. {mcq['question']}"):
                    with st.form(f"edit_mcq_question_{mcq_index}"):
                        edited_mcq_question = st.text_area(
                            "Question",
                            value=mcq.get("question", ""),
                            key=f"edit_mcq_text_{mcq_index}",
                        )
                        edited_mcq_description = st.text_area(
                            "Description / help text",
                            value=mcq.get("description", ""),
                            key=f"edit_mcq_description_{mcq_index}",
                        )
                        current_options = list(mcq.get("options", []))
                        edited_mcq_options = [
                            st.text_input(
                                f"Option {option_number}",
                                value=current_options[option_number - 1] if option_number <= len(current_options) else "",
                                key=f"edit_mcq_option_{mcq_index}_{option_number}",
                            ).strip()
                            for option_number in range(1, 5)
                        ]
                        edited_mcq_options = [option for option in edited_mcq_options if option]
                        current_answer_index = (
                            current_options.index(mcq.get("answer")) + 1
                            if mcq.get("answer") in current_options else 1
                        )
                        edited_answer_number = st.selectbox(
                            "Correct option number",
                            [1, 2, 3, 4],
                            index=current_answer_index - 1 if current_answer_index <= 4 else 0,
                            key=f"edit_mcq_answer_{mcq_index}",
                        )
                        edited_mcq_unit = st.selectbox(
                            "Unit",
                            UNIT_NAMES,
                            index=UNIT_NAMES.index(_quiz_question_unit(mcq))
                            if _quiz_question_unit(mcq) in UNIT_NAMES else 0,
                            key=f"edit_mcq_unit_{mcq_index}",
                        )
                        edited_mcq_points = st.number_input(
                            "Points",
                            min_value=0,
                            value=int(mcq.get("points", 10)),
                            step=1,
                            key=f"edit_mcq_points_{mcq_index}",
                        )
                        edited_mcq_required = st.checkbox(
                            "Required question",
                            value=mcq.get("required", True),
                            key=f"edit_mcq_required_{mcq_index}",
                        )
                        edited_mcq_shuffle = st.checkbox(
                            "Shuffle options for each student",
                            value=mcq.get("shuffle_options", False),
                            key=f"edit_mcq_shuffle_{mcq_index}",
                        )
                        edited_mcq_one_response = st.checkbox(
                            "Limit students to one response",
                            value=mcq.get("one_response", False),
                            key=f"edit_mcq_one_response_{mcq_index}",
                        )
                        edited_mcq_explanation = st.text_area(
                            "Explanation",
                            value=mcq.get("explanation", ""),
                            key=f"edit_mcq_explanation_{mcq_index}",
                        )
                        if st.form_submit_button("💾 Save MCQ Changes"):
                            normalized_options = [option.casefold() for option in edited_mcq_options]
                            if not edited_mcq_question.strip():
                                st.error("Add a question before saving.")
                            elif len(edited_mcq_options) < 2:
                                st.error("Add at least two answer choices.")
                            elif edited_answer_number > len(edited_mcq_options):
                                st.error("Choose a correct option that has text.")
                            elif len(set(normalized_options)) != len(edited_mcq_options):
                                st.error("Answer choices must be unique.")
                            else:
                                st.session_state.quiz_questions[mcq_index] = {
                                    **mcq,
                                    "unit": edited_mcq_unit,
                                    "question": edited_mcq_question.strip(),
                                    "description": edited_mcq_description.strip(),
                                    "options": edited_mcq_options,
                                    "answer": edited_mcq_options[edited_answer_number - 1],
                                    "points": int(edited_mcq_points),
                                    "required": edited_mcq_required,
                                    "shuffle_options": edited_mcq_shuffle,
                                    "one_response": edited_mcq_one_response,
                                    "explanation": edited_mcq_explanation.strip(),
                                }
                                sync_to_disk()
                                st.success("MCQ updated successfully.")
                                st.rerun()
                    confirm_delete_mcq = st.checkbox(
                        "Confirm delete this MCQ",
                        key=f"confirm_delete_mcq_{mcq_index}",
                    )
                    if st.button(
                        "🗑 Delete MCQ",
                        key=f"delete_mcq_{mcq_index}",
                        type="secondary",
                    ):
                        if confirm_delete_mcq:
                            st.session_state.quiz_questions.pop(mcq_index)
                            sync_to_disk()
                            st.success("MCQ deleted. Student response records were preserved.")
                            st.rerun()
                        else:
                            st.warning("Confirm deletion before removing this MCQ.")

            st.markdown("#### Student Responses")
            response_sheet = build_mcq_response_sheet(trainer_unit)
            if response_sheet.empty:
                st.info(f"No MCQ responses have been submitted for {trainer_unit} yet.")
            else:
                st.dataframe(response_sheet, use_container_width=True)
                st.download_button(
                    "📥 Download Student Responses (CSV)",
                    response_sheet.to_csv(index=False).encode("utf-8"),
                    file_name=f"{trainer_unit.lower().replace(' ', '_')}_mcq_responses.csv",
                    mime="text/csv",
                    type="primary",
                )

        with tab5:
            render_student_management_panel()

        with tab6:
            st.subheader("Create Assignment")
            with st.form("assignment_form"):
                assignment_title = st.text_input("Assignment title")
                assignment_description = st.text_area("Assignment description")
                if st.form_submit_button("➕ Publish Assignment") and assignment_title:
                    st.session_state.assignments[assignment_title] = {
                        "description": assignment_description,
                        "starter_code": "# Write your solution here\n",
                    }
                    sync_to_disk()
                    st.success("Assignment published successfully.")

            st.markdown("#### Existing Assignments")
            if not st.session_state.assignments:
                st.info("No assignments have been published yet.")
            for assignment_title, assignment in list(st.session_state.assignments.items()):
                with st.expander(assignment_title):
                    with st.form(f"edit_assignment_form_{assignment_title}"):
                        edited_assignment_title = st.text_input(
                            "Assignment title",
                            value=assignment_title,
                        )
                        edited_assignment_description = st.text_area(
                            "Assignment description",
                            value=assignment.get("description", ""),
                        )
                        edited_assignment_starter = st.text_area(
                            "Starter code",
                            value=assignment.get("starter_code", "# Write your solution here\n"),
                        )
                        if st.form_submit_button("💾 Save Assignment Changes"):
                            normalized_title = edited_assignment_title.strip()
                            duplicate_title = (
                                normalized_title != assignment_title
                                and normalized_title in st.session_state.assignments
                            )
                            if not normalized_title:
                                st.error("Assignment title cannot be empty.")
                            elif duplicate_title:
                                st.error("An assignment with this title already exists.")
                            else:
                                updated_assignment = {
                                    "description": edited_assignment_description,
                                    "starter_code": edited_assignment_starter,
                                }
                                if normalized_title != assignment_title:
                                    st.session_state.assignments.pop(assignment_title)
                                st.session_state.assignments[normalized_title] = updated_assignment
                                sync_to_disk()
                                st.success("Assignment updated successfully.")
                                st.rerun()

                    confirm_delete_assignment = st.checkbox(
                        "Confirm delete this assignment",
                        key=f"confirm_delete_assignment_{assignment_title}",
                    )
                    if st.button(
                        "🗑 Delete Assignment",
                        key=f"delete_assignment_{assignment_title}",
                        type="secondary",
                    ):
                        if confirm_delete_assignment:
                            st.session_state.assignments.pop(assignment_title, None)
                            sync_to_disk()
                            st.success("Assignment deleted successfully.")
                            st.rerun()
                        else:
                            st.warning("Confirm deletion before removing this assignment.")

    # -------------------------------------------------------------
    # ROLE B: STUDENT PORTAL
    # -------------------------------------------------------------
    else:
        if "student_nav_override" in st.session_state:
            st.session_state.student_portal_nav = st.session_state.pop("student_nav_override")
        selected_unit = st.session_state.get("selected_student_unit")
        student_nav_options = ["🧭 Unit Navigation", "👤 My Profile"]
        if selected_unit:
            student_nav_options = [
                "🎮 MCQ Assignment",
                "📝 Assessment Coding Studio",
                "📚 Assignments",
                "🏆 MCQ Leaderboard",
                "🏆 Class Leaderboard",
            ]
        if st.session_state.get("student_portal_nav") not in student_nav_options:
            st.session_state.student_portal_nav = student_nav_options[0]
        student_nav = st.sidebar.radio(
            "🎮 Portal Navigation",
            student_nav_options,
            key="student_portal_nav",
        )

        if selected_unit and student_nav != "🧭 Unit Navigation":
            if st.button("← Back to Unit Navigation", type="secondary"):
                st.session_state.pop("selected_student_unit", None)
                st.session_state.student_nav_override = "🧭 Unit Navigation"
                st.rerun()

        if student_nav == "🧭 Unit Navigation":
            st.title("⚡ B.Tech ML Learning Dashboard")
            st.caption("Choose a unit to view its progress and continue your assessment.")

            student_scores = st.session_state.student_scores.get(current_username, {})
            unit_columns = st.columns(3)
            for unit_index, unit_name in enumerate(UNIT_NAMES):
                unit_titles = [
                    title
                    for title, question in st.session_state.questions.items()
                    if _student_question_unit(title, question) == unit_name
                ]
                unit_passed = sum(
                    1
                    for title in unit_titles
                    if student_scores.get(title, {}).get("status") == "Passed"
                )
                unit_marks = sum(
                    st.session_state.questions[title].get("points", 10)
                    for title in unit_titles
                    if student_scores.get(title, {}).get("status") == "Passed"
                )
                if unit_passed:
                    record_label = f"{unit_passed} solved · {unit_marks} marks"
                else:
                    record_label = "NO RECORD"
                unit_quiz_questions = [
                    quiz_question
                    for quiz_question in st.session_state.quiz_questions
                    if _quiz_question_unit(quiz_question) == unit_name
                ]
                if unit_quiz_questions:
                    detail_label = f"Assessment: {len(unit_titles)} questions · MCQ: {len(unit_quiz_questions)} questions"
                elif unit_passed:
                    detail_label = f"Assessment: {len(unit_titles)} questions · MCQ: NO RECORD"
                else:
                    detail_label = "Assessment: NO RECORD · MCQ: NO RECORD"
                podium_class = ["podium-1", "podium-2", "podium-3"][unit_index % 3]

                with unit_columns[unit_index % 3]:
                    st.markdown(
                        f'<div class="{podium_class}"><h2>{unit_name}</h2>'
                        f'<p style="font-size:1.35rem; font-weight:800;">{record_label}</p>'
                        f'<small>{detail_label}</small></div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Open {unit_name}", key=f"open_{unit_name}", use_container_width=True):
                        st.session_state.selected_student_unit = unit_name
                        st.session_state.student_nav_override = "📝 Assessment Coding Studio"
                        st.rerun()

        elif student_nav == "👤 My Profile":
            st.title("👤 My Profile")
            profile = st.session_state.users[current_username]
            with st.form("student_profile_form"):
                profile_name = st.text_input("Full Name", value=profile.get("name", ""))
                profile_email = st.text_input("Email", value=profile.get("email", ""))
                department_options = ["AIML-E"]
                profile_department = st.selectbox("Department", department_options, index=department_options.index(profile.get("department", "")) if profile.get("department", "") in department_options else 0)
                profile_student_id = st.text_input("Student ID", value=profile.get("student_id", ""))
                profile_password = st.text_input("New Password", type="password")
                if st.form_submit_button("Save Profile"):
                    normalized_email = profile_email.strip().casefold()
                    duplicate_email = any(
                        username != current_username
                        and user.get("email", "").strip().casefold() == normalized_email
                        for username, user in st.session_state.users.items()
                    )
                    if not normalized_email or "@" not in normalized_email:
                        st.error("Please enter a valid email address.")
                    elif duplicate_email:
                        st.error("This email is already registered to another account.")
                    else:
                        profile["name"] = profile_name.strip() or profile.get("name", "")
                        profile["email"] = profile_email.strip()
                        profile["department"] = profile_department
                        profile["student_id"] = profile_student_id.strip()
                        if profile_password.strip():
                            profile["password"] = profile_password.strip()
                        sync_to_disk()
                        st.success("Profile updated.")

        elif student_nav == "🎮 MCQ Assignment":
            st.title("🎮 MCQ Assignment")
            st.caption("Answer the published MCQ assessment questions for this unit.")

            unit_name = st.session_state.get("selected_student_unit", "Unit 1")
            unit_quiz_questions = [
                quiz_question
                for quiz_question in st.session_state.quiz_questions
                if _quiz_question_unit(quiz_question) == unit_name
            ]
            if not unit_quiz_questions:
                st.info(f"No quiz questions are available for {unit_name} yet.")
                st.stop()

            student_attempts = [
                attempt
                for attempt in st.session_state.get("quiz_attempts", {}).get(current_username, [])
                if attempt.get("unit", "Unit 1") == unit_name
            ]
            latest_attempts = {
                attempt.get("question", ""): attempt
                for attempt in student_attempts
            }
            unanswered_questions = [
                question
                for question in unit_quiz_questions
                if question.get("question", "") not in latest_attempts
            ]
            answered_count = len(latest_attempts)
            current_score = sum(int(attempt.get("points", 0)) for attempt in latest_attempts.values())

            g1, g2, g3 = st.columns(3)
            with g1:
                st.markdown(f'<div class="metric-card"><div class="metric-title">MCQ Score</div><div class="metric-value">⭐ {current_score}</div></div>', unsafe_allow_html=True)
            with g2:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Current Streak</div><div class="metric-value">🔥 {st.session_state.quiz_streak}x</div></div>', unsafe_allow_html=True)
            with g3:
                progress = answered_count / len(unit_quiz_questions)
                st.markdown(f'<div class="metric-card"><div class="metric-title">Quiz Completion</div><div class="metric-value">{int(progress*100)}%</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            if unanswered_questions:
                q_curr = unanswered_questions[0]
                question_number = answered_count + 1
                
                st.markdown('<div class="game-card">', unsafe_allow_html=True)
                st.subheader(f"Question {question_number} of {len(unit_quiz_questions)}")
                st.markdown(f"#### {q_curr['question']}")
                if q_curr.get("description"):
                    st.caption(q_curr["description"])
                
                answer_options = list(q_curr["options"])
                if q_curr.get("shuffle_options"):
                    shuffle_seed = f"{current_username}:{q_curr['question']}"
                    random.Random(shuffle_seed).shuffle(answer_options)
                user_choice = st.radio("Choose the correct answer:", answer_options, key=f"q_{unit_name}_{question_number}_{q_curr['question']}")
                
                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if st.button("🚀 Lock Answer", type="primary"):
                        quiz_attempt = {
                            "question": q_curr["question"],
                            "selected_answer": user_choice,
                            "correct_answer": q_curr["answer"],
                            "correct": user_choice == q_curr["answer"],
                            "points": q_curr.get("points", 10) if user_choice == q_curr["answer"] else 0,
                            "unit": _quiz_question_unit(q_curr),
                            "answered_at": datetime.now(timezone.utc).isoformat(),
                        }
                        st.session_state.quiz_attempts.setdefault(current_username, []).append(quiz_attempt)
                        if question_number == len(unit_quiz_questions):
                            st.session_state.quiz_completed[current_username] = quiz_attempt["answered_at"]
                            st.session_state.quiz_completion_times.setdefault(current_username, {}).setdefault(
                                unit_name, quiz_attempt["answered_at"]
                            )
                        if user_choice == q_curr["answer"]:
                            st.session_state.quiz_streak += 1
                            pts_gained = 10 * st.session_state.quiz_streak
                            st.session_state.quiz_score += pts_gained
                            st.success(f"🎉 Correct! +{pts_gained} XP (Streak: {st.session_state.quiz_streak}x)")
                            st.info(f"💡 Explanation: {q_curr['explanation']}")
                            st.balloons()
                        else:
                            st.session_state.quiz_streak = 0
                            st.error(f"❌ Incorrect! The right answer was: **{q_curr['answer']}**")
                            st.info(f"💡 Explanation: {q_curr['explanation']}")
                        
                        st.session_state.quiz_progress.setdefault(current_username, {})[unit_name] = {
                            "score": st.session_state.quiz_score,
                            "streak": st.session_state.quiz_streak,
                            "index": question_number,
                        }
                        sync_to_disk()
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.balloons()
                st.success("🏆 Quest Complete! Your MCQ answers have been recorded by the portal.")
                st.markdown(f"### Final XP Score: **{st.session_state.quiz_score} Points**")
                quiz_export = "\n\n".join(
                    f"{item['question']}\nAnswer: {item['selected_answer']}\nCorrect: {item['correct_answer']}"
                    for item in st.session_state.quiz_attempts.get(current_username, [])
                )
                assessment_download("MCQ Practice Answers", "Quiz response record", quiz_export, "mcq_answers.html")
                has_one_response_rule = any(
                    question.get("one_response", False)
                    for question in unit_quiz_questions
                )
                if has_one_response_rule:
                    st.info("This form accepts one response per student. Restarting is disabled.")
                elif st.button("🔄 Restart Quiz Arena"):
                    st.session_state.quiz_index = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_streak = 0
                    st.session_state.quiz_progress[current_username] = {
                        "score": 0,
                        "streak": 0,
                        "index": 0,
                    }
                    st.session_state.quiz_completed.pop(current_username, None)
                    st.session_state.quiz_attempts[current_username] = []
                    sync_to_disk()
                    st.rerun()

        elif student_nav == "📚 Assignments":
            st.title("📝 Assignments")
            if not st.session_state.assignments:
                st.info("No assignments have been published yet.")
            for assignment_title, assignment in st.session_state.assignments.items():
                with st.expander(assignment_title):
                    st.markdown(assignment.get("description", ""))

        elif student_nav == "🏆 MCQ Leaderboard":
            render_student_mcq_leaderboard_view(
                current_username,
                st.session_state.get("selected_student_unit", "Unit 1"),
            )

        elif student_nav == "🏆 Class Leaderboard":
            render_leaderboard_view(st.session_state.get("selected_student_unit", "Unit 1"))

        else:
            st.title("⚡ B.Tech ML Assessment Portal")

            topics = list(set(q["topic"] for q in st.session_state.questions.values()))
            unit_number = st.session_state.get("selected_student_unit", "All Units")
            st.subheader(f"📊 {unit_number} Dashboard")
            selected_topic = st.sidebar.selectbox("Filter Category:", ["All"] + sorted(topics))

            unit_titles = [
                title
                for title, question in st.session_state.questions.items()
                if unit_number == "All Units" or _student_question_unit(title, question) == unit_number
            ]
            filtered_titles = [
                t for t, q in st.session_state.questions.items()
                if (unit_number == "All Units" or _student_question_unit(t, q) == unit_number)
                and (selected_topic == "All" or q["topic"] == selected_topic)
            ]

            if not filtered_titles:
                st.info("No problems are available for this unit and category.")
                st.stop()
            selected_title = st.sidebar.selectbox("Choose Problem:", filtered_titles)
            q_data = st.session_state.questions[selected_title]

            user_submissions = st.session_state.student_scores.get(current_username, {})
            unit_submissions = {
                title: user_submissions.get(title, {})
                for title in unit_titles
            }
            solved_qs = sum(1 for q in unit_submissions.values() if q.get("status") == "Passed")
            unit_points = sum(
                st.session_state.questions[title].get("points", 10)
                for title, submission in unit_submissions.items()
                if submission.get("status") == "Passed"
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Unit Problems Solved</div><div class="metric-value">{solved_qs} / {len(unit_titles)}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Unit Marks</div><div class="metric-value">{unit_points}</div></div>', unsafe_allow_html=True)
            with c3:
                status_curr = user_submissions.get(selected_title, {}).get("status", "Not Solved")
                st.markdown(f'<div class="metric-card"><div class="metric-title">Status</div><div class="metric-value" style="font-size:1.4rem;">{status_curr}</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader(selected_title)
                st.caption(f"**Category:** {q_data['topic']}")
                st.markdown(q_data["description"])

                with st.expander("👁️ View Sample Input / Expected Output"):
                    st.code(f"Input:\n{q_data['inputs'][0]}")
                    st.code(f"Expected Output:\n{q_data['expected_outputs'][0]}")

            with col2:
                st.subheader("Your Solution")
                code_input = st.text_area(
                    "Write your Python code below:",
                    value=q_data["starter_code"],
                    height=280,
                )
                assessment_download(selected_title, q_data["description"], code_input, f"{selected_title}.html")

                if st.button("▶ Submit & Evaluate", type="primary", use_container_width=True):
                    test_results = evaluate_script(
                        code_input, q_data["inputs"], q_data["expected_outputs"]
                    )

                    all_passed = True
                    for passed, test_in, exp_out, act_out in test_results:
                        if not passed:
                            all_passed = False
                            st.error("❌ Submission Failed")
                            st.write(f"**Your Output:** `{act_out}`")
                            st.write(f"**Expected Output:** `{exp_out}`")
                            break

                    if all_passed:
                        st.success("✅ Correct Answer! Points awarded.")
                        st.balloons()
                        st.session_state.student_scores[current_username][selected_title] = {
                            "status": "Passed",
                            "score": q_data.get("points", 10),
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                        }
                    else:
                        st.session_state.student_scores[current_username][selected_title] = {
                            "status": "Failed",
                            "score": 0,
                        }

                    sync_to_disk()
