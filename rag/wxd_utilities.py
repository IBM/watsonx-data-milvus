#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#	
#	Utility Code
#
#	This code contains several utility routines used by the system.
#

import streamlit as st
import hmac
import pandas as pd
from streamlit import session_state as sts


def runOS(command,logit=True):
	"""
	runOS takes a bash command and executes in the current environment. The results are split by
	newline and returned back to the program as an array of lines. If there is a failure in executing the 
	code, the details of the error are placed into the log file and no output is returned.
	"""
	import subprocess

	program = "runOS"

	success = False

	log(program,f"Executing command: {command}")

	if ("systemctl" in command):
		log(program,"Systemctl command may restart the application so results will not be logged")
		
	try:
		output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
		success = True 
	except subprocess.CalledProcessError as e:
		output = e.output
		log(program,f"[1] Execution of command failed: {command}")
		if logit: 
			log(program,f"[1] {output}")
	except Exception as e:
		log(program,f"[2] Execution of command failed: {command}")
		if logit:
			log(program,f"[2] {repr(e)}")

	if (success == True):
		results = output.split('\n')
		output = []
		for result in results:
			if (result.strip() != ""):
				output.append(result)
		log(program,f"Command: {command}")
		if logit:
			for line in output:
				if (line.strip() != ""):
					log("Output",line)
	else:
		output = None

	return output

def checkStatus():
	"""
	checkStatus runs the watsonx.data status command and returns the list of running processes as an 
	array. Note that the program has a list of default programs that run in a watsonx.data environment and
	so it checks to make sure that these systems are running. The value that is returned is an array of 
	values with the service name and the status. The status can be unknown (we didn't find it in the list of running
	services), or it is the status that is returned by the watsonx.data command.
	"""

	import subprocess
	watsonx = {
		"ibm-lh-cpg"               : "Unknown",
		"ibm-lh-etcd"              : "Unknown",
		"ibm-lh-mds-rest"		   : "Unknown",
		"ibm-lh-mds-thrift"		   : "Unknown",
		"ibm-lh-milvus"            : "Unknown",
		"ibm-lh-minio"             : "Unknown",
		"ibm-lh-postgres"          : "Unknown",
		"ibm-lh-presto"            : "Unknown",
		"ibm-lh-validator"         : "Unknown",
		"lhconsole-api"            : "Unknown",
		"lhconsole-nodeclient-svc" : "Unknown",
		"lhconsole-ui"             : "Unknown",
		"lhingestion-api"		   : "Unknown"
	}

	status_list = runOS('sudo /root/ibm-lh-dev/bin/status --all')
	for service in status_list:
		if (service in [None,""]): continue
		service = service.replace("\t"," ")
		service = service.replace(",","")
		service = service.replace("0.0.0.0:","")
		items = service.split()
		if (items[0] == "Checking"): continue
		service = items[0].strip()
		status = items[1].strip()
		if (service in watsonx):
			watsonx[service] = status.title()

	return watsonx

def log(program,text):
	"""
	The log function will write the text into a log file that can be used for diagnostics. The log
	file is erased when this system initially starts so that the log file is valid for the current
	session only. The log file can be found at /tmp/watsonx.log.
	"""

	import datetime, textwrap

	if (text in [None,""] or program in [None,""]):
		return

	with open("/tmp/watsonx.log","a") as fd:

		today = datetime.datetime.now().strftime("%H:%M:%S")
		
		lines = text.split('\n')
		initial = True
		chunk_count = 0
		for line in lines:
			out = line.replace('\t',' ')
			if (out.strip() != ""):
				chunks = textwrap.wrap(out,width=80)
				for chunk in chunks:
					if initial:
						fd.write(f"{today},{program},{chunk}\n")
						initial = False
					else:
						fd.write(f" , ,{chunk}\n")
					chunk_count = chunk_count + 1
					if (chunk_count == 5):
						fd.write(f" , ,*** Output truncated ***\n")
						return

	return

