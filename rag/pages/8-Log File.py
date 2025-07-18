#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Log file panel
#

import streamlit as st
import wxd_data as db
import datetime
from wxd_utilities import log, runOS, checkStatus, check_password, setPage
from streamlit import session_state as sts
import pandas as pd


setPage("Log File")

st.header("Log File",divider=True)
description = '''
The log file (/tmp/watsonx.log) contains information on what code was run during your session and any error messages that may have been generated. Use the refresh button to get the latest version of the log file into the display.
'''    
st.write(description)

st.page_link("https://ibm.github.io/watsonx-data-milvus/wxd-demo-log/", label="Additional Help",icon=":material/help:") 

logfile = None
with open("/tmp/watsonx.log","r") as fd:
    lines = fd.readlines()
    for line in lines:
        comma1 = line.find(",")
        comma2 = line.find(",",comma1+1)
        ts     = line[:comma1]
        routine = line[comma1+1:comma2]
        output  = line[comma2+1:]
        if (logfile is None):
            logfile =  f"{ts:8s}  {routine:17s}  {output}"
        else:
            logfile += f"{ts:8s}  {routine:17s}  {output}"

with st.container(height=500):            
    st.code(logfile,language=None)

# df = pd.read_csv("/tmp/watsonx.log",quotechar="`")
# st.dataframe(df.sort_index(axis=0),hide_index=True,use_container_width=True)

if (st.button("Clear Log")):
    try:
        with open("/tmp/watsonx.log","w") as fd:
            if ("version" in sts):
               v = sts.version
            else:
               v = "Unknown"
            today = datetime.datetime.now().strftime("%H:%M:%S")
            fd.write(f"{today},Log Start,================================================\n")
            fd.write(f"{today},Version,{v}\n")
            fd.write("Time,Routine,Message\n")    
    except:
        pass