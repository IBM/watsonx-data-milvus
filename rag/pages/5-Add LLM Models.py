#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Import an LLM Panel
#

import streamlit as st
import wxd_ollama
import pandas as pd
from wxd_utilities import runOS, setCredentials, log, check_password, version_reset
from streamlit import session_state as sts
from wxd_ollama import getLLMs, deleteLLM

st.set_page_config(
    page_title="Settings",
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

program = "Settings"

st.header("LLM Models",divider=True)

introduction = \
'''
This system has been built using the IBM instructlab/granite-7b-lab model. You can load additional models into the
system by using the load option below. Note that not all models can be downloaded into this environment. You must review the results of the load command to determine if the LLM was successfully loaded into the system. 
'''

st.write(introduction)

st.subheader("Current LLMs",divider=True)

introduction = \
'''
The following list contains all of the LLMs that are currently used in the system.
'''

st.write(introduction)

with st.form("Refresh", clear_on_submit=True):
    df = pd.DataFrame(wxd_ollama.getLLMs(),columns=['Model'])
    st.dataframe(df,use_container_width=True,hide_index=True)

    button = st.form_submit_button("Refresh List")

st.subheader("Load LLM",divider=True)

introduction = \
'''
Enter the name of the LLM that you want to load into the system below and press the Load button. Check the results of the load to make sure that the LLM was properly loaded into the system. The load process can take several minutes.

LLMs can be found at [Ollama](https://ollama.com/library) and [Hugging Face](https://huggingface.co/models).
'''

st.write(introduction)

with st.form("Upload", clear_on_submit=False):
    col1, col2 = st.columns([0.15,0.85])
    with col1:
        submitted = st.form_submit_button("Load LLM ")
    with col2:
        llmname = st.text_input("Enter an LLM model name",label_visibility="collapsed",placeholder="Enter an LLM model name")

    if submitted and llmname not in [None,""]: 
        with st.spinner(f"Loading LLM {llmname}"):
            loaded = wxd_ollama.loadLLM(llmname)
            if loaded:
                st.success(f"LLM {llmname} was successfully loaded.")
                if (sts.model == None):
                    sts.model = llmname
            else:
                st.error(f"LLM load of {llmname} failed. See the log file for details.")

    elif submitted: 
        st.error("You need to supply an LLM name to load!")
    else:
        pass

st.subheader("Remove LLM",divider=True)

introduction = \
'''
Select which LLM you want to remove from the system below.
'''

st.write(introduction)

with st.form("Delete", clear_on_submit=False):
    llmnames = wxd_ollama.getLLMs()
    col1, col2 = st.columns([0.15,0.85])
    with col1:
        submitted = st.form_submit_button("Delete LLM")
    with col2:
        selected_model = st.selectbox("LLM Models", llmnames,label_visibility="collapsed",placeholder="Enter an LLM model name")    
    
    if submitted and selected_model not in [None,""]: 
        results = deleteLLM(selected_model)
        llmnames = wxd_ollama.getLLMs()
        if (len(llmnames) == 0):
            st.warning("You need to load at least one model into the system before using the Chat system.")
            sts.model = None
        else:
            if (selected_model == sts.model):
                sts.model = llmnames[0]
                st.warning(f"The default model has changed to {sts.model}")
            else:
                st.success(f"The model {selected_model} was removed from the system.")        

    elif submitted: 
        st.error("You need to select an LLM to delete!")
    else:
        pass

st.page_link("Watsonx_Milvus_Demo.py",label=":blue-background[Home]",icon=":material/arrow_forward:")