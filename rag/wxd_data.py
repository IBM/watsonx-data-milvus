#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
#	This code contains routines that are used to store, retrieve, and manipulate documents in
#	watsonx.data
#

import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from streamlit import session_state as sts
from wxd_minio import resetMinio
from wxd_utilities import log

def connectPresto():
	"""
	connectPresto is used to connect to Presto engine that is running in the watsonx.data system. The credentials are hardcoded for the watsonx.data developer edition system.
	"""

	import prestodb
	from prestodb import transaction
	import pandas as pd
	import sqlalchemy
	from sqlalchemy import create_engine
	import warnings
	warnings.filterwarnings("ignore")

	program = "connectPresto"

	if ("watsonxConnection" in sts):
		if (sts.watsonxConnection is not None):
			return sts.watsonxConnection

	# Connection Parameters

	userid     = sts['presto_userid']  
	password   = sts['presto_password']
	hostname   = sts['presto_host']    
	port       = sts['presto_port']    
	catalog    = sts['presto_catalog'] 
	schema     = sts['presto_schema']  
	certfile   = sts['presto_certfile']	

	# Connect Statement
	try:
		connection = prestodb.dbapi.connect(
				host=hostname,
				port=port,
				user=userid,
				catalog=catalog,
				schema=schema,
				http_scheme='https',
				auth=prestodb.auth.BasicAuthentication(userid, password)
		)
		if (certfile != None):
			connection._http_session.verify = certfile

		log(program,f"Successful connection")

	except Exception as e:
		log(program,f"[1] Connection failed: {repr(e)}")
		sts.watsonxConnection = None
		connection = None

	sts.watsonxConnection = connection
	
	return(connection)

def runSQL(_connection, sql):
	"""
	runSQL will run the sql command and return a Panda dataframe as the output. If the SQL fails, the 
	error is logged and the program returns an empty dataframe.
	"""
	import pandas as pd

	program = "runSQL"
	log(program,sql)

	# The df contains the answer set in a Pandas dataframe
	try:
		df = pd.read_sql(sql,_connection)
		log(program,f"SQL completed. Row count = {len(df)}")
	except Exception as e:
		df = pd.DataFrame()
		log(program,f"[1] SQL failed: {repr(e)}")

	return df
	
def runDML(_connection, sql):
	"""
	runDML is used for executing SQL statements such as table creation, insert statements, etc... that do not return a value. 
	"""
	program = "runDML"
	log(program,sql)

	cursor = _connection.cursor()

	try:
		cursor.execute(sql)
		cursor.close()
		log(program,"SQL completed.")
		return True
	except Exception as err:
		log(program,f"[1] SQL failed: {repr(err)}")
		return False
	
def getID(_connection,filename):
	"""
	Get the ID of the filename, or return the next valid ID number in the database. If the filename already
	exists, the meta data needs to refreshed and the current document deleted from the table.
	"""

	program = "getID"

	if (filename in [None,""]):
		log(program,f"[1] Invalid filename '{filename}' provided in the function")
		return None
	
	# Check to see if the document already exists

	sql = f"select id from iceberg_data.documents.metadata where document = '{filename}'"
	idfound = runSQL(_connection, sql)
	if (len(idfound) == 0):
		# Retrieve last document number in the table
		sql = "select max(id) as last from iceberg_data.documents.metadata"
		count = runSQL(_connection, sql)
		count = count['last'][0]
		if (count in [None, ""]):
			id = 1
		else:
			id = int(count) + 1    
	else:
		# Document was found but needs to be deleted
		id = idfound['id'][0]
		log(program,f"[1] Deleting id={id}")
		sql = f"delete from iceberg_data.documents.metadata where id = {id}"
		ok = runDML(_connection,sql)
		sql = f"delete from iceberg_data.documents.rawdata  where id = {id}"
		ok = runDML(_connection,sql)

	return id

def getRAWFile(filename):
	"""
	Return the contents of a raw file name
	"""

	program = "getRAWfile"

	try:
		rawdata = open(filename,"rb").read()
	except Exception as e:
		rawdata = None
		log(program,f"[1] Unable to read the file {filename}.")
		log(program,f"{repr(e)}")

	return rawdata


