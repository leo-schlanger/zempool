from discord import app_commands
from .generate import generate
from .help import show_help

class ZenPoolCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="zenpool", description="ZenPool analysis commands")

    @generate
    async def generate(self, interaction, network: str, pair: str):
        pass

    @show_help
    async def help(self, interaction):
        pass