def setCredentials():
	"""
	setCredentials is used to set the credentials for the watsonx.data system. Each of the settings 
	are placed into the streamlit service so that the values are available across the web pages. Normally you
	would use either global variables or classes to contain the values, but due to the way that streamlit works,
	the safest way to keep the values is by using the builtin session state.
	"""

	import streamlit as st
	import warnings, os
	warnings.filterwarnings('ignore')

	log("Credentials","Setting credentials for the system.")

	sts['version']         = '1.3.0'
	sts['initialized']     = False
	sts['minio_host']      = "watsonxdata"
	sts['minio_port']      = "9000"
	sts['minio_bucket']	   = 'documents'
	sts['hive_host']       = "watsonxdata"
	sts['hive_port']       = "9083"
	sts['presto_userid']   = 'ibmlhadmin'
	sts['presto_password'] = 'password'
	sts['presto_host']     = 'watsonxdata'
	sts['presto_port']     = '8443'
	sts['presto_catalog']  = 'tpch'
	sts['presto_schema']   = 'tiny'
	sts['presto_certfile'] = "/certs/lh-ssl-ts.crt"	
	sts['complaints']      = "/home/watsonx/rag/samples/complaints-2025.csv"
	sts['rag']			   = True
	sts['terse']           = True
	sts['displayrag']      = True
	sts['milvus_host']     = 'watsonxdata'
	sts['milvus_port']     = 19530
	sts['milvus_user']     = 'ibmlhadmin'
	sts['milvus_password'] = 'password'
	sts['server_pem_path'] = "/certs/lh-ssl-ts.crt" # '/tmp/presto.crt'
	sts['model']           = "instructlab/granite-7b-lab"
	sts['queries']         = []
	sts['sentences']       = 3
	sts['vectorsize']      = "Small"
	sts['temperature']     = .70
	sts['displaysettings'] = True
	sts["random"]          = True
	sts["catalog"]		   = None
	sts["schema"]          = None
	sts["table"]           = None
	sts["catalogs"]        = pd.DataFrame()
	sts["schemas"]         = pd.DataFrame()
	sts["tables"]          = pd.DataFrame()
	sts["predicates"]      = None
	sts["language"]		   = "English"
	sts["languages"]	   = [
			"Abaza",
			"Adyghe",
			"Afrikaans",
			"Angika",
			"Arabic",
			"Assamese",
			"Avar",
			"Azerbaijani",
			"Belarusian",
			"Bulgarian",
			"Bihari",
			"Bhojpuri",
			"Bengali",
			"Bosnian",
			"Simplified Chinese",
			"Traditional Chinese",
			"Chechen",
			"Czech",
			"Welsh",
			"Danish",
			"Dargwa",
			"German",
			"English",
			"Spanish",
			"Estonian",
			"Persian (Farsi)",
			"French",
			"Irish",
			"Goan Konkani",
			"Hindi",
			"Croatian",
			"Hungarian",
			"Indonesian",
			"Ingush",
			"Icelandic",
			"Italian",
			"Japanese",
			"Kabardian",
			"Kannada",
			"Korean",
			"Kurdish",
			"Latin",
			"Lak",
			"Lezghian",
			"Lithuanian",
			"Latvian",
			"Magahi",
			"Maithili",
			"Maori",
			"Mongolian",
			"Marathi",
			"Malay",
			"Maltese",
			"Nepali",
			"Newari",
			"Dutch",
			"Norwegian",
			"Occitan",
			"Pali",
			"Polish",
			"Portuguese",
			"Romanian",
			"Russian",
			"Serbian (cyrillic)",
			"Serbian (latin)",
			"Nagpuri",
			"Slovak",
			"Slovenian",
			"Albanian",
			"Swedish",
			"Swahili",
			"Tamil",
			"Tabassaran",
			"Telugu",
			"Thai",
			"Tajik",
			"Tagalog",
			"Turkish",
			"Uyghur",
			"Ukranian",
			"Urdu",
			"Uzbek",
			"Vietnamese",
	]

	sts["codes"]	   = [
			"abq", "ady", "af", "ang", "ar", "as", "ava", "az", 
			"be", "bg", "bh", "bho", "bn", "bs",
			"ch_sim", "ch_tta",	"che", "cs", "cy",
			"da", "dar", "de",
			"en", "es",	"et",
			"fa", "fr",
			"ga",  "gom",
			"hi", "hr", "hu",
			"id", "inh", "is", "it",
			"ja",
			"kbd", "kn", "ko", "ku",
			"la", "lbe", "lez", "lt",
			"lv",
			"mah", "mai", "mi",	"mn", "mr", "ms", "mt",
			"ne", "new", "nl", "no",
			"oc",
			"pi", "pl",	"pt",
			"ro", "ru", "rs_cyrillic", "rs_latin",
			"sck", "sk", "sl", "sq", "sv", "sw",
			"ta", "tab", "te", "th", "tjk", "tl", "tr",
			"ug", "uk",	"ur", "uz",
			"vi",
	]	

	sts.languages.sort()
	sts.languages.insert(0,"English")
	sts.codes.insert(0,"en")

	hive_id           = None
	hive_password     = None
	minio_access_key  = None
	minio_secret_key  = None
	keystore_password = None	

	try:
		with open('/certs/passwords') as fd:
			certs = fd.readlines()
		for line in certs:
			args = line.split()
			if (len(args) >= 3):
				system   = args[0].strip()
				user     = args[1].strip()
				password = args[2].strip()
				if (system == "Minio"):
					minio_access_key = user
					minio_secret_key = password
				elif (system == "Thrift"):
					hive_id = user
					hive_password = password
				elif (system == "Keystore"):
					keystore_password = password
				else:
					pass
	except Exception as e:
		st.error("Certificate file with passwords could not be found.")
		return False	
	
	sts['hive_id']           = hive_id           
	sts['hive_password']     = hive_password     
	sts['minio_access_key']  = minio_access_key  
	sts['minio_secret_key']  = minio_secret_key  
	sts['keystore_password'] = keystore_password 
	sts['initialized']       = True

	return True

