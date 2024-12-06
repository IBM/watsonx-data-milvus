# Query LLM

The Query LLM panel is used to ask questions of the LLM.

![Browser](wxd-images/demo-queryllm-main.png)

The central part of the screen contains the chat window.

![Browser](wxd-images/demo-queryllm-chat.png)

The question that you want to ask the LLM is placed into the text box at the bottom of the screen, press ++enter++, and the response will be placed into the chat window underneath your question.

![Browser](wxd-images/demo-queryllm-response.png)

The bottom of the question will include the settings that were used when querying the LLM. 

![Browser](wxd-images/demo-queryllm-viewsettings.png)

The ++"Clear"++ button will clear all the questions and replies from the screen.

While the LLM is answering the question, a ++"Stop"++ button will be displayed.

![Browser](wxd-images/demo-queryllm-stop.png)

If you find that the LLM is taking too long to respond (or saying too much), press the stop button. Stopping the LLM will clear the last response on the screen.

!!! warning "System performance is limited by the lack of GPUs"

    Note that this system does not have GPUs attached to it so the response may take a minute or so to return. The initial question will load the LLM into memory which will result in a delay in answering the question. Subsequent questions will usually be answered faster.

    When you switch LLMs, the new LLM will need to be loaded into memory. Take this into account when you are demoing different LLMs.

The left side of the screen contains options that will change the behavior of the LLM.

![Browser](wxd-images/demo-queryllm-options.png)

These options are discussed in the sections below.

## LLM Options

### Current LLM Model

The LLM table provides a list of LLMs that are currently loaded into the system. The value that is listed will be the one that is used for your query.

![Browser](wxd-images/demo-queryllm-model.png)

Choose which LLM you want to use to answer your query. The default LLM is the Instructlab/granite-7b-lab model. If you want to add more LLMs to the system, use the Add LLM model dialog.

### Current Collection
The list of collections that have been vectorized are found in this table. 

![Browser](wxd-images/demo-queryllm-collection.png)

Select which collection you want to use when generating the RAG prompt. Make sure that you are using a document collection that matches the question you are asking the LLM!

### Prompt Settings

The Prompt Settings determine how the RAG prompt gets generated when querying the LLM.

![Browser](wxd-images/demo-queryllm-settings.png)

When an option is selected, it will be highlighted in red.

#### Hide RAG

The default setting for the system is to display the RAG prompt that is generated. Select this option is you want to turn the Display RAG prompt off.

#### Verbose Reply

The system will generate a RAG prompt that tells the LLM to provide a concise response. If you select a Verbose Reply, the LLM will be allowed to answer your question without length restrictions. The trade-off when turning off the concise option is the amount of time it takes to return the full output from the LLM.  

#### Repeatable

The LLM is provided with a random seed whenever a question is asked. When a random number is used, the answer to the same question may vary between runs. If you select the Repeatable option, the LLM will be provided with the same random number (42 - Ask the LLM what that number means!). In most cases, the answer will be the same between runs.


#### Maximum RAG Sentences

The Maximum RAG Sentences setting is used to limit the number of sentences that the RAG program will use in the question. The default number of sentences is 4. Using a larger number of sentences will slow down the LLM response, but it may result in a higher quality answer. Setting the value to zero will stop any RAG generation.

#### Creativity (Temperature)

The Creativity (Temperature) setting determines how the LLM will answer the question. The possible values are None (0), Low (0.3), Medium (0.7), and High (1.5), with Medium being the default value. Use a lower temperature value when you want more dependable output. Use a higher temperature value when you want to increase the randomness and variability or the output, such as when you want creative output. Remember, randomness can also lead to inaccurate or nonsensical output.

### Questions

The left sidebar includes a list of questions previously sent to the LLM.

![Browser](wxd-images/demo-queryllm-questions.png)

To copy a question into the LLM prompt, use the following steps:

1. Click on the question you want to copy from the list (it will be highlighted)
2. Use the keyboard copy button (Windows/Linux ++ctrl+"c"++, Mac ++command+"c"++) to place the value onto the clipboard
3. Click on the LLM question input line
4. Use keyboard paste button (Windows/Linux ++ctrl+"v"++, Mac ++command+"v"++) to place the copied value into the line

## Technical Details

The process which takes place when you enter a question is:

* The question is turned into a vector value
* The value is compared to the sentence vectors that were generated in the Vectorize Document step (Document collection)
* The 3 best sentences (or whatever you may have set the sentence limit to) will be used to generate a RAG prompt
* The RAG prompt is sent to the LLM
* The program displays the results as they are generated by the LLM

If you want to view the Milvus vector distance for the RAG prompts, view the LOG file output.