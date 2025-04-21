#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# Import Documents Panel
#

import streamlit as st
from streamlit import session_state as sts
import wxd_data as db
import pandas as pd 
import wikipedia
from wxd_utilities import setCredentials, log, check_password, getLanguageCode
from llama_index.readers.web import SimpleWebPageReader
from wxd_wiki import getArticles
from time import sleep

def wiki_selection():
    """
    Wiki_selection is called by the edit Dataframe control to save the users selection. If you 
    don't save the selection, the values are lost when the screen refreshes itself.
    """
    
    if ("_wikidocs" not in sts):
        if ("wikiSelection" in sts):
            del sts.wikiSelection
    else:
        sts["wikiSelection"] = sts._wikidocs

def getScan():
    """
    Is this a scanned document? True for TIFF, JPG and PNG, and possibly for PDFs.
    """
    sts["scan"] = sts._scan

def getLanguage():
    """
    What language is found in the PDF or image (only scanned documents).
    """
    sts["language"] = sts._language

def getTopic():
    """
    What topic did the user request when searching Wikipedia?
    """
    sts["topic"] = sts._topic

def getFilename():
    """
    If the file is a scanned PDF, or an image (TIFF, PNG, JPG), we need to know that it was 
    scanned and what language was used in the image.
    """
    import os 

    sts["language"] = "English"
    if (sts._filedescriptor in [None,""]):
        sts["filename"] = None
        sts["filehandle"] = None
        sts["filetype"] = None
        sts["scan"] = False
    else:
        file = sts._filedescriptor.name
        filename = os.path.basename(file)
        name, type = os.path.splitext(filename)
        filetype = type.replace(".","").lower()
        sts["filehandle"] = sts._filedescriptor
        sts["filename"] = name
        sts["filetype"] = filetype
        if (filetype in ["jpg","tiff","png","jpeg"]):
            sts["scan"] = True
        else:
            sts["scan"] = False

@st.fragment
def list_documents():
    """
    Dialog to display the current documents in the system.
    """
                    
    st.subheader("Document list",divider="blue")
    description = '''
    The current documents that are stored in watsonx.data are listed below. To delete an article, select it from the list and press the Delete key. Press the Refresh button to update the document list after adding new documents from the options below.
    '''    

    st.write(description)

    with st.container(border=True):

        selectDocuments()
                    
        columns = st.columns([6,7,87])
        with columns[0]:
            delete_button = st.button("Delete")  
        with columns[1]:
            refresh_button = st.button("Refresh")               

        if delete_button:
            while True:
                if ("docs_selected" not in sts):
                    st.error("You need to select at least one document to delete.")
                    break

                rows = False
                edited_rows = sts.docs_selected['edited_rows']
                for row_no in edited_rows:
                    if edited_rows[row_no]["Selected"]:
                        rows = True
                        break     
                
                if (rows == False):
                    st.error("You need to select at least one document to delete.") 
                    break
                    
                ids = []
                with st.spinner("Deleting documents"):
                    edited_rows = sts.docs_selected['edited_rows']
                    for row_no in edited_rows:
                        if edited_rows[row_no]["Selected"]:
                            df = sts.doc_details
                            id = df.loc[row_no,'id']
                            log(program,f"[1] Deleting id={id}")
                            sql = f"delete from iceberg_data.documents.metadata where id = {id}"
                            ok = db.runDML(connection,sql)
                            sql = f"delete from iceberg_data.documents.rawdata  where id = {id}"
                            ok = db.runDML(connection,sql)                    

                st.rerun()
                break    

        elif refresh_button:
            st.rerun()
        else:
            pass

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

