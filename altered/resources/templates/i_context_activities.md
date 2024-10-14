## User and System Activities
The following shows the recent {{ context.activities|length }} activites as well as PS cmds performed on the underlying system. Reading this can improve context understanding.
{%- for activity in context.activities %}

### Activity {{ loop.index }}
- **Application Name:** {{ activity.application_name }}
{%- if activity.active_window %}
- **Window:** {{ activity.active_window }}
{%- endif %}
- **Activity Duration (seconds):** {{ activity.duration_seconds }}
- **Mouse Click Count:** {{ activity.mouse_click_count }}
- **Key Press Count:** {{ activity.key_press_count }}
{%- if activity.keyboard_shortcuts %}
- **Elevator Keys History:** {{ activity.keyboard_shortcuts }}
{%- endif %}
{% endfor %}

{% if context.ps_history %}
### Powershell cmd History
{%- for ps in context.ps_history %}
- **{{ loop.index }}:** {{ ps }}
{%- endfor %}
{% endif %}

### Git Diffs Log
The following section shows the recent {{ context.git_diffs|length }} `git diff` code changes, listed as txt files, sorted from recent to oldest.

{% for git_diff in context.git_diffs %}
### Change {{ loop.index }}
- **File Path:** {{ git_diff.file_path }}
- **Lines Changed (Start/End):** Old: {{ git_diff.start_ends[0] }}, New: {{ git_diff.start_ends[1] }}
#### Change Content:
```txt
{{ git_diff.content }}
```
{% endfor %}