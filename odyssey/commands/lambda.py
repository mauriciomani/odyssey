import boto3
import click
import os


# Probably I can change
class CloudInfo:
    """
    Class to store the necessary information of AWS cloud provider.
    """
    def __init__(self, region, image, role, timeout, memory):
        self.account =  boto3.client("sts").get_caller_identity()["Account"]
        self.region = region
        self.image = '{}.dkr.ecr.{}.amazonaws.com/{}:latest'.format(self.account, self.region, image)
        self.role = role
        self.timeout = timeout
        self.memory = memory


@click.group()
@click.option("--region", type=str, help="Region to deploy lambda. According to role.")
@click.option("--role", type=str, help="Role to use when deploying lambda function.")
@click.option("--image", type=str, help="You shoul only provide image name, latest will be used.")
@click.option("-t", "--timeout", type=int, help="Seconds take to complete lambda function.")
@click.option("--memory", type=int, help="Memory size to provide to lambda function.")
def cli(ctx, region, role, image, timeout, memory):
    """
    Deploy lambda functions for train and serve 
    from dedicated lambda image.
    """
    # Consider using default values from click
    if region is None:
        client = boto3.client('s3')
        region = client.meta.region_name
    # Try placing same names in sagemkaer and lambda
    if image is None:
        image = os.path.basename(os.getcwd())
        click.echo("Image name not provided, then will be used: " + click.style(image, bold=True))
    if timeout is None:
        timeout = 3
    if memory is None:
        memory = 250
    
    ctx.obj = CloudInfo(region, image, role, timeout, memory)
    click.echo("Role is {}".format(ctx.obj.role))
    click.echo("Timeout of lambda function is {}".format(ctx.obj.timeout))
    click.echo("Memory size of the lambda function is {}".format(ctx.obj.memory))


@cli.command()
@click.option("-n", "--name", type=str, help="Name to give to the function. If None train")
@click.pass_context
def train(ctx, name):
    if name is None:
        name = "train"
    session = boto3.Session()
    lambda_client = session.client('lambda', region_name=ctx.obj.region)
    response = lambda_client.create_function(FunctionName=name,
                                             Role=ctx.obj.role,
                                             Code={
                                                 'ImageUri': ctx.obj.image},
                                             Handler='app.train',
                                             Timeout=ctx.obj.timeout,
                                             MemorySize=ctx.obj.memory,
                                             Runtime='python3.8')
