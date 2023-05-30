import os
from datetime import datetime, timedelta

import mlflow
import numpy as np
import pandas as pd
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from mlflow.models.signature import infer_signature
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

default_args = {
    'owner': 'gustavo',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 6),
    'email': ['gust4vo-mlo@hotmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}
dag = DAG(
    'train_boston_housing_model',
    default_args=default_args,
    description='Train and log a linear regression model to MLflow',
    schedule_interval='0 0 15 * *',
    tags=['ml', 'ds']
)

endpoint_mlflow = Variable.get("mlflow_tracking")


def train_and_log_model():
    """Train and log a model.

    This function reads the Boston Housing dataset from a URL, preprocesses the data,
    splits it into training and testing sets, trains a linear regression model,
    and logs the metrics and the model in MLflow.

    Returns:
        None
    """
    data_url = "http://lib.stat.cmu.edu/datasets/boston"
    raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
    data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
    target = raw_df.values[1::2, 2]

    feature_names = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX',
                     'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B', 'LSTAT']
    df = pd.DataFrame(data, columns=feature_names)
    df['target'] = target

    X = df.drop('target', axis=1)
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    signature = infer_signature(X_train, model.predict(X_train))
    mse = mean_squared_error(y_test, y_pred)

    mlflow.set_tracking_uri(endpoint_mlflow)
    mlflow.set_experiment("boston-housing")
    with mlflow.start_run(run_name="run_" + datetime.now().strftime("%Y%m%d_%H%M%S")):
        mlflow.log_metric("mse", mse)
        mlflow.sklearn.log_model(
            model, "linear_regression", signature=signature)


train_and_log_model_task = PythonOperator(
    task_id="train_and_log_model",
    python_callable=train_and_log_model,
    dag=dag,
)

train_and_log_model_task
