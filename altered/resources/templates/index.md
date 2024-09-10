
# {{ prompt_title|default("Untitled Prompt") }}
This is a LLM (Large Language Model) prompt, asking the LLM to answer a user quesiton or solve a user problem. 
The prompt consists of 3 blocks.
1. Context Information '<context>': Contains relevant context information to understand the prompt.
2. User Prompt '<user_prompt>': The last/current message from the user from the underlying chat.
3. Instructions '<INST>': Instructions for the LLM to follow.
{% block content %}
{% endblock %}
