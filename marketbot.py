import discord
import asyncio
from market_scanner import mainObj
from io import StringIO 
import sys
import time

HOURS_BETWEEN_SCANS = 3
STD_DEV = 10
MONTHS = 5
DAYS = 2

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

class MarketClient(discord.Client):
    started = False

    async def on_ready(self):
        print(f'{self.user} has connected.')
        print(self.guilds)
        if self.started:
            return
        self.started = True
        asyncio.create_task(self.runScanner())
    
    async def runScanner(self):
        scanner = mainObj()
        while True:
            for output in scanner.main_func(STD_DEV, MONTHS, DAYS):
                for guild in self.guilds:
                    if len(guild.text_channels) > 0:
                        await guild.text_channels[0].send(output)
            time.sleep(HOURS_BETWEEN_SCANS * 60*60)
