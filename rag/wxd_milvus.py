#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
#   Milvus routines
#
#   loadvectors - Given a list of document IDs, load the documents in as vectors into Milvus
#   querymilvus - Given a string, retrieve the vectors from Milvus that best match
#

import warnings
import streamlit as st
from streamlit import session_state as sts
from wxd_utilities import log

def connectMilvus():
    """
    Connect to the local Milvus service using the ORM service. 
    The MilvusClient is defective and not recommended at the present time.
    """
        
    from pymilvus import connections

    program = "connectMilvus"

    if ("milvusConnection" in sts):
        connection = sts.milvusConnection
        if (connection is not None):
            return connection
        
    host            = sts['milvus_host']    
    port            = sts['milvus_port']    
    user            = sts['milvus_user']    
    password        = sts['milvus_password']
    server_pem_path = sts['server_pem_path']

    try:
        connections.connect(alias='default',
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        server_pem_path=server_pem_path,
                        server_name='watsonxdata',
                        secure=True)
        connection = True     
        log(program,"Connected to Milvus")   
    
    except Exception as e:
        log(program,"[1] Unable to connect to Milvus")
        log(program,f"[1] {repr(e)}")
        connection = False

    sts.milvusConnection = connection

    return connection

def dropCollections(deleteOnly=None):
    """
    Remove all of the collections that are currently in the Milvus database.
    """

    from pymilvus import utility

    program = "dropCollections"

    if (connectMilvus() == False):
        log(program,"[1] Unable to drop collections")
        return False
    
    collections = listCollections()

    for collection in collections:
        if (deleteOnly is not None):
            if (collection in deleteOnly):
                try:
                    utility.drop_collection(collection)
                except:
                    pass
        else:
            try:
                utility.drop_collection(collection)
            except:
                pass
            
    return True

@st.fragment
def listCollections(_checkbox=False):
    """
    This function will return a list of document collections that have been stored in Milvus. If the _checkbox value is set to true, the value returned includes a selection box (for editting) in a Pandas dataframe.
    """

    import pandas as pd
    from pymilvus import utility
    from wxd_data import connectPresto, badConnection, storeDocument
    from wxd_utilities import log

    program = "listCollections"

    if (connectMilvus() == False):
        log(program,"[1] Unable to list collections")
        return None
    
    collection_list = utility.list_collections()

    if _checkbox:
        false_list = [False] * len(collection_list)
        collection_list = pd.DataFrame(zip(false_list,collection_list),columns=['Selected','Collection']).sort_values("Collection")    

    return collection_list

