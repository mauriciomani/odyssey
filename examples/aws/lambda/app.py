import json
import pickle
import boto3
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np


def train(event, context):
    """
    This function trains a particular ML problem.
    It can be useful for a daily training.
    The pickle model is sabed in particular model path inside given bucket.
    Parameters
    ----------
    event : json
        Carries the input parameter
    context : json
        Provides methods and properties about invocation, function and execution of lambda.

    Returns
    -------
    None
    """
    session = boto3.session.Session()
    s3_resource = session.client("s3")
    # No need to use event or context. Do not remove.
    bucket = "testbucket"
    # This includes the name of the input file 
    data_path = "testapp/input/data/training/iris.data"
    # Can use response body if using pandas you do not need to read
    response = s3_resource.get_object(Bucket=bucket, Key=data_path)
    df = pd.read_csv(response["Body"], names=["sepal_length", "sepal_width", "petal_length", "petal_width", "target"])
    df.replace({"Iris-setosa": 1, "Iris-versicolor": 2, "Iris-virginica": 3}, inplace=True)
    X = df.iloc[:, :4]
    y = df.target
    lr = LogisticRegression().fit(X, y)
    # No need to add bucket
    model_path = "testapp/model/logistic_regression.pkl"
    binary_model = pickle.dumps(lr)
    s3_resource.put_object(Bucket=bucket, Key=model_path, Body=binary_model)


def serve(event, context):
    """
    This function saves the model from train inside tmp.
    Load it and use it to predict from event parameter input.
    Finally returns prediction.
    Parameters
    ----------
    event : json
        Carries the input parameter
    context : json
        Provides methods and properties about invocation, function and execution of lambda.

    Returns
    -------
    json
        Kindly change the format if needed
    """
    # This function uses event, however most sure you will not be using context.
    s3 = boto3.client("s3")
    # Kindly add the model_name as well
    bucket = "testbucket"
    model_path = "testapp/model/logistic_regression.pkl"
    model_name = model_path.split("/")[-1]
    temp_file_path = "/tmp/" + model_name
    s3.download_file(bucket, model_path, temp_file_path)
    with open(temp_file_path, "rb") as f:
        model = pickle.load(f)

    # Kindy use event as the input of the lambda function
    # Be aware data needs to be preprocessed and most sure comes from event.
    data = event["data"]
    predictions = model.predict([data])
    output = {"prediction": int(predictions[0])}
    output = json.dumps(output)
    return(output)
