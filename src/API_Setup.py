from openai import OpenAI
import os
from dotenv import load_dotenv
from agents import Agent, Runner
import asyncio

"You exist to look for a context of conversation between an ai streamer streaming with the main human streamer plus"
                 " input from chat snice we have a limited amount of tokens you need to pick the most relevant and most self identifying conversations in these files"
                 "to upload as context for next stream youll be handed 21 files and you pick the most non essential file to pass in since well"
                 " be always passing in 20 txt files if you conclude that all files are important "
load_dotenv()
OAIkey = os.getenv("OAI")


client = OpenAI(api_key=OAIkey)


importantMemoryChecker = Agent(
    name="Memory Checker",
    instructions="You exist to look for a context of conversation between an ai streamer streaming with the main human streamer plus"
                 " input from chat snice we have a limited amount of tokens you need to pick the most relevant and most self identifying conversations in these files"
                 "to upload as context for next stream youll be handed 21 files and you pick the most non essential file to pass in since well"
                 " be always passing in 20 txt files if you conclude that all files are important ",
)

def MemoryChecker():

    return None
