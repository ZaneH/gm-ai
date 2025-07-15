from mcp_agent.app import MCPApp
from src.workflows.read_notes import read_notes

app = MCPApp(name="gm_ai_app")

async def start_bot():
    async with app.run() as gmai_app:
        await read_notes(gmai_app)

class Bot:
    def __init__(self):
       self.personality = ""
       self.memory = {}
       self.recent_notes = []