def storeDocument(_connection, filename=None, filetype="txt", data=None, scan=False, language="en"):
	"""
	The document that is provided is read and broken up into chunks that
	are then inserted into watsonx.data in the rawdata control table. The document ID 
	is used in the procedure to provide the unique identifier for the chunks. The return
	value is the number of chunks generated.
	"""
								
	from base64 import urlsafe_b64encode, urlsafe_b64decode

	chunk_size=750000

	program = "storeDocument"

	id = insertMetadata(_connection, filename=filename, filetype=filetype, scan=scan, language=language)
	if (id in [None,"",0]):
		log(program,f"[1] Unable to retrieve a document ID.")
		return None

	if (data in [None,""]):
		return None

	encoded = urlsafe_b64encode(data)

	file_size = len(encoded)
	total_chunk = (file_size // chunk_size) + 1

	pos = 0
	chunk_id = 0
	while pos <= len(encoded):
		chunk_id += 1
		chunk = encoded[pos:pos+chunk_size].decode('utf-8')
		sql = f"insert into iceberg_data.documents.rawdata values ({id}, {chunk_id}, '{chunk}')"
		okay = runDML(_connection,sql)
		pos += chunk_size

	return chunk_id

def insertMetadata(_connection, filename=None, filetype="txt", scan=False, language="en"):
	"""
	Insert the filename details into the control table. The value that
	is returned is the document ID that was created.
	"""
	
	program = "insertMetadata"

	# Get the ID for the document

	id = getID(_connection,filename)
	log(program,f"[1] id={id} filename={filename} filetype={filetype} scan={scan} language={language}")

	if (id is None):
		log(program,f"[1] Failed to retrieve ID value.")
	else:
		sql = f"insert into iceberg_data.documents.metadata values ({id},'{filename}','{filetype}',{scan},'{language}')"
		rc = runDML(_connection, sql)
		if (rc == False):
			log(program,f"Metadata insert failed")
			id = None

	return id

def badConnection():
	"""
	We can't connect to the database so we need issue this message.
	"""

	st.header("Oops! Something has gone wrong!")
	error = \
"""
I can't connect to the watsonx.data service!
Check the following:
* In your reservation, click on the watsonx.data UI link
   * If you cannot connect, the service is down or unavailable
   * Press the Diagnostics button below and choose the Restart Server option
* If you can connect to the watsonx.data UI, log into the service as ibmlhadmin / password
   * Use the Data Manager view and check the schemas under the iceberg_data catalog
   * Three tables should exists - metadata, rawdata, and questions
   * If the tables do not exists, press the Diagnostics button below and choose the Rebuild Database option
* If all else fails, request another image.
"""
	st.error(error)
	if st.button("Diagnostics"):
		st.switch_page("pages/70-Diagnostics.py")
	return

def rebuildDatabase(_connection):
	"""
	Rebuild the contents of the database.
	"""

	import csv, prestodb

	program = "rebuildDB"

	if (_connection == None):
		error = \
"""
I can't connect to the watsonx.data service!
Check the following:
* In your reservation, click on the watsonx.data UI link
   * If you cannot connect, the service is down or unavailable
   * Press the Troubleshooting button and choose the Restart Server option
* If you can connect to the watsonx.data UI, log into the service as ibmlhadmin / password
   * Use the Data Manager view and check to see if you can view ANY schemas
   * If you can view the schemas then this program has an issue and you need to report it
   * If you cannot view any schema then the Presto engine may be down or restarting
   * Try pressing the Recreate Database button again and if it fails then you may want to 
	 restart the server.
"""
		st.error(error)
		log(program,"[1] Can't connect to watsonx.data.")
		return False
	
	if ('initialized' not in sts):
		st.error("The system variables have not been initialized.")
		log(program,"[2] The system variables and passwords have not been initialized.")
		return False
	
	schema = sts["minio_bucket"]

	sql = f'show tables from "iceberg_data"."{schema}"'
	alltables = runSQL(_connection,sql)
	for table in alltables['Table']:
		sql = f'DROP TABLE IF EXISTS "iceberg_data"."{schema}"."{table}"'
		_  = runDML(_connection, sql)

	sql = f"DROP SCHEMA IF EXISTS iceberg_data.{schema}"
	if (runDML(_connection, sql) == False):
		return False

	if (resetMinio() == False):
		st.error("Unable to create the document bucket.")
		log(program,"[3] Unable to create the document bucket.")
		return False
	
	sql = f"""
		CREATE SCHEMA IF NOT EXISTS 
			iceberg_data.documents
		WITH ( location = 's3a://iceberg-bucket/{schema}')
		"""
	if (runDML(_connection, sql) == False):
		return False
	
	sql = f"""
		CREATE TABLE iceberg_data.{schema}.metadata
			(
			"id"          int,
			"document"    varchar,
			"type"        varchar,
			"scan"        boolean,
			"language"    varchar
			)
		  """
	if (runDML(_connection,sql) == False):
		return False
	
	sql = f"""
		CREATE TABLE iceberg_data.{schema}.rawdata
			(
			"id"          int,
			"chunk_id"    int,
			"chunk"       varchar
			)
		"""
	if (runDML(_connection,sql) == False):
		return False

	sql = f"""
		CREATE TABLE iceberg_data.{schema}.complaints 
			(
			"issue"     varchar,
			"subissue"  varchar,
			"complaint" varchar,
			"company"   varchar,
			"state"     varchar
			)
		"""
	if (runDML(_connection,sql) == False):
		return False

	try:
		with open(sts.complaints) as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='"')

			header = True
			preINSERT = f'INSERT INTO "iceberg_data"."{schema}"."complaints" VALUES '
			record_count = 0
			records = [preINSERT]			
			comma = ""

			for row in reader:
				if header: 				# Ignoring the header line
					header = False
					continue

				if record_count == 100:
					sql = " ".join(records)
					if (runDML(_connection,sql) == False):
						return False
					records = [preINSERT]
					record_count = 0
					comma = ""

				complaint = row[2].replace("'","`")
				value = f" {comma} ('{row[0]}','{row[1]}','{complaint}','{row[3]}','{row[4]}')"
				comma = ","
				records.append(value)
				record_count = record_count + 1

			if record_count > 0:
				sql = " ".join(records)
				if (runDML(_connection,sql) == False) :
					return False					

			log(program,f"Complaints table loaded successfully")
			return True	
		
	except Exception as e:
		log(program,f"Unable to open complaints data file: {repr(e)}")
		return False
	
	# userid     = sts['presto_userid']  
	# password   = sts['presto_password']
	# hostname   = sts['presto_host']    
	# port       = sts['presto_port']    
	# catalog    = "iceberg_data" 
	# schema     = "documents"  
	# table      = "complaints"
	# certfile   = sts['presto_certfile']	

	# # Connect Statement
	# try:
	# 	connection = prestodb.dbapi.connect(
	# 			host=hostname,
	# 			port=port,
	# 			user=userid,
	# 			catalog=catalog,
	# 			schema=schema,
	# 			http_scheme='https',
	# 			auth=prestodb.auth.BasicAuthentication(userid, password)
	# 	)
	# 	if (certfile != None):
	# 		connection._http_session.verify = certfile

	# 	df = pd.read_csv(sts.complaints)

	# 	data = [tuple(x) for x in df.to_numpy()]

	# 	sql = 'INSERT INTO complaints VALUES (%s, %s, %s, %s, %s)'

	# 	cursor = connection.cursor()
	# 	cursor.executemany(sql,data)
	# 	connection.commit()
	# 	cursor.close()



	# 	# with open(sts.complaints) as csvfile:
	# 	# 	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	# 	# 	first = True
	# 	# 	cursor = _connection.cursor()

	# 	# 	for row in reader:
	# 	# 		if first:
	# 	# 			first = False
	# 	# 			continue
	# 	# 		complaint = row[2].replace("'","`")
	# 	# 		sql = f"""INSERT INTO "{catalog}"."{schema}"."{table}" values ('{row[0]}','{row[1]}','{complaint}','{row[3]}','{row[4]}')"""	
	# 	# 		st.write(sql)
	# 	# 		try:
	# 	# 			cursor.execute(sql)		
	# 	# 		except Exception as e:
	# 	# 			st.error(row[0])
	# 	# 			st.error(row[1])
	# 	# 			st.error(row[2])
	# 	# 			st.error(row[3])
	# 	# 			st.error(row[4])
	# 	# 			st.error(repr(e))
	# 	# 			cursor.close()
	# 	# 			return False

	# 	# cursor.close()
	# except Exception as e:
	# 	st.error(repr(e))	
	# 	return False
	
	# return True
	

