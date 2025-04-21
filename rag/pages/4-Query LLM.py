#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Query LLM Panel
#

import streamlit as st
import pandas as pd
from streamlit import session_state as sts
from wxd_milvus import query_milvus, createPrompt, listCollections
from wxd_utilities import log, runOS, setCredentials, check_password, version_reset
from wxd_data import getDocuments, connectPresto, badConnection, getDocument
from wxd_ollama import getLLMs, askLLM

def add_prompt(prompt):
    """
    Place a prompt into the saved queries array for future retrieval
    """

    log("prompt",prompt)
    if (prompt not in [None, ""]):
        if ("queries" in sts):
            if (prompt not in sts.queries):
                sts.queries.append(prompt)

@st.fragment
def collection_select():
    """
    Retrieve a list of collections that are currently registered in Milvus and
    allow the user to select from one to use in the search.
    """
    collection_list = listCollections()
    collection_list.sort()        
    col_name = st.selectbox("Milvus Collection", collection_list, index=0,label_visibility="visible",placeholder="Milvus Collection")
    if (col_name not in [None, ""]):
        sts.collection_name = col_name 
        sts.collection_index = collection_list.index(sts.collection_name)

@st.fragment
def document_select(connection):
    """
    Retrieve a list of documents currently in the watsonx.data catalog and allow the
    user to select one as the source to be used for a question. You can optionally 
    include a RAG prompt with this. 
    """
    document_list = getDocuments(connection)
    display_text = []
    for index, row in document_list.iterrows():
        index = row['id']
        document = row['document']
        display_text.append(f"{index}: {document}")

    col_name = st.selectbox("Source Document", display_text, index=None,label_visibility="visible",placeholder="None")
    if (col_name not in [None, ""]):
        splitargs = col_name.split(":")
        sts.document_index = int(splitargs[0])  
        sts.document_name = splitargs[1] 
    else:
        sts.document_index = None
        sts.document_name = None    

def toSettings():
    settings = []
    if (sts.displayrag == False):
        settings.append("Hide RAG")
    if (sts.random == False):
        settings.append("Repeatable")
    return settings

def toTemperature():
    temp = "Medium"
    if (sts.temperature == 0):
        temp = "None"
    elif (sts.temperature == 0.3):
        temp = "Low"
    elif (sts.temperature == 0.7):
        temp = "Medium"
    elif (sts.temperature == 1.5):
        temp = "High"
    else:
        temp = "Medium"
    return temp

def doClear():
    if (sts.clearit == "Clear"):
        sts.messages  = []
    sts.clearit = None

def getSentences():
    """
    The maximum number of sentences to use during RAG generation is set from
    none (off) to 3/6/9. 
    """
    sts['sentences'] = sts.llm_sentences
    if (sts.sentences == "Off"):
        sts.rag = False
    else:
        sts.rag = True

def getTemperature():
    """
    Temperature is a settings used with LLMs to determine how much creativity
    is used when generating the answer. None tells the LLM to stick 
    strictly to the facts while moving into higher settings will
    provide for some more flexibility in the answer.
    """
    if (sts.llm_temperature == "None"):
        sts.temperature = 0
    elif (sts.llm_temperature == "Low"):
        sts.temperature = 0.3
    elif (sts.llm_temperature == "Medium"):
        sts.temperature = 0.7
    elif (sts.llm_temperature == "High"):
        sts.temperature = 1.5
    else:
        sts.temperature = 0.7

def getSettings():
    """
    LLM settings. Display the RAG prompt on the screen (default is yes), and 
    use repeatible seeds when generating the reply (default is no).
    """
    sts['displayrag'] = True
    sts['random'] = True
    if (len(sts.llm_settings) > 0):
        for key in sts.llm_settings:
            if ("Hide" in key):
                sts['displayrag'] = False
            elif ("Repeatable" in key):
                sts['random'] = False
            else:
                pass

def setMenu():
    """
    Set whether we see the menus in the sidebar or inline with the prompt
    """            
    sts["menu_inline"] = sts._menu_inline

st.set_page_config(
    page_title="Chat",
    page_icon=":infinity:",
    layout="wide"
)                

if not check_password():
    st.stop()

