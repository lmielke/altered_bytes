## Package Info
{%-   if not context.package_info.is_package %}
The selected folder contains no packgage information or it is not a package.
{%-   else %}
The following section shows information about the package in the cwd.
- Project Name: `{{ context.package_info.pr_name }}`
- Package Name: `{{ context.package_info.pg_name }}`
- Project Dir: `{{ context.package_info.project_dir }}`

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

{%   endif %}

{% if context.package_info.tree %}
### Directory File Structure
```text
{{ context.package_info.tree }}
```
{%   endif %}

{% if context.package_info.selected_files %}
### Top {{ context.package_info.selected_files|length }} Selected Package Files
Here are some files of interest. They may be relevant for solving the problem.
{% for file in context.package_info.selected_files %}
{% if loop.index == 1 %}
#### File {{ loop.index }}:  {{ file.file_path }}
The user specifically attached this file because it may be relevant for solving the problem.
{% elif loop.index == 2 %}
{% else %}
#### File {{ loop.index }}:  {{ file.file_path }}
{% endif %}
```{{ file.file_type }}

{{ file.file_content }}

```
{% endfor %}
{% endif %}
