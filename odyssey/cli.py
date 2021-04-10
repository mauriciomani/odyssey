import click
import os

class ComplexCLI(click.MultiCommand):
    """
    Class to create the whole command line logic for odissey.
    """
    def list_commands(self, ctx):
        """
        This function extracts the commands from the 'commands' path.
        """
        rv = []
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), "commands")):
            if filename.endswith(".py") and not filename.startswith("__"):
                rv.append(filename.replace(".py", ""))
                
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        """
        This function get the commands from te command line.
        """
        try:
            mod = __import__(f"odyssey.commands.{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli


@click.command(cls=ComplexCLI)
def cli():
    """
    Welcome to Odyssey, a cloud machine Learning tool, currently using AWS only but aims to integrate Azure, GCP, etc. 
    Very easy to use, just with a few lines.
    Just needed to fill train and serve scripts and odyssey creates both batch transforms and endpoints.
    """
    pass