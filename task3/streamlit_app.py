import streamlit as st
from dotenv import load_dotenv
from executor import run_pipeline

load_dotenv()

st.set_page_config(page_title="Text-to-SQL Prompt Chaining", layout="wide")
st.title("Text-to-SQL Pipeline and Query Execution System")
st.write(
    "Enter a natural language question and the system will generate, validate, execute, and return a PostgreSQL result set."
)

question = st.text_area("Ask your question", height=150)
if st.button("Run Query"):
    if not question.strip():
        st.warning("Please enter a question before running the pipeline.")
    else:
        with st.spinner("Processing your query..."):
            output = run_pipeline(question)

        st.subheader("Pipeline Result")
        st.write("**Status:**", output.get("status"))
        st.write("**Retry Needed:**", output.get("retry_needed", False))

        if output.get("sql"):
            st.code(output.get("sql"), language="sql")

        if output.get("status") == "success":
            st.write(f"Returned {len(output.get('result', []))} rows")
            if output.get("result"):
                st.dataframe(output.get("result"))
        else:
            st.error("Query execution failed.")
            if output.get("error"):
                st.write("**Error:**", output.get("error"))