@st.fragment
def selectDocuments():
    """
    Select which documents you want to delete.
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

@st.fragment
def upload_document():
    """
    Dialog for uploading a file into the system.
    """    

    if ("scan" not in sts):
        sts.scan = False
    
    if ("language" not in sts):
        sts.language = "English"

    st.subheader("Upload Document",divider="blue")
    description = '''
    To upload a new document into the database, either drag or drop the document onto the control below or press the Browse Files button. Documents that already exist in the database will be replaced.

    ##### PDF Scans
    If you are uploading a PDF, you must specify if it is a regular document or a scanned image. If the PDF was generated from an application like Word, it can be vectorized without any modification (Document). PDFs that are scanned images (e.g., fax or photocopy), will require additional information on the language that was used in the text (Scan). 

    ##### Document Language
    For scanned images (PDF scans, JPG, PNG, TIFF), you must specify the primary language that it was written in. The default is English (and is always used in addition to the language you select). This will ensure that the application will be able to properly parse the text found in the image.
    ''' 
    st.write(description)

    with st.container(border=True):
        submitted = False
        st.file_uploader("Select a file to upload",label_visibility="visible",on_change=getFilename,key="_filedescriptor")  
        col1, col2 = st.columns([0.50,0.50])
        with col1:
            fileSettings = f"Scanned image: :green[{sts.scan}] Language: :green[{sts.language}]"
            with st.expander(fileSettings):

                st.write(
                    """
                    All images (JPG, PNG, TIFF) should be marked as a scanned document. If the PDF being upload was generated by scanning software (e.g., fax, scanner), then you must mark it as as a scanned document. 
                    """)
                st.checkbox("Scanned document",value=sts.scan,key="_scan",on_change=getScan)
                
                st.write(
                    """
                    For all scanned images, the primary language of the document must be provided in order to properly parse the contents of the image. Select which language the image or PDF was written in.
                    """)
                st.selectbox("PDF/Image Language",sts.languages,key="_language",index=getLanguageCode(sts.language),on_change=getLanguage,label_visibility="collapsed")

        submitted = st.button("Upload File",) # st.form_submit_button("Upload Doc/URL")        

        if submitted:
            if sts.filename not in [None,""]:
                with st.spinner(f"Loading document {sts.filename}"):
                    sleep(0.5)
                    data = sts.filehandle.getvalue()
                    languageCode = getLanguageCode(sts.language,indexValue=False)
                    chunks = db.storeDocument(connection,
                                            filename=sts.filename,
                                            filetype=sts.filetype,
                                            data=data,
                                            scan=sts.scan,
                                            language=languageCode
                    )
                    if (chunks is not None):
                        st.success("Document uploaded")
                        db.log(program,f"File {sts.filename} uploaded.")  
                    else:
                        st.error("Document upload failed. See log file for details.")
            else:
                st.error("No file supplied for uploading.")

@st.fragment
def upload_url():
    """
    Dialog to ask if the user wants to upload a URL into the system
    """
    st.subheader("Upload URL",divider="blue")
    description = '''
    To upload then contents of a URL, enter the URL in the text field below. Note that only the main page of the URL will be retrieved.
    ''' 
    st.write(description)

    with st.container(border=True):
        submitted = False
        url = st.text_input("Enter a URL")
        submitted = st.button("Upload URL",)

        if submitted: 
            if url not in [None,""]:                
                if ('HTTP' not in url.upper()):
                    url = f"https://{url}"
                with st.spinner(f"Loading URL {url}"):
                    rawdata = ""
                    try:
                        documents = SimpleWebPageReader(html_to_text=True).load_data([url])                  
                        for doc in documents: # iterate the document pages
                            if (rawdata == None):
                                rawdata = doc.text
                            else:
                                rawdata += doc.text

                        if (rawdata == ""):
                            st.error(f"The URL {url} was invalid or could not be reached.")
                        else:
                            rawdata = rawdata.encode(encoding='utf-8') 
                            chunks = db.storeDocument(connection,
                                                    filename=url,
                                                    filetype="html",
                                                    data=rawdata,
                                                    scan=False,
                                                    language="en")         

                            if (chunks in [None,""]):
                                st.error(f"The URL {url} contains no valid data. See the log for more details.")
                            else:
                                st.success("URL Loaded")
                                db.log(program,f"URL {url} uploaded.")

                    except Exception as e:
                        st.error(f"Error parsing the URL {url}. {repr(e)}")

            else: 
                st.error("You need to supply a URL to upload!")


@st.fragment
def upload_wiki():
    """
    Dialog for user to enter a wikipedia article search and then select which documents to upload into the system.
    """

    st.subheader("Upload Wikipedia Articles",divider="blue")
    description = '''
    When you provide a Topic below, the program will query Wikipedia to find articles that best match your topic. You can then select which articles to upload into the system.
    ''' 
    st.write(description)

    with st.container(border=True):

        topic = st.text_input("Enter a topic",label_visibility="collapsed",placeholder="Enter a topic",key="_topic",on_change=getTopic)
        submitted_search = st.button("Get Articles",on_click=wiki_selection)    

    df = pd.DataFrame()

    if submitted_search:
        display_articles = []
        topic = sts.topic
        if topic.strip() not in ["",None]:
            topic = topic.strip()
            with st.spinner("Searching for documents"):
                sts['topic'] = topic
                search_results = wikipedia.search(topic)
                display_articles = []
                for i in range (0,len(search_results)):
                    try:
                        summary = wikipedia.summary(search_results[i])
                        display_articles.append([False,search_results[i],summary])
                    except Exception as err:
                        continue

                sts['articles'] = display_articles
                if (len(display_articles) == 0):
                    st.error("No articles were found.")
                else:
                    df = pd.DataFrame(display_articles,columns=['Selected','Title','Summary'])
                    showWikiArticles(df)

@st.fragment
def showWikiArticles(df):
    """
    This portion of code displays a dataframe that a user will select Wiki articles from.
    The reason that this has the special fragment directive is to allow this code to
    be independent from the other controls on the screen. If we don't separate this
    code from the rest of the screen, selecting on articles will fire off the
    wiki_selection code above with just one item! You want the user to select 
    multiple documents to upload and this syntax will allow the code to wait until 
    all of the articles have been selected. 
    """

    wikilist = st.data_editor(df,
        column_config={
        "selected" : st.column_config.Column(st.column_config.CheckboxColumn("Selected"),width="small"),
        "topic"    : st.column_config.Column("Topic",width="small",disabled=True),
        "summary " : st.column_config.Column("Summary",width="large",disabled=True),
        },
        on_change=wiki_selection,
        key="_wikidocs",
        hide_index=True,
        use_container_width=True
    )    

    submitted_load = st.button("Upload")

    if submitted_load: 
        with st.spinner("Retrieving articles"):
            msg = None
            edited_rows = sts.wikiSelection['edited_rows']
            wiki_titles, wiki_text = getArticles(sts.articles,edited_rows)
            if (wiki_text is None):
                st.error("No articles found.")
            else:
                tempfile = "/tmp/wiki.txt"
                open(tempfile,"w").write(wiki_text)
                connection = db.connectPresto()
                if (connection == None):
                    db.badConnection()
                    st.stop()

                data = db.getRAWFile(tempfile)
                chunks = db.storeDocument(connection,
                                        filename=wiki_titles,
                                        filetype="wiki",
                                        data=data,
                                        scan=False,
                                        language="en")

                if (chunks is not None):
                    st.success("Upload completed")
                    db.log(program,f"Wikipedia text updated. Topic: {sts.topic}")                    
                else:
                    st.error("Wiki upload failed. See log file for details.")    

# Upload watsonx.data table code

def getCatalog():
    """
    Get the catalog we want to look at.
    """
    if (sts._catalog != sts.catalog):
        sts["catalog"] = sts._catalog
        sts.schemas = pd.DataFrame()
        sts.tables = pd.DataFrame()
        sts.schema = None
        sts.table = None
        sts.analyze = False

def getSchema():
    """
    What schema did you request?
    """
    if (sts._schema != sts.schema):
        sts["schema"] = sts._schema
        sts.tables = pd.DataFrame()
        sts.table = None
        sts.analyze = False

def getTable():
    """
    What table did you request?
    """
    if (sts.catalog != None and sts.schema != None):
        sts["table"] = sts._table     
        sts.analyze = True   

def catalogIndex(catalog,catalogs):
    """
    Return the catalog location
    """
    position = None
    if catalog != None and catalogs.empty == False:
        for index, row in catalogs.iterrows():
            if row['Catalog'][0] == catalog:
                position = index
                break
    return position

def schemaIndex(schema,schemas):
    """
    Return the schema location
    """
    position = None
    if schema != None and schemas.empty == False:
        for index, row in schemas.iterrows():
            if row['Schema'][0] == schema:
                position = index
                break
    return position    

def tableIndex(table,tables):
    """
    Return the table location
    """
    position = None
    if table != None and tables.empty == False:
        for index, row in tables.iterrows():
            if row['Table'][0] == table:
                position = index
                break
    return position        

def setAnalyze():
    """
    Check to see if we can analyse the data or not.
    """

    if sts.catalog == None or sts.schema == None or sts.table == None:
        st.error("You must select a table before running the Analyze step.")
        sts.analyze = False
    else:
        sts.analyze = True

@st.fragment
def showTables(connection):
    """
    Show a dialog to select the table that you want to review.
    """

    description = """
    ##### Table Selection
    Select the table you want to analyze by selecting the catalog, schema and table names below. Press the Analyze button to retrieve details of the table.
    """

    st.markdown(description)

    textColumns = st.columns([10,18,18,18,18,18])

    with textColumns[1]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Catalogs</span>
        """,unsafe_allow_html=True)

    with textColumns[2]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Schemas</span>
        """,unsafe_allow_html=True)

    with textColumns[3]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Tables</span>
        """,unsafe_allow_html=True)

    columns = st.columns([10,18,18,18,18,18])

    if sts.catalogs.empty == True:
        sql = "show catalogs"
        sts.catalogs = db.runSQL(connection,sql)
        sts.schemas = pd.DataFrame()
        sts.tables = pd.DataFrame()
        sts.catalog = None
        sts.schema = None
        sts.table = None
        sts.analyze = False

    with columns[0]:
        doAnalysis = st.button("Analyze")            

    with columns[1]:
        _ = st.selectbox("Catalog",sts.catalogs,index=catalogIndex(sts.catalog,sts.catalogs),key="_catalog",on_change=getCatalog,placeholder="Select a catalog",label_visibility="collapsed")

    with columns[2]:
        if sts.catalog != None:
            if sts.schema == None:
                sql = f"show schemas in {sts.catalog}"
                sts.schemas = db.runSQL(connection,sql)
                sts.schema = None
            _ = st.selectbox("Schemas",sts.schemas,index=schemaIndex(sts.schema,sts.schemas),key="_schema",on_change=getSchema,placeholder="Select a schema",label_visibility="collapsed")
    
    with columns[3]:
        if sts.catalog != None and sts.schema != None:
            if (sts.table == None):
                sql = f'show tables from "{sts.catalog}"."{sts.schema}"'
                sts.tables = db.runSQL(connection,sql)
                sts.table = None
            _ = st.selectbox("Tables",sts.tables,index=tableIndex(sts.table,sts.tables),key="_table",on_change=getTable,placeholder="Select a table",label_visibility="collapsed")  

    if doAnalysis:
        if sts.catalog == None or sts.schema == None or sts.table == None:
            st.error("You must select catalog/schema/table before running the Analyze step.")
        else:
            results = showStats(connection) 
            if (results == False):
                st.error("Unable to find columns with less than 100 distinct values to filter the results")
            else:
                results = filterColumns(connection)               


