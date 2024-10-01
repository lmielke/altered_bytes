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