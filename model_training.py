import mlflow as mlf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import pickle


rel_columns = [
    'ID',
    'LIMIT_BAL',
    'SEX',
    'EDUCATION',
    'MARRIAGE',
    'AGE',
    'PAY_0',
    'PAY_2',
    'PAY_3',
    'PAY_4',
    'PAY_5',
    'PAY_6',
    'default.payment.next.month'
]

df_ccd = pd.read_csv('./UCI_Credit_Card.csv', usecols=rel_columns)

for col in ['PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6']:
    df_ccd[col] = df_ccd[col].apply(lambda x: 0 if x <0 else x)

X_train, X_test, y_train, y_test = train_test_split(
    df_ccd.iloc[:, 0:-1],
    df_ccd.iloc[:, -1],
    test_size=0.2,
    random_state=100
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train,
    y_train, 
    test_size=0.25,
    random_state=100
)

mlf.set_experiment("Random-Forest")

count = 0
n_estimators_permute = [100, 250, 500, 1000]
max_depth_permute = [None, 3, 8]
for n in n_estimators_permute:
    for d in max_depth_permute:
        with mlf.start_run(run_name=f"run-{count}"):
            rf_clf = RandomForestClassifier(n_estimators=n, max_depth=d, random_state=100)
            rf_clf.fit(X_train, y_train)
            mlf.log_param(key='n_estimators', value=n)
            mlf.log_param(key='max_depth', value=d)
            pred_vals = rf_clf.predict(X_val)
            auc_val = roc_auc_score(y_val, pred_vals)
            pred_train = rf_clf.predict(X_train)
            auc_train = roc_auc_score(y_train, pred_train)
            mlf.log_metric(key='roc_auc_val', value=auc_val)
            mlf.log_metric(key='roc_auc_train', value=auc_train)
            count += 1
        mlf.end_run()

mlf.set_experiment(experiment_name="LogisticRegression")

count = 0
penalties = ['l2', None]
max_iter_permute = [100, 200, 400, 1000]
for n in penalties:
    for d in max_iter_permute:
        with mlf.start_run(run_name=f"run-{count}"):
            lr_clf = LogisticRegression(penalty=n, max_iter=d, random_state=100)
            lr_clf.fit(X_train, y_train)
            mlf.log_param(key='penalty', value=n)
            mlf.log_param(key='max_iter', value=d)
            pred_vals = lr_clf.predict(X_val)
            auc_val = roc_auc_score(y_val, pred_vals)
            pred_train = lr_clf.predict(X_train)
            auc_train = roc_auc_score(y_train, pred_train)
            mlf.log_metric(key='roc_auc_val', value=auc_val)
            mlf.log_metric(key='roc_auc_train', value=auc_train)
            count += 1
        mlf.end_run()

final_model = RandomForestClassifier(n_estimators=250, max_depth=8, random_state=100)
final_model.fit(df_ccd.iloc[:, 0:-1], df_ccd.iloc[:, -1])

with open('final_model', 'wb') as f:
    pickle.dump(final_model, f)