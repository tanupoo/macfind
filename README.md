macfind
=======

A vendor name finder from the mac address.

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

## Usage

    usage: macfind.py [-h] [-z] MAC_ADDR or update [MAC_ADDR or update ...]
    
    It finds a company name by the mac address specified. if you specify 'update'
    as the mac_addr, it is going to update the OUI database taken from the IEEE
    server.
    
    positional arguments:
      MAC_ADDR or update  MAC address or update.
    
    optional arguments:
      -h, --help          show this help message and exit
      -z                  specify online mode. it's going to ask
                          http://api.macvendors.com/.

Thanks to MACVENDORS.COM for providing nice REST API.
