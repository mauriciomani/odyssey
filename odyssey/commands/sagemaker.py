import click
import os
import boto3
from sagemaker import get_execution_role
import sagemaker as sage


# We can add logic here to upload data to s3 as well

class CloudInfo:
    """
    Class to store the necessary information of AWS cloud provider.
    """
    def __init__(self, instance, role, name, count=1):
        # Can be the name of the root folder
        self.name = name
        self.instance = instance
        self.count = count
        # Define IAM role
        self.role = role
        # Create session
        self.session = sage.Session()
        self.account =  self.session.boto_session.client('sts').get_caller_identity()['Account']
        self.region = self.session.boto_session.region_name
        self.image = '{}.dkr.ecr.{}.amazonaws.com/{}:latest'.format(self.account, self.region, self.name)


@click.group()
@click.option("-in", "--instance", type=str, help="Instance machine for training the model")
@click.option("-c", "--count", type=int, help="Number of instances to use")
@click.option("-r", "--role", type=str, help="Kindly create the execution role for sagemaker under IAM.")
@click.option("-n", "--name", type=str, help="Name of the image")
@click.pass_context
def cli(ctx, instance, count, role, name):
    """
    Strongly recommend creating a folder inside any given bucket.
    This folder needs the following structure:
    input -> data -> training
    model
    output
    In case you are deploying and endpoint, output is not necessary.
    """
    if count is None:
        count = 1
    if instance is None:
        # Since it is the smallest one
        instance = "ml.m5.large"
    if name is None:
        name = os.path.basename(os.getcwd())
        click.echo("Image name not provided, then will be used: " + click.style(name, bold=True))
    ctx.obj = CloudInfo(instance, role, name, count)
    click.echo("Role is {}".format(ctx.obj.role))
    click.echo("Instance machine name {}".format(ctx.obj.instance))


@cli.command()
@click.option("-i", "--input", type=str, help="Input of the model. Has to be all the s3 path")
@click.option("-m", "--model", type=str, help="Where to save the model. Has to be all the s3 path")
@click.pass_context
def train(ctx, input, model):
    """
    This will work for both endpoint deployments and batch-transforms.
    Is important that you provide both input and model. 
    The latter is the location where you will store the model.tar.gz
    """
    model = sage.estimator.Estimator(ctx.obj.image, 
                                     ctx.obj.role,
                                     instance_count=ctx.obj.count,
                                     instance_type=ctx.obj.instance,
                                     output_path=model,
                                     sagemaker_session=ctx.obj.session,
                                     disable_profiler=True)
    model.fit(input)


@cli.command()
@click.option("--content-type", type=str, help="Content type for example text/csv")
@click.option("--split-type", type=str, help="Split type, for example Line")
@click.option("-o", "--output", type=str, help="Output of the model. Has to be all the s3 path")
@click.option("-m", "--model", type=str, help="Model artifact. Has to be all the s3 path")
@click.option("-i", "--input", type=str, help="Input data, that is going to be predicted. Has to be all the s3 path")
@click.option("--strategy", type=str, help="Strategy to use on batch records")
@click.pass_context
def batch_transform(ctx, content_type, split_type, output, model, input, strategy):
    """
    Perform a sagemaker batch transform. 
    It is important that instance_count and instance_type is brought befor batch_transform.
    If split-type not selected the Line as default.
    If content-type not selected used text/csv.
    If strategy not selected used MultiRecord.
    """
    if split_type == None:
        split_type = "Line"
    if content_type == None:
        content_type = "text/csv"
    if strategy == None:
        strategy = "MultiRecord"
    # Sagemaker model object can receive a parameter for model name, call name.
    model_name = model[model.find("model/") + 6 : model.find("/output")]
    # print("Name of the model is {}".format(model_name))
    
    model = sage.model.Model(ctx.obj.image, 
                             model_data=model,
                             role=ctx.obj.role, 
                             sagemaker_session=ctx.obj.session)
    
    transformer = model.transformer(instance_count = ctx.obj.count,
                                    instance_type = ctx.obj.instance,
                                    output_path = output)

    transformer.transform(input, content_type = content_type, split_type=split_type)      


# Kindly add more arguments
@cli.command()
@click.option("--endpoint-name", type=str, help="Name to give to the endpoint")
@click.option("-m", "--model", type=str, help="Model artifact. Has to be all the s3 path")
@click.pass_context
def serve(ctx, model, endpoint_name):
    """
    Perform a sagemaker batch transform. 
    It is important that instance_count and instance_type is brought befor batch_transform.
    If split-type not selected the Line as default.
    If content-type not selected used text/csv.
    If strategy not selected used MultiRecord.
    """
    if endpoint_name == None:
        endpoint_name = ctx.obj.name

    # Sagemaker model object can receive a parameter for model name, call name.
    model_name = model[model.find("model/") + 6 : model.find("/output")]
    # print("Name of the model is {}".format(model_name))
    
    model = sage.model.Model(ctx.obj.image, 
                             model_data=model,
                             role=ctx.obj.role, 
                             sagemaker_session=ctx.obj.session)

    model.deploy(initial_instance_count=ctx.obj.count,
                 instance_type=ctx.obj.instance,
                 endpoint_name=endpoint_name)                  
    
    click.echo("Model successfully deployed with name {}!".format(endpoint_name))