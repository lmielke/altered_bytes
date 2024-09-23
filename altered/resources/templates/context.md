{%- if context %}

# 1. Context Information
Here you find all available context information possibly relevant for this prompt.
{%- if context.context_history %}
{% include "context_history.md" ignore missing %}
{%- endif %}

{%- if context.context_search_results is not none and context.context_search_results %}
{% include "context_search_results.md" ignore missing %}
{%- endif %}

{%- if context.rag_selection is not none and context.rag_selection %}
{% include "context_rag.md" ignore missing %}
{%- endif %}

{%- else %}
No context information available.
{%- endif %}