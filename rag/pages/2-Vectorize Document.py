#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Vectorize documents panel
#

import streamlit as st
import wxd_data as db
import wxd_milvus as wxd_milvus
import pandas as pd
import re
from streamlit import session_state as sts
from wxd_utilities import setCredentials, log, check_password, version_reset

def document_selection():
    """
    Document_selection is called by the edit Dataframe control to save the users selection. If you 
    don't save the selection, the values are lost when the screen refreshes itself.
    """
    
    if ("vectordocs" not in sts):
        if ("docs_selected" in sts):
            del sts.docs_selected
    else:
        sts["docs_selected"] = sts.vectordocs

def getVectorsize():
    """
    The vector size is small, medium, or large. This will impact the size of the
    paragraphs that are stored in the vector database.
    """
    sts['vectorsize'] = sts._vectorsize

@st.fragment()
def selectDocuments():
    connection = db.connectPresto()
    if (connection == None):
        db.badConnection()
        st.stop()

    details = db.runSQL(connection,'select False as "Selected", id, document, type from iceberg_data.documents.metadata order by id asc')
    sts.doc_details = details

    docs = st.data_editor(details,
        column_config={
        "selected" : st.column_config.Column(st.column_config.CheckboxColumn("Selected"),width="small"),
        "id"       : st.column_config.Column("ID",width="small",disabled=True),
        "document" : st.column_config.Column("Document/URL",width="large",disabled=True),
        "type"     : st.column_config.Column("Type",width="small",disabled=True)
        },
        # disabled=["id","document","type"],
        on_change=document_selection,
        key="vectordocs",
        hide_index=True,
        use_container_width=True
    )

st.set_page_config(
    page_title="Prompts",
    page_icon=":infinity:",
    layout="wide"
)

if not check_password():
    st.stop()

# version_reset()    

if ('initialized' not in sts):
    if (setCredentials() == False):
        st.error("Unable to get credentials required to connect to watsonx.data.")
        log("Startup","[1] Unable to get credentials required to connect to watsonx.data")
        st.stop()

connection = db.connectPresto()
if (connection == None):
    db.badConnection()
    st.stop()

program = "Prompts"

st.header("Milvus - Vector Storage",divider=True)
description = """
The Milvus vector database is used to store sentences extracted from documents, and then converted into vectors for searching. Choose one or more documents from the uploaded files to have them stored into Milvus and vectorized for use in RAG generation on the LLM screen.
"""
st.write(description)

with st.container(border=False,height=40):
    with st.popover("Technical Details"):
        details = \
"""
##### Vectorize Documents
In order to create a RAG (Retrieval Augmented Generation), one or more documents must be selected from the database, the text
extracted, and then stored into Milvus and vectorized.

The process to vectorize a document involves converting the document (PPT, PDF, etc...) into RAW text. Once the text
is available, the text is split into smaller chunks, with each chunk containing 250 or so words. These chunks are stored
in a Milvus database and the text is vectorized using an algorithm (sentence-transformers/all-MiniLM-L6-v2).

Once the vectorization is completed, we can use search the data for similar sentences when generating a RAG prompt.

The LLM can run without vectorizing a database, but it will not be able to generate a RAG prompt. The system will display
a warning if you attempt to use a RAG prompt without a document that has been vectorized.

##### Vector Size
The document is broken up into tokens which are then inserted into Milvus. The size of the tokens determines the number of words that are captured in each vector. The three options (Small, Medium, Large) translate to 512, 1024, and 2048 tokens. This is roughly equal to 64, 128, and 256 words per vector. The tradeoffs between the different sizes are:

  * Smaller vector size may require more sentences in the RAG prompt to provide enough details for the LLM
  * Larger vector size will take more time for the LLM to process
  * The tradeoff is between number of vectors, processing time, and size of RAG prompt

##### Collections
One or more documents make up a collection. Select the documents that you want to be included in a collection, and they will be vectorized as a group in Milvus. When you query the LLM, select the collection which best matches your question and the RAG prompt will use the data from the collection to generate the text.

If you use the name of an existing collection, the contents of that collection will be overwritten with the new documents.
"""
        st.markdown(details)

with st.sidebar:

    col1, col2  = st.columns([0.95,0.05])
    st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:5px ;
        }
        </style>
        """,unsafe_allow_html=True)
    with col1:
        st.pills("Vector Size",
                 ["Small","Medium","Large"],
                 selection_mode="single",
                 on_change=getVectorsize,
                 key="_vectorsize",
                 default=sts.vectorsize
                 )

st.subheader("Current Document Collections",divider=True)

description = \
"""
The following is a list of document collections that have already been vectorized. 
"""

st.markdown(description)

with st.form("Refresh", clear_on_submit=False):

    collection_list = wxd_milvus.listCollections()
    collection_list.sort()

    col1, col2 = st.columns([0.5,0.5])
    with col1:
        df = pd.DataFrame(collection_list,columns=["Collection Name"])
        st.dataframe(df,hide_index=True,height=150,width=400)

    button =  st.form_submit_button("Refresh List")

st.subheader("Document list",divider=True)
description = '''
The current collection of documents that are stored in watsonx.data are found in the list below. Select the document(s) that you want vectorized and press the Vectorize button. If you use an existing collection name (see above), it will replace the contents of that collection. Note that you must have at least one collection in order to use RAG prompts.
'''

st.write(description)

selectDocuments()

collection_name = st.text_input("Enter collection name",value="Default") 

vectorize = st.button("Vectorize Collection")

if vectorize:
    if (collection_name.strip() in ["","None"]):
        st.error("Please supply a name for the document collection.")
    else:
        collection_name = re.sub('\W|^(?=\d)','_', collection_name.strip())
        collection_name = collection_name.strip("_")
        if ("docs_selected" not in sts):
            st.error("You need to select at least one document to vectorize.")
        else:
            with st.spinner("Vectorizing collection"):
                ids = []
                edited_rows = sts.docs_selected['edited_rows']
                for row_no in edited_rows:
                    if edited_rows[row_no]["Selected"]:
                        df = sts.doc_details
                        id = df.loc[row_no,'id']
                        ids.append(id)

                collection = wxd_milvus.storeVectors(connection,collection_name,ids,sts.vectorsize)
                if (collection in [None,""]):
                    st.error("Error in vectorizing the document. Check the log for details.")
                    sts.collection = None
                else:
                    st.success("Documents successfully vectorized.")
                    sts.collection = collection

st.page_link("Watsonx_Milvus_Demo.py",label=":blue-background[Home]",icon=":material/arrow_forward:")
