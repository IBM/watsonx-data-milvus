#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------

import streamlit as st
import wxd_data as db
from streamlit import session_state as sts
from wxd_utilities import log, runOS

def getLLMs():
	"""
	getLLMs will generate a list of models that are currently found in the system.
	"""

	from ollama import Client
	client = Client(host='http://localhost:11434')

	llmlist = client.list()
	models = []
	for model in llmlist['models']:
		model_name = model['name'].replace(':latest','')
		models.append(model_name)
 
	models.sort()
	return models

def deleteLLM(model):
	"""
	deleteModel will remove the LLM from the system.
	"""

	program = "deleteLLM"

	from ollama import Client
	client = Client(host='http://localhost:11434')

	ok = True

	try:
		client.delete(model)
	except Exception as e:
		log(program,f"[1] Error deleting model: {repr(e)}")
		ok = False
 
	return ok

def loadLLM(llmname):
	"""
	loadLLM will ask Ollama to load the model into the system.
	"""

	program = "loadLLM"

	log(program,f"Loading model {llmname}")

	from ollama import Client
	client = Client(host='http://localhost:11434')

	loaded = True

	try:
		client.pull(llmname)
	except Exception as e:
		log(program,f"[1] Error pulling the model: {repr(e)}")
		loaded = False
 
	return loaded


def askLLM(prompt,temperature,random):
	"""
	This function will call the LLM system to ask the question and retrieve the feedback from the
	model. The async function is used to print out the answer as the results come back.
	"""

	from llama_index.llms.ollama import Ollama
	import streamlit as st
	import re

	program = "askLLM"

	try:
		model = sts.model 
	except:
		model = 'instructlab/granite-7b-lab'

	options = {
		"seed"        : 42,
	}
   
	llm = Ollama(base_url='http://localhost:11434',model=model, request_timeout=1000.0, streaming=True)
	llm.temperature = temperature

	if (random == False):
		llm.additional_kwargs = options
	
	content = ""
	for completion in llm.stream_complete(prompt):

		fixed_text = re.sub(r"\$",r":heavy_dollar_sign:",completion.delta)
		content += fixed_text
		yield fixed_text
	