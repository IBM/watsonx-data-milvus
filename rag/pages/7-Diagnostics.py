#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Diagnostic Panel
#

import streamlit as st
import wxd_data as db
from wxd_utilities import log, runOS, checkStatus, setCredentials, check_password, version_reset
from wxd_milvus import dropCollections, storeVectors
from streamlit import session_state as sts
from time import sleep
import pandas as pd
import os

@st.fragment
def getDownload():

    filename = st.text_input("Enter a filename",key="filename_download",value=sts.filename)
    col1, col2 = st.columns([0.15,0.85])
    with col1:
        submitted = st.button("Check file",on_click=getFilename)

    if (submitted and sts.validfile):
        with open(sts.filename, "rb") as file:
            with col2:
                btn = st.download_button(
                    label=f"Download {sts.filename}",
                    data=file,
                    file_name=sts.short,
                    )
    else:
        if sts.file_error not in [None,""]:
            st.error(sts.file_error)


def getFilename():
    sts["validfile"] = False
    sts["filename"] = sts.filename_download
    sts["file_error"] = None
    
    if (sts.filename not in [None,""]):       
        try:
            if os.path.isfile(sts.filename):
                sts["short"] = os.path.basename(sts.filename)
                sts["validfile"] = True
            else:
                sts.file_error = f"File does not exist: {sts.filename}"
        except Exception as e:
            sts.file_error = f"Invalid file name: {sts.filename} {repr(e)}"

