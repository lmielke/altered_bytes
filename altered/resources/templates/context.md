# Context Information
Please find attached some context information possibly relevant for this prompt.
{%- if context %}
  {%- if context.chat_history %}
## Chat History
This is what was discussed so far.
{%- for entry in context.chat_history %}
{{ loop.index }}. {{ entry.role }}: {{ entry.content }}
{%- endfor %}
The recent chat question will be provided as <user_prompt> further below in this prompt.
{%- endif %}
{%- if context.rag_selection is not none and context.rag_selection %}
## RAG Selection (Retrieval-Augmented Generation)
The following data was automatically added using RAG. Since RAG is an experimental feature,
the data attached may or may not be relevant for solving the problem.
  {%- if context.rag_selection is mapping %}
    {%- for key, value in context.rag_selection.items() %}
### {{ key|capitalize }}
{{ value }}
    {%- endfor %}
  {%- else %}
{{ context.rag_selection }}
  {%- endif %}
{%- endif %}
{%- for key, value in context.items() %}
  {%- if key not in ['chat_history', 'rag_selection'] and value is not none %}
## {{ key|capitalize }}
{{ value }}
  {%- endif %}
{%- endfor %}
{%- else %}
No context information available.
{%- endif %}