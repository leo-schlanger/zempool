from discord import app_commands
from .generate import GenerateCommand
from .help import HelpCommand

class ZenPoolGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="zenpool", description="ZenPool commands")
        self.add_command(GenerateCommand())
        self.add_command(HelpCommand())