@st.fragment
def showStats(connection):
    """
    Generate the statistics for the table that was selected.
    """

    with st.spinner("Analyzing table"):
        sql = f'show columns from "{sts.catalog}"."{sts.schema}"."{sts.table}"'
        column_info = db.runSQL(connection,sql)
        sql = None
        sts.column_names = []
        sts.column_unique = []
        sts.column_types = []
        sts.column_values = []

        for index, row in column_info.iterrows():
            sts.column_names.append(row['Column'])
            datatype = row['Type']
            if datatype in ['varchar','char','json','varbinary','date','time','timestamp']:
                sts.column_types.append('string')
            else:
                sts.column_types.append('number')

            sqlcolumn = f'''count(distinct "{row['Column']}") as "{row['Column']}" '''
            if (sql == None):
                sql = f'select {sqlcolumn}'
            else:
                sql = f'{sql}, {sqlcolumn}'


        sql = f'{sql} from "{sts.catalog}"."{sts.schema}"."{sts.table}" limit 10000'
        column_stats = db.runSQL(connection,sql)

        for column_name in sts.column_names:
            sts.column_unique.append(column_stats[column_name][0])

        col_values = pd.DataFrame({'column': sts.column_names, 'datatype': sts.column_types, 'count': sts.column_unique}).sort_values('count')

        colno = 0
        sts.selected_columns = []
        sts.selected_values = []
        sts.selected_filters = []
        sts.selected_types = []
        for index, row in col_values.iterrows():
            if (row['count'] <= 100):
                sql = f'''select distinct({row['column']}) from "{sts.catalog}"."{sts.schema}"."{sts.table}"'''
                column_values = db.runSQL(connection,sql)
                sts.selected_columns.append(row['column'])
                sts.selected_values.append(column_values)
                sts.selected_types.append(row['datatype'])
                sts.selected_filters.append(None)
                colno = colno + 1
                if (colno == 5):
                    break            

        if colno == 0:
            return False
        else:
            return True
        