def storeVectors(_connection, collection_name, ids, vectorsize):
    """
    Given a text document, split the text into chunks and then load them into
    Milvus. After the load is completed, return the collection that can be
    used for queries.
    """

    from wxd_data import getDocument
    from pymilvus import utility, FieldSchema, CollectionSchema, Collection, DataType
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from sentence_transformers import SentenceTransformer
  
    program = "loadVectors"

    if (connectMilvus() == False):
        log(program,"[1] Unable to list collections")
        return None

    document = None
    for id in ids:
        if (document == None):
            document = getDocument(_connection, id)
        else: 
            nextdoc  = getDocument(_connection, id)
            document = f"{document}\n{nextdoc}"

    if (document in [None,""]):
        log(program,"[2] Error extracting the document")
        return None
 
    title = "Document"

    log(program,f"Loading document with length={len(document)}")
    
    warnings.filterwarnings('ignore')
    
    if (vectorsize == "Small"):
        chunk_size = 512
    elif (vectorsize == "Medium"):
        chunk_size = 1024
    elif (vectorsize == "Large"):
        chunk_size = 2048
    else:
        chunk_size = 512
        
    chunk_overlap = 32
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap) 
        docs = text_splitter.create_documents([document])
    except Exception as e:
        log(program,f"[3] Error in Text Splitter")
        log(program,f"[3] {repr(e)}")
        return None
    
    passages = []
    passage_titles = []
    for doc in docs:
        passages.append(doc.page_content)
        passage_titles.append(title)
    
    utility.drop_collection(collection_name)
    
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True), # Primary key
        FieldSchema(name="article_title", dtype=DataType.VARCHAR, max_length=255,),
        FieldSchema(name="article_text", dtype=DataType.VARCHAR, max_length=2500,),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),
    ]
    
    schema = CollectionSchema(fields, "Documents")
    
    collection = Collection(collection_name, schema)
    
    # Create index
    index_params = {
            'metric_type':'L2',
            'index_type':"IVF_FLAT", #IVF_FLAT
            'params':{"nlist":2048}
    }

    try:
        collection.create_index(field_name="vector", index_params=index_params)
    except Exception as e:
        log(program,f"[4] Error in Index Creation")
        log(program,f"[4] {repr(e)}")
        return None


    # Create vector embeddings + data
    try:
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2') # 384 dim
        passage_embeddings = model.encode(passages)
    except Exception as e:
        log(program,f"[5] Error in Sentence Transformer")
        log(program,f"[5] {repr(e)}")
        return None    
    
    basic_collection = Collection(collection_name) 
    data = [
        passage_titles,        
        passages,
        passage_embeddings
    ]

    try:
        out = basic_collection.insert(data)
        basic_collection.flush()  # Ensures data persistence

    except Exception as e:
        st.error("Vector loading error. Check the log for details.")	          
        log(program,f"[6] Error in Vector load step.")
        log(program,f"[6] {repr(e)}")
        return None

    log(program,f"Loading complete")        
    return basic_collection 

#new

def query_milvus(query, collection_name, max_results):
    """
    Given a query, convert the text into a vector and then look for similar text chunks in the document(s) 
    that you vectorized. The max_results field determines how many sentences are returned.
    """

    from sentence_transformers import SentenceTransformer
    from pymilvus import Collection
    import pandas

    program = "query_milvus"

    if (connectMilvus() == False):
        log(program,"[1] Unable to query collections")
        return None    
    
    collection = Collection(collection_name) 
    collection.load()    

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2') # 384 dim
    query_embeddings = model.encode([query])

    # Search
    search_params = {
        "metric_type": "L2", 
        "params": {"nprobe": 5}
    }

    results = collection.search(
        data=query_embeddings, 
        anns_field="vector", 
        param=search_params,
        limit=max_results,
        expr=None, 
        output_fields=['article_text'],
    )

    distances = []
    text = []

    for i in range(0,len(results[0])):
        distances.append(results[0][i].distance)
        text.append(results[0][i].entity.get('article_text'))
    
    df = pandas.DataFrame(zip(distances,text),columns=['distance','text']).sort_values(by=['distance'])

    log(program,f"Milvus query - records returned = {len(df)}")
    
    return df

def createPrompt(prompt, results):
    """
    Given a question (prompt), generate the sentence that will be provided to the LLM.
    """

    import re
    from wxd_utilities import log

    program = 'createPrompt'

    relevant_chunks  = []
    min_distance = 999

    for _, row in results.iterrows():
        chunk = row['text'].strip()
        # chunk = re.sub(r"^[a-z].*?\.(.*)$",r"\1",chunk).strip()
        relevant_chunks.append(chunk) # row['text']) # re.sub(r"^.*?\. (.*\.).*$",r"\1",row['text']))
        if row['distance'] < min_distance:
            min_distance = row['distance']

    if (len(relevant_chunks) == 0):
        log(program,f"[1] No sentences were found to create a RAG prompt.")
        return None
    else:
        log(program,f"RAG generated with {len(relevant_chunks)} sentences. Minimum distance={min_distance}")
    
    data = "\n\n".join(relevant_chunks)

    header = """Answer the question based on the context below. If the question cannot be answered using the information provided answer with "I don't know"."""

    question = f"{header}\n\nContext:\n\n{data}.\n\nQuestion: {prompt}"

    return question, min_distance
