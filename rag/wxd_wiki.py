#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
# 	This code is used to query Wikipedia to extract documents to use as part of a RAG prompt.
#

import streamlit as st
from streamlit import session_state as sts
import wxd_data as db
from wxd_utilities import log

def getArticles(articles,selection):
	"""
	getArticles is used to retrieve articles from Wikipedia and return a list of documents. The 
	value that is returned is the concatenation of the articles and the titles.
	"""

	import wikipedia
	import warnings
	warnings.filterwarnings("ignore")

	program = "getArticles"

	allArticles = None
	allTitles = None

	if (selection is None):
		log(program,"[1] No articles were selected when requesting article downloads")
		return allArticles
	
	for row_no in selection:
		try:
			article = articles[row_no][1]
			article_text = wikipedia.page(article)
			if (allArticles is None):
				allArticles = article_text.content
				allTitles = article
			else:
				allArticles = f"{allArticles}\n\n{article_text.content}"
				allTitles = f"{allTitles} & {article}"
		except:
			continue

	log(program,f"Wikipedia articles retrieved: {len(selection)}")

	return allTitles, allArticles
