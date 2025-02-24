#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
# 
# Entry point for the RAG Demo
#

import streamlit as st
import datetime
from streamlit import session_state as sts 
import hmac
import wxd_data as db
from wxd_utilities import setCredentials, log, check_password, version_reset
import os

st.set_page_config(
		page_title="Introduction",
		page_icon=":infinity:",
		layout="wide",
		menu_items={
				        # 'Get Help': 'https://ibm.com',
				}
)

# Turn off parallelism for Tokenizers to avoid errors
os.environ["TOKENIZERS_PARALLELISM"] = "true"

if not check_password():
    st.stop()

# Get all userids and credentials
if ("initialized" not in sts):
	
    if (setCredentials() == False):
        st.error("Unable to get credentials required to connect to watsonx.data.")
        log("Startup","Unable to get credentials required to connect to watsonx.data")    
    
    try:
        with open("/tmp/watsonx.log","a") as fd:
            if ("version" in sts):
               v = sts.version
            else:
               v = "Unknown"
            today = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
            fd.write(f"{today},Log Start,================================================\n")
            fd.write(f"{today},Version,{v}\n")
            fd.write("Time,Routine,Message\n")    
    except:
        pass

# Connect to presto
connection = db.connectPresto()
if (connection == None):
	db.badConnection()
	st.stop()

# version_reset()

row_height = 360
col_height = 350
txt_height = 260
but_height = 40

st.image("/home/watsonx/rag/watsonxdata.png",output_format="PNG")
html = """
<h3 style='font-family: "IBM Plex Sans";text-decoration: bold;'>System Overview</h3>
"""
st.html(html)

with st.container(height=row_height, border=False):
    cols = st.columns(3)
    with cols[0]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Introduction</h4>
<p style='font-family: "IBM Plex Sans";'>This system demonstrates the use of IBM watsonx.data for managing documents, Milvus for storing document vectors, and a RAG generator to create prompts used to query an LLM. Click the link for additional details.
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/0-Introduction.py",label="Introduction",icon=":material/arrow_forward:")
                    
    with cols[1]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Retrieval Augmented Generation</h4>
<p style='font-family: "IBM Plex Sans";'>RAG is an AI framework for retrieving facts from an external knowledge base to ground large language models (LLMs) on the most accurate, up-to-date information and to give users insight into LLMs' generative process.
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/0-What is RAG.py",label="More on RAG",icon=":material/arrow_forward:")
                    
    with cols[2]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Documentation and Support</h4>
<p style='font-family: "IBM Plex Sans";'>Documentation for this system can be found by selecting the link below. Most of the information you need is also contained in the Technical Details button found on most pages.
"""
                st.html(html,)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("https://ibm.github.io/watsonx-data-milvus",label="Documentation",icon=":material/arrow_forward:")


html = """
<h3 style='font-family: "IBM Plex Sans";text-decoration: bold;'>Document Storage, Vectorization, and LLM Queries</h3>
"""
st.html(html)

with st.container(height=row_height, border=False):
    cols = st.columns(3)
    with cols[0]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Import Documents</h4>
<p style='font-family: "IBM Plex Sans";'>This system requires that you upload documents or URLs to be used for RAG generation. You can upload documents from your workstation (PDF, PPT, DOC, TXT), choose a website (URL), or query Wikipedia and retrieve documents based on a topic.
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/1-Import Documents.py",label="Import Files",icon=":material/arrow_forward:")
                    
    with cols[1]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Vectorize Documents</h4>
<p style='font-family: "IBM Plex Sans";'>The Milvus vector database is used to store sentences extracted from documents, and then converted into vectors for searching. Choose one or more documents from the uploaded files to have them stored into Milvus and vectorized for use in RAG generation.
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/2-Vectorize Document.py",label="Vectorize",icon=":material/arrow_forward:")
                    
    with cols[2]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Query LLM</h4>
<p style='font-family: "IBM Plex Sans";'>The Query LLM dialog is used to ask questions to a selected LLM. You have the option of changing the LLM, selecting which document collection to use, and adjusting the RAG output.
"""
                st.html(html,)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/4-Query LLM.py",label="Query LLM",icon=":material/arrow_forward:")					

html = """
<h3 style='font-family: "IBM Plex Sans";text-decoration: bold;'>LLM Maintenance, Diagnostics and Support</h3>
"""
st.html(html)

with st.container(height=row_height, border=False):
    cols = st.columns(3)
    with cols[0]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Manage LLMs</h4>
<p style='font-family: "IBM Plex Sans";'>This system has been built using the IBM instructlab/granite-7b-lab model. You can load additional models into the system by using the load LLM option. Note that not all models can be downloaded into this environment.
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/5-Add LLM Models.py",label="Manage LLMs",icon=":material/arrow_forward:")
                    
    with cols[1]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Diagnostics</h4>
<p style='font-family: "IBM Plex Sans";'>You will end up here if something went wrong with the image. Sorry about that! Hopefully you can figure out what went wrong and get it back up and running.
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/7-Diagnostics.py",label="Diagnostics",icon=":material/arrow_forward:") 
                    
    with cols[2]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Log File</h4>
<p style='font-family: "IBM Plex Sans";'>Status information is written to a common log file which can be used to diagnose problems with the software. In addition, control information (such as document sizes, vector distances) are written to the log file for review. 
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/8-Log File.py",label="Log File",icon=":material/arrow_forward:")
                    
with st.container(height=row_height, border=False):
    cols = st.columns(3)
    with cols[0]:
        with st.container(height=col_height,border=True):
            with st.container(height=txt_height,border=False):
                html = """
<h4 style='font-family: "IBM Plex Sans Light";'>Support</h4>
<p style='font-family: "IBM Plex Sans";'>The support section contains information on the various components that were used to create this system, as well as links to the libraries and LLM websites. You will also find the link to the most up-to-date documentation for the system.
"""
                st.html(html)
            with st.container(height=but_height,border=False):
                colsfooter = st.columns([0.5,0.5])
                with colsfooter[1]:
                    st.page_link("pages/9-Support.py",label="Support",icon=":material/arrow_forward:")
                    
			