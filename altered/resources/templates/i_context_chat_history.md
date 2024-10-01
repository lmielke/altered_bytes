
## General Background/History
### Original Prompt
This is the original prompt, which the entire chat is based on. Keep this in mind at all times!
__role: {{ context.init_prompt.role }}, content: {{ context.init_prompt.content }}__

### Chat History
The following is an abstract of the current discussion state for this prompt.
{%- for entry in context.chat_history %}
{{ loop.index }}. {{ entry.role }}: {{ entry.content }}
{%- endfor %}
... pls find the continuation inside <user_prompt> or <INST>

