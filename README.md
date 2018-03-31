macfind
=======

A vendor name finder from the mac address.

## Usage

    usage: macfind.py [-h] [-z] [-x] [-v]
                      MAC_ADDR or update [MAC_ADDR or update ...]
    
    It finds a company name by the mac address specified.
    If you specify 'update' as the mac_addr, it is going to update
    the OUI database taken from the IEEE server below:

        http://standards-oui.ieee.org/oui/oui.txt
    
    positional arguments:
      MAC_ADDR or update  MAC address or update.
    
    optional arguments:
      -h, --help          show this help message and exit
      -z                  specify online mode. it's going to ask
                          http://api.macvendors.com/.
      -x                  specify reverse lookup. the -z option is ignored.
      -v                  enable verbose mode.

Thanks to MACVENDORS.COM for providing nice REST API.
