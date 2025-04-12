import os
import httpx

from typing import cast
from dotenv import load_dotenv
from datetime import datetime, UTC

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import OpenAI Agents SDK
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider

from models import Message, Response, Metadata

# load the envirionment variables from .env
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# check if api key is present if it is not raise error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEy is not found")


# configuration GEMINI to work as the Agents SDK Client
# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=cast(ModelProvider, external_client), # satisfy type checker
    tracing_disabled=True
)


# initialization of FastAPI App

app : FastAPI = FastAPI(
    title="Dapr Agentic Cloud Ascent",
    description="A FastAPI application",
    version="0.1.0"
)


# add cross origin resource sharing middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# create a function to fetch the current time
@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

# root endpoint

@app.get("/")
async def root():
    return {"message": "Welcome to the DAPR Agentic Cloud Ascent API"}


# Post endpoint for chatting
@app.post("/chat", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    
    async with httpx.AsyncClient() as client:
        try:
            memory_response = await client.get(f"http://localhost:8001/memories/{message.user_id}")
            memory_response.raise_for_status()
            memory_data = memory_response.json()
            past_actions = memory_data.get("past_actions", [])
        
        except httpx.HTTPStatusError:
            past_actions = [] # fallback to empty list if memory service is not available
            
    # Personalize agent instructions with procedural memories
    memory_context = "The user has no past actions." if not past_actions else f"The user’s past actions include: {', '.join(past_actions)}."
    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"{memory_context} Use this to personalize your response."
    )

    chat_agent = Agent(
        name="ChatAgent",
        instructions=personalized_instructions,
        tools=[get_current_time],  # Add the time tool
        model=model
    )
    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text, run_config=config)
    reply_text = result.final_output  # Get the agent's response

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )