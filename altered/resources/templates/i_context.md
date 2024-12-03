{%- if context %}

# 1. Context Information
Here you find all context information that might be relevant for the task below.

{% if context.sys_info %}
{% include "i_context_sys_info.md" ignore missing %}
{%- endif %}

{%- if context.chat_history %}
{% include "i_context_chat_history.md" ignore missing %}
{%- endif %}

{%- if context.user_info %}
{% include "i_context_user_info.md" ignore missing %}
{%- endif %}

{%- if context.package_info %}
{% include "i_context_package_info.md" ignore missing %}
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
