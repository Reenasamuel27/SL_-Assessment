import io
import json
import os
import sys
import traceback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="B.Tech ML Coding Portal", layout="wide", page_icon="⚡"
)

DB_FILE = "db.json"

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
    "prof_admin": {
        "password": "admin123",
        "role": "Professor",
        "name": "Prof. Sadaiyandi",
        "email": "prof@institution.edu",
    }
}

def load_db():
    if not os.path.exists(DB_FILE):
        data = {
            "users": DEFAULT_USERS,
            "student_scores": {},
            "questions": DEFAULT_QUESTIONS,
        }
        save_db_data(data)
        return data

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = DEFAULT_USERS
            if "student_scores" not in data:
                data["student_scores"] = {}
            if "questions" not in data:
                data["questions"] = DEFAULT_QUESTIONS
            return data
    except Exception:
        data = {
            "users": DEFAULT_USERS,
            "student_scores": {},
            "questions": DEFAULT_QUESTIONS,
        }
        save_db_data(data)
        return data

def save_db_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def sync_to_disk():
    db = {
        "users": st.session_state.users,
        "student_scores": st.session_state.student_scores,
        "questions": st.session_state.questions,
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
        new_password = st.text_input("Password", type="password", value=student_data.get("password", ""))
        reset_scores = st.checkbox("Reset all scores and attempts for this student", value=False)

        submitted = st.form_submit_button("💾 Save Student Changes")
        if submitted:
            st.session_state.users[selected_student]["name"] = new_name.strip() or student_data.get("name", "")
            st.session_state.users[selected_student]["email"] = new_email.strip() or student_data.get("email", "")
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

# Initialize Session State
db_data = load_db()

if "users" not in st.session_state:
    st.session_state.users = db_data["users"]

if "student_scores" not in st.session_state:
    st.session_state.student_scores = db_data["student_scores"]

if "questions" not in st.session_state:
    st.session_state.questions = db_data["questions"]

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

# Game Quiz State Variables
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_streak" not in st.session_state:
    st.session_state.quiz_streak = 0

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

def build_leaderboard_data():
    leaderboard_list = []
    for u_name, data in st.session_state.users.items():
        if data["role"] == "Student":
            scores = st.session_state.student_scores.get(u_name, {})
            passed_qs = [q for q, info in scores.items() if info.get("status") == "Passed"]
            total_pts = sum(
                st.session_state.questions[q].get("points", 10)
                for q in passed_qs
                if q in st.session_state.questions
            )
            leaderboard_list.append({
                "Username": u_name,
                "Student Name": data["name"],
                "Email": data["email"],
                "Questions Solved": len(passed_qs),
                "Total Points": total_pts,
            })

    df = pd.DataFrame(leaderboard_list)
    if not df.empty:
        df = df.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index + 1
    return df

def render_leaderboard_view():
    st.title("🏆 Interactive Leaderboard & Performance Hub")
    st.caption("Live standings, animated top performers, and export options.")

    df_lb = build_leaderboard_data()

    if df_lb.empty:
        st.info("No student activity recorded yet.")
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
        filtered_df[["Rank", "Student Name", "Email", "Questions Solved", "Total Points"]],
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

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            with st.form("form_login"):
                username = st.text_input("Username").strip()
                password = st.text_input("Password", type="password").strip()
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if submitted:
                    if (
                        username in st.session_state.users
                        and st.session_state.users[username]["password"] == password
                    ):
                        st.session_state.authenticated_user = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_register:
            with st.form("form_register"):
                new_name = st.text_input("Full Name *")
                new_email = st.text_input("Email Address *")
                new_username = st.text_input("Choose Username *").strip()
                new_password = st.text_input("Choose Password *", type="password")
                reg_submit = st.form_submit_button("Register Account", type="primary", use_container_width=True)

                if reg_submit:
                    if not (new_name.strip() and new_email.strip() and new_username and new_password):
                        st.error("⚠️ All fields marked with * are mandatory!")
                    elif "@" not in new_email:
                        st.error("⚠️ Please enter a valid Email Address!")
                    elif new_username in st.session_state.users:
                        st.error("⚠️ Username already taken! Please choose another.")
                    else:
                        st.session_state.users[new_username] = {
                            "password": new_password,
                            "role": "Student",
                            "name": new_name.strip(),
                            "email": new_email.strip(),
                        }
                        st.session_state.student_scores[new_username] = {}
                        sync_to_disk()
                        st.success("🎉 Account created successfully! Switch to 'Sign In' to log in.")

# Dynamic CSS injection for inner application theme when logged in
# Dynamic CSS injection for inner application theme when logged in
def apply_inner_app_theme():
    st.markdown(
        """
        <style>
            /* Main Dark Background */
            .stApp {
                background-color: #0d1117;
                color: #f0f6fc;
            }
            
            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background-color: #161b22 !important;
                border-right: 1px solid #30363d !important;
            }
            [data-testid="stSidebar"] *, 
            [data-testid="stSidebar"] label, 
            [data-testid="stSidebar"] p, 
            [data-testid="stSidebar"] span, 
            [data-testid="stSidebar"] div,
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {
                color: #f0f6fc !important;
            }

            /* --- FIX 1: RADIO BUTTON TEXT VISIBILITY --- */
            [data-testid="stRadio"] label, 
            [data-testid="stRadio"] p, 
            [data-testid="stRadio"] span,
            div[role="radiogroup"] label p {
                color: #f0f6fc !important;
                font-weight: 500 !important;
            }

            /* --- FIX 2: SELECTBOX / DROPDOWN CONTRAST --- */
            div[data-baseweb="select"] > div {
                background-color: #21262d !important;
                border: 1px solid #30363d !important;
                border-radius: 8px !important;
            }
            div[data-baseweb="select"] * {
                color: #f0f6fc !important;
            }
            div[data-baseweb="select"] svg {
                fill: #f0f6fc !important;
            }
            /* Dropdown popup menu items */
            ul[role="listbox"] {
                background-color: #161b22 !important;
                border: 1px solid #30363d !important;
            }
            li[role="option"] {
                color: #f0f6fc !important;
                background-color: #161b22 !important;
            }
            li[role="option"]:hover, li[aria-selected="true"] {
                background-color: #1f6beb !important;
                color: #ffffff !important;
            }

            /* Sidebar buttons */
            [data-testid="stSidebar"] button {
                background-color: #21262d !important;
                color: #f0f6fc !important;
                border: 1px solid #30363d !important;
                border-radius: 6px !important;
            }
            [data-testid="stSidebar"] button:hover {
                background-color: #30363d !important;
                border-color: #8b949e !important;
            }

            /* Cards & Podium Styling */
            .metric-card {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
                transition: transform 0.2s ease, border-color 0.2s ease;
            }
            .metric-card:hover {
                transform: translateY(-3px);
                border-color: #58a6ff;
            }
            .metric-title {
                font-size: 0.85rem;
                color: #8b949e !important;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .metric-value {
                font-size: 2.2rem;
                font-weight: 800;
                color: #58a6ff !important;
            }
            @keyframes pulseGlow {
                0% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
                50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.6); }
                100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
            }
            .podium-1 {
                background: linear-gradient(145deg, #1f1a00, #161b22);
                border: 2px solid #ffd700;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                animation: pulseGlow 2.5s infinite;
            }
            .podium-2 {
                background: linear-gradient(145deg, #1a1d24, #161b22);
                border: 2px solid #c0c0c0;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
            }
            .podium-3 {
                background: linear-gradient(145deg, #24160c, #161b22);
                border: 2px solid #cd7f32;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
            }
            .game-card {
                background: #161b22;
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
                background-color: #21262d;
                color: #c9d1d9 !important;
                border: 1px solid #30363d;
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

    st.sidebar.markdown(f"### 👤 {current_user['name']}")
    st.sidebar.caption(f"📧 {current_user['email']}")
    st.sidebar.caption(f"🛡️ Role: **{current_user['role']}**")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated_user = None
        st.rerun()

    st.sidebar.markdown("---")

    # -------------------------------------------------------------
    # ROLE A: PROFESSOR ADMIN PANEL
    # -------------------------------------------------------------
    if current_user["role"] == "Professor":
        st.title("👑 Professor Control & Analytics Panel")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📈 Analytics Dashboard", "📊 Student Gradebook", "🏆 Class Leaderboard", "➕ Add New Question", "👥 Student Management"]
        )

        with tab1:
            st.subheader("📊 Class Performance & Analytics Dashboard")

            students_list = [u for u, data in st.session_state.users.items() if data["role"] == "Student"]
            filter_student = st.selectbox("🎯 Filter Analytics by Student:", ["All Students"] + students_list)

            total_qs = len(st.session_state.questions)
            total_registered = len(students_list)

            all_passed_count = 0
            all_failed_count = 0
            student_scores_list = []

            for s in students_list:
                scores = st.session_state.student_scores.get(s, {})
                passed = sum(1 for q in scores.values() if q.get("status") == "Passed")
                failed = sum(1 for q in scores.values() if q.get("status") == "Failed")
                
                if filter_student == "All Students" or filter_student == s:
                    all_passed_count += passed
                    all_failed_count += failed
                    
                student_scores_list.append({
                    "Student": st.session_state.users[s]["name"],
                    "Solved": passed,
                    "Failed": failed,
                    "Total Points": sum(st.session_state.questions[q]["points"] for q, inf in scores.items() if inf.get("status") == "Passed" and q in st.session_state.questions)
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
            st.subheader("Student Gradebook & Question Matrix")
            students = [u for u, data in st.session_state.users.items() if data["role"] == "Student"]

            gradebook_data = []
            for student in students:
                user_info = st.session_state.users[student]
                s_data = {
                    "Student Name": user_info["name"],
                    "Email": user_info["email"],
                    "Username": student,
                    "Total Score": 0,
                    "Solved Count": 0,
                }
                scores = st.session_state.student_scores.get(student, {})

                for q_title, q_info in st.session_state.questions.items():
                    status = scores.get(q_title, {}).get("status", "Not Attempted")
                    s_data[q_title] = status
                    if status == "Passed":
                        s_data["Total Score"] += q_info.get("points", 10)
                        s_data["Solved Count"] += 1

                gradebook_data.append(s_data)

            if gradebook_data:
                df_gradebook = pd.DataFrame(gradebook_data)
                st.dataframe(df_gradebook, use_container_width=True)
            else:
                st.info("No registered students yet.")

        with tab3:
            render_leaderboard_view()

        with tab4:
            st.subheader("Create New Problem")
            with st.form("add_q_form"):
                q_title = st.text_input("Problem Title:")
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
                        "topic": q_topic,
                        "points": q_points,
                        "description": q_desc,
                        "inputs": [in1],
                        "expected_outputs": [out1],
                        "starter_code": starter,
                    }
                    sync_to_disk()
                    st.success(f"Added '{q_title}' successfully!")

        with tab5:
            render_student_management_panel()

    # -------------------------------------------------------------
    # ROLE B: STUDENT PORTAL
    # -------------------------------------------------------------
    else:
        student_nav = st.sidebar.radio(
            "🎮 Portal Navigation", ["🎮 Practice Quiz Game Studio", "📝 Assessment Coding Studio", "🏆 Class Leaderboard"]
        )

        if student_nav == "🎮 Practice Quiz Game Studio":
            st.title("🎮 Code Quest - Interactive Quiz Arena")
            st.caption("Practice key ML & Python concepts in game mode before tackling graded assessments!")

            g1, g2, g3 = st.columns(3)
            with g1:
                st.markdown(f'<div class="metric-card"><div class="metric-title">XP Points</div><div class="metric-value">⭐ {st.session_state.quiz_score}</div></div>', unsafe_allow_html=True)
            with g2:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Current Streak</div><div class="metric-value">🔥 {st.session_state.quiz_streak}x</div></div>', unsafe_allow_html=True)
            with g3:
                progress = (st.session_state.quiz_index / len(QUIZ_QUESTIONS))
                st.markdown(f'<div class="metric-card"><div class="metric-title">Quiz Completion</div><div class="metric-value">{int(progress*100)}%</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            if st.session_state.quiz_index < len(QUIZ_QUESTIONS):
                q_curr = QUIZ_QUESTIONS[st.session_state.quiz_index]
                
                st.markdown('<div class="game-card">', unsafe_allow_html=True)
                st.subheader(f"Question {st.session_state.quiz_index + 1} of {len(QUIZ_QUESTIONS)}")
                st.markdown(f"#### {q_curr['question']}")
                
                user_choice = st.radio("Choose the correct answer:", q_curr["options"], key=f"q_{st.session_state.quiz_index}")
                
                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if st.button("🚀 Lock Answer", type="primary"):
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
                        
                        st.session_state.quiz_index += 1
                        st.button("Next Question ▶")
                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.balloons()
                st.success("🏆 Quest Complete! You've finished all quiz practice questions!")
                st.markdown(f"### Final XP Score: **{st.session_state.quiz_score} Points**")
                if st.button("🔄 Restart Quiz Arena"):
                    st.session_state.quiz_index = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_streak = 0
                    st.rerun()

        elif student_nav == "🏆 Class Leaderboard":
            render_leaderboard_view()

        else:
            st.title("⚡ B.Tech ML Assessment Portal")

            q_titles = list(st.session_state.questions.keys())
            topics = list(set(q["topic"] for q in st.session_state.questions.values()))
            selected_topic = st.sidebar.selectbox("Filter Category:", ["All"] + sorted(topics))

            filtered_titles = [
                t for t, q in st.session_state.questions.items()
                if selected_topic == "All" or q["topic"] == selected_topic
            ]

            selected_title = st.sidebar.selectbox("Choose Problem:", filtered_titles)
            q_data = st.session_state.questions[selected_title]

            user_submissions = st.session_state.student_scores.get(current_username, {})
            solved_qs = sum(1 for q in user_submissions.values() if q.get("status") == "Passed")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Total Solved</div><div class="metric-value">{solved_qs} / {len(q_titles)}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Points Value</div><div class="metric-value">{q_data.get("points", 10)} Pts</div></div>', unsafe_allow_html=True)
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
                        }
                    else:
                        st.session_state.student_scores[current_username][selected_title] = {
                            "status": "Failed",
                            "score": 0,
                        }

                    sync_to_disk()
