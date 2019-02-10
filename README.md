macfind
=======

A vendor name finder from the mac address.

Thanks to MACVENDORS.COM for providing nice REST API.

## Requirement

- Python2 or 3
- requests

## How to use

You can use MAC address of which the hex strings are separated by
either '-', '.', ':' and ' '.

For example,

    macfind ac-bc-32-ba-1c-9f
    macfind ac.bc.32.ba.1c.9f
    macfind acbc.32ba.1c9f
    macfind ac:bc:32:ba:1c:9f
    macfind 'ac bc 32 ba 1c 9f'

Additionally, it supports taking a MAC address from an IPv6 full address.

## Usage

    usage: macfind.py [-h] [-z] STRING [STRING ...]
    
        It finds a company name by the mac address specified.
        
        If you specify 'update', it is going to update the OUI database taken
        from the IEEE server.  It takes a few minutes.
    
        Usage example:
            macfind (mac_addr)
            macfind -z (mac_addr)
            macfind update
    
    positional arguments:
      STRING      MAC address or update.
    
    optional arguments:
      -h, --help  show this help message and exit
      -z          specify online mode. it's going to ask
                  http://api.macvendors.com/.

