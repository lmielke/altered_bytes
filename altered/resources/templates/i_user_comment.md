{%- if user_comment %}
# 2. User Comment
{%- if user_comment.prompt_str %}
The user was asked:
    - {{ user_comment.prompt_str }}
The user wrote:
{% endif%}
{{ user_comment.user_prompt }}
{% endif%}