{{ prompt_summary }}
{%- if prompt_summary %}
# 1. Prompt Summary
## Original Question/Problem Statement
{{ prompt_summary.question }}

## Original Objective
{{ prompt_summary.objective }}
{%- endif %}
