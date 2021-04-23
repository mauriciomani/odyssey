import click
from odyssey.service.generator import Generator


class Provider:
    """ 
    This class stores all the information of the selected provider and service.
    """
    def __init__(self, service_provider, service_name):
        self.service_provider = service_provider
        self.service_name = service_name
        self.generator = Generator(service_provider, service_name)


@click.group()
@click.option("-p",
              "--provider",
              type=str,
              help="Select cloud provider to deploy ML product")
@click.option("-s",
              "--service",
              type=str,
              help="Select cloud provider service to deploy ML product")
@click.pass_context
def cli(ctx, provider, service):
    """
    Initialize the project.
    You will be asked to give a name to the application.
    It is important that you understand what provider and service want to work:
    AWS, Azure, GCP, and as a service, Sagemaker, Machine Learning Studio, etc.
    Remember to add start at the end.
    """
    ctx.obj = Provider(provider, service)


@cli.command()
@click.pass_context
def start(ctx):
    """
    Start the application creation.
    This will create a folder with the odyssey app.
    I strongly recommend creating the enviroment prior executing this command.
    """
    click.echo("Using the following cloud provider: "
               + click.style(ctx.obj.service_provider, bold=True))
    if ctx.obj.service_name is None:
        click.echo("Using Sagemaker microservice to deploy app")
    else:
        click.echo("Using {} microservice to deploy app".format(ctx.obj.service_name))
    click.secho('''




                           *     .--.
                                / /  `
               +               | |
                      '         \ \__,
                  *          +   '--'  *
                      +   /\
         +              .'  '.   *
                *      /======\      +
                      ;:.  _   ;
                      |:. (_)  |
                      |:.  _   |
            +         |:. (_)  |          *
                      ;:.      ;
                    .' \:.    / `.
                   / .-'':._.'`-. \
                   |/    /||\    \|
                 _..--"""````"""--.._
           _.-'``                    ``'-._
         -'                                '-

   ____      __                          
  / __ \____/ /_  _______________  __  __
 / / / / __  / / / / ___/ ___/ _ \/ / / /
/ /_/ / /_/ / /_/ (__  |__  )  __/ /_/ / 
\____/\__,_/\__, /____/____/\___/\__, /  
           /____/               /____/   ''', fg="bright_cyan", bold=True)

    ctx.obj.generator.generate_files()
