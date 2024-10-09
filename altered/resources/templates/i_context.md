{%- if context %}

# 1. Context Information

{%- if context.os_infos is not none and context.os_infos %}
{% include "i_context_os_system.md" ignore missing %}
{%- endif %}

Here you find all available context information possibly relevant for this prompt.
{%- if context.chat_history %}
{% include "i_context_chat_history.md" ignore missing %}
{%- endif %}

{%- if context.activities is not none and context.activities %}
{% include "i_context_activities.md" ignore missing %}
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