def selectFilter(idx):
    """
    Save the value that the user wants to filter the data on
    """
    sts.selected_filter[idx] = sts._filter

@st.fragment
def filterColumns(connection):
    """
    Display the columns that were found in the table and the 
    values that are associated with it.
    """

    description = """
    ##### Filter Rows
    The following columns were found in the table that contained less than 100 unique values. The columns are ordered by the number of unique values (cardinality) found in the column. Select one or more values from each of these columns to filter the results extracted from the table. These filtered values will be used to create a document that can be placed into a collection for further analysis. Note that only the first 50 rows are returned to reduce processing time.
    """

    st.markdown(description)

    textcols = st.columns([10,18,18,18,18,18])

    if len(sts.selected_columns) > 0:
        for idx in range(0,len(sts.selected_columns)):    
            with textcols[idx+1]:
                header = f"<style>[data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{{gap:0rem ;}}</style><span style='font-size: 14px'>{sts.selected_columns[idx]}</span>"
                st.markdown(header,unsafe_allow_html=True)

    columns = st.columns([10,18,18,18,18,18]) 

    colno = 1

    with columns[0]:
        doFilter = st.button("Filter") 

    if len(sts.selected_columns) > 0:
        for idx in range(0,len(sts.selected_columns)):
            with columns[idx+1]:
                filter = st.selectbox(sts.selected_columns[idx],sts.selected_values[idx],index=None,label_visibility="collapsed")
                sts.selected_filters[idx] = filter

    if doFilter:
        where = ""
        sql = f'select * from "{sts.catalog}"."{sts.schema}"."{sts.table}"'
        for i in range(0,len(sts.selected_columns)):
            if sts.selected_filters[i] != None:
                if (sts.selected_types[i] == "string"):
                    compare = f'''"{sts.selected_columns[i]}" = '{sts.selected_filters[i]}' '''
                else:
                    compare = f'''"{sts.selected_columns[i]}" = {sts.selected_filters[i]} '''

                if where == "":
                    where = f"where {compare}"
                else:
                    where = f"{where} and {compare}"

        sql = f"{sql} {where} limit 50"
        sts.where_clause = where

        filtered_rows = db.runSQL(connection,sql)

        if (len(filtered_rows) == 0):
            st.error("No rows could be found with those filter values. Adjust the settings and try again.")
        else:
            description = """
            ##### Results
            """
            st.markdown(description)             
            st.dataframe(filtered_rows)  
            extractText(connection)  

