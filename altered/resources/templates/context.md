{%- if context %}

# Context Information
Please find attached some context information possibly relevant for this prompt.

{%- if context.history %}
{%- include "context_history.md" ignore missing %}
{%- endif %}

{%- if context.rag_selection is not none and context.rag_selection %}
{%- include "context_rag.md" ignore missing %}
{%- endif %}

{%- include "context_other.md" ignore missing %}

{%- else %}
No context information available.
{%- endif %}