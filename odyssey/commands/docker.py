import click
import os
import subprocess
import requests
import json


# Consider using default
@click.group()
@click.option("-n",
              "--name",
              type=str,
              help="Select image name to push to ECR for AWS")
@click.pass_context
def cli(ctx, name):
    """
    Use docker to train and serve.
    I kindly recommend you first locally train and test.
    Remember that once you push you are already in aws.
    In order to do this kindly run 'odyssey train' and 'odyssey serve'.
    """
    list_files = os.listdir()
    if "Dockerfile" not in list_files:
    #if "rocket" not in list_files or "train.py" not in list_files or "serve.py" not in list_files or "Dockerfile" not in list_files:
        click.echo("You are " 
                   + click.style("not inside an odyssey app. ", bold=True)
                   + "Kindly change the path.")
        quit()

    if name is None:
        # The name given to the bruce app (parent folder name)
        ctx.obj = os.path.basename(os.getcwd())
        click.echo("Name of Image not provided, then will be used: "
                   + click.style(ctx.obj, bold=True))
    else:
        ctx.obj = name


@cli.command()
@click.pass_context
def build(ctx):
    """
    Build docker image from given name.
    If name not provided then we will use the oyssey app.
    """
    os.system("docker build -t {} .".format(ctx.obj))


@cli.command()
@click.pass_context
def push(ctx):
    """
    Push the created image to ECR. 
    If not allowed then kindly use odyssey configure.
    """
    account = subprocess.getoutput('account=$(aws sts get-caller-identity --query Account --output text); echo $account')
    click.echo("Uploading container to {}".format(account))
    region = subprocess.getoutput('region=$(aws configure get region); region=${region:-us-west-2}; echo $region')
    click.echo("Uploading container to {}".format(region))
    fullname = '{account}.dkr.ecr.{region}.amazonaws.com/{image}:latest'.format(account=account, region=region, image=ctx.obj)
    check_repository = subprocess.getoutput('aws ecr describe-repositories --repository-names "{}" > /dev/null 2>&1; echo $?'.format(ctx.obj))
    if check_repository != 0:
        os.system('aws ecr create-repository --repository-name "{}" > /dev/null'.format(ctx.obj))
    login = 'aws ecr get-login-password --region "{region}" | docker login --username AWS --password-stdin "{account}".dkr.ecr."{region}".amazonaws.com'.format(region = region, account = account)
    os.system(login)
    os.system('docker tag {} {}'.format(ctx.obj, fullname))
    os.system("docker push {}".format(fullname))
    click.echo("Successfully pushed {}".format(fullname))


@cli.command()
@click.pass_context
def train(ctx):
    """
    Train the application inside the container.
    """
    os.system("docker run -v $(pwd):/opt/ml --rm {} train".format(ctx.obj))


@cli.command()
@click.pass_context
def serve(ctx):
    """
    Serve the trained model inside the container.
    """
    # docker inspect <containerNameOrId>
    os.system("docker run -p 8080:8080 -v $(pwd):/opt/ml --rm {} rocket/serve".format(ctx.obj))


@cli.command()
@click.pass_context
@click.option("--data",
              type=str,
              help="Information to send to locally created endpoint")
@click.option("--url",
              type=str,
              help="Information to send to locally created endpoint",
              default="127.0.0.1:8080")
def request(ctx, data, url):
    """
    This to request docker serve.
    Once you have odyssey docker train
    and odyssey docker serve open another terminal
    and you can test the endpoint.
    You can also use odyssey local request
    """
    r = requests.post(url="http://" + url + "/invocations",
                      json=json.loads(data))
    click.echo(r.text)