@st.fragment
def extractText(connection):
    """
    Extract the text from the table.
    """     

    description = """
    ##### Document Creation
    Enter a name for this document (the default is the table name). Then select which column should be used to generate the document, along with the number of rows to use. Note that LLM processing time will increase significantly as you increase the number of sentences in the document.
    """
    st.markdown(description)    

    textColumns = st.columns([10,18,18,18,18,18])

    with textColumns[1]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Document Name</span>
        """,unsafe_allow_html=True)    
    
    with textColumns[2]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Text Column</span>
        """,unsafe_allow_html=True)

    with textColumns[3]:
        st.markdown("""
        <style>
        [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
            gap:0rem ;
        }
        </style><span style="font-size: 14px">Row Limit</span>
        """,unsafe_allow_html=True)

    columns = st.columns([10,18,18,18,18,18])

    with columns[0]:
        doFilter = st.button("Upload")          

    with columns[1]:
        sts.filename = st.text_input("Document Name",f'{sts.catalog}.{sts.schema}.{sts.table}',label_visibility="collapsed")          

    with columns[2]:
        textcolumn = st.selectbox("Text Column",sts.column_names,index=None,label_visibility="collapsed")

    with columns[3]:
        rowlimit   = st.selectbox("Row Limit",[10,20,30,40,50],index=0,label_visibility="collapsed")    

    if doFilter:
        if sts.filename in [None, ""]:
            st.error("Invalid document name provided")
        else:
            sts.filetype = "txt"
            sql = f'select "{textcolumn}" from "{sts.catalog}"."{sts.schema}"."{sts.table}" {sts.where_clause} limit {rowlimit}'        
            filtered = db.runSQL(connection,sql)
            if len(filtered) == 0:
                st.error("No rows were found matching the filters selected.")
            else:
                wxd_text = ""
                for index, row in filtered.iterrows():
                    if wxd_text == "":
                        wxd_text = row[textcolumn]
                    else:
                        wxd_text = f"{wxd_text}\n{row[textcolumn]}"

                tempfile = "/tmp/watsonx.txt"
                open(tempfile,"w").write(wxd_text)
                data = db.getRAWFile(tempfile)

                with st.spinner(f"Loading document {sts.filename}"):
                    sleep(0.5)
                    chunks = db.storeDocument(connection,
                                            filename=sts.filename,
                                            filetype="txt",
                                            data=data,
                                            scan=False,
                                            language="en"
                    )
                    if (chunks is not None):
                        st.success("Document uploaded")
                        db.log(program,f"File {sts.filename} uploaded.")  
                    else:
                        st.error("Document upload failed. See log file for details.")        