if ('initialized' not in sts):
    if (setCredentials() == False):
        st.error("Unable to get credentials required to connect to watsonx.data.")
        log("Startup","[1] Unable to get credentials required to connect to watsonx.data")
        st.stop()

connection = connectPresto()
if (connection == None):
    badConnection()
    st.stop()    

program = "Chat"

st.header("Query LLM",divider=True)

introduction = \
'''
Enter your questions below and wait for the response from the LLM. Note that this system does not have GPUs attached to it so the response may take a minute or so to return. Update these settings on the left side to adjust the text provided to the LLM.
'''

st.write(introduction)

if (sts.model == None):
    st.error("A model needs to be loaded into the system before you attempt to begin a chat session. Please use the LLM Models screen to upload a model to use.")
    st.stop()

with st.container(border=False,height=40):
    cols = st.columns(2)
    with cols[0]:    
        with st.popover("Technical Details",use_container_width=True):
            details = \
    """
    ###### Press Escape to Close this Window

    ##### LLM Query
    This dialog is used to query the LLM using a set of parameters to modify the original prompt. 

    The LLM parameters on the left side of the screen provides an opportunity to adjust which LLM to use when requesting a response as well as limit the number of sentences that the RAG process generates.

    ##### Inline Settings
    Turning this setting ON will place the settings in the Chat window rather than in the sidebar.

    ##### Current LLM Model
    The LLM pulldown displays the current LLM model being used and provides a list of LLMs that are currently available in the system. Choose which LLM you want to use to answer your query. The default LLM is the Instructlab/granite-7b-lab model.

    ##### Current Collection
    The current collection pulldown displays the collection that is being used to generate the RAG prompts. You can select from your other document collections by selecting one from the pulldown list. 

    ##### Source Document
    If you specific a document in this pulldown, the LLM will be provided with the contents of this document before answering your question. Using a document will stop the RAG generation since the generated sentences will already be included in the document.

    ##### LLM Settings
    To select one of the options, press on the option name so that it is highlighted in red. 
    * Hide RAG - The system default is to display the RAG prompt that is generated. You can turn this off by selecting the "Hide RAG" option.
    * Repeatible - The LLM is provided with a random seed every time a question is asked. This usually results in slightly different answers when you repeat a question. By selecting the Repeatible option, the LLM is always provided with the same seed value (42 - Ask the LLM what that number means!).

    ##### Maximum RAG Sentences
    The **Maximum RAG Sentences** provides values of 0ff, 3, 6, 9 as the maximum number of sentences to generate for a RAG prompt. The default value is 3. Setting the value to Off will turn off the RAG prompt. Using a larger number of sentences will slow down the LLM response but may result in a higher quality answer.

    The **Creativity (Temperature)** values are None (0), Low (0.3), Medium (0.7), and High (1.5). Use a lower temperature value when you want more dependable output. Use a higher temperature value when you want to increase the randomness and variability or the output, such as when you want creative output. Remember, randomness can also lead to inaccurate or nonsensical output. The default setting is Medium.

    ##### Previous Questions
    The left sidebar includes a list of questions previously sent to the LLM. To copy a question into the LLM prompt, use the following steps:
    1. Click on the question you want to copy from the list (it will be highlighted)
    2. Use the keyboard copy button (Windows/Linux &#8963;&#8211;c, Mac &#8984;&#8211;c) to place the value into the clipboard
    3. Click on the LLM question input line
    4. Use keyboard paste button (Windows/Linux &#8963;&#8211;v, Mac &#8984;&#8211;v) to place the copied value into the line

    ##### Clear and Stop

    The bottom of the LLM Chat window will have a Clear button. This button will clear the history of questions and LLM responses. 

    The LLM window will display a Stop button while the LLM is answering a question. If you find that the LLM is taking too long to respond (or saying too much), press the Stop LLM button. Note that stopping the LLM will clear the response on the screen.

    ##### Application Logic
    The process which takes place when you enter a question is:
    * The question is turned into a vector value
    * The value is compared to the sentence vectors that were generated in the Vectorize Document step
    * The 3 best sentences (or whatever you may have set the sentence limit to) will be used to generate a RAG prompt
    * The RAG prompt is sent to the LLM
    * The program displays the results as they are generated by the LLM

    Note that this system does not have GPUs available to it. This means that the response from the LLM could be in the order of minutes so you will need some patience! If you think you have seen enough output, press the STOP button.

    If you want to view the Milvus vector distance for the RAG prompts, view the LOG file output.
    """
            st.markdown(details)

