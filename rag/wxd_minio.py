#---------------------------------------------------------------------------------------------
# Licensed Materials - Property of IBM 
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP 
# Schedule Contract with IBM Corp.
#
# Developed by George Baklarz
#---------------------------------------------------------------------------------------------
#
#   Minio module
#
#	Minio is used to simulate S3 buckets in a standalone watsonx.data system. This code contains 
#   a routine used to clear out the MinIO buckets so that we can start from an empty S3
#   environment for the demo.
#

import streamlit as st
from streamlit import session_state as sts
from wxd_utilities import log

def resetMinio():
	"""
	The resetMinio function will delete the existing document bucket and recreate it.
	"""
 
	from wxd_utilities import runOS

	program = "resetMinio"

	if ('initialized' not in sts):
		log(program,"[1] The credentials for the MinIO and Presto connections were not loaded.")
		return False
	
	minio_host        = sts['minio_host']  
	minio_port        = sts['minio_port']
	minio_bucket      = sts['minio_bucket']  
	minio_access_key  = sts['minio_access_key'] 
	minio_secret_key  = sts['minio_secret_key'] 

	runOS(f"mc alias set watsonxdata http://{minio_host}:{minio_port} {minio_access_key} {minio_secret_key}")
	runOS(f"mc rm --recursive --force watsonxdata/iceberg-bucket/{minio_bucket}",logit=False)
	return True
