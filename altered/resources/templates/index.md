
# {{ prompt_title|default("Untitled Prompt") }}
This is a LLM (Large Language Model) prompt, asking the LLM to answer a given quesiton, or to solve a problem. 
The LLM prompt consists of 3 blocks.
1. Context Information '<context>': Contains relevant context information to better understand the problem.
2. User Prompt '<user_prompt>': The recent user message coming from the underlying discussion.
3. Instructions '<INST>': Immediate instructions for the LLM to follow now.
{% block content %}
{% endblock %}
