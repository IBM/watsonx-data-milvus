#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Import Documents Panel
#

import streamlit as st
from streamlit import session_state as sts
from wxd_utilities import check_password, version_reset

if not check_password():
    st.stop()
    
# version_reset()	

st.header("Introduction",divider=True)

topic = \
'''
This system demonstrates the use of watsonx.data, Milvus, and the use of the
IBM Instructlab Granite model to answer questions regarding a variety of topics. The system has a built-in example of creating a RAG prompt from the IBM web site. You can add additional content to the system to try other scenarios with the system.

The system is designed around five steps:
	 
- The watsonx.data product is used to store control information and the raw
	documents (PDF, Powerpoint, Word, URLs).
- The Milvus vector database contains vectors that are built from the raw documents
	stored in the watsonx.data database.
- A prompt is generated from the question that is supplied by querying the Milvus database
	for the document segments that best match the request.
- The prompt is sent to an AI engine to process. This process is done locally in this
	system using Ollama. Since there are no GPUs in this system, performance will be slow.
- The answer is returned to the user

Start by importing documents, web sites, or articles from Wikipedia into the system. As a starter document, the IBM 2023 annual report web page has been preloaded. You can ask questions about the earnings to see how the LLM answers your question. An example would be to ask the LLM "What were IBMs earning in 2023" *without using RAG* and then ask the question again *using RAG*. This provides a comparison of the types of responses you may get from an LLM.

Once you have imported one or more documents, you must select which ones to vectorize. The documents will be split into chunks which are then stored and vectorized into the Milvus database. These chunks will be used to generate the RAG prompt when you query the LLM.

The Query LLM page will provide an interface for asking questions to the LLM. There are additional settings here which lets you change the LLM that is being used (the IBM instructlab/granite-7b-lab model is the default). Each LLM will behave differently so it is often an interesting exercise to try the same questions with different models. You can set whether or not a RAG prompt is generated as part of your query, as well as adjust how many sentence chunks from the vector database will be used to construct the prompt.

If you want to try a different LLM, you can use the Add LLM panel to load an LLM found in the Ollama or Hugging Face library. The load step will download the model to the local server and then make it available as an LLM that you can ask questions of. Note the process to download the model may take several minutes.

If you find that the system is not being responsive, you may want to check the Diagnostics page to see if the watsonx.data services are running. You can restart many of the services from this dialog. In addition, the Log file may provide more details on what went wrong.

Finally, details about this system and the programs that were used to create this are listed in the Support section.

Remember that this system does not contain GPUs which limits the performance of the LLM. However, it does provide an environment to try out RAG prompts and observe how different LLMs behave with and without RAG prompts.
'''
st.markdown(topic)
st.page_link("Watsonx_Milvus_Demo.py",label=":blue-background[Home]",icon=":material/arrow_forward:")