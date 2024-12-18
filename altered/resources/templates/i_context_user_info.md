## User and System Activities
The following shows some stats about recent user activities and their intensity.
{%- if context.user_info.user_act %}
{%- for activity in context.user_info.user_act %}
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
Overall the user spend {{ activity.intensity | default('little') }} time in this activity.
{% endfor %}
{%- endif %}

{%- if context.user_info.ps_history %}
## Powershell cmd History
The following shows the recent {{ context.user_info.ps_history|length }} Powershell commands executed by the user.
{%- for ps in context.user_info.ps_history %}
- **{{ loop.index }}:** {{ ps }}
{%- endfor %}
{% endif %}

## Git Diffs Log
The following section shows the recent {{ context.user_info.git_diffs|length }} `git diff` code changes, listed as txt files, sorted from recent to oldest.
{% if context.user_info.git_diffs %}
{% for git_diff in context.user_info.git_diffs %}
### Change {{ loop.index }}
- **File Path:** {{ git_diff.file_path }}
- **Lines Changed (Start/End):** Old: {{ git_diff.start_ends[0] }}, New: {{ git_diff.start_ends[1] }}
#### Change Content:
```txt
{{ git_diff.content }}
```
{% endfor %}
{% else %}
No git diffs found.
{% endif %}
