## Package Info
The following section shows used Package information.

{%   if context.package_info.digraph %}
### Package Import Structure starting at {{ context.package_info.work_file_name }}
```dot
{{ context.package_info.digraph }}
```
{%- endif %}

### Installed Package Libraries
```{{ context.package_info.req_format }}
{{ context.package_info.pg_requirements }}
```

### Package File Structure
```text
{{ context.package_info.tree }}
```

{% if context.package_info.selected_files %}
### Top {{ context.package_info.selected_files|length }} Selected Package Files
{% for file in context.package_info.selected_files %}
{% if loop.index == 1 %}
#### File {{ loop.index }}:  {{ file.file_path }} <- Current Work File
{% else %}
#### File {{ loop.index }}:  {{ file.file_path }}
{% endif %}
```{{ file.file_type }}

{{ file.file_content }}

```
{% endfor %}
{% endif %}
