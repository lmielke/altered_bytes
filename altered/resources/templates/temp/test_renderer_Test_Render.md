
# Unittest
This is a LLM (Large Language Model) prompt, asking the LLM to answer a given quesiton, or to solve a problem. 
The LLM prompt consists of 3 blocks.
1. Context Information '<context>': Contains relevant context information to better understand the problem.
2. User Prompt '<user_comment>': The recent user message coming from the underlying discussion.
3. Instructions '<INST>': Immediate instructions for the LLM to follow now.


<context>



# Context Information
Please find attached some context information possibly relevant for this prompt.
## Chat History
This is what was discussed so far.
1. user: Hello
2. assistant: Hello! How can I assist you today?
The recent chat question will be provided as <user_comment> further below in this prompt.
## RAG Selection (Retrieval-Augmented Generation)
The following data was automatically added using RAG. Since RAG is an experimental feature,
the data attached may or may not be relevant for solving the problem.
### Os_infos
Windows 10
### Project_infos
altered_bytes infos
## Additional Context
### Unittest info
This is test_renderer.
</context>

<user_comment>
Why is the sky blue?
</user_comment>

<INST>
You are a helpful assistant.
You have been provided with a <user_comment> ...some text... </user_comment>.  Answer the <user_comment> directly. 


# Prompt_aggregations
Provide a comprehensive summary that captures the summary of all ideas provided by all input responses, include all aspects regardless of their relevance.
 Only leave out aspects that are obviously completely irrelevant.

</INST>

