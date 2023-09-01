import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.agents.agent_types import AgentType
from html_templates import css, user_template, bot_template


def main():
    st.set_page_config(page_title="MTI Pandas Agent")
    logo_url = "https://i.imgur.com/9DLn81j.png"
    st.image(logo_url, width=400)
    st.subheader("MTI Pandas Agent")
    st.write("Upload a CSV or XLSX file and query answers from your data.")
     
    


    # Apply CSS
    st.write(css, unsafe_allow_html=True)

    # Define chat history session state variable
    st.session_state.setdefault('chat_history', [])

    # Temperature slider
    with st.sidebar:
        with st.expander("Settings",  expanded=True):
            TEMP = st.slider(label="LLM Temperature", min_value=0.0, max_value=1.0, value=0.5)
            st.markdown("Adjust the LLM Temperature: A higher value makes the output more random, while a lower value makes it more deterministic.")
            st.markdown("NOTE: Anything above 0.7 may produce hallucinations")
            st.divider()
            st.markdown("You will need a OpenAI api key to upload and chat. You can obtain it from https://platform.openai.com/account/api-keys")

    # Upload File
    file = st.file_uploader("Upload CSV or XLSX file", type=["csv", "xlsx"])

   
    
    if file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        data = pd.read_excel(file)
    elif file_type == "text/csv":
        data = pd.read_csv(file)
    else:
        st.error("Unsupported file type")


  

    # Display Data Head
    st.write("Data Preview:")
    st.dataframe(data.head(50)) 
    
    
    chart_type = st.selectbox("Choose a chart type", ["Line Graph", "Bar Chart", "Scatter Plot"])
    x_column = st.selectbox("Choose the x-axis column", data.columns)
    y_column = st.selectbox("Choose the y-axis column", data.columns)

    if st.button("Generate Chart"):
            fig, ax = plt.subplots()
            data[x_column] = data[x_column].astype(str)
            data[y_column] = data[y_column].astype(str)
            if chart_type == "Line Graph":
                ax.plot(data[x_column], data[y_column])
            elif chart_type == "Bar Chart":
                ax.bar(data[x_column], data[y_column])
            elif chart_type == "Scatter Plot":
                ax.scatter(data[x_column], data[y_column])

            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)

            # Sparse Labeling for x-axis
            data[x_column] = data[x_column].astype(str)
            abbrev_x_labels = [str(label)[:4] + '...' if len(str(label)) > 4 else str(label) for label in data[x_column]]
            n_x = 5 # Show every nth label for x-axis (adjust as needed)
            sparse_x_labels = [label if i % n_x == 0 else '' for i, label in enumerate(abbrev_x_labels)]
            ax.set_xticks(range(len(sparse_x_labels)))
            ax.set_xticklabels(sparse_x_labels, rotation=45)

            # Sparse Labeling for y-axis
            data[y_column] = data[y_column].astype(str)
            abbrev_y_labels = [str(label)[:4] + '...' if len(str(label)) > 4 else str(label) for label in data[y_column]]   
            n_y = 5  # Show every nth label for y-axis (adjust as needed)
            sparse_y_labels = [label if i % n_y == 0 else '' for i, label in enumerate(abbrev_y_labels)]
            ax.set_yticks(range(len(sparse_y_labels)))
            ax.set_yticklabels(sparse_y_labels)

            st.pyplot(fig)

    # Define large language model (LLM)
    llm = OpenAI(temperature=TEMP, openai_api_key=st.secrets["openai_api_key"])


    # Define pandas df agent
    agent = create_pandas_dataframe_agent(llm, data, verbose=True) 

    # Accept input from user
    query = st.text_input("Enter a query:") 

    # Execute Button Logic
    if st.button("Execute") and query:
        with st.spinner('Generating response...'):
            try:
                # Define prompt for agent
                prompt = f'''
                    Consider the uploaded pandas data, respond intelligently to user input
                    \nCHAT HISTORY: {st.session_state.chat_history}
                    \nUSER INPUT: {query}
                    \nAI RESPONSE HERE:
                '''

                # Get answer from agent
                answer = agent.run(prompt)

                # Store conversation
                st.session_state.chat_history.append(f"USER: {query}")
                st.session_state.chat_history.append(f"AI: {answer}")

                # Display conversation in reverse order
                for i, message in enumerate(reversed(st.session_state.chat_history)):
                    if i % 2 == 0: st.markdown(bot_template.replace("{{MSG}}", message), unsafe_allow_html=True)
                    else: st.markdown(user_template.replace("{{MSG}}", message), unsafe_allow_html=True)

            # Error Handling
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    load_dotenv() # Import enviornmental variables
    main()   