@st.fragment
def upload_watsonx(connection):
    """
    Dialog for user to select a table from watsonx.data and create a document from the results to use in an LLM query.
    """

    st.subheader("Upload watsonx.data Table",divider="blue")
    description = '''
    Select data from a table in watsonx.data to create a new document. This document can then be included in a collection for RAG generation or as direct input to the LLM.
    ''' 
    st.write(description)

    with st.container(border=True):
        showTables(connection)



st.set_page_config(
    page_title="Documents",
    page_icon=":infinity:",
    layout="wide"    
)

if not check_password():
    st.stop()

program = "Documents"

if ('initialized' not in sts):
    if (setCredentials() == False):
        st.error("Unable to get credentials required to connect to watsonx.data.")
        log("Startup","[1] Unable to get credentials required to connect to watsonx.data.")
        st.stop()
    
connection = db.connectPresto()
if (connection == None):
    db.badConnection()
    st.stop()

st.header("Watsonx.data - Document Storage",divider=True)

introduction = \
'''
This system requires that you upload documents or URLs to be used for RAG generation. There is one documents provided in the system that you can use for your queries. You have the option of uploading documents from your workstation (PDF, PPT, DOC, TXT, TIFF, JPG, PNG) and having it catalogued in watsonx.data. You can also point to a website (URL) which will be analyzed and the contents extracted and stored in watsonx.data. Finally, you can query Wikipedia and retrieve documents based on a topic.
'''
st.write(introduction)

with st.container(border=False,height=40):
    cols = st.columns(2)
    with cols[0]:
        with st.popover("Technical Details",use_container_width=True):
            details = \
    """
    ###### Press Escape to Close this Window
         
    ##### Document Storage
    This screen is used to stored documents into watsonx.data. There are two Iceberg tables within watsonx.data that store
    details of the documents. The first table contains document metadata:
    ```sql
    CREATE TABLE iceberg_data.documents.metadata
        (
        "id"          int,
        "document"    varchar,
        "type"        varchar,
        "scan"        boolean,
        "language"    varchar
        )
    ```
    The METADATA table tracks the document name (or URL) along with the type of document. The type of document will determine
    what routine will be used to extract the text from the contents. The scan field is required to differentiate scanned PDF documents (e.g., using a scanner, or print to PDF of an image) and images. The language field must also be set when using scanned images. A pre-processing step is required to extract the text from these documents before vectorizing them and the language field makes the text extraction more accurate.

    The RAWDATA table contains the data from the document.
    ```sql
    CREATE TABLE iceberg_data.documents.rawdata
        (
        "id"          int,
        "chunk_id"    int,
        "chunk"       varchar
        )
    ```

    The data is split into approximately 1M base64 chunks. The reason for the chunking of the data is due to a Presto client limit
    of 1M messages. Once the data is stored in watsonx.data, access to the underlying object can be controlled through
    user and group authentication. 

    An alternate strategy would be to upload the document and store it in an S3-like bucket. The downside is that the document is exposed in the bucket rather than obfuscated in Iceberg table format.

    ##### Web Pages
    Regular documents are stored "as-is" in watsonx.data, but URLs are handled differently. A web scraping routine extracts the text from the website and stores it in watsonx.data as a text document. What this means is that the data watsonx.data is valid as of the time the URL was uploaded. If the web page changes, it will not be reflected in the stored document. 

    ##### Pre-loaded Documents
    There is one document that has been pre-loaded into the system for your use (2023 IBM Annual Report). You can choose to upload your own documents to use with the LLMs. Some observations regarding documents.
    * PDFs, DOCs, and Text create good RAG prompts with a minimum of 3 sentences
    * PPTs require much more time to extract text and require more sentences (>5) to generate useful RAG prompts
    * URLs generate RAG prompts that may contain images that are ignored
    """
            st.markdown(details)

# Display current Documents
list_documents()

# Upload new document List
upload_document()

# Upload URL Dialog
upload_url()

# Upload Wikipedia Dialog
upload_wiki()

# Upload watsonx.data Data
upload_watsonx(connection)