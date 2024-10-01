{%- if context %}

# 1. Context Information
Here you find all available context information possibly relevant for this prompt.
{%- if context.chat_history %}
{% include "i_context_chat_history.md" ignore missing %}
{%- endif %}

{%- if context.search_results is not none and context.search_results %}
{% include "search_results.md" ignore missing %}
{%- endif %}

{%- if context.rag_selection is not none and context.rag_selection %}
{% include "i_context_rag.md" ignore missing %}
{%- endif %}

{%- else %}
No context information available.
{%- endif %}