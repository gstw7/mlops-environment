import mlflow
from airflow import DAG
from sklearn.datasets import load_iris
from datetime import datetime, timedelta
from sklearn.tree import DecisionTreeClassifier
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
    'train_iris_model',
    default_args=default_args,
    description='Train and log a decision tree model to MLflow',
    schedule_interval='0 0 15 * *', 
    tags=['ml', 'ds']
)

def train_model():

    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2)
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)

    mlflow.set_tracking_uri("http://172.29.0.5:5000")
    mlflow.set_experiment("iris")
    with mlflow.start_run(run_name="run_" + datetime.now().strftime("%Y%m%d_%H%M%S")):
        mlflow.log_metric("score", score)
        mlflow.sklearn.log_model(clf, "decision_tree")

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

train_model_task