st.set_page_config(
    page_title="Diagnostics",
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

st.header("Diagnostics",divider=True)

description = '''
You are here because something went wrong with the image. Sorry about that. Hopefully you can figure out what went 
wrong and get it back up and running. 
'''    
st.write(description)

col1, col2, col3, _ = st.columns(4)

with col1:
    st.subheader("Watsonx.data")
    toc = """
    * [Check Connection](#check-connection)
    * [Check watsonx.data](#check-watsonx-system)
    * [Restart Presto](#restart-presto)
    * [Restart watsonx.data](#restart-watsonx)
    """
    st.markdown(toc)

with col2:
    st.subheader("Credentials")

    toc = """
    * [Passwords](#passwords)
    * [Certificates](#certificates)
    * [Upload files](#upload-file)
    * [Download file](#download-file)
    """
    st.markdown(toc)

with col3:
    st.subheader("RAG Demo")

    toc = """
    * [Restart and Update the LLM Service](#restart-and-update-the-llm-service)
    * [Rebuild Database](#rebuild-database)
    * [Add Library](#add-library)
    * [Update Software](#update-software)
    * [Restart Application](#restart-application)
    """
    st.markdown(toc)

st.header("Watsonx.data Diagnostics",divider=False)

st.subheader("Check Connection",divider="blue")

with st.form("Connection", clear_on_submit=True):
    description = 'Press the Check Connection button to determine if a connection can be established with the watsonx.data system.'
    st.write(description)
    if st.form_submit_button("Check Connection", type="secondary"):
        with st.container(height=80,border=False):
            with st.spinner("Connecting to Presto"):
                sleep(0.5)
                connection = db.connectPresto()
                result = db.runSQL(connection,"select * from tpch.tiny.customer limit 1")
                if (connection == None or len(result) == 0):
                    error = \
                    """
                    Connection Error! We have a problem connecting to the Presto engine. Odds are that it is broken,
                    in a loop of some sort, or it hasn't completed startup. Try the next section to see if the services are 
                    running. If they are, trying connecting again after a minute.
                    """
                    st.error(error)    
                else:
                    message = \
                    """
                    Good news! The connection is working! In theory you should be able to use the system. If you 
                    can't get the RAG program to work, consider resetting the database using the button further down this web page.
                    """
                    st.success(message)

st.subheader("Check watsonx System",divider="blue")

with st.form("Presto", clear_on_submit=True):
    description = "If your connection failed (hint, see button above) then something may be wrong with the Presto engine or watsonx.data. You can check to see what services are up and running in our server by pressing the Check Services button. If you find that the Presto instance is missing, restart Presto. If more than one service is missing, you will need to restart the watsonx.data services."
    st.write(description)
    if st.form_submit_button("Check Services", type="secondary"):
        running = False
        services = pd.DataFrame()
        with st.spinner("Checking watsonx.data"):
            sleep(0.5)        
            watsonx = checkStatus()
            services = pd.DataFrame(watsonx.items(), columns=['Service','Status'])
            running = True
            for service in watsonx:
                if (watsonx[service] != "Running"):
                    running = False
                    break

        st.dataframe(services,use_container_width=True)

        if (running == False):
            st.error("Ouch! One or more of the watsonx.data services is not running! If it is the Presto service, trying restarting it using the section below. If it is more than one service, restart all of the watsonx.data services.")
        else:
            st.success("The watsonx.data system appears to working fine. If you still can't connect, you may want to restart the Presto service")                

st.subheader("Restart Presto",divider="blue")

with st.form("presto", clear_on_submit=True):
    description = "If the Presto engine is not responding, you will need to restart the engine. Clicking the button below will stop the Presto service and then restart it. If this does not fix the problem, you may need to restart the entire cluster."

    st.write(description)

    if st.form_submit_button("Restart Presto", type="secondary"):
        with st.container(height=80,border=False):

            with st.spinner("Stopping Presto"):
                sleep(0.5)
                command = f"sudo /root/ibm-lh-dev/bin/stop_service ibm-lh-presto"
                _ = runOS(command)

            with st.spinner("Starting Presto"):
                sleep(0.5)
                command = f"""sudo LH_RUN_MODE=diag /root/ibm-lh-dev/bin/start_service ibm-lh-presto"""
                _ = runOS(command)

            with st.spinner("Waiting for Presto to initialize (Patience!)"):
                sleep(0.5)
                running = False
                check_count = 0
                progressBar = st.progress(0,"Initializing")
                while running == False:
                    results = runOS('sudo /root/ibm-lh-dev/bin/presto-run <<< "show catalogs;"',logit=False)
                    for result in results:
                        if (result.find("FINISHED") != -1):
                            running = True
                            break
                    check_count += 1
                    progressBar.progress(check_count, "Initializing")
                    if (check_count >= 100):
                        break
                progressBar.empty()
    
            if (check_count >= 100):
                st.error("We could not get the watsonx.data services up and running. The Presto service appears to be stuck starting up. Try connecting to Presto to see if it wakes up after a period of time. The log files may provide some more details on what went wrong.")
            else:
                st.success("Presto is now up and running. Try using the system or the demo now.")               

st.subheader("Restart watsonx",divider="blue")

with st.form("watsonx.data", clear_on_submit=True):
    description = "If all hope is lost, you can try stop and restarting all of the services in the system. This process will take several minutes to complete, but hopefully this will resolve any of the issues you may be having."
    st.write(description)

    if st.form_submit_button("Restart watsonx.data", type="secondary"):

        with st.container(height=80,border=False):
            with st.spinner("Stopping Milvus"):
                sleep(0.5)
                command = "sudo /root/ibm-lh-dev/bin/stop-milvus"
                _ = runOS(command)
                # We do it twice because there is a bug in the way the stop service command works.
                command = "sudo /root/ibm-lh-dev/bin/stop-milvus"
                _ = runOS(command)

            with st.spinner("Stopping watsonx.data"):
                sleep(0.5)
                command = "sudo /root/ibm-lh-dev/bin/stop"
                _ = runOS(command)

            with st.spinner("Starting watsonx.data (5 minutes)"):
                sleep(0.5)
                command = "sudo LH_RUN_MODE=diag /root/ibm-lh-dev/bin/start"
                _ = runOS(command)

            with st.spinner("Starting Milvus"):
                sleep(0.5)
                command = "sudo LH_RUN_MODE=diag /root/ibm-lh-dev/bin/start-milvus"
                _ = runOS(command)            

            check_count = 0
            with st.spinner("Waiting for Presto to initialize (Patience!)"):
                sleep(0.5)
                running = False
                progressBar = st.progress(0,"Initializing")
                while running == False:
                    results = runOS('sudo /root/ibm-lh-dev/bin/presto-run <<< "show catalogs;"',logit=False)
                    for result in results:
                        if (result.find("FINISHED") != -1):
                            running = True
                            break
                    check_count += 1
                    progressBar.progress(check_count, "Initializing")
                    if (check_count >= 100):
                        break
                progressBar.empty()

            if (check_count >= 100):
                st.error("We could not get the watsonx.data services up and running. The Presto service appears to be stuck starting up. Try connecting to Presto to see if it wakes up after a period of time. Otherwise, try to restart the Presto service. The log files may provide some more details on what went wrong.")
            else:
                st.success("The watsonx.data system appears to be up and running. Try using the system now.")

st.header("Credentials and Utilities",divider=False)

# Passwords

st.subheader("Passwords",divider="blue")

with st.container(border=True):
    description = '''
    The following table contains the userids and passwords used in the system. 
    ''' 
    st.write(description)

    with open("/certs/passwords") as fd:
        credentials = fd.readlines()
        userids = []
        count = 0
        for user in credentials:
            idinfo = user.split()
            entry = [f"{idinfo[0]}",idinfo[1],idinfo[2]]
            if (count in [0,1]):
                if (count == 0):
                    header = entry
                count = count + 1
                continue
            userids.append(entry)
        th_props = [
            ('font-size', '16px'),
            ('text-align', 'left'),
            ('font-weight', 'normal'),
            ('color', 'black'),
            ('background-color', '#f7ffff')
            ]

        td_props = [
            ('font-family', 'monospace,monospace'),
            ('font-size', '14px')
            ]
                        
        styles = [
            dict(selector="th", props=th_props),
            dict(selector="td", props=td_props)
                ]

        df = pd.DataFrame(userids,columns=header).style.set_table_styles(styles)
        st.table(df)  # ,hide_index=True)

# Certificates


st.subheader("Certificates",divider="blue")

with st.container(border=True):
    description = '''
    The following section includes certificates that you need to connect to the watsonx.data and presto engines. Use the buttons to download the files. 
    ''' 
    st.write(description)

    st.markdown("##### Certificate file")

    filename = "lh-ssl-ts.crt"
    with open(f"/certs/{filename}", "rb") as file:
        btn = st.download_button(
            label=f"Download {filename}",
            data=file,
            file_name=filename,
            )

    st.markdown("##### Java Keystore file")
    filename = "lh-ssl-ts.jks"
    with open(f"/certs/{filename}", "rb") as file:
        btn = st.download_button(
            label=f"Download {filename}",
            data=file,
            file_name=filename,
            )

    st.markdown(
    """
    ##### Presto Java Certificate

    The password for the Presto certificate is <span style="color: blue; font: mono;">watsonx.data</span>. When attempting to connect to the database externally, you must use the TechZone server name as the host and use the port that was assigned to the Presto service. 
    """
    ,unsafe_allow_html=True)

    filename = "presto-key.jks"
    with open(f"/certs/{filename}", "rb") as file:
        btn = st.download_button(
            label=f"Download {filename}",
            data=file,
            file_name=filename,
            )
        
    st.markdown(
    """
    ##### Generate Certificate

    If you need the certificate as a text string, click on the button below and it will generate the certificate text.
    """
    )

    showcert = st.button("Generate certificate")
    if showcert:
        command = "echo QUIT | openssl s_client -showcerts -connect watsonxdata:8443 | awk '/-----BEGIN CERTIFICATE-----/ {p=1}; p; /-----END CERTIFICATE-----/ {p=0}' > ./certs/presto.crt"
        results = runOS(command)
        try:
            fd = open("/certs/presto.crt","r")
            output = '<div style="line-height: 14px;"><span style="font-family: monospace, monospace; font-size: 12px;">'
            for input in fd:
                output = f"{output}<br>{input}"
            fd.close()
            output = f"{output}</span></div>"
            st.html(output)
        except Exception as e:
            st.error(f"Unable to generate the certificate file: {repr(e)}")

# Upload new document List

st.subheader("Upload File",divider="blue")

with st.form("Upload", clear_on_submit=False):
    description = '''
To upload one file into the system, either drag or drop the document into the control below or press the Browse Files button. The file is placed into the /tmp directory.
''' 
    st.write(description)
    col1, col2 = st.columns([0.15,0.85])
    with col1:
        submitted = st.form_submit_button("Upload Files")
    with col2:
        files = st.file_uploader("Select a file to upload",label_visibility="collapsed",accept_multiple_files=True)
    
    if submitted and len(files) > 0:
        for file in files:
            with st.spinner(f"Uploading file {file.name}"):
                sleep(0.5)
                import os
                filename = os.path.basename(file.name)             
                with open(f"/tmp/{filename}","wb") as fd:
                    fd.write(file.getvalue())
                
                okay = True
                if (okay is not None):
                    st.success("Document uploaded")
                else:
                    st.error("Document upload failed. See log file for details.")
                         
    elif submitted: 
        st.error("You need to supply a document for me to upload!")
    else:
        pass

# Download a document

st.subheader("Download File",divider="blue")

with st.container(border=True):
    description = '''To download a file from the system, enter the filename below and then press the validate button to check that the file exits. If the file does exist, a download button will appear.''' 
    st.write(description)

    if ("validfile" not in sts):
        sts["validfile"] = False

    if ("filename" not in sts):
        sts["filename"] = ""

    if ("file_error" not in sts):
        sts["file_error"] = None

    getDownload()

st.header("RAG Demonstration Settings",divider=False)

st.subheader("Restart and Update the LLM Service", divider="blue")

with st.form("ollama", clear_on_submit=True):
    description = "If the LLM is not being responsive, you may have to restart the service. Clicking the button below will stop the LLM service, refresh the image, and then restart it."

    st.write(description)

    if st.form_submit_button("Restart LLM Service", type="secondary"):

        results = None
        with st.container(height=60,border=False):
            with st.spinner("Stopping LLM Service"):
                sleep(0.5)
                command = "sudo docker stop ollama"
                _ = runOS(command)

            with st.spinner("Removing LLM container"):
                sleep(0.5)
                command = "sudo docker rm ollama"
                _ = runOS(command)

            with st.spinner("Removing LLM images"):
                command = """sudo docker images -a | grep "ollama" | awk '{print $1":"$2}' | xargs sudo docker rmi"""
                _ = runOS(command)

            with st.spinner("Restarting LLM Service (This will take a few minutes)"):
                sleep(0.5)
                command = "sudo docker run -d --restart always -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:latest"
                _ = runOS(command)

            with st.spinner("Checking status"):
                sleep(0.5)
                command = 'sudo docker ps --filter "name=ollama" --filter "status=running"'
                results = runOS(command)
                if (len(results) > 1):
                    st.success("LLM service started")
                else:
                    st.error("The LLM service does not appear to be running. Check the log file for details.")
  
st.subheader("Rebuild Database", divider="blue")

with st.container(border=True):

    description = """
    Your database is messed up or corrupted and you've decided to rebuild the database? This will completely remove all of the hard work you put into uploading documents so be prepared to do all of that work over again! Press the Rebuild Database button to destroy the existing database and create a new one. Included below are links to the IBM 2023 Earnings report and the CSV Complaint file that are used for the examples.
    
    Note: The Consumer complaints file needs to be uploaded into watsonx.data separately. See the documentation for more details on what steps are required to do this.
    """
    st.write(description)

    filename = "/home/watsonx/rag/samples/IBM_Annual_Report_2023.txt"
    with open(f"{filename}", "rb") as file:
        btn = st.download_button(
            label=f"Download IBM Annual Report 2023",
            data=file,
            file_name="IBM_Annual_Report_2023.txt",
            )    

    filename = "/home/watsonx/rag/samples/complaints-2025.csv"
    with open(f"{filename}", "rb") as file:
        btn = st.download_button(
            label=f"Download 2025 Consumer Complaints",
            data=file,
            file_name="complaints-2025.csv",
            ) 

    rebuild = st.button("Rebuild Database", type="secondary")

    if rebuild:
        connection = db.connectPresto()
        if (connection == None):
            error = \
            """
            Connection Error! Did you check the connection earlier? You missed a step! Get the watsonx.data system up and running before attempting to recreate the database. Otherwise I will print exactly the same error message over and over again...
            """
            st.error(error)    
        else:
            with st.container(height=60,border=False):
                while True:
                    with st.spinner("Recreating Database"):
                        sleep(0.5)
                        if (db.rebuildDatabase(connection) == False):
                            error = "On no! We can't create the database for some reason! Review the log files to determine what the reason may be. No idea how to fix it at this moment, but perhaps the log file will provide us with a clue."
                            st.error(error)
                            break

                    with st.spinner("Removing collections"):
                        sleep(0.5)               
                        if (dropCollections() == False):
                            db.log("Rebuild","[1] Unable to clear Milvus collections")
                            st.error("Unable to clear Milvus collections. See the log for details.")
                            break

                    with st.spinner("Storing default document"):
                        sleep(0.5)                 
                        filename = "/home/watsonx/rag/samples/IBM_Annual_Report_2023.txt"
                        rawdata = db.getRAWFile(filename)
                        if (rawdata is None):
                            st.error(f"Could not find the default file {filename}")
                            break

                        okay = db.storeDocument(connection, 
                                                filename="IBM_Annual_Report_2023", 
                                                filetype="txt", 
                                                data=rawdata,
                                                scan=False, 
                                                language="en"
                                            )
                        if (okay is None):
                            db.log("Rebuild","[2] Unable to store the default document. See the log for details.")
                            st.error("Could not initialize the database. See the log for details.")
                            break

                    with st.spinner("Creating document vectors"):
                        sleep(0.5)                    
                        collection_name = "IBM 2023 Annual Report"
                        collection_name = collection_name.replace(" ","_")
                        ids = [1]
                        collection = storeVectors(connection,collection_name,ids,"Small")
                        if (collection in [None,""]):
                            db.log("Rebuild","[3] Unable to vectorize the default document. See the log for details.")
                            st.error("Error in vectorizing the document. Check the log for details.")
                            break
                        db.log("Rebuild",f"File {filename} uploaded.")
                        st.success("Success! You have recreated the database so you can try running the demo again.")
                    break

        #progressBar.empty()

st.subheader("Add Library", divider="blue")

with st.form("Library", clear_on_submit=False):
    description = "If you encounter an error while vectorizing a database, it may be due to the conversion library was missing. If this is the case, enter the name of the Python library needed below. The program will attempt to install the libraries and you can try the vectorization step again."
    st.write(description)
    pip = st.text_input("Enter library name or pip options")
    if st.form_submit_button("Install Libraries", type="secondary"):
        if (pip in [None,""]):
            st.error("You need to supply the library name in order for me to install it!")
        else:
            with st.container(height=60,border=False):
                with st.spinner("Loading library"):
                    sleep(0.5)  
                    command = f"sudo python3 -m pip install {pip}"
                    _ = runOS(command)
                st.success("Command completed. Check the log for more details.")

st.subheader("Update Software",divider="blue")

with st.form("Software Update", clear_on_submit=True):

    description = "In the remote chance that there is a problem with the software itself, you can download the latest copy by pressing the refresh button. The documents and LLMs that you have loaded will not be affected by this refresh command. The webpage you are currently using to access the program will become unresponsive for a period of time while the code is downloaded and restarted. The version number found below will be updated to the latest release number in the event you need to report an issue with the code."
    st.write(description)

    st.success(f"Current software version: {sts.version}")
    if st.form_submit_button("Update software", type="secondary"):
        sts['reset'] = False
        with st.container(height=60,border=False):
            with st.spinner("Updating software"):
                sleep(0.5)  
                command = f"sudo /usr/local/bin/refresh-rag"
                _ = runOS(command)
                del sts.initialized                
                sleep(5)
                st.switch_page("Watsonx_Milvus_Demo.py")

st.subheader("Restart Application",divider="blue")

with st.form("Application Restart", clear_on_submit=True):

    description = "If you find that you are unable to upload documents (403 code), you may need to restart the application. This will stop the program and restart it. The application will stop responding for a few minutes while the service restarts. If you receive an error code on the screen, continue to refresh the browser until the log in window displays."
    st.write(description)

    if st.form_submit_button("Restart Application", type="secondary"):
        with st.container(height=60,border=False):
            with st.spinner("Restarting application (3-5 minutes)"):
                sleep(0.5)  
                command = f"sudo systemctl restart rag"
                _ = runOS(command)
                sleep(5)
                st.switch_page("Watsonx_Milvus_Demo.py")