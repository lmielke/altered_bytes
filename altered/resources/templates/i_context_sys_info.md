{% if context.sys_info %}
{%- if context.sys_info.sys_info_ops %}
{% include "i_context_sys_info_ops.md" ignore missing %}
{%- endif %}

{% if context.sys_info.sys_info_usr %}
{% include "i_context_sys_info_usr.md" ignore missing %}
{%- endif %}
{%- endif %}

