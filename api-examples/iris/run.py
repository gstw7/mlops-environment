import mlflow
import pandas as pd
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

mlflow.set_tracking_uri("http://mlflow:5000")

app = FastAPI(
    title="BGR - Iris prediction",
    description="Iris prediction API helps you do awesome stuff 🚀",
    version="1.0.0",
    contact={
        "name": "BGR InfraData",
        "email": "gust4vo-mlo@hotmail.com"
    },
    openapi_url="/v1/openapi.json"
)


class IrisData(BaseModel):
    """Pydantic model that represents the input data for the prediction endpoint.

    Attributes:
        sepal_length_cm (float): The sepal length in centimeters.
        sepal_width_cm (float): The sepal width in centimeters.
        petal_length_cm (float): The petal length in centimeters.
        petal_width_cm (float): The petal width in centimeters.
    """
    sepal_length_cm: float
    sepal_width_cm: float
    petal_length_cm: float
    petal_width_cm: float


@app.get("/")
async def health() -> dict:
    """Endpoint that returns the health status of the server.

    Returns:
        dict: A dictionary containing a message indicating that the server is up and running.
    """
    return {"message": "The server is up and running!"}


@app.post("/predict")
async def predict(data: IrisData) -> dict:
    """Endpoint that makes predictions using a Machine Learning model.

    Args:
        data (IrisData): A Pydantic model representing the input data for the prediction.

    Returns:
        dict: A dictionary containing the prediction made by the model.
    """
    model_uri = "models:/iris-model/production"
    class_names = {
        0: 'Iris Setosa',
        1: 'Iris Versicolour',
        2: 'Iris Virginica'
    }

    transformed_data = {
        "sepal length (cm)": data.sepal_length_cm,
        "sepal width (cm)": data.sepal_width_cm,
        "petal length (cm)": data.petal_length_cm,
        "petal width (cm)": data.petal_width_cm
    }
    try:
        model = mlflow.pyfunc.load_model(model_uri)
    except mlflow.exceptions.RestException as rest_exception:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model from MLflow: {rest_exception}"
        ) from rest_exception

    try:
        prediction = model.predict(pd.DataFrame(transformed_data, index=[0]))
    except Exception as prediction_error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to make prediction with loaded model: {prediction_error}"
        ) from prediction_error

    return {"prediction": class_names[int(prediction[0])]}
