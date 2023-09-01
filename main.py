import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
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

    st.session_state.setdefault('chat_history', [])
    
    # Temperature slider
    with st.sidebar:
        with st.expander("Settings",  expanded=True):
            TEMP = st.slider(label="LLM Temperature", min_value=0.0, max_value=1.0, value=0.5)
            ("Adjust the LLM Temperature: A higher value makes the output more random, while a lower value makes it more deterministic.")
            ("NOTE: Anything above 0.7 may produce hallucinations")
            st.divider()
            st.markdown("You will need a OpenAI api key to upload and chat. You can obtain it from https://platform.openai.com/account/api-keys")
            st.divider()
            st.markdown("To set API key As Environment Variable on a MAC Open Terminal and type export OPENAI_API_KEY = 'your_api_key'")
            st.markdown("**To set up Environment Variable on Windows**")
            st.markdown("""
                       1. Open the Start Menu and search for **Environment Variables**
                       2. Under the "System variables" section, click the "New" button.
                       3. In the "Variable name" field, enter `OPENAI_API_KEY`.
                       4. In the "Variable value" field, enter your actual OpenAI API key.
                       5. Click "OK" to close all of the windows.                       
                       """)             
    # Upload File
    file = st.file_uploader("Upload CSV or XLSX file", type=["csv", "xlsx"])
    
          
    data = None
    
    if file:
        file_type = file.type
        
        try:
            if file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                data = pd.read_excel(file)
            elif file_type == "text/csv":
                data = pd.read_csv(file)
            else:
                st.error("Unsupported file type")
                return
    
            # Show a data preview and available columns after reading the file
            st.write("Data Preview:")
            st.write(data.head())
            st.write("Available Columns:")
            st.write(data.columns.tolist())
    
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return  # Exit if an error occurs
    
    else:
        st.warning("No file uploaded yet.")
    
    if data is not None:
        # UI elements related to chart and data operations
        chart_type = st.selectbox("Choose a chart type", ["Line Graph", "Bar Chart", "Scatter Plot"])
        x_column = st.selectbox("Choose the x-axis column", data.columns)
        y_column = st.selectbox("Choose the y-axis column", data.columns)
        query = st.text_input("Enter a query:")  # Moved inside this block
    # Data manipulations
    if 'your_column' in data.columns:
        data.dropna(subset=['your_column'], inplace=True) 
        data['your_column'] = data['your_column'].astype(float)
    else:
        st.error(f"The column 'your_column' does not exist. Available columns are: {data.columns.tolist()}")
    
       if 'your_column' in data.columns:
            data.dropna(subset=['your_column'], inplace=True) 
            data['your_column'] = data['your_column'].astype(float)
        else:
            st.error(f"The column 'your_column' does not exist. Available columns are: {data.columns.tolist()}")
    

        
        if st.button("Generate Chart"):
            fig, ax = plt.subplots()
            if chart_type == "Line Graph":
                ax.plot(data[x_column], data[y_column])
            elif chart_type == "Bar Chart":
                ax.bar(data[x_column], data[y_column])
            elif chart_type == "Scatter Plot":
                ax.scatter(data[x_column], data[y_column])
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_horizontalalignment('right')
            ax.tick_params(axis='x', labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            st.pyplot(fig)
        llm = OpenAI(temperature=TEMP, openai_api_key=st.secrets["openai_api_key"])        
        agent = create_pandas_dataframe_agent(llm, data, verbose=True)
        
    if st.button("Execute") and query:
        with st.spinner('Generating response...'):
            try:
                prompt = f'''
                    Consider the uploaded pandas data, respond intelligently to user input
                    \\nCHAT HISTORY: {st.session_state.chat_history}
                    \\nUSER INPUT: {query}
                    \\nAI RESPONSE HERE:
                    '''
                answer = agent.run(prompt)
                st.session_state.chat_history.append(f"USER: {query}")
                st.session_state.chat_history.append(f"AI: {answer}")
                for i, message in enumerate(reversed(st.session_state.chat_history)):
                    if i % 2 == 0:
                        st.markdown(bot_template.replace("{{MSG}}", message), unsafe_allow_html=True)
                    else:
                        st.markdown(user_template.replace("{{MSG}}", message), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
if __name__ == "__main__":
    load_dotenv()
    main()
