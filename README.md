# Golden Popcorn Scraper

## Installation
I recommend setting up a virtualenv in which to run the script.

To install the dependencies: ```pip install -r requirements.txt```

You will also need to install firefox for selenium. If you're attempting to use this package
over an ssh connection, you'll likely need to execute ```export DISPLAY=:0``` to avoid "display not
found errors." After completing the configuration, you must rename the the example configuration
file to be ```config.yaml```.

## Running the script
It's easy -- ```python gps.py```
