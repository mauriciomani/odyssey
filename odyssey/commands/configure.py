import click
import os


# You can also use default
@click.group(invoke_without_command=True)
@click.option("-p", "--provider", type=str, help="Select the cloud provider")
@click.pass_context
def cli(ctx, provider):
    """
    Use the 'aws configure' inside odyssey.
    Using this command is not necessary you can use aws confugure.
    From pip installed awscli
    """
    if provider == "aws" or provider is None:
        os.system("aws configure")
