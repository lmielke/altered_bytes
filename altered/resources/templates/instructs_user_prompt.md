{%- if instructs.user_prompt.user_prompt %}

# 2. User Prompt
{%- if instructs.user_prompt.prompt_str %}
The user was asked:
    - {{ instructs.user_prompt.prompt_str }}
The user wrote:
{% endif%}
{{ instructs.user_prompt.user_prompt }}
{% endif%}