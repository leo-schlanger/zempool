import logging
logger = logging.getLogger("group")
logger.setLevel(logging.DEBUG)
from discord import app_commands
from .generate import get_generate_command
from .defi import DefiTopCommand
from .help import HelpCommand

class ZenPoolGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="zenpool", description="ZenPool commands")
        self.add_command(get_generate_command())
        self.add_command(DefiTopCommand())
        self.add_command(HelpCommand())