st.subheader("Chat",divider="blue")

with st.sidebar:

    st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:5px ;
        }
        </style>
        """,unsafe_allow_html=True)    

    if ("menu_inline" not in sts):
        sts["menu_inline"] = False
    
    col1, col2  = st.columns([0.95,0.05])

    with col1:
        _ = st.toggle("Inline Settings",value=sts.menu_inline,on_change=setMenu,key="_menu_inline")

        if (sts.menu_inline == False):
            llmnames = getLLMs()
            index = llmnames.index(sts.model)
            selected_model = st.selectbox("Current LLM Model", llmnames, index=index,label_visibility="visible",placeholder="LLM Models")
            if (selected_model not in [None, ""]):
                sts.model = selected_model

            collection_select()

            document_select(connection)

            previous_prompt = None

            st.pills("LLM Settings",
                    ["Hide RAG","Repeatable"],
                    selection_mode="multi",
                    on_change=getSettings,
                    key="llm_settings",
                    default=toSettings(),
                    label_visibility="visible"
                    )
            st.pills("Maximum RAG Sentences",
                    ["Off",3,6,9],
                    selection_mode="single",
                    on_change=getSentences,
                    key="llm_sentences",
                    default=sts.sentences
                    )
            st.pills("Creativity (Temperature)",
                    ["None","Low","Medium","High"],
                    selection_mode="single",
                    on_change=getTemperature,
                    key="llm_temperature",
                    default=toTemperature()
                    )

    df = pd.DataFrame(sts.queries,columns=['Previous Questions']).sort_values(by=['Previous Questions'])      
    st.dataframe(df,hide_index=True,selection_mode="single-column",use_container_width=True)

if "messages" not in sts:
    sts.messages = []

# Display chat messages from history on app rerun
for message in sts.messages:
    if (message["role"] == "user"): 
        avatar = ":material/face:"
    else:
        avatar = ":material/memory:" #  ":material/screen_search_desktop:"
    with st.chat_message(message["role"],avatar=avatar):
        st.write(message["content"],unsafe_allow_html=True)
    
cols = st.columns([3,9,9,9,8,8,12])
with cols[0]:
    _ = st.pills("",["Clear"],selection_mode="single",label_visibility="collapsed",default=None,key="clearit",on_change=doClear)
    if (sts.menu_inline == True):
        with cols[1]:
            llmnames = getLLMs()
            index = llmnames.index(sts.model)
            selected_model = st.selectbox("Current LLM Model", llmnames, index=index,label_visibility="visible",placeholder="LLM Models")
            if (selected_model not in [None, ""]):
                sts.model = selected_model
        
        with cols[2]:

            collection_select()

        with cols[3]:

            document_select(connection)

        previous_prompt = None

        with cols[4]:
            st.pills("LLM Settings",
                    ["Hide RAG","Repeatable"],
                    selection_mode="multi",
                    on_change=getSettings,
                    key="llm_settings",
                    default=toSettings(),
                    label_visibility="visible"
                    )

        with cols[5]:
            st.pills("Maximum RAG Sentences",
                    ["Off",3,6,9],
                    selection_mode="single",
                    on_change=getSentences,
                    key="llm_sentences",
                    default=sts.sentences
                    )

        with cols[6]:                    
            st.pills("Creativity (Temperature)",
                    ["None","Low","Medium","High"],
                    selection_mode="single",
                    on_change=getTemperature,
                    key="llm_temperature",
                    default=toTemperature()
                    )

# Accept user input

if prompt := st.chat_input(placeholder="Enter your question"):
    add_prompt(prompt)

    bold = "normal"
    span_green   = f'<span style="color: green; font-weight: {bold};">'
    span_red     = f'<span style="color: red; font-weight: {bold};">'
    span_blue    = f'<span style="color: blue; font-weight: {bold};">'
    span_yellow  = f'<span style="color: orange; font-weight: {bold};">'    
    span_end     = '</span>'

    if sts.rag:
        rag_color = span_green
    else:
        rag_color = span_red

    if sts.random:
        random_color = span_green
    else:
        random_color = span_red
    
    with st.chat_message("user",avatar=":material/face:"):

        llm_prompt = None
        display_prompt = None

        # 1: Are you providing a document as reference? If so, RAG is disabled
        if (sts.document_index not in [None,""]):

            # question = f"{header}\n\nContext:\n\n{data}.\n\nQuestion: {prompt}"            

            document_text = getDocument(connection,sts.document_index)
            if (document_text not in [None,""]):
                prefix = """Answer the question based on the context below. If the question cannot be answered using the information provided answer with "I don't know"."""
                suffix  = "With the provided document, answer the following question: "
                llm_prompt = f"{prefix}\n\nContext:\n\n{document_text}\n\nQuestion: {prompt}"
                display_prompt = f"{prefix}\n\nSource Document: {sts.document_name}\n\nQuestion: {prompt}"
            else:
                llm_prompt = prompt
                display_prompt = prompt

        # 2: Are you including a RAG prompt with the prompt? If NO -> Just ask the question
        elif (sts.rag == False):

            llm_prompt = prompt
            display_prompt = prompt

        # 3: Yes you do want a RAG prompt to be generated
        else:

            sentences = query_milvus(prompt,sts.collection_name,sts.sentences)
            llm_prompt, min_distance = createPrompt(prompt,sentences)
            if (llm_prompt == None):
                st.error("Unable to create a RAG prompt based on the collection that was provided.")
                log(program,"[1] Unable to create a RAG prompt based on the collection that was provided.")
                llm_prompt = "No RAG was generated!"

            if sts.displayrag:
                display_prompt = llm_prompt
            else:
                display_prompt = prompt    

        if (sts.document_index not in [None,""]):
            settings = f"Model: {span_blue}{sts.model}{span_end}&emsp;Document: {span_blue}{sts.document_name}{span_end}&emsp;Temperature: {span_blue}{toTemperature()}{span_end}&emsp;Random Seed: {random_color}{sts.random}{span_end}" 
        elif (sts.rag == False):
            settings = f"Model: {span_blue}{sts.model}{span_end}&emsp;RAG: {rag_color}{sts.rag}{span_end}&emsp;Temperature: {span_blue}{toTemperature()}{span_end}&emsp;Random Seed: {random_color}{sts.random}{span_end}&emsp;Collection: {span_blue}{sts.collection_name}{span_end}&emsp;"                          
        else:
            if (min_distance <= .75):
                distance_color = span_green
            elif (min_distance <= 1):
                distance_color = span_yellow
            else:
                distance_color = span_red
            settings = f"Model: {span_blue}{sts.model}{span_end}&emsp;RAG: {rag_color}{sts.rag}{span_end}&emsp;Sentences: {span_blue}{sts.sentences}{span_end}&emsp;Temperature: {span_blue}{toTemperature()}{span_end}&emsp;Random Seed: {random_color}{sts.random}{span_end}&emsp;Collection: {span_blue}{sts.collection_name}{span_end}&emsp;Distance: {distance_color}{min_distance:.2f}{span_end}"                            

        display_prompt = f"{display_prompt}\n\n{settings}"

        sts.messages.append({"role": "user", "content": display_prompt})

        st.write(display_prompt,unsafe_allow_html=True)
  
    # Display assistant response in chat message container

    with st.chat_message("assistant",avatar=":material/memory:"):
        with st.status(f"LLM: {sts.model} is processing...", expanded=True, state="running") as status:
            try:
                _ = st.pills("",["Stop"],selection_mode="single",default=None,label_visibility="collapsed")
                answer = st.write_stream(askLLM(llm_prompt,sts.temperature,sts.random))
                status.update(label="Answered", state="complete")
                sts.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as e:
                answer = f"LMM Error: {repr(e)}"
                status.update(label="LLM Failed",state="error")
                sts.messages.append({"role": "assistant", "content": answer})
                log(program,answer)
                st.error(answer)
