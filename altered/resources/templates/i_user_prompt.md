{%- if user_prompt.user_prompt %}

# 2. User Prompt
{%- if user_prompt.prompt_str %}
The user was asked:
    - {{ user_prompt.prompt_str }}
The user wrote:
{% endif%}
{{ user_prompt.user_prompt }}
{% endif%}