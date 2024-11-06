# Example LLM Queries

This section includes some sample LLM queries and the results. One thing to note is that if you attempt these examples, the output can be different than what is shown here. The reason for this is that LLMs are not deterministic which means the same question can result in different answers. Hopefully in our case, the answers are similar!

For each example, note the settings that are used. These settings will displayed in each section. 

|LLM|Use RAG Prompt|Display RAG Prompt|Concise Response|Sentences
|-----|:------------:|:----------------:|:--------------:|:-------:
|granite-7b-lab |&#9989;|&#9989;|&#10060;|3
   
## Question with no RAG Support

The first example will ask the LLM the question with all settings turned off. 

|LLM|Use RAG Prompt|Display RAG Prompt|Concise Response|Sentences
|-----|:------------:|:----------------:|:--------------:|:-------:
|granite-7b-lab |&#10060;|&#10060;|&#10060;|-

#### Question

> What is IBMs 2023 revenue.

#### Answer

> As a helpful AI assistant, I don't have real-time access to the internet or proprietary company information, so I can't provide you with the exact 2023 revenue of IBM. However, I can give you some context about IBM's financial performance and how to find this information officially.
&nbsp;<p>
IBM is a multinational technology corporation that provides various products and services, including hardware, software, cloud, consulting, and support. The company releases its annual reports and financial statements, which contain detailed revenue information for different segments and geographical regions. To access IBM's 2023 revenue, I recommend visiting the official IBM investor relations website (https://www.ibm.com/investor/reports-and-presentations) or the Securities and Exchange Commission (SEC) filings database (https://www.sec.gov/).
&nbsp;<p>
These resources will provide you with the most accurate and up-to-date financial information about IBM, including its revenue for the year 2023, once it is officially released.

#### Analysis

The LLM does not have the information for 2023 results and provided us with an answer on how to get the results we want.

## Question with no RAG Support but Concise Response

The first example let the LLM display as much output as it wanted. In this example, the Concise Response is turned on, as well as the Display RAG prompt so you can see how the program modified the question.

|LLM|Use RAG Prompt|Display RAG Prompt|Concise Response|Sentences
|-----|:------------:|:----------------:|:--------------:|:-------:
|granite-7b-lab |&#9989;|&#10060;|&#9989;|-

#### Question

> Provide a concise response to this prompt: What is IBMs 2023 revenue?

#### Answer

> As an AI language model, I don't have real-time capabilities or access to current, confidential, or proprietary information from IBM or any other organizations. I cannot provide the exact 2023 revenue for IBM. For accurate financial data, I encourage you to consult IBM's official financial statements or trusted business resources.

### Analysis

You can limit the amount of output from the LLM by turning on the concise flag. While this will speed up the processing of the question by the LLM, it may reduce the amount of useful information that you get back.

## Question with RAG On, Concise On, RAG Display, and 3 Sentences

The question that we ask the LLM will now use RAG to generate it. The document collection that is being used is called IBM_2023_Annual_Report and contains the summary of the IBM 2023 earning report.

|LLM|Use RAG Prompt|Display RAG Prompt|Concise Response|Sentences
|-----|:------------:|:----------------:|:--------------:|:-------:
|granite-7b-lab |&#9989;|&#9989;|&#9989;|3

#### Question

> Answer the question based on the context below. If the question cannot be answered using the information provided answer with "I don't know".
&nbsp;<p>
Context:
&nbsp;<p>
Todays IBM is more capable and more productive. We have a strong portfolio and a solid foundation to support sustainable growth. And we are delivering on our promise to be the catalyst that makes the world work better. 2023 performance For the year, IBM generated $61.9 billion in revenue, up 3% at constant currency, and $11.2 billion of free cash flow, up $1.9 billion year-over-year. We experienced growing demand for our new watsonx platform, marked by thousands of client
&nbsp;<p>
Infrastructure revenues decreased by 4% at constant currency, in line with the typical product cycle dynamics in this segment. IBM z16 is significantly outperforming previous cycles, demonstrating the enduring value this platform provides to our clients. IBMs revenue growth and cash generation enabled us to make substantial investments in the business and deliver value to our shareholders. In 2023, IBM spent nearly $7 billion on research and
&nbsp;<p>
IBM spent nearly $7 billion on research and development, more than $5 billion to acquire nine companies, and returned more than $6 billion to stockholders through dividends. small arrow software Software consulting Consulting infrastructure Infrastructure Technology and expertise AI and hybrid cloud continue to drive value creation, allowing businesses to scale,.
&nbsp;<p>
Question: Provide a concise response to What is IBMs 2023 revenue?

#### Answer

> IBM's 2023 revenue was $61.9 billion, as stated in the context.

#### Analysis

The generated RAG prompt contains sentences from the earnings report that most closely match the original question. You will note that several of the  paragraphs are not complete and may contain special characters that are not seen on the screen. The reason for incomplete sentences is that the vectors are created by taking tokens (loosely translated to words) until they equal a set number of vectors. Vectors need to be of equal distance in order to do valid comparisons. For this reason, you tend to get sentences that are not complete.

## Question with RAG On, Concise On, RAG Display, and 1 Sentence

In this example, we will ask the LLM about the number of acquisitions IBM made in 2023 and constrain the RAG to only one sentence. This will demonstrate that having more "details" in the RAG prompt will provide for a better response from the LLM.

|LLM|Use RAG Prompt|Display RAG Prompt|Concise Response|Sentences
|-----|:------------:|:----------------:|:--------------:|:-------:
|granite-7b-lab |&#9989;|&#9989;|&#9989;|1

#### Question

> Answer the question based on the context below. If the question cannot be answered using the information provided answer with "I don't know".
&nbsp;<p>
Context:
&nbsp;<p>
IBM spent nearly $7 billion on research and development, more than $5 billion to acquire nine companies, and returned more than $6 billion to stockholders through dividends. small arrow software Software consulting Consulting infrastructure Infrastructure Technology and expertise AI and hybrid cloud continue to drive value creation, allowing businesses to scale,.
&nbsp;<p>
Question: How many companies did IBM acquire in 2023?

#### Answer

> The context provided does not include information about the number of companies IBM acquired in 2023. The latest year with available data for the number of companies IBM acquired is 2022, which was nine companies. Therefore, I cannot provide an answer to this question using the information given.

#### Analysis

You will notice that the LLM could not determine the date of the statement above and assumed that it was 2022. It may help to include more details in the RAG prompt to provide the LLM with more information it can use.

If we change the prompt to include 5 sentences, the answer is correct but the LLM doesn't think it is!

> Based on the context provided, the information about IBM's acquisitions in 2023 is not explicitly stated. The text mentions that IBM spent nearly $7 billion on research and development, more than $5 billion to acquire nine companies, and returned more than $6 billion to stockholders through dividends in a previous year. Therefore, I cannot provide an accurate answer to the question about the number of companies IBM acquired in 2023 based on the given information.


