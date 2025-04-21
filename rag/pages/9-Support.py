#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Support panel
#

import streamlit as st
import wxd_data as db
from wxd_utilities import log, runOS, checkStatus, check_password, version_reset
from streamlit import session_state as sts
import pandas as pd

st.set_page_config(
    page_title="Support",
    page_icon=":infinity:",
    layout="wide"
)

if not check_password():
    st.stop()

# version_reset()

st.subheader("Credits",divider=True)

description = '''
##### Development
* George Baklarz, Americas Data and AI Technical Sales

##### Testing
* Dale McInnis, Americas Data and AI Technical Sales

##### Concept
* Based on work by Elena Márquez and Srajan Dube

##### Milvus Vector Encoding
* Based on work by Katherine Ciaravalli

##### TechZone Support
* Special Thanks to Ben Foulkes for supporting this effort in TechZone
'''    
st.write(description)

st.subheader("Hardware and Software",divider=True)

description = '''
**Server**    
- Techzone VMWare environment  
- [Red Hat Linux 9](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux/workstations)  
- 16 VPC, 64 Gb Server  

**System Software**
* [Watsonx.data 2.1.0](https://www.ibm.com/docs/en/watsonx/watsonxdata/2.1.x) - IBM Data Lakehouse environment
* [Presto 0.286](https://prestodb.io/docs/0.286/) - Database engine used to query data in the lakehouse
* [Milvus](https://milvus.io/docs) - Vector database included in watsonx.data
* [Ollama](https://ollama.com/) - Platform for running LLMs locally

**Application Libraries**
* [Streamlit](https://streamlit.io/) - Web interface framework 
* [Llama Index](https://www.llamaindex.ai/) - Data framework for building LLM applications
* [pyMilvus](https://milvus.io/api-reference/pymilvus/v2.4.x/About.md) - Python SDK of Milvus
* [prestodb](https://github.com/prestodb/presto-python-client) - Presto client
* [langchain](https://www.langchain.com/langchain) - LangChain is a framework designed to simplify LLM applications
* [sqlalchemy](https://www.sqlalchemy.org/) - SQLAlchemy is an Object Relational Mapper for database interactions
* [sentence_transformer](https://sbert.net/) - Sentence Transformers provides modules for accessing, using, and training embedded models
* [pandas](https://pandas.pydata.org/) - pandas provides data structures designed to work with relational or tabular data
* [easyocr](https://github.com/JaidedAI/EasyOCR) - OCR reader which scans images and extracts text in 80+ languages
* [pymupdf](https://github.com/pymupdf/PyMuPDF) - PyMuPDF is a high performance Python library for data extraction, analysis, conversion & manipulation of PDF documents
'''

st.write(description)

st.subheader("Documentation",divider=True)

description = '''
The documentation for this system can be found at the [watsonx.data and Milvus demo](https://IBM.github.io/watsonx-data-milvus/) site.
'''

st.write(description)