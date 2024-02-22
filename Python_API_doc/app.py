import PyPDF2
import os
import openai
import re
# from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import AzureSearch
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import TokenTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes.models import HnswVectorSearchAlgorithmConfiguration

app = Flask(__name__)
CORS(app)

# llm = AzureChatOpenAI(
#     openai_api_key = "411da2482a0945629107681bdb72740c",
#     openai_api_base = "https://openai-test-005.openai.azure.com/",
#     openai_api_version = "2023-07-01-preview",
#     temperature=0,    
#     deployment_name="gptnew")


# embeddings = OpenAIEmbeddings(
#     openai_api_key = "411da2482a0945629107681bdb72740c",
#     openai_api_base = "https://openai-test-005.openai.azure.com/",
#     openai_api_type = "azure",
#     openai_api_version = "2023-07-01-preview",
#     deployment="textnew005", 
#     chunk_size=1
#     )

# # Connect to Azure Cognitive Search
# acs = AzureSearch(azure_search_endpoint="https://ai-dev-ss-fts.search.windows.net",
#                  azure_search_key="ICyDmM0S3sWaLpYwNGPfUOz7jblRyOHnE6p7uDHPRRAzSeAaLBFM",
#                  index_name="azureblob-goodbooks-index",
#                  embedding_function=embeddings.embed_query)

def parse_response(response):
        result = response['result']
        sources = []
        for source_name in response["source_documents"]:
            sources.append(re.search(r'[^\\/:*?"<>|\r\n]+$', source_name.metadata['source']).group())
            break

        # Combine the result and sources into a single string.
        response_string = f"{result}\n\nSources: {', '.join(sources)}"

        return response_string


#api server part
@app.route('/api', methods=['POST'])
def ask_question():
    # Get the question and additional parameters from the POST request data
    
    question = request.json.get('question')
    openai_endpoint = "https://openai16.openai.azure.com/"
    openai_key = "a829ebd3b2934986a0a66f47c9be1a32"
    openai_apiversion = "2023-07-01-preview"
    openai_llmdeployname = "gpt35"
    openai_embeddeployname = "embed"
    search_endpoint = "https://aisearch16.search.windows.net"
    search_key = "Z8gUp48Kj5OC9AMC0M6dzhVG7l3eToCYMM25SCfUABAzSeBVSG22"
    index_name = "check-001"

    # Create an instance of the llm,embeding,AzureSearch class with the provided parameters
    llm = AzureChatOpenAI(
    openai_api_key = openai_key,
    openai_api_base = openai_endpoint,
    openai_api_version = openai_apiversion,
    temperature=0,    
    deployment_name=openai_llmdeployname)
    
    embeddings = OpenAIEmbeddings(
    openai_api_key = openai_key,
    openai_api_base = openai_endpoint,
    openai_api_type = "azure",
    openai_api_version = openai_apiversion,
    deployment=openai_embeddeployname, 
    chunk_size=1
    )
    acs = AzureSearch(azure_search_endpoint=search_endpoint,
                     azure_search_key=search_key,
                     index_name=index_name,
                     embedding_function=embeddings.embed_query)
    
    retriever = acs.as_retriever(
                    include_metadata=True, 
                    metadata_key = 'source'
                    )

    chain  = RetrievalQA.from_chain_type(
                            llm=llm, 
                            chain_type= "stuff", 
                            retriever=retriever, 
                            return_source_documents=True
                            )
    
    

    # Perform on OpenAI GPT 3.5 Model Format
    response = chain(question)
    result = parse_response(response)

    # if result:
    #     response = result["answer"]
    # else:
    #     response = "No relevant documents found."

    # Create a JSON response
    response_data = {'answer': result}
    return jsonify(response_data)
