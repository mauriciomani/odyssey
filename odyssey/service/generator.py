import logging
import os

logger = logging.getLogger(__name__)


class Generator():
    """
    This class currently creates the Sagemaker AWS files.
    """
    def __init__(self, provider, service):
        self.provider = provider
        self.service = service
        self.app_name = None
        self.sagemaker_app = "rocket"
        self.bucket = None
        self.data_path = None
        self.model_path = None

    def generate_files(self):
        """
        Generate the odissey app.
        We keep the input/data/training; model; output currently.
        """
        self.app_name = input("1. Name of app: ")
        os.mkdir(self.app_name)
        if self.provider == "aws":
            os.mkdir(os.path.join(self.app_name, "input"))
            os.mkdir(os.path.join(self.app_name, "input/data"))
            os.mkdir(os.path.join(self.app_name, "input/data/training"))
            os.mkdir(os.path.join(self.app_name, "output"))
            os.mkdir(os.path.join(self.app_name, "model"))
            if ((self.service == "sagemaker") or (self.service is None)):
                self.generate_sagemaker_aws()
            elif self.service == "lambda":
                print("Making progress already! Kindly fill the information provided. You can change this later. You can always pass.")
                # Consider adding a wrapper
                self.bucket = input("2. Name of Bucket: ")
                if self.bucket == "":
                    self.bucket = '""'
                self.data_path = input("3. Input data path [do not add the bucket]: ") 
                if self.data_path == "":
                    self.data_path = '""'
                self.model_path = input("4. Model path [do not add the bucket]: ")
                if self.model_path == "":
                    self.model_path = '""'
                self.generate_lambda_aws()
            elif self.service == "ec2":
                pass
            else:
                self.generate_sagemaker_aws()
        else:
            pass

    def generate_lambda_aws(self):
        """
        This generate all the necessary files
        in order to create serverless ML app.
        In this case there is no rocket application
        inside created app.
        """
        logger.debug("Generating project for AWS lambda")

        def generate_app():
            script_name = "app.py"
            save_path = os.path.join(self.app_name, script_name)
            # This very complicated
            script = 'import json\nimport pickle\nimport boto3\n\n\ndef train(event, context):\n    """\n    This function trains a particular ML problem.\n    It can be useful for a daily training.\n    The pickle model is sabed in particular model path inside given bucket.\n    Parameters\n    ----------\n    event : json\n        Carries the input parameter\n    context : json\n        Provides methods and properties about invocation, function and execution of lambda.\n\n    Returns\n    -------\n    None\n    """\n    session = boto3.session.Session()\n    s3_resource = session.client("s3")\n    # No need to use event or context. Do not remove.\n    bucket = {bucket}\n    # This includes the name of the input file \n    data_path = {dp}\n    # Can use response body if using pandas you do not need to read\n    #response = s3_resource.get_object(Bucket=bucket, Key=data_path)\n    # No need to add bucket\n    model_path = {mp}\n    #binary_model = pickle.dumps(model_object)\n    #s3_resource.put_object(Bucket=bucket, Key=model_path, Body=binary_model)\n\n\ndef serve(event, context):\n    """\n    This function saves the model from train inside tmp.\n    Load it and use it to predict from event parameter input.\n    Finally returns prediction.\n    Parameters\n    ----------\n    event : json\n        Carries the input parameter\n    context : json\n        Provides methods and properties about invocation, function and execution of lambda.\n\n    Returns\n    -------\n    json\n        Kindly change the format if needed\n    """\n    # This function uses event, however most sure you will not be using context.\n    s3 = boto3.client("s3")\n    # Kindly add the model_name as well\n    model_path = {mp}\n'.format(bucket=self.bucket, dp=self.data_path, mp=self.model_path) + '    model_name = model_path.split("/")[-1]\n    temp_file_path = "/tmp/" + model_name\n    #s3.download_file(bucket, model_path, temp_file_path)\n    #with open(temp_file_path, "rb") as f:\n    #    model = pickle.load(f)\n\n    # Kindy use event as the input of the lambda function\n    # Be aware data needs to be preprocessed and most sure comes from event.\n    #predictions = model.predict(data)\n    #output = {"prediction": int(predictions[0])}\n    #output = json.dumps(output)\n    #return(output)\n'
            f = open(save_path, "w")
            f.write(script)
            f.close()

        def generate_docker():
            """
            Generate the Dockerfile
            """
            script_name = "Dockerfile"
            save_path = os.path.join(self.app_name, script_name)
            script = '# https://hub.docker.com/r/amazon/aws-lambda-python\nFROM public.ecr.aws/lambda/python:3.8\n\n# Copy function code\nCOPY app.py ./\n\nCOPY requirements.txt requirements.txt\n\nRUN pip --no-cache-dir install -r requirements.txt\n\n# If only serve set the CMD to your handler, E.g. CMD ["app.train"]'
            f = open(save_path, "w")
            f.write(script)
            f.close()

        def generate_requirements():
            """
            Generate the requirements file
            """
            script_name = "requirements.txt"
            save_path = os.path.join(self.app_name, script_name)
            f = open(save_path, "w")
            f.close()

        generate_app()
        generate_docker()
        generate_requirements()


    def generate_sagemaker_aws(self):
        """
        This generate all the necessary files
        in order to bring your own application.
        """
        logger.debug('Generating project for AWS Sagemaker')
        os.mkdir(os.path.join(self.app_name, "rocket"))

        def generate_train():
            """
            Generate train file
            """
            script_name = "train.py"
            save_path = os.path.join(self.app_name, script_name)
            script = 'import pickle\nimport os\n\ndef train(input_path, model_path, param_path=None):\n    """\n    Write the necessary logic for a train procedure. \n    Input data path provides the place where input data has been placed.\n    In this function nothing is returned. You can add paramaters. However, you cannot delete them.\n    Parameters\n    ----------\n    input_path : str\n        Place wwhere input data is store \n    model_path : str\n        Place wehere model is store.\n    param_path : str [None]\n        Place wehere params for the model are stored.\n\n    Returns\n    -------\n    None\n        You need to save your model\n    """\n\n    #example for saving your model, you have to change model name, can save any number of models\n    #model_path = os.path.join(model_path, model_name)\n    #pickle.dump(model, open(model_path, "wb"))\n'
            f = open(save_path, "w")
            f.write(script)
            f.close()

        def generate_serve():
            """
            Generate serve file
            """
            script_name = "serve.py"
            save_path = os.path.join(self.app_name, script_name)
            script = '''import pickle\nimport os\n\n# We try to create a singleton for holding the model. This simply loads the model and holds it.\n# It has a predict function that does a prediction based on the model and the input data.\n\n\ndef get_model(model_save_path):\n    """\n    This function imports the model(s) generated by the train.py file.\n    Please add model name. Remember is not necessary to have only one model but can import multiple.\n    Return models if more than 1 as a list of models.\n    Parameters\n    ----------\n    model_save_path : str\n        Place where model is stored\n    \n    Returns\n    -------\n    ML object\n        Use any python ML library\n    """\n    model_name = ""\n    model_path = os.path.join(model_save_path, model_name)\n    loaded_model = pickle.load(open(model_path, "rb"))\n    return(loaded_model)\n\n\ndef predict(input_data, model):\n    """\n    This functions is used to predict input_data using model.\n    Predictions are returned to be used, can either be json, csv, parquet, float or any data type.\n    Parameters\n    ----------\n    inut_data : json | csv | parquet \n        can be either single or batch transform\n    model : ML object\n        imported by import_models\n    \n    Returns\n    -------\n    json | csv | float\n        Any file that fit needs\n    """\n    predictions = model.predict(input_data)\n    return(predictions)'''
            f = open(save_path, "w")
            f.write(script)
            f.close()

        def generate_docker():
            """
            Generate the Dockerfile
            """
            script_name = "Dockerfile"
            save_path = os.path.join(self.app_name, script_name)
            script = 'FROM ubuntu:18.04\n\nRUN apt-get -y update && apt-get install -y --no-install-recommends \\\n         wget \\\n         python3-pip \\\n         python3-setuptools \\\n         nginx \\\n         ca-certificates \\\n    && rm -rf /var/lib/apt/lists/*\n\nRUN ln -s /usr/bin/python3 /usr/bin/python\nRUN ln -s /usr/bin/pip3 /usr/bin/pip\n\nCOPY ./ /opt/program\nWORKDIR /opt/program\n\nRUN chmod +x rocket/train\nRUN chmod +x rocket/serve\n\nRUN pip --no-cache-dir install -r requirements.txt\n\nENV PYTHONUNBUFFERED=TRUE\nENV PYTHONDONTWRITEBYTECODE=TRUE\nENV PATH="/opt/program/rocket:${PATH}"\n'
            f = open(save_path, "w")
            f.write(script)
            f.close()

        def generate_requirements():
            """
            Generate the requirements file
            """
            script_name = "requirements.txt"
            save_path = os.path.join(self.app_name, script_name)
            script = 'Flask>=1.1.2\ngunicorn>=20.1.0\n'
            f = open(save_path, "w")
            f.write(script)
            f.close()

        def generate_rocket_app():
            """
            Generate all rocket. This is were all the magic happens.
            rocket is the path were all sagemaker train and serve is hold.
            Plus it contains the flask application.
            """
            train_name = "train"
            train_save_path = os.path.join(self.app_name, self.sagemaker_app, train_name)
            train_script = '#!/usr/bin/env python\n\n# Change from statement into a built-in function\nfrom __future__ import print_function\nimport sys\nimport os\nsys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))\nfrom train import train\nimport os\nimport json\nimport pickle\nimport traceback\n\n# These are the paths to where SageMaker mounts interesting things in your container.\n\ncwd = os.getcwd()\nif cwd.find("/opt/program") >= 0:\n    print("Working on Cloud")\n    prefix = \'/opt/ml/\'\n    input_path = prefix + \'input/data\'\n    output_path = os.path.join(prefix, \'output\')\n    model_path = os.path.join(prefix, \'model\')\n    param_path = os.path.join(prefix, \'input/config/hyperparameters.json\')\nelse:\n    print("Working locally")\n    input_path = \'input/data\'\n    output_path = \'output\'\n    model_path = \'model\'\n    param_path = \'input/config/hyperparameters.json\'\n\n# This algorithm has a single channel of input data called \'training\'. Since we run in\n# File mode, the input files are copied to the directory specified here.\nchannel_name = \'training\'\ntraining_path = os.path.join(input_path, channel_name)\n\n# The function to execute the training.\ndef rocket_train():\n    print(\'Starting the training.\')\n    try:\n        train(training_path, model_path)\n        print(\'Training complete.\')\n    except Exception as e:\n        # Write out an error file. This will be returned as the failureReason in the\n        # DescribeTrainingJob result.\n        trc = traceback.format_exc()\n        with open(os.path.join(output_path, \'failure\'), \'w+\') as s:\n            s.write(\'Exception during training: \' + str(e) + \'\\n\' + trc)\n        # Printing this causes the exception to be in the training job logs, as well.\n        print(\'Exception during training: \' + str(e) + \'\\n\' + trc, file=sys.stderr)\n        # A non-zero exit code causes the training job to be marked as Failed.\n        sys.exit(255)\n\n\nif __name__ == \'__main__\':\n    rocket_train()\n\n    # A zero exit code causes the job to be marked a Succeeded.\n    sys.exit(0)\n'
            f = open(train_save_path, "w")
            f.write(train_script)
            f.close()

            serve_name = "serve"
            serve_save_path = os.path.join(self.app_name, self.sagemaker_app, serve_name)
            serve_script = '#!/usr/bin/env python\n\n# This file implements the scoring service shell. You don\'t necessarily need to modify it for various\n# algorithms. It starts nginx and gunicorn with the correct configurations and then simply waits until\n# gunicorn exits.\n#\n# The flask server is specified to be the app object in wsgi.py\n#\n# We set the following parameters:\n#\n# Parameter                Environment Variable              Default Value\n# ---------                --------------------              -------------\n# number of workers        MODEL_SERVER_WORKERS              the number of CPU cores\n# timeout                  MODEL_SERVER_TIMEOUT              60 seconds\n\nimport multiprocessing\nimport os\n# For some reason not inside rocket\nos.chdir("rocket")\nimport signal\nimport subprocess\nimport sys\n\ncpu_count = multiprocessing.cpu_count()\n\nmodel_server_timeout = os.environ.get(\'MODEL_SERVER_TIMEOUT\', 60)\nmodel_server_workers = int(os.environ.get(\'MODEL_SERVER_WORKERS\', cpu_count))\n\ndef sigterm_handler(nginx_pid, gunicorn_pid):\n    try:\n        os.kill(nginx_pid, signal.SIGQUIT)\n    except OSError:\n        pass\n    try:\n        os.kill(gunicorn_pid, signal.SIGTERM)\n    except OSError:\n        pass\n\n    sys.exit(0)\n\ndef start_server():\n    print(\'Starting the inference server with {} workers.\'.format(model_server_workers))\n\n    cwd = os.getcwd()\n    if cwd.find("/opt/program") >= 0:\n        # link the log streams to stdout/err so they will be logged to the container logs\n        subprocess.check_call([\'ln\', \'-sf\', \'/dev/stdout\', \'/var/log/nginx/access.log\'])\n        subprocess.check_call([\'ln\', \'-sf\', \'/dev/stderr\', \'/var/log/nginx/error.log\'])\n\n        nginx = subprocess.Popen([\'nginx\', \'-c\', \'/opt/program/rocket/nginx.conf\'])\n    else:\n        nginx = subprocess.Popen([\'nginx\', \'-c\', cwd + "/nginx.conf"])\n\n    gunicorn = subprocess.Popen([\'gunicorn\',\n                                 \'--timeout\', str(model_server_timeout),\n                                 \'-k\', \'sync\',\n                                 \'-b\', \'unix:/tmp/gunicorn.sock\',\n                                 \'-w\', str(model_server_workers),\n                                 \'wsgi:app\'])\n\n    signal.signal(signal.SIGTERM, lambda a, b: sigterm_handler(nginx.pid, gunicorn.pid))\n\n    # If either subprocess exits, so do we.\n    pids = set([nginx.pid, gunicorn.pid])\n    while True:\n        pid, _ = os.wait()\n        if pid in pids:\n            break\n\n    sigterm_handler(nginx.pid, gunicorn.pid)\n    print(\'Inference server exiting\')\n\n# The main routine just invokes the start function.\n\nif __name__ == \'__main__\':\n    start_server()'
            f = open(serve_save_path, "w")
            f.write(serve_script)
            f.close()

            wsgi_app = "wsgi.py"
            wsgi_save_path = os.path.join(self.app_name, self.sagemaker_app, wsgi_app)
            wsgi_script = 'import predictor as myapp\n\n# This is just a simple wrapper for gunicorn to find your app.\n# If you want to change the algorithm file, simply change "predictor" above to the new file.\n# This might not be necessary. Kindly double check.\n\napp = myapp.app'
            f = open(wsgi_save_path, "w")
            f.write(wsgi_script)
            f.close()

            predictor_app = "predictor.py"
            predictor_save_path = os.path.join(self.app_name, self.sagemaker_app, predictor_app)
            predictor_script = 'from __future__ import print_function\n\nimport os\nimport sys\nsys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))\nimport json\nimport pickle\nimport io\nimport sys\nimport signal\nimport traceback\nimport flask\nimport pandas as pd\nimport serve\nimport json\n\ncwd = os.getcwd()\nif cwd.find("/opt/program") >= 0:\n    prefix = \'/opt/ml/\'\n    model_path = os.path.join(prefix, \'model\')\nelse:\n    os.chdir(\'..\')\n    model_path = \'model\'\n\n# The flask app for serving predictions\napp = flask.Flask(__name__)\n\n@app.route(\'/ping\', methods=[\'GET\'])\ndef ping():\n    """\n    Determine if the container is working and healthy. \n    In this sample container, we declare it healthy if we can load the model successfully.\n    """\n    health = serve.get_model(model_path) is not None  # You can insert more health check here\n\n    status = 200 if health else 404\n    return flask.Response(response=\'\\n\', status=status, mimetype=\'application/json\')\n\n\n@app.route(\'/invocations\', methods=[\'POST\'])\ndef transformation():\n    """\n    Do an inference on either an endpoint or single batch of data. \n    It depends on the type of data you sending.\n    We take data as csv and convert to pandas data frame for internal use \n    this is the input_data of the serve.py file.\n    Then convert the predictions back to CSV.\n    """\n    data = None\n    batch_transform = False\n\n    # Convert from CSV to pandas. If not csv the kindly change this.\n    if flask.request.content_type == \'text/csv\':\n        batch_transform = True\n        data = flask.request.data.decode(\'utf-8\')\n        s = io.StringIO(data)\n        # If needed specific parameters when\n        data = pd.read_csv(s)\n        print(\'Invoked with {} records\'.format(data.shape[0]))\n    elif flask.request.content_type == "application/json":\n        # Do not know if keeping here or on serve\n        data = json.loads(flask.request.data)\n    else:\n        return flask.Response(response=\'This predictor only supports CSV data or json\', status=415, mimetype=\'text/plain\')\n\n    # Do the prediction\n    model = serve.get_model(model_path)\n    predictions = serve.predict(data, model)\n\n    if batch_transform:\n        # Convert from numpy back to CSV\n        out = io.StringIO()\n        # Save the csv\n        predictions.to_csv(out, header=False, index=False)\n        result = out.getvalue()\n        return flask.Response(response=result, status=200, mimetype=\'text/csv\')\n    else:\n        return flask.Response(response=predictions, status=200, mimetype=\'application/json\')\n'
            f = open(predictor_save_path, "w")
            f.write(predictor_script)
            f.close()

            nginx_app = "nginx.conf"
            nginx_save_path = os.path.join(self.app_name, self.sagemaker_app, nginx_app)
            nginx_script = 'worker_processes 1;\ndaemon off; # Prevent forking\n\n\npid /tmp/nginx.pid;\nerror_log /var/log/nginx/error.log;\n\nevents {\n  # defaults\n}\n\nhttp {\n  include /etc/nginx/mime.types;\n  default_type application/octet-stream;\n  access_log /var/log/nginx/access.log combined;\n  \n  upstream gunicorn {\n    server unix:/tmp/gunicorn.sock;\n  }\n\n  server {\n    listen 8080 deferred;\n    client_max_body_size 5m;\n\n    keepalive_timeout 5;\n    proxy_read_timeout 1200s;\n\n    location ~ ^/(ping|invocations) {\n      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n      proxy_set_header Host $http_host;\n      proxy_redirect off;\n      proxy_pass http://gunicorn;\n    }\n\n    location / {\n      return 404 "{}";\n    }\n  }\n}\n'
            f = open(nginx_save_path, "w")
            f.write(nginx_script)
            f.close()

        # Might be a smarter way to achieve this
        generate_train()
        generate_serve()
        generate_docker()
        generate_requirements()
        generate_rocket_app()
