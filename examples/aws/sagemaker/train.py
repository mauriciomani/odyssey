import pickle
import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
import logging

logging.basicConfig(level=logging.INFO)

# Train can work for both serve_endpoint.py and serve_batch_transform.py
# We are using simple iris.data file https://archive.ics.uci.edu/ml/datasets/iris

def train(input_path, model_path, param_path=None):
    """
    Write the necessary logic for a train procedure. 
    Input data path provides the place where input data has been placed.
    In this function nothing is returned. You can add paramaters. However, you cannot delete them.
    Parameters
    ----------
    input_path : str
        Place wwhere input data is store 
    model_path : str
        Place wehere model is store.
    param_path : str [None]
        Place wehere params for the model are stored.

    Returns
    -------
    None
        You need to save your model
    """
    data_path = os.path.join(input_path, "iris.data")
    df = pd.read_csv(data_path, names=["sepal_length", "sepal_width", "petal_length", "petal_width", "target"])
    df.replace({"Iris-setosa": 1, "Iris-versicolor": 2, "Iris-virginica": 3}, inplace=True)
    X = df.iloc[:, :4]
    y = df.target
    lr = LogisticRegression().fit(X, y)
    logging.info("Saving model")
    model_path = os.path.join(model_path, "logistic_regression.pkl")
    pickle.dump(lr, open(model_path, "wb"))
    logging.info("Model saved")
