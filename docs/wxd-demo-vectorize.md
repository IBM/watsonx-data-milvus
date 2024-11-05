# Vectorize Documents

Milvus is a vector database that stores, indexes, and manages massive embedding vectors that are developed by deep neural networks and other machine learning (ML) models. It is developed to empower embedding similarity search and AI applications. Milvus makes unstructured data search more accessible and consistent across various environments.

The watsonx.data system that you are running includes the Milvus server. The Milvus vector database is used to store sentences extracted from documents, and then convert them into vectors for searching. 

## Vectorize Documents

The Vectorize panel displays the list of document collections, the documents stored in the watsonx.data system, and an option to vectorize one or more documents. 

![Browser](wxd-images/demo-vector-main.png)

### Current Document Collections

A document collection is made up of a series of documents that have been vectorized. 

![Browser](wxd-images/demo-vector-collections.png)

In the screen above, only one collection (IBM_2023_Annual_Report) is currently loaded into the system. If you decide to generate a RAG prompt when querying an LLM, you must specify this document collection. 

A document collection is made up of a one or more documents (or URLs) that are transformed into vectors and stored in Milvus. When querying an LLM, the Milvus vector database will search the document collection for sentences to use as part of the RAG generation. 

!!! abstract "Document Collections"

    You can include as many documents, URLs, or Wiki documents in your document collection. The documents will be combined and stored as vectors in the Milvus database. The only criteria for your documents is that the topics covered by your documents are the same. 

### Document List

The document list contains all the documents and URLs that have been registered in the system.

![Browser](wxd-images/demo-vector-documents.png)

One or more documents make up a collection. Select the documents that you want to be included in a collection, and they will be vectorized as a group in Milvus. Provide a unique name for your collection and then press the Vectorize Collection button.

If you use the name of an existing collection, the contents of that collection will be overwritten with the new documents.

Once you press the ++"Vectorize Collection"++ button, the documents will be converted into vectors and stored in Milvus. This process may take a few minutes to complete depending on the size of the documents.

![Browser](wxd-images/demo-vector-vectorizing.png)

The collection will now be available for your RAG generation step.

## Technical Details

In order to create a RAG (Retrieval Augmented Generation), one or more documents must be selected from the database, the text
extracted, and then stored into Milvus and vectorized.

The process to vectorize a document involves converting the document (PPT, PDF, etc...) into RAW text. Once the text is available, the text is split into smaller chunks, with each chunk containing 512 or so tokens. A token is loosely compared to a word. These chunks are stored in the Milvus database and the text is vectorized using an algorithm (sentence-transformers/all-MiniLM-L6-v2).

Once the vectorization is completed, we can search the data for similar sentences when generating a RAG prompt.

The LLM can run without using a document collection, but it will not be able to generate a RAG prompt. 