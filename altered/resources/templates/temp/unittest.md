
# Unittest
This is a LLM (Large Language Model) prompt, asking the LLM to answer a user quesiton or solve a user problem. 
The prompt consists of 3 blocks.
1. Context Information '<context>': Contains relevant context information to understand the prompt.
2. User Prompt '<user_prompt>': The last/current message from the user from the underlying chat.
3. Instructions '<INST>': Instructions for the LLM to follow.


<context>
# Context Information
Please find attached some context information possibly relevant for this prompt.
## Chat History
This is what was discussed so far.
1. user: Hello
2. assistant: Hello! How can I assist you today?
The recent chat question will be provided as <user_prompt> further below in this prompt.
## RAG Selection (Retrieval-Augmented Generation)
The following data was automatically added using RAG. Since RAG is an experimental feature,
the data attached may or may not be relevant for solving the problem.
### Os_infos
Windows 10
### Project_infos
altered_bytes infos
## Infos
This is Unittest.
</context>

<user_prompt>
Why is the sky blue?
</user_prompt>

<INST>
You are a helpful assistant!
# Instruct
Please provide an answer to the user's question.
</INST>

