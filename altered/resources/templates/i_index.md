# {{ prompt_title|capitalize|default("Untitled Prompt") }}
This is a LLM (Large Language Model) prompt, asking the LLM to answer a given quesiton, or to solve a problem. 
The LLM prompt consists of 3 blocks.
1. Context Information '<context>': Relevant available information for the LLM to better understand the problem.
2. User Prompt '<user_prompt>': The most recent user Question or Instruction.
3. Instructions '<INST>': __Master instructions__ for the _LLM_ to follow imediately.

{% block content %}
{% endblock %}
