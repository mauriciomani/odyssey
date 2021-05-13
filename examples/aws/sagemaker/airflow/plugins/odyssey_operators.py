from airflow.operators.bash import BashOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults
import boto3
import logging


logging = logging.getLogger(__name__)
s3_client = boto3.client('s3')

class OdysseySagemakerTrain(BashOperator):
    """
    A class used to create odyssey train operator.
    """
    @apply_defaults
    def __init__(self,
                 role,
                 image_name,
                 input_path,
                 model_path,
                 *args, **kwargs):
        """
        Parameters
        ----------
        role : str
            Role to execute train command
        image_name : str
            Name of the image from the buid and push command
        input_path : str
            S3 path to the input file
        model_path : str
            S3 path to where model be saved
        """
        self.role = role
        self.image_name = image_name
        self.input_path = input_path
        self.model_path = model_path
        self.bash_command = ""
        super(OdysseySagemakerTrain, self).__init__(bash_command=self.bash_command,
                                                    role=role,
                                                    image_name=image_name,
                                                    input_path=input_path,
                                                    model_path=model_path,
                                                    *args, **kwargs)

    def execute(self, context):
        """
        This function deals with the execution of odyssey train.
        """
        logging.info("Sagemaker role is {}".format(self.role))
        logging.info("Image name is {}".format(self.image_name))
        logging.info("S3 input path is {}".format(self.input_path))
        logging.info("S3 model path is {}".format(self.model_path))
        self.bash_command = "odyssey sagemaker -r {role} -n {image} train -i {input_path} -m {model_path}".format(role=self.role, image=self.image_name, input_path=self.input_path, model_path=self.model_path)
        logging.info("Executing Sagemaker Odyssey train.")
        super(OdysseySagemakerTrain, self).execute(context)
        logging.info("Execution has been finished.")


class OdysseySagemakerServe(BashOperator):
    """
    A class used to create odyssey serve operator.
    """
    @apply_defaults
    def __init__(self,
                 role,
                 image_name,
                 endpoint_name,
                 bucket,
                 odyssey_app,
                 *args, **kwargs):
        """
        Parameters
        ----------
        role : str
            Role to execute train command
        image_name : str
            Name of the image from the buid and push command
        endpoint_name : str
            Name to give to the endpoint
        bucket : str
            Name of the bucket. It will select most recent model
        odyssey_app : str
            Name of the folder that stores the input, model, output structure
        """
        self.role = role
        self.image_name = image_name
        self.endpoint_name = endpoint_name
        self.bucket = bucket
        if self.image_name.find("_") >= 0:
            base_job_name = odyssey_app + "/model/" + self.image_name.replace("_", "-")
        else:
            base_job_name = odyssey_app + "/model/" + self.image_name
        try:
            get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
            objs = s3_client.list_objects_v2(Bucket=self.bucket,
                                             Prefix=base_job_name)["Contents"]
            self.model_path = "s3://" + self.bucket + "/" + [obj['Key'] for obj in sorted(objs, key=get_last_modified, reverse=True)][0]
        except:
            self.model_path = ""
        self.bash_command = ""
        super(OdysseySagemakerServe, self).__init__(bash_command=self.bash_command,
                                                    role=role,
                                                    image_name=image_name,
                                                    endpoint_name=endpoint_name,
                                                    bucket=bucket,
                                                    odyssey_app=odyssey_app,
                                                    *args, **kwargs)

    def execute(self, context):
        """
        This function deals with the execution of odyssey serve.
        """
        logging.info("Sagemaker role is {}".format(self.role))
        logging.info("Image name is {}".format(self.image_name))
        logging.info("S3 model path is {}".format(self.model_path))
        logging.info("Enpoint name is {}".format(self.endpoint_name))
        self.bash_command = "odyssey sagemaker -r {role} -n {image} serve -m {model} --endpoint-name {endpoint_name}".format(role=self.role, image=self.image_name, model=self.model_path, endpoint_name=self.endpoint_name)
        logging.info("Executing Sagemaker Odyssey Serve.")
        super(OdysseySagemakerServe, self).execute(context)
        logging.info("Execution has been finished.")


# try extracting the bucket automatically
class OdysseySagemakerBatchTransform(BashOperator):
    """
    A class used to create odyssey batch transform operator.
    """
    @apply_defaults
    def __init__(self,
                 role,
                 image_name,
                 output_path,
                 input_path,
                 bucket,
                 odyssey_app,
                 *args, **kwargs):
        """
        Parameters
        ----------
        role : str
            Role to execute train command
        image_name : str
            Name of the image from the buid and push command
        output_path : str
            Path to S3 folder where output will be stored
        input_path : str
            Path to S3 folder where input is stored. Complete path
        bucket : str
            Name of the bucket. It will select most recent model
        odyssey_app : str
            Name of the folder that stores the input, model, output structure
        """
        self.role = role
        self.image_name = image_name
        self.output_path = output_path
        self.input_path = input_path
        self.bucket = bucket
        if self.image_name.find("_") >= 0:
            base_job_name = odyssey_app + "/model/" + self.image_name.replace("_", "-")
        else:
            base_job_name = odyssey_app + "/model/" + self.image_name
        try:
            get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
            objs = s3_client.list_objects_v2(Bucket=self.bucket,
                                         Prefix=base_job_name)["Contents"]
            self.model_path = "s3://" + self.bucket + "/" + [obj['Key'] for obj in sorted(objs, key=get_last_modified, reverse=True)][0]
        except:
            self.model_path = ""
        self.bash_command = ""
        super(OdysseySagemakerBatchTransform, self).__init__(bash_command=self.bash_command,
                                                             role=role,
                                                             image_name=image_name,
                                                             output_path=output_path,
                                                             input_path=input_path,
                                                             bucket=bucket,
                                                             odyssey_app=odyssey_app,
                                                             *args, **kwargs)

    def execute(self, context):
        """
        This function deals with the execution of odyssey batch-transform.
        """
        logging.info("Sagemaker role is {}".format(self.role))
        logging.info("Image name is {}".format(self.image_name))
        logging.info("S3 model path is {}".format(self.model_path))
        logging.info("S3 output path is {}".format(self.output_path))
        logging.info("S3 input path is {}".format(self.input_path))
        self.bash_command = "odyssey sagemaker -r {role} -n {image} batch-transform -m {model} -o {output} -i {input}".format(role=self.role, image=self.image_name, model=self.model_path, output=self.output_path, input=self.input_path)
        print(self.model_path)
        print(self.bash_command)
        logging.info("Executing Sagemaker Odyssey Serve.")
        super(OdysseySagemakerBatchTransform, self).execute(context)
        logging.info("Execution has been finished.")


class OdysseyPlugin(AirflowPlugin):
    """
    A class used to specify the airflow operators:
    * train
    * serve and 
    * batch-transform
    Be aware serve and batch-transform are exclusive.
    """
    name = "odyssey_plugin"
    operators = [OdysseySagemakerTrain,
                 OdysseySagemakerServe,
                 OdysseySagemakerBatchTransform]
