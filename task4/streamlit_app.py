import os
from typing import Any

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000/query")

st.set_page_config(page_title="Agentic Text-to-SQL", page_icon="SQL", layout="wide")
st.title("Agentic Text-to-SQL")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask a question about customers, orders, products, payments, employees, or offices.",
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sql"):
            st.code(message["sql"], language="sql")
        if message.get("rows"):
            st.dataframe(message["rows"], use_container_width=True)

question = st.chat_input("Ask a business question")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Planning, validating, querying, and summarizing..."):
            try:
                response = requests.post(API_URL, json={"question": question}, timeout=90)
                response.raise_for_status()
                payload: dict[str, Any] = response.json()
                answer = payload.get("answer") or "No answer returned."
                st.markdown(answer)
                if payload.get("sql"):
                    st.code(payload["sql"], language="sql")
                if payload.get("rows"):
                    st.dataframe(payload["rows"], use_container_width=True)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sql": payload.get("sql"),
                        "rows": payload.get("rows"),
                    }
                )
            except requests.RequestException as exc:
                message = f"Request failed: {exc}"
                st.error(message)
                st.session_state.messages.append({"role": "assistant", "content": message})
