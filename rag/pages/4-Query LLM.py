#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
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
    collection_list = listCollections()
    collection_list.sort()        
    col_name = st.selectbox("Current Collection", collection_list, index=0,label_visibility="visible",placeholder="Current Collection")
    if (col_name not in [None, ""]):
        sts.collection_name = col_name 
        sts.collection_index = collection_list.index(sts.collection_name)

def toSettings():
    settings = []
    if (sts.displayrag == False):
        settings.append("Hide RAG")
    if (sts.terse == False):
        settings.append("Verbose")
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
    sts['sentences'] = sts.llm_sentences
    if (sts.sentences == "Off"):
        sts.rag = False
    else:
        sts.rag = True

def getTemperature():
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
    sts['terse'] = True
    sts['displayrag'] = True
    sts['random'] = True
    if (len(sts.llm_settings) > 0):
        for key in sts.llm_settings:
            if ("Verbose" in key):
                sts['terse'] = False
            elif ("Hide" in key):
                sts['displayrag'] = False
            elif ("Repeatable" in key):
                sts['random'] = False
            else:
                pass

st.set_page_config(
    page_title="Chat",
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
    with st.popover("Technical Details"):
        details = \
"""
##### LLM Query
This dialog is used to query the LLM using a set of parameters to modify the original prompt. 

The LLM parameters on the left side of the screen provides an opportunity to adjust which LLM to use when requesting a response as well as limit the number of sentences that the RAG process generates.

##### Current LLM Model

The LLM pulldown displays the current LLM model being used and provides a list of LLMs that are currently available in the system. Choose which LLM you want to use to answer your query. The default LLM is the Instructlab/granite-7b-lab model.

#### Current Collection
The current collection pulldown displays the collection that is being used to generate the RAG prompts. You can select from your other document collections by selecting one from the pulldown list. 

##### LLM Settings
To select one of the options, press on the option name so that it is highlighted in red. 
* Hide RAG - The system default is to display the RAG prompt that is generated. You can turn this off by selecting the "Hide RAG" option.
* Verbose - The system default is to tell the LLM to limit the output (terse). Selecting the Verbose option will allow the LLM to generate more output.
* Repeatible - The LLM is provided with a random seed every time a question is asked. This usually results in slightly different answers when you repeat a question. By selecting the Repeatible option, the LLM is always provided with the same seed value (42 - Ask the LLM what that number means!).

##### Maximum RAG Sentences
The **Maximum RAG Sentences** provides values of 0, 2, 4, 6, 8 as the maximum number of sentences to generate for a RAG prompt. The default value is 4. Setting the value to zero will turn off the RAG prompt. Using a larger number of sentences will slow down the LLM response but may result in a higher quality answer.

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

st.subheader("Chat",divider=True)

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
        llmnames = getLLMs()
        index = llmnames.index(sts.model)
        selected_model = st.selectbox("Current LLM Model", llmnames, index=index,label_visibility="visible",placeholder="LLM Models")
        if (selected_model not in [None, ""]):
            sts.model = selected_model

        collection_select()

        previous_prompt = None
      
        st.pills("LLM Settings",
                 ["Hide RAG","Verbose","Repeatable"],
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
    with st.chat_message(message["role"]):
        st.write(message["content"],unsafe_allow_html=True)
_ = st.pills("",["Clear"],selection_mode="single",label_visibility="collapsed",default=None,key="clearit",on_change=doClear)

# Accept user input

if prompt := st.chat_input(placeholder="Enter your question"):
    add_prompt(prompt)

    bold = "normal"
    span_green = f'<span style="color: green; font-weight: {bold};">'
    span_red   = f'<span style="color: red; font-weight: {bold};">'
    span_blue  = f'<span style="color: blue; font-weight: {bold};">'
    span_end   = '</span>'

    if sts.rag:
        rag_color = span_green
    else:
        rag_color = span_red
    
    if sts.terse:
        terse_color = span_green
    else:
        terse_color = span_red

    if sts.random:
        random_color = span_green
    else:
        random_color = span_red

    settings = f"Model: {span_blue}{sts.model}{span_end}&emsp;Use RAG: {rag_color}{sts.rag}{span_end}&emsp;Concise: {terse_color}{sts.terse}{span_end}&emsp;Sentences: {span_blue}{sts.sentences}{span_end}&emsp;Temperature: {span_blue}{toTemperature()}{span_end}&emsp;Random Seed: {random_color}{sts.random}{span_end}&emsp;Collection: {span_blue}{sts.collection_name}{span_end}"
    
    with st.chat_message("user"):
        if (sts.rag == False):
            if sts.terse:
                llm_prompt = f"Provide a concise response to this prompt: {prompt}"
            else:
                llm_prompt = prompt

            if sts.displayrag:
                display_prompt = llm_prompt
            else:
                display_prompt = prompt

        else:

            sentences = query_milvus(prompt,sts.collection_name,sts.sentences)
            llm_prompt = createPrompt(prompt,sts.terse,sentences)
            if (llm_prompt == None):
                st.error("Unable to create a prompt based on the document that was provided.")
                log(program,"[1] Unable to create a prompt based on the document that was provided.")
            if sts.displayrag:
                display_prompt = llm_prompt
            else:
                display_prompt = prompt                

        if sts.displaysettings:
            display_prompt = f"{display_prompt}\n\n{settings}"

        sts.messages.append({"role": "user", "content": display_prompt})

        st.write(display_prompt,unsafe_allow_html=True)
  
    # Display assistant response in chat message container

    with st.chat_message("assistant"):
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
