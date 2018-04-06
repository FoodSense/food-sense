# CHANGELOG

Record of all changes made to the hx711.py and scale.py files.
See README for further details.
See LICENSE for licensing information.

## scale.py

* 4/6/18:

Added dout and pd_sck params to __init__() method.

Added self.weight to __init__() method.

Changed getWeight() method so that it does not return a value. Instead, it'll round that average weight to the closest 0.5 and update self.weight.
