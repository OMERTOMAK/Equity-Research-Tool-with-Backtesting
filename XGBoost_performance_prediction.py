# We will use XGBoost to predict stock performance.
# XGBoost is a machine learning algorithm that relies on decision trees. It uses gradient descent to optimize the model. 

import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

fundamentals = pd.read_csv("fundamentals.csv")
returns = pd.read_csv("returns.csv")

table_df = pd.merge(fundamentals, returns, on=["ticker", "year"])

# We build a target label for supervised learning: 0 if stock underperformed the S&P 500, 1 if it outperformed.
table_df["label"] = (table_df["stock_return"] > table_df["sp500_return"]).astype(int)

# We will focus on a set of features we calculated using our financial_statements pipeline.
feature_cols = [
    "ROE",
    "Operating_Margin",
    "Interest_Coverage_Ratio",
    "Trailing_PE",
    "Diluted_EPS",
    "Revenue_Growth",
    "Gross_Profit_Growth",
    "Operating_Income_Growth",
    "Net_Income_Growth",
    "EBITDA_Growth",
    "EPS_Growth",
    "RD_Growth",
    "Operating_CF_Growth",
    "ROE_Growth"
]

x = table_df[feature_cols]
y = table_df["label"]

# Temporal train-test split - no shuffling
train_cutoff = table_df["year"].max() - 1
X_train = x[table_df["year"] <= train_cutoff]
X_test = x[table_df["year"] > train_cutoff]
Y_train = y[table_df["year"] <= train_cutoff]
Y_test = y[table_df["year"] > train_cutoff]

# Convert to DMatix format for XGBoost
dtrain = xgb.DMatrix(X_train, label=Y_train)
dtest = xgb.DMatrix(X_test, label=Y_test)

# Model parameters
params = {
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "max_depth": 4,
    "eta": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "seed": 42
}

# Train

num_rounds = 100
model = xgb.train(
    params, 
    dtrain, 
    num_boost_round = num_rounds,
    evals = [(dtrain, "train"), (dtest, "test")],
    verbose_eval = 10
)

# Evaluate model performance
predictions = model.predict(dtest)
prediction_labels = (predictions > 0.5).astype(int)
print(f"Accuracy: {accuracy_score(Y_test, prediction_labels):.2f}")
print(classification_report(Y_test, prediction_labels))
print(confusion_matrix(Y_test, prediction_labels))

