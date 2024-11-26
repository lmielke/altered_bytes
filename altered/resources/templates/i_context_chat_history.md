
## General Background/History
### Original Prompt
This is the original prompt, which the entire chat is based on. Keep this in mind at all times!
__role: {{ context.init_prompt.role }}, content: {{ context.init_prompt.content }}__

### Chat History
The following is the current summary of the ongoing discussion.

{%- for entry in context.chat_history %}
{{ entry.role|upper }}:
    {{ entry.content }}
{% endfor %}
