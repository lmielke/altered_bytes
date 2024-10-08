# Activity Log
The following section shows the last {{ context.activities|length }} activites and the last {{ context.activities|length*2 }} PS commands the user performed. Although this only provides limitd statistical infos, looking at these can help the LLM to better understand the surronding context of the problem.
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
# PS History
{%- for ps in context.ps_history %}
- **{{ loop.index }}:** {{ ps }}
{%- endfor %}
{% endif %}
