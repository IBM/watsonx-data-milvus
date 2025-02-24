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

st.header("What is Retrieval-augmented Generation?",divider=True)

topic = \
"""
 > RAG is an AI framework for retrieving facts from an external knowledge base to ground large language models (LLMs) on the most accurate, up-to-date information and to give users insight into LLMs' generative process.
 > 
 > Large language models can be inconsistent. Sometimes they nail the answer to questions, other times they regurgitate random facts from their training data. If they occasionally sound like they have no idea what they're saying, it's because they don't. LLMs know how words relate statistically, but not what they mean.
 > 
 > Retrieval-augmented generation (RAG) is an AI framework for improving the quality of LLM-generated responses by grounding the model on external sources of knowledge to supplement the LLM's internal representation of information.
 > 
 > Implementing RAG in an LLM-based question answering system has two main benefits: It ensures that the model has access to the most current, reliable facts, and that users have access to the model's sources, ensuring that its claims can be checked for accuracy and ultimately trusted.
 > 
 > RAG has additional benefits. By grounding an LLM on a set of external, verifiable facts, the model has fewer opportunities to pull information baked into its parameters. This reduces the chances that an LLM will leak sensitive data, or 'hallucinate' incorrect or misleading information.
 > 
 > RAG also reduces the need for users to continuously train the model on new data and update its parameters as circumstances evolve. In this way, RAG can lower the computational and financial costs of running LLM-powered chatbots in an enterprise setting. IBM unveiled its new AI and data platform, watsonx, which offers RAG, back in May.
 > 
 > Credit: Kim Martineau
 > URL: [What is retrieval-augmented generation?](https://research.ibm.com/blog/retrieval-augmented-generation-RAG)

This system is designed to use information found in documents and URLs to generate a RAG prompt to an LLM. You can experiment with using different documents, RAG settings, and LLMs to discover how the answers to your questions can change. 
"""
st.markdown(topic)
st.page_link("Watsonx_Milvus_Demo.py",label=":blue-background[Home]",icon=":material/arrow_forward:")