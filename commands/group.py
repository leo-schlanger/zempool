import logging
logger = logging.getLogger("group")
logger.setLevel(logging.DEBUG)
from discord import app_commands
from .generate import GenerateCommand
from .defi import DefiTopCommand
from .help import HelpCommand

class ZenPoolGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="zenpool", description="ZenPool commands")
        self.add_command(GenerateCommand())
        self.add_command(DefiTopCommand())
        self.add_command(HelpCommand())
