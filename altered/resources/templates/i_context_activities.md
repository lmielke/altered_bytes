# Activity Log
The following section shows the USERs last {{ context.activities|length }} activites and the last {{ context.activities|length*2 }} PS commands performed by the USER. Although this simple log only provides statistical information, it can improve your context understanding.
{%- for activity in context.activities %}
## Activity {{ loop.index }}
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
# Powershell cmd History
{%- for ps in context.ps_history %}
- **{{ loop.index }}:** {{ ps }}
{%- endfor %}
{% endif %}

# Git Diffs Log
The following section shows the last {{ git_diffs|length }} code changes. The changes are listed in the order in which they appeared in the `git diff`, showing the file path, lines changed, and the specific content of each modification.

{% for git_diff in context.git_diffs %}
## Change {{ loop.index }}
- **File Path:** {{ git_diff.file_path }}
- **Lines Changed (Start/End):** Old: {{ git_diff.start_ends[0] }}, New: {{ git_diff.start_ends[1] }}
### Change Content:
```diff
{{ git_diff.content }}
{% endfor %}