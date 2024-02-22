import PyPDF2
import os
import openai
import re
# from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models import AzureChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql.base import SQLDatabaseChain
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine
import sqlalchemy
import pyodbc
app = Flask(__name__)
CORS(app)




#api server part
@app.route('/api', methods=['POST'])
def ask_question():
    # Get the question and additional parameters from the POST request data
    
    question = request.json.get('question')
    openai_endpoint = "https://openai16.openai.azure.com/"
    openai_key = "a829ebd3b2934986a0a66f47c9be1a32"
    openai_apiversion = "2023-07-01-preview"
    openai_llmdeployname = "gpt35"

    # Create an instance of the llm,embeding,AzureSearch class with the provided parameters
    llm = AzureChatOpenAI(
    openai_api_key = openai_key,
    azure_endpoint = openai_endpoint,
    openai_api_version = openai_apiversion,
    temperature=0.3,    
    azure_deployment=openai_llmdeployname, max_retries=15)
    
    
    server = 'serversql16.database.windows.net'
    database = 'sqldb'
    username = 'serveradmin'
    password = 'HanuSoft143'

    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    conn = pyodbc.connect(conn_str)


    eng = create_engine('mssql+pyodbc://', creator = lambda : conn)


    db = SQLDatabase(eng)
    db_chain = SQLDatabaseChain.from_llm(llm = llm, db = db, verbose=True)
    result  = db_chain.run(question)

    

    
    

    # Perform on OpenAI GPT 3.5 Model Format

    # if result:
    #     response = result["answer"]
    # else:
    #     response = "No relevant documents found."

    # Create a JSON response
    response_data = {'answer': result}
    return jsonify(response_data)
