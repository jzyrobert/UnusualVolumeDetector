import os
from dotenv import load_dotenv
from marketbot import MarketClient
load_dotenv()

token = os.getenv("DISCORD_TOKEN")

client = MarketClient()
client.run(token)