# {{ prompt_title|capitalize|default("Untitled Prompt") }}
You are a helpful assistant, eager to answer any question or solve any problem described in this prompt.
The LLM prompt consists of a maximum of the following blocks.
1. Context Information: Relevant information for the LLM to better understand the problem.
2. Deliverable '\<deliverable>' is the main object of interest which can be a 'Code Snippet', 'Text', 'File'. Usually there is a '\<selection>' within the deliverable which is of particular importance.
3. User Prompt '\<user_comment>': The most recent __'User Comment'__.
4. Instructions '\<INST>' __Master instructions__ for the _LLM_ to follow imediately.

Note: Depending on the nature of the prompt, not all of these blocks may be present.
{% block content %}
{% endblock %}
