import click
import os
import requests
import json


@click.group()
@click.pass_context
def cli(ctx):
    """
    Train and serve your already modify train and serve files.
    Remember is important to have logic already added in both files.
    train.py needs all the information for training.
    """
    list_files = os.listdir()
    if "rocket" not in list_files or "train.py" not in list_files or "serve.py" not in list_files:
        raise("You are not inside an odyssey app. Kindly change path.")
    pass


@cli.command()
@click.pass_context
def train(ctx):
    """
    Once train file is been modified. You can execute this command.
    """
    os.system("python rocket/train")


@cli.command()
@click.pass_context
def serve(ctx):
    """
    Onced trained you can serve the model that is already stored.
    """
    os.system("python rocket/serve")
    # sudo pkill -f nginx & wait $!


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
    This to request local serve.
    Once you have odyssey local train
    and odyssey local serve open another terminak
    and you can test the endpoint.
    """
    r = requests.post(url="http://" + url + "/invocations",
                      json=json.loads(data))
    click.echo(r.text)
