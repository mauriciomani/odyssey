import click
import os
import boto3
import time
import paramiko
from scp import SCPClient
import json


def add_values_json(_key, value):
    """
    This function creates a json file and stores relevant EC2 information.
    Parameters
    ----------
    _key : str
        Name of the key
    value : str
        Value to pass
    
    Returns
    -------
    None
    """
    if "ec2_information.json" in os.listdir():
        f = open("ec2_information.json")
        information = json.load(f)
    else:
        information = {}
    information[_key] = value
    with open('ec2_information.json', 'w') as f:
        json.dump(information, f)


class CloudObject:
    """
    This class stores the necessary information to create EC2 instance.
    """
    def __init__(self):
        """
        Create EC2 resource and client.
        Using boto3 and stores key name, group_id for EC2 and public dns.
        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.ec2 = boto3.resource("ec2", region_name="us-east-1")
        self.client = boto3.client("ec2", region_name="us-east-1")
        self.key_name = None
        self.group_id = None
        self.public_dns = None

    def get_key_name(self):
        """
        Stores the key pair file name.
        This the one helpful to make available ports.
        Parameters
        ----------
        instance_group_id : str
            Is thr group id that the instance belongs to.

        Returns
        -------
        None
        """
        f = open("ec2_information.json")
        information = json.load(f)
        self.key_name = information["key_name"]

    def get_group_id(self):
        """
        Stores the group id.
        This the one helpful to make available ports.
        Parameters
        ----------
        instance_group_id : str
            Is thr group id that the instance belongs to.

        Returns
        -------
        None
        """
        f = open("ec2_information.json")
        information = json.load(f)
        self.group_id = information["group_id"]

    def get_public_dns(self):
        """
        Get the public DNS to connect through SSH, for example.
        Parameters
        ----------
        dns : str
            The public DNS

        Returns
        -------
        None
        """
        f = open("ec2_information.json")
        information = json.load(f)
        self.public_dns = information["public_dns"]


@click.group()
@click.pass_context
def cli(ctx):
    """
    Create EC2 instance. Everything is built under odyssey_app.
    Any given name to the generated application will not be replicated.
    """
    if "app.py" in os.listdir() or "inference.py" in os.listdir() or "requirements.txt" in os.listdir():
        ctx.obj = CloudObject()
    else:
        raise(Exception("Not in odyssey app."))


@cli.command()
@click.option("--key-name",
              type=str,
              help="Name of the created key pair",
              default="ec2-keypair")
@click.pass_context
def create_key(ctx, key_name):
    """
    Creates the key to connect with the instance. key-name can be provided instead.
    This is mandatory for ssh connection, therefore por 22 has to be opened as well.
    """
    add_values_json("key_name", key_name)
    files = os.listdir()
    if key_name + ".pem" in files:
        raise(Exception("key pair name already exists."))
    try:
        outfile = open("{}.pem".format(key_name), "w")
        key_pair = ctx.obj.ec2.create_key_pair(KeyName=key_name)

        key_pair_out = str(key_pair.key_material)
        click.echo(key_pair_out)
        outfile.write(key_pair_out)
        click.echo("Changing permission 400")
        os.system("chmod 400 {}.pem".format(key_name))
    except Exception as e:
        print(e)
        click.echo(".pem file not in the path. Kindly write it to path.")


@cli.command("create-instance")
@click.option("--min-count",
              type=int,
              help="Instance min count",
              default=1)
@click.option("--max-count",
              type=int,
              help="Max instance count",
              default=1)
@click.option("--instance-type",
              type=str,
              help="Instance type, default t2.micro",
              default="t2.micro")
@click.option("--image",
              type=str,
              help="Image ID, default ami-0747bdcabd34c712a. Ubuntu 18.04",
              default="ami-0747bdcabd34c712a")
@click.pass_context
def create_instance(ctx, min_count, max_count, instance_type, image):
    """
    Extremely important to use create_key command before or already have a pem file.
    This is only useful for ubuntu machines.
    """
    ctx.obj.get_key_name()
    instances = ctx.obj.ec2.create_instances(ImageId=image,
                                             MinCount=min_count,
                                             MaxCount=max_count,
                                             InstanceType=instance_type,
                                             KeyName=ctx.obj.key_name)

    instance = instances[0]
    instance.wait_until_running()
    instance.load()
    add_values_json("public_dns", instance.public_dns_name)
    add_values_json("group_id", instance.security_groups[0]["GroupId"])
    click.echo("Creating instance...")
    time.sleep(60)
    click.echo("Instance created!")


@cli.command()
@click.pass_context
def security_group(ctx):
    """
    Open both ports 22 for SSH and port 80 for HTTP.
    Both will be opened, if either one already exists will throw an error.
    Kindly do it manually under the security groups on EC2 dashboard.
    """
    ctx.obj.get_group_id()
    ctx.obj.get_public_dns()
    response = ctx.obj.client.authorize_security_group_ingress(
                    GroupId=ctx.obj.group_id,
                    IpPermissions=[
                        {
                            'FromPort': 22,
                            'IpProtocol': 'tcp',
                            'IpRanges': [
                                {
                                    'CidrIp': '0.0.0.0/0',
                                    'Description': 'SSH access',
                                },
                            ],
                            'ToPort': 22,
                        },
                        {
                            'FromPort': 80,
                            'IpProtocol': 'tcp',
                            'IpRanges': [
                                {
                                    'CidrIp': '0.0.0.0/0',
                                    'Description': 'HTTP Port 80',
                                },
                            ],
                            'ToPort': 80,
                            },
                    ],
                )
    click.echo(response)
    click.echo("Activating security group. Sleeping for 30 seconds")
    time.sleep(30)


@cli.command()
@click.option("--model",
              type=str,
              help="Name of the model. If None will be not transfered.")
@click.option("--input-data",
              type=str,
              help="Name of the input. If None will be not transfered.")
@click.pass_context
def activate_instance(ctx, model, input_data):
    """
    Model can be transferred as well as input data,
    you can use boto3 to read ec2 data, both the input and write the model.
    We use gunicorn as web server gateway interface and unix as reverse proxy,
    The former is a web server to forward requests to web applications.
    The latter is a web server/inverse proxy. A proxy is an intermediary for requests from clients.
    Works on behalf of clients when requesting service, this is instead of connecting directly.
    A proxy first evaluates the request.
    Without the importance of the app name we create inside the ec2 instance and odyssey_app folder.
    A virtual enviroment is created and requirements are installed.
    We activate gunicorn using daemon and nginx.
    """
    ctx.obj.get_key_name()
    ctx.obj.get_public_dns()
    key = paramiko.RSAKey.from_private_key_file("{}.pem".format(ctx.obj.key_name))
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=ctx.obj.public_dns,
                           username="ubuntu",
                           pkey=key)
        click.echo("Connected")
        ssh_client.exec_command("mkdir odyssey_app")
        click.echo("Making odyssey_app dir")
        time.sleep(1)
        ssh_client.exec_command("mkdir odyssey_app/model")
        click.echo("Making model dir")
        time.sleep(1)
        ssh_client.exec_command("mkdir odyssey_app/input")
        click.echo("Making input dir")
        time.sleep(1)
        ssh_client.exec_command("sudo apt-get update")
        click.echo("Update library")
        time.sleep(60)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command("sudo apt-get install python3-venv")
        ssh_stdin.write('yes\n')
        ssh_stdin.flush()
        output = ssh_stdout.read()
        time.sleep(60)
        ssh_client.exec_command("python3 -m venv odyssey_app/venv")
        time.sleep(10)
        click.echo("Activating enviroment")
        with SCPClient(ssh_client.get_transport()) as scp:
            scp.put('app.py', 'odyssey_app/app.py')
            click.echo("Transfering app.py")
            if model:
                scp.put("odyssey_app/model/{}".format(model), "odyssey_app/model/{}".format(model))
                click.echo("Transfering pickle model.")
            if input_data:
                scp.put("odyssey_app/input/{}".format(input_data), "odyssey_app/input/{}".format(input_data))
                click.echo("Transfering input data.")
            scp.put("requirements.txt", "odyssey_app/requirements.txt")
            click.echo("Transfering requirements model")
            scp.put("inference.py", "odyssey_app/inference.py")
            click.echo("Transfering inference")
        click.echo("Installing requirements...")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command("source odyssey_app/venv/bin/activate; pip3 install -r odyssey_app/requirements.txt")
        output = ssh_stdout.read()
        print(output)
        time.sleep(120)
        click.echo("Requirements installed!")
        click.echo("Installing nginx...")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command("sudo apt-get install nginx")
        ssh_stdin.write('Y\n')
        ssh_stdin.flush()
        output = ssh_stdout.read()
        print(output)
        time.sleep(60)
        click.echo("nginx installed")
        ssh_client.exec_command("""sudo bash -c 'echo "[Unit]\nDescription=Gunicorn instance for odyssey app\nAfter=network.target\n[Service]\nUser=ubuntu\nGroup=www-data\nWorkingDirectory=/home/ubuntu/odyssey_app\nExecStart=/home/ubuntu/odyssey_app/venv/bin/gunicorn -b localhost:8000 app:app\nRestart=always\n[Install]\nWantedBy=multi-user.target" > /etc/systemd/system/odyssey.service'""")
        ssh_client.exec_command("sudo systemctl daemon-reload")
        time.sleep(1)
        ssh_client.exec_command("sudo systemctl start odyssey")
        time.sleep(1)
        ssh_client.exec_command("sudo systemctl enable odyssey")
        time.sleep(1)
        click.echo("Starting and enabling nginx...")
        ssh_client.exec_command("sudo systemctl start nginx")
        time.sleep(1)
        ssh_client.exec_command("sudo systemctl enable nginx")
        time.sleep(1)
        ssh_client.exec_command("""sudo bash -c 'echo "upstream odyssey_app {\n    server 127.0.0.1:8000;\n}\n\nserver {\n        listen 80 default_server;\n        listen [::]:80 default_server;\n\n        root /var/www/html;\n\n        index index.html index.htm index.nginx-debian.html;\n\n        server_name _;\n\n        location / {\n                proxy_pass http://odyssey_app;\n        }\n}" > /etc/nginx/sites-available/odyssey_app'""")
        ssh_client.exec_command("sudo rm /etc/nginx/sites-available/default")
        ssh_client.exec_command("sudo rm /etc/nginx/sites-enabled/default")
        ssh_client.exec_command("sudo ln -s /etc/nginx/sites-available/odyssey_app /etc/nginx/sites-enabled")
        ssh_client.exec_command("sudo systemctl restart nginx")
        click.echo("nginx restarted and ready")
        ssh_client.close()
        click.echo("Finished activating instance!")
    except Exception as e:
        click.echo("Could not activate instance")
        click.echo(e)
