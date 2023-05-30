import os
import mlflow
import numpy as np
import pandas as pd
from airflow import DAG
from airflow.models import Variable
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from airflow.operators.python_operator import PythonOperator


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

def train_and_log_model():

    data_url = "http://lib.stat.cmu.edu/datasets/boston"
    raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
    X = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
    y = raw_df.values[1::2, 2]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    mlflow.set_tracking_uri("http://172.29.0.5:5000")
    mlflow.set_experiment("boston-housing")
    with mlflow.start_run(run_name="run_" + datetime.now().strftime("%Y%m%d_%H%M%S")):
        mlflow.log_metric("mse", mse)
        mlflow.sklearn.log_model(model, "model")


train_and_log_model_task = PythonOperator(
    task_id="train_and_log_model",
    python_callable=train_and_log_model,
    dag=dag,
)

train_and_log_model_task
