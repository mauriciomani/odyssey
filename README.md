<p align="center">
<img src="resources/rocket.jpg" alt="rocket" width="400"/>
</p>

-----------------

# Odyssey - Cloud Machine Learning
[![Package Status](https://img.shields.io/badge/status-dev-success)](https://github.com/mauriciomani/odyssey)

<br>
Odyssey makes super easy predicting either a single element or a whole file. We aim to be "cloud agnostic", however currently only working on Sagemaker (endpoint deployment and batch-transform) and working on improving serverless AWS lambda's.
This is as simple as Cookiecooter command line file making, combined with AWS bring your own to easily deploy machine learning models. Yeah, we are a command line tool!
<br>

## AWS Sagemaker
For AWS Sagemaker it is as simple as:

```
$ pip install git+https://github.com/mauriciomani/odyssey.git
$ odyssey init -p aws -s sagemaker start
$ cd testapp
$ odyssey configure
$ odyssey docker -n testapp build
$ odyssey docker -n testapp push
$ odyssey sagemaker -r arn:aws:iam::__rolename__:role/sagemaker_role -n testapp train -i s3://testapp/app_folder/input/data/training/iris.data -m s3://testapp/app_folder/model/

$ odyssey sagemaker -r arn:aws:iam::__rolename__:role/sagemaker_role -n testapp serve -m s3://testapp/app_folder/model/testapp-timestamp/output/model.tar.gz --endpoint-name testapp

$ odyssey sagemaker -r arn:aws:iam::__rolename__:role/sagemaker_role -n testapp batch-transform -m s3://testapp/app_folder/model/testapp-timestamp/output/model.tar.gz -o s3://testapp/app_folder/output/ -i s3://testapp/app_folder/input/data/iris.csv
```

The **p** argument stands for the cloud provider and the **s** for the service. Be aware that the service needs to be a service provided by the cloud provider. You will need to name your app, for example testapp. Inside the created folder kindly add the train and serve logic, under the train.py and serve.py. Then you have to build the docker image, kindly add the requierements under the requierements file provided (be aware that if you pip freeze to add the requierements remove the odyssey library since it is not necessary), the **n** argument is optional and if not provided the name of the app will be used. Then you need to add **input/data/training** path under a given folder inside any wanted bucket, plus **model** and **output** folder (output only if considering multiple observations). Inside training, kindly provide the data for training. That is all you have to do inside s3, plus use **odyssey configure** that is only an aws configure implementation, for more information regarding IAM roles, please look under **Cloud Permissions**. Then push the docker image, after that you can train inside sagemaker, you can provide the **number, c** of instances and the **type, in** of instance, you will need to provide the **role**, the **name, n** of the image, the **input, i**, that is the complete path to the training file, and the place were you will save the **model, m**, again the s3 path. Finally we can either **serve an endpoint**, or **batch-transform** (again, number of instances and type of instances can be provided). For both models this time you need to provide the whole model path, (model.tar.gz). For the former, you need to provide the endpoint name. For the latter, the place were the **output, o** will be saved and the **input, i** to predict. Split-type, strategy and content-type can also be provided.


### Helpful commands
We have also provided a series of commands that will help you make sure your app is ready before training and predicting on sagemaker but even better before pushing your docker image. Those commands are:

```
$ odyssey local train
$ odyssey local serve
```

In order to use this you will need to add into the provided paths the input data and once trained the models will be saved under model. Once the image has been built you can also train and serve the image:

```
$ odyssey docker -n testapp build
$ odyssey docker -n testapp train
$ odyssey docker -n testapp serve
```

Once you have made sure train and serve under the docker image works properly, you can push it. For more information you can always use `odyssey --help` or `odyssey docker --help` or even `odyssey docker train --help`.


### Cloud permissions
In order to succesfully run everything from pushing the image to serving the app on sagemaker. You need to create a role and a user. The role is Sagemaker oriented, but the user needs the following permissions:
* AmazonEC2ContainerRegistryFullAccess
* EC2InstanceProfileForImageBuilderECRContainerBuilds
* AmazonS3FullAccess
* AmazonSageMakerFullAccess

Kindly make sure your created role with following policies attached:
* AmazonS3FullAccess
* AmazonSageMakerFullAccess


### What are train and serve files?
Train files are those that will **create the model**, a model that is reusable. For example, say you want to predict churn of customers, then you can use any [scikit-learn](https://scikit-learn.org/stable/), [tensorflow](https://www.tensorflow.org/?hl=es-419), [pytorch](https://pytorch.org/), or any other, such as [implicit](https://implicit.readthedocs.io/en/latest/) for recommendations etc. and you can even use other objects such as dictionaries (that will work as models) that includes all the customers that will churn and save that as a json file. Plus, you can save various files, for example, a pickle and a json. You can also use [pandas](https://pandas.pydata.org/), [dask](https://dask.org/) or any other python library. The main goal of a **train file** is to save that created model. Taking into consideration that, we will use it to make predictions, either, following the example, a single customer or file containing various customers.
Once we have the model obtained from the train file we can use the **serve file** to create the necessary preprocessing for the input and pass it to the already saved model, for example with the **predict method** from the model and then return that data. Say you create a web app that consumes the information from a single customer, then you will send that to the serve file and the serve file can return, for example, a json file that can be consumed by the web app.
**odyssey** create a template for train and serve applications where you can easily add the logic for training and serving. Be aware that **you can add any other file needed or function inside the given train template**, for example a utils file that can be consumed by train or serve template or both.


### Difference between a single observation and multiple observations
Currently, when predicting single observations you want your endpoint to be upp at all time. If you do not want this, you can still use multiple observations just be aware you will need to change some code in the rocket path. Sending a single observation can be a json as an input and a json as an output as well. For example: `{"customer": [1, 2, 3, 4, 5]}` we can extract the **key** customer, and we will have a list containing all the 5 attributes for customers that we will be passed to the model's object. Then we can return, for example, `{"predictions": 0}`. Now imagine you need to predict a whole file every day or every week with a lot of customers, then you can do, what in the jargon of AWS is called **batch-transform**. This mean we will input a csv and output a csv as well.


### Having my models in a Jupyter Notebook
In the future **Odyssey** will include the option to upload your pickle models, this being said, if you do not want to train on a regular basis you can push the model and serve. However, you still need to push the model and have a serve file to handle the requests. Commonly when working on a [Jupyter Notebook](https://jupyter.org/) the logic for training is accurately written, except for some problems regarding ordering incorrectly the cells. So you just have to copy the code of the cells into the train function and write the created model to the **model_path**. You can also create a whole class for preprocessing in a different file and consume it inside the train file. 
However, **you need to add** the serve logic. Where you need to think about the format of the current input of the data and the expected output. That expected output will be placed in the return statement. For example if that return file is a csv, due to expecting multiple observations you can return the data as pandas and odyssey will deal with the rest to convert to a csv. 


### The rocket app (AWS Sagemaker)
Odyssey creates one very important folder where all the magic happens: the **rocket** folder. You can modify it if necessary, you can always modify it and if you do not like the results (screw it) just create a new one. But is highly recommend you do not do it unless you know what your are doing. In a nutshell, you have a flask app called **predictor.py** that handle all the input and outputs, you have a **wsgi.py** and a **nginx.conf** files that the only proposed modifications are to completely remove (with the necessary modifications) and a **train** and **serve**. The latter call both respective files inside your created app. The files that continously can be modified are **predictor.py** and **serve**. In the former you can add more input types and output types, for example. In the latter you can have larger response times.
**Again, it is strongly suggested not to modify anything, except for train.py and serve.py (outside of rocket), unless you know what you are doing**.


## AWS Serverless Lambda Functions
Serverless functions have the goal of building agile applications to respond easily to changes. Managing the infraestructure is no longer necessary, you just have to worry about the code, serverless services have automatic scaling, high availability and pay for use. With this you can move faster, at your own rythm, with low-costs


### Odyssey and Lambda
You just need of 5 lines of tools. Initizaling the application, cloud provider **p** the same, but service **s** is now different, you have to specify **lambda**.
Modify the dockerfile, add train and serve logic and **build** and **push** the application just as you would in aws sagemaker. You can provide the timeout and memory, both would be good to have high values, for example 59 seconds and 256MB, as the example below. You also need to spcify region, role and image name, this is different to the name of the app.

It is very important you do not change the function parameters of application, once done that you can call odyssey train and odyssey serve to create respective functions, currently we do not have command lines to call the service.

```
$ pip install git+https://github.com/mauriciomani/odyssey.git
$ odyssey init -p aws -s lambda start
$ odyssey docker -n testlambda build
$ odyssey docker -n testlambda push
$ odyssey lambda -t 59 --memory 256 --region us_east_1 --role arn:aws:iam::__rolename__:role/lambda_role train --image lambda_image -n train
$ odyssey lambda -t 59 --memory 256 --region us_east_1 --role arn:aws:iam::__rolename__:role/lambda_role --image lambda_image serve -n serve
```

## Examples
Kindly visit our [examples path](examples) to check how to implement odyssey for Sagemaker batch-transform, endpoint deployment and serverless AWS lambda functions.


## Next Steps
* Create request cloud in sagemaker.
* Improve Sagemaker endpoint (docker & architecture).
* Add sagemaker possibility of hyperparameters.
* Avoid using complete path on train.
* Option to upload sagemaker model.
* Train lambda locally.
* Make sure roles are minimum.
* Add airflow init.
* Add Jenkins pipeline.
* Add AWS EC2.
* Price comparison for AWS products.
* Agnostic tool, research Azure, and Google Cloud.