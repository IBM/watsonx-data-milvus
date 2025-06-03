#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
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
from time import sleep
from streamlit import session_state as sts
from wxd_utilities import setCredentials, log, check_password, setPage

def document_selection():
    """
    Document_selection is called by the edit Dataframe control to save the users selection. If you 
    don't save the selection, the values are lost when the screen refreshes itself.
    """
    
    if ("_vectordocs" not in sts):
        if ("docs_selected" in sts):
            del sts.docs_selected
    else:
        sts["docs_selected"] = sts._vectordocs

def getVectorsize():
    """
    The vector size is small, medium, or large. This will impact the size of the
    paragraphs that are stored in the vector database.
    """
    sts['vectorsize'] = sts._vectorsize

def getCollectionName():
    """
    Get the name of the selected document
    """
    sts["collection_name"] = sts._collection_name

@st.fragment
def selectDocuments():
    """
    Select the documents you want to place into a collection.
    """
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
        key="_vectordocs",
        hide_index=True,
        use_container_width=False
    )

def delete_collection():
    """
    Remember the name of the collection you selected
    """
    sts["collection_delete"] = sts._collection_delete

@st.fragment
def list_collections():
    """
    Select a Collection that you want to delete, or to refresh the list.
    """

    details = wxd_milvus.listCollections(True)
    sts.collection_list = details

    if ("select_collection" not in sts):
        sts.selected_collection = None

    with st.container(border=True):    

        st.selectbox("Collections",sts.collection_list['Collection'],index=None,on_change=delete_collection,key="_collection_delete",placeholder="Select a collection to delete")

        columns = st.columns([8,10,80])

        with columns[0]:
            delete_button = st.button("Delete")
        with columns[1]:
            refresh_button = st.button("Refresh")    

        if delete_button:

            if ("collection_delete" not in sts or sts.collection_delete == None):
                st.error("You need to select a collection to delete.")
                return
            
            wxd_milvus.dropCollections(deleteOnly=sts.collection_delete)  

            st.success(f"Collection {sts.collection_delete} successfully deleted.") 
            sleep(0.5)     

            st.rerun()   

        elif refresh_button:

            sts.collection_delete = None
            st.rerun()

        else:
            pass

setPage("Vectorize")

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

st.header("Milvus - Vector Storage",divider="blue")
description = """
The Milvus vector database is used to store sentences extracted from documents, and then converted into vectors for searching. Choose one or more documents from the uploaded files to have them stored into Milvus and vectorized for use in RAG generation on the LLM screen.
"""
st.write(description)

st.page_link("https://ibm.github.io/watsonx-data-milvus/wxd-demo-vectorize/", label="Additional Help",icon=":material/help:")

st.subheader("Current Document Collections",divider="blue")

description = \
"""
The following is a list of document collections that have already been vectorized. To delete a collection, select the collection from the drop down list and press the Delete button. To update the list, press the Refresh button after adding a new collection.
"""

st.write(description)

list_collections()

st.subheader("Document list",divider="blue")
description = '''
The current collection of documents that are stored in watsonx.data are found in the list below. Select the document(s) that you want vectorized and press the Vectorize button. If you use an existing collection name (see above), it will replace the contents of that collection. Note that you must have at least one collection in order to use RAG prompts.
'''

st.write(description)

with st.container(border=True):

    selectDocuments()

    textColumns = st.columns([20,80])

    with textColumns[0]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Collection Name
        """,unsafe_allow_html=True)

    with textColumns[1]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Vector Size
        """,unsafe_allow_html=True)

    textColumns = st.columns([20,80])    

    with textColumns[0]:
        st.text_input("Enter collection name",value="Default",key="_collection_name",on_change=getCollectionName,label_visibility="collapsed")         
    with textColumns[1]:
        st.pills("Vector Size",
                 ["Small","Medium","Large"],
                 selection_mode="single",
                 on_change=getVectorsize,
                 key="_vectorsize",
                 default=sts.vectorsize,
                 label_visibility="collapsed"
                 )      
          
    vectorize = st.button("Vectorize Collection")          
    
    if vectorize:
        if ('collection_name' in sts):
            collection_name = sts['collection_name']
        else:
            collection_name = None
        if (collection_name == None or collection_name.strip() == ""):
            st.error("Please supply a name for the document collection.")       
        else:
            collection_name = re.sub('\W|^(?=\d)','_', collection_name.strip())
            errorCode = 0
            try:
                if (collection_name[0].isalpha() == False):
                    if (collection_name[0] == "_"):
                        errorCode = 0
                    else:
                        errorCode = 1
                elif ("docs_selected" not in sts):
                    errorCode = 2
                else:
                    rows = False
                    edited_rows = sts.docs_selected['edited_rows']
                    for row_no in edited_rows:
                        if edited_rows[row_no]["Selected"]:
                            rows = True
                            break
                    if (rows == False):
                        errorCode = 2
            except Exception as e:
                errorCode = 3

            if (errorCode != 0):
                if (errorCode == 1):
                    st.error("The first character of collection name must be a letter or underscore.")
                elif (errorCode == 2):
                    st.error("You need to select at least one document to vectorize.")
                else:
                    st.error("Unknown error")
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