def check_password():
	"""
	Returns True if the user had a correct password.
	"""

	def login_form():
		"""
		Form with widgets to collect user information
		"""
		col1, col2 = st.columns([0.5,0.5])
		with col1:
			with st.form("Credentials"):
				text = \
"""
##### IBM watsonx.data and Milvus RAG Demonstration
Enter you credentials below.
"""
				st.markdown(text)
				st.text_input("Username", key="username")
				st.text_input("Password", type="password", key="password")
				st.form_submit_button("Log in", on_click=password_entered)

	def password_entered():
		"""
		Checks whether a password entered by the user is correct.
		"""
		if st.session_state["username"] in st.secrets[
			"passwords"
		] and hmac.compare_digest(
			st.session_state["password"],
			st.secrets.passwords[st.session_state["username"]],
		):
			st.session_state["password_ok"] = True
			del st.session_state["password"]  # Don't store the username or password.
			del st.session_state["username"]
		else:
			st.session_state["password_ok"] = False

	# Return True if the username + password is validated.
	if st.session_state.get("password_ok", False):
		return True

	# Show inputs for username + password.
	login_form()
	if "password_ok" in st.session_state:
		st.error("User not known or password incorrect.")
	return False

def getLanguageCode(language,indexValue=True):
	"""
    Provided with the language (English), return the language key [en] associated with it
	or the index into the language list.
    """

	log("getindex",f"language={language}")
	
	if (language in [None,""]):
		language = "English"

	try:
		languageIndex = sts.languages.index(language)
		languageCode = sts.codes[languageIndex]
	except:
		log("getindex","Not found")
		languageIndex = 0
		languageCode = "en"
		
	log("getindex",f"languageIndex={languageIndex} languageCode={languageCode}")	
	if (indexValue == True):
		return languageIndex
	else:
		return languageCode

def version_reset():
	"""
	Every time a new software release is done, this code gets called at the top of every 
	routine to make sure that any updates to the documents are done.
	"""
	
	from pymilvus import utility
	from wxd_data import connectPresto, badConnection, storeDocument
	from wxd_milvus import connectMilvus, storeVectors
	from wxd_utilities import log
	from streamlit import session_state as sts
	from time import sleep

	program = "reset"

	if "reset" in sts:
		if sts.reset:
			return
		
	sts.reset = False

	progressBar = st.progress(25,"Initializing system, please wait")
	sleep(0.5)
	setCredentials()

	progressBar.progress(50,"Checking Milvus")
	sleep(0.5)
	if (connectMilvus() == False):
		log(program,"[1] Unable to connect to Milvus")
		return None

	progressBar.progress(75,"Checking watsonx.data")
	sleep(0.5)
	connection = connectPresto()
	if (connection == None):
		log(program,"[2] Cannot connect to Presto engine")
		badConnection()
		st.stop()

	progressBar.progress(100,"Finalizing")
	sleep(0.5)
	progressBar.empty()
	sts.reset = True   

	return 

def buttonWidth(button_list):
	"""
	A shortcut routine used to place buttons on a screen. Since buttons are not placed one after another, the column control needs to be used to place buttons beside one another. The spacing is always an issue, so this routine returns the number of button slots we need which includes 1 column that acts as a spacer at the end.

	Given a list of button names, return the size of the columns needs to display them properly
	"""
	if (button_list in [None,""]):
		return None
	
	total_width = 0
	button_widths = []
	for button in button_list:
		button_width = len(button)
		button_widths.append(button_width)
		current_width = button_width + 2
		if (total_width == 0):
			total_width = current_width
		else:
			total_width = total_width + 2 + current_width
	button_width = 80 - total_width
	if (button_width < 0):
		button_width = 0
	button_widths.append(button_width)

	return button_widths
	
def setPage(title):
	"""
	This routine is used to set the sidebar width when displaying the screen. Appears that there is no global way of setting the size other than running this code at the beginning of every window.
	"""

	st.set_page_config(
		page_title=title,
		page_icon=":infinity:",
		layout="wide"    
	)

	st.markdown(
		"""
		<style>
			section[data-testid="stSidebar"] {
				width: 250px !important; # Set the width to your desired value
			}
		</style>
		""",
		unsafe_allow_html=True,
	)	

	if check_password():
		return True
	else:
		st.stop()