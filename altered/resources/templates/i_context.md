{%- if context %}

# 1. Context Information
Here you find all available context information possibly relevant for this prompt.

{% if context.sys_info %}
{% include "i_context_sys_info.md" ignore missing %}
{%- endif %}

{%- if context.chat_history %}
{% include "i_context_chat_history.md" ignore missing %}
{%- endif %}

{%- if context.activities %}
{% include "i_context_activities.md" ignore missing %}
{%- endif %}

{%- if context.package_infos %}
{% include "i_context_package_infos.md" ignore missing %}
{%- endif %}

{%- if context.search_results %}
{% include "search_results.md" ignore missing %}
{% include "i_context_search_results.md" ignore missing %}
{%- endif %}

{%- if context.rag_selection %}
{% include "i_context_rag.md" ignore missing %}
{%- endif %}

{%- else %}
No context information available.
{%- endif %}
