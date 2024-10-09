# OS System Infos

The following section shows the USER's Operating System and System Information.

## Operating System
**OS**: {{ context.os_infos.os }}

## CPU
**CPU Name**: {{ context.os_infos.cpu_type.Name }}
**CPU Load**: {{ context.os_infos.cpu_type.LoadPercentage }}%

## Memory
**RAM Size**: {{ context.os_infos.ram_size }}

## Storage
**Disk Size**: {{ context.os_infos.disk_size }}

## GPU(s)
{% for key, value in context.os_infos.gpu_info.items() %}
**{{ key }}**: {{ value }}
{% endfor %}

## Network
**Hostname**: {{ context.os_infos.hostname }}
**IP Address**: {{ context.os_infos.ip_address }}

## User
**Username**: {{ context.os_infos.username }}

## PowerShell Version Information
**PS Version**: {{ context.os_infos.psversiontable.PSVersion }}
**PS Edition**: {{ context.os_infos.psversiontable.PSEdition }}
**Platform**: {{ context.os_infos.psversiontable.Platform }}
**PS Remoting Protocol Version**: {{ context.os_infos.psversiontable.PSRemotingProtocolVersion }}
**Serialization Version**: {{ context.os_infos.psversiontable.SerializationVersion }}
**WSMan Stack Version**: {{ context.os_infos.psversiontable.WSManStackVersion }}
