from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()
OAIkey = os.getenv("OAI")


client = OpenAI(api_key=OAIkey)
def Create_Thread():
    return client.beta.threads.create()

def New_Message(usermessage, threadID):
    return client.beta.threads.messages.create(
        thread_id=threadID,
        role="user",
        content=usermessage

    )
def Create_Run(threadID, AssistantID):
    return client.beta.threads.runs.create(
        thread_id=threadID,
        assistant_id=AssistantID,

    )
def Grab_Result(threadID, runID):
    received = False
    while not received:

        # Retrieve the latest run status
        results = client.beta.threads.runs.retrieve(
            thread_id=threadID,
            run_id=runID
        )

        # Check if the run is completed
        if results.status == 'completed':

            messages = client.beta.threads.messages.list(thread_id=threadID)
            for message in messages.data:
                role = message.role
                content = message.content[0].text.value
                received = True
                return