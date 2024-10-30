## System Information
The following section shows performance relevant System runtime Information.
It can be used to identify potential bottlenecks and to optimize the performance of the system.
### Operating System
**OS**: {{ context.sys_info.os }}

### CPU
**CPU Name**: {{ context.sys_info.cpu_type.Name }}
**CPU Load**: {{ context.sys_info.cpu_type.LoadPercentage }}%

### Memory
**RAM Size**: {{ context.sys_info.ram_size }}

### Storage
**Disk Size**: {{ context.sys_info.disk_size }}

### GPU(s)
{%- for key, value in context.sys_info.gpu_info.items() %}
**{{ key }}**: {{ value }}
{%- endfor %}

### Network
**Hostname**: {{ context.sys_info.hostname }}
**IP Address**: {{ context.sys_info.ip_address }}

### User
**Username**: {{ context.sys_info.username }}

### PowerShell Version Information
**PS Version**: {{ context.sys_info.psversiontable.PSVersion }}
**PS Edition**: {{ context.sys_info.psversiontable.PSEdition }}
