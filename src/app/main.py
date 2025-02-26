import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import time
import logging
import streamlit as st
from openai import OpenAI
from datetime import datetime
from reservation_tool import get_output_for_tool_call, get_assistant


# Configure logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Streamlit UI Configuration
st.set_page_config(
    page_title="Ivy AI",
    layout="wide",
)

st.title("Ivy AI")
st.subheader("Your AI concierge for making reservations in NYC")

# User inputs API key and Assistant ID
api_key = st.text_input("Enter your OpenAI API Key:", type="password")
assistant_id = st.text_input("Enter your OpenAI Assistant ID:")

if api_key and assistant_id:
    try:
        # OpenAI API Client
        client = OpenAI(
            api_key=api_key,
            default_headers={"OpenAI-Beta": "assistants=v2"}
        )

        # Validate assistant ID
        st.session_state['assistant'] = get_assistant(client, assistant_id)
        st.success(f"Connected to Assistant: {st.session_state['assistant'].name}")

        # Initialize thread with tools if not already created
        if "thread" not in st.session_state:
            st.session_state['thread'] = client.beta.threads.create()

        if "run" not in st.session_state:
            st.session_state['run'] = None

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.warning("Please enter both your OpenAI API Key and Assistant ID.")

# Store conversation history
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

# Display conversation messages in correct order (newest at the bottom)
for role, message in reversed(st.session_state["conversation"]):
    with st.chat_message(role):
        st.write(message)

# Function to handle user input
def on_text_input():
    user_message = st.session_state["input_user_msg"]
    st.session_state["conversation"].append(("user", user_message))

    # Send message to OpenAI thread with attachments (if applicable)
    client.beta.threads.messages.create(
    thread_id=st.session_state["thread"].id,
    role="user",
    content=user_message
    )

    # Create a run for the assistant
    st.session_state["run"] = client.beta.threads.runs.create(
        thread_id=st.session_state["thread"].id,
        assistant_id=st.session_state["assistant"].id
    )

    # Poll for run completion
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state["thread"].id,
            run_id=st.session_state["run"].id
        )

        if run.status == "completed":
            break

        elif run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = list(map(get_output_for_tool_call, tool_calls))
            logging.info(f"Tool Outputs: {tool_outputs}")

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=st.session_state["thread"].id,
                run_id=st.session_state["run"].id,
                tool_outputs=tool_outputs
            )
        else:
            time.sleep(0.5)  # Reduce polling frequency

    # Update conversation history
    messages = client.beta.threads.messages.list(st.session_state["thread"].id).data
    st.session_state["conversation"] = [(m.role, m.content[0].text.value) for m in messages]

# Chat input for user messages
st.chat_input(
    placeholder="What occasion can we find food for today?",
    key="input_user_msg",
    on_submit=on_text_input
)