def getDocument(_connection,id):
	"""
	The document with the provided id is retrieved and recombined to create the 
	original document. The document name provided will be overwritten by the contents
	of the database. The return value is either None (error) or the text of the 
	document.
	"""

	from base64 import urlsafe_b64encode, urlsafe_b64decode
	from llama_index.core.text_splitter import SentenceSplitter
	from llama_index.core import SimpleDirectoryReader
	import pymupdf, easyocr
	import re 

	program = "getDocument"

	if ('initialized' not in sts):
		st.error("The system variables have not been initialized.")
		log(program,"[1] The system variables and passwords have not been initialized.")
		return False
	
	# Check the data
	if (id in [None,"",0]):
		st.error("Document retrieval failed. Check the log for details.")			
		log(program,f"[2] An invalid document ID {id} was passed to the program.")
		return None

	sql = f"select document, type, scan, language from iceberg_data.documents.metadata where id = {id}"
	results = runSQL(_connection,sql)

	if (results.empty == True):
		st.error("SQL statement failure. Check the log for details.")			
		log(program,f"[3] SQL Error or Document ID {id} was not found.")
		return None

	document = results['document'][0]
	doctype  = results['type'][0]
	docscan  = results['scan'][0]
	doclanguage = results['language'][0]

	if (document in [None,""] or doctype in [None,""]):
		st.error("Document not found. Check the log for details.")			
		log(program,f"[4] SQL Error or Document ID {id} was not found.")
		return None	

	languages = ["en"]
	if (docscan == True): 
		if (doclanguage not in languages):
			languages.append(doclanguage)
			
	if (doctype in ["html","wiki"]):
		filetype = "txt"
	else:
		filetype = doctype

	sql = f"select chunk_id, chunk from iceberg_data.documents.rawdata where id = {id} order by chunk_id asc"
	
	chunks = runSQL(_connection,sql)
		
	if (len(chunks) == 0):
		st.error(f"The document ID {id} has no data in the control table.")
		log(program,f"[5] Document ID {id} has no data.")
		return None

	targetDocument = f"/tmp/vector.{filetype}"

	reconstituted = None
	chunklist = chunks['chunk'].tolist()
	reconstituted = ''.join(chunklist)

	try:
		with open(targetDocument,"wb") as fd:
			rawchunk = urlsafe_b64decode(reconstituted)
			fd.write(rawchunk)
	except Exception as e:
		st.error(f"Failed to write document. See log for details.")
		log(program,f"[6] Error writing data to file {targetDocument}")
		log(program,f"[6] {repr(e)}")
		return None
	
	if (doctype in ["png","jpg","jpeg","tiff"]):
		returnText = None
		try:
			reader = easyocr.Reader(languages,gpu=False,verbose=False)
			result = reader.readtext(targetDocument,paragraph=True,detail=0)
			returnText = " ".join(result)
		except Exception as e:
			st.error(f"Failed to process document. See log for details.")
			log(program,f"[7.1] Unable to process the image file")
			log(program,f"[7.1] {repr(e)}")				

	elif (docscan == True and doctype == "pdf"):
		returnText = None
		try:
			pymupdf.TOOLS.mupdf_display_warnings(False)
			pymupdf.TOOLS.mupdf_display_errors(False)
			pdfimages = pymupdf.open(targetDocument)
			zoom = 4
			matrix = pymupdf.Matrix(zoom, zoom)

			page_count = len(pdfimages)
			for page_no in range(page_count):
				imageFile = f"/tmp/image_{page_no+1}.png"
				page = pdfimages.load_page(page_no)
				pixels = page.get_pixmap(matrix=matrix)
				pixels.save(imageFile)
			
			pdfimages.close()

			reader = easyocr.Reader(languages,gpu=False,verbose=False)

			returnText = None
			for page_no in range(page_count):
				result = reader.readtext(f"/tmp/image_{page_no+1}.png",paragraph=True,detail=0)
				page_contents = " ".join(result)
				if (returnText is None):
					returnText = f"Page: 1\n\n{page_contents}"
				else:
					returnText = f"{returnText}\n\nPage: {page_no+1}\n\n{page_contents}"
		except:
			st.error(f"Failed to process document. See log for details.")
			log(program,f"[7.2] Unable to process the PDF image file")
			log(program,f"[7.2] {repr(e)}")	

	else:
		returnText = None				
		try:
			documents = SimpleDirectoryReader(input_files=[targetDocument]).load_data()
			for doc in documents: # iterate the document pages
				if (returnText == None):
					returnText = doc.text
				else:
					returnText += doc.text
		except Exception as e:
			st.error(f"Failed to process document. See log for details.")
			log(program,f"[7.3] Unable to process the file")
			log(program,f"[7.3] {repr(e)}")	

	if (returnText not in [None,""]):
		try:
			clean1 = ''.join([i if ord(i) < 128 else ' ' for i in returnText])
			clean2 = " ".join(clean1.split())
			clean3 = clean2.replace("\n","")
			clean4 = re.sub(r" ([s]) ",r"\1 ",clean3)
			clean5 = re.sub(r" ([b-hj-z]) ",r" \1",clean4)
			clean6 = re.sub(r'http\S+', ' ', clean5)
			returnText = re.sub(r"\$",r"\$",clean6)
		except Exception as e:
			st.error(f"Failed to process document. See log for details.")
			log(program,f"[7.4] Unable to clean up the document")
			log(program,f"[7.4] {repr(e)}")	
			returnText = None	

	return returnText

def getDocuments(_connection):
	"""
	Get the list of documents and that are currently in the database. The list that is returned
	is the document number and the document name.
	"""
	documents = None
	
	if (_connection in [None,""]):
		return None

	sql = "select id, document from iceberg_data.documents.metadata order by id asc"
	
	documents = runSQL(_connection, sql)
	
	return documents