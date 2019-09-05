Country-level GeoNames geocoder
===============================

**ggeocode** is a simple geocoding library uses free GeoNames database to construct a fast and simple local Python geocoding library. It is designed to geocode only to the **country** level, and considers only administrative subdivisions and populated places, not other features like parks, rivers, etc. It does not distinguish languages, and will attempt to geocode names in all languages available.

# Installation

    $ cd ggeocode
    $ python setup.py install

# Usage

## One-time preparation

Before using ggeocode, you need to compile your local JSON mapping file from the GeoNames database.

1. Download the GeoNames ``allCountries.zip`` data file from http://download.geonames.org/export/dump/allCountries.zip
2. Unzip the archive to get the file ``allCountries.txt`` (approximately 1.5 GB)
3. Compile a local JSON mapping table using the command below.

Compilation command:

    $ python -m ggeocode.parser allCountries.txt > name-map.lines.json

## Command-line use

You need to have compiled your local JSON mapping file first.  Assuming your mapping file is in ``name-map.lines.json``, you can geocode a collection of names using the following syntax:

    $ python -m ggeocode.coder name-map.lines.json Name1 "Name 2" [... NameN]

The program will print a list of JSON objects (one per line) with the results of geocoding each string, including zero or more ISO3 country codes most-likely associated with each name (the order is not significant). Note that startup time for the command-line version is slow, because it has to read a large database first: the more names you geocode with a single command, the less the overhead will matter.

### Command-line example

This command-line example attempts to geocode four strings:

    $ python -m ggeocode.coder name-map.lines.json Ottawa "Ottawa KS" Winnipeg Belleville "Belleville, ON"
    {"text": "Ottawa", "status": true, "score": 3, "countries": ["CAN"]}
    {"text": "Ottawa KS", "status": true, "score": 5, "countries": ["USA"]}
    {"text": "Winnipeg", "status": true, "score": 3, "countries": ["CAN"]}
    {"text": "Belleville", "status": true, "score": 2, "countries": ["CAN", "FRA", "USA"]}
    {"text": "Belleville, ON", "status": true, "score": 5, "countries": ["CAN"]}
    $

Note that the only result for "Ottawa" is "CAN" (Canada); because Ottawa is the national capital, ggeocode gives it more prominance, and assumes that's what the user means; however, "Ottawa KS" (Ottawa, Kansas) correctly resolves to "USA". "Winnipeg" is not a national capital, but it's the only city with that name. There are several "Belleville"'s in Canada, France, and the USA, and all get returned as possible results; however, when you specify "Belleville, ON" (Belleville, Ontario), you correctly get only Canada as a result.

## Library usage

To use ggeocode as a library, compile your JSON mapping file as explained in "One-time preparation" above, and include the following at the top of your Python module:

    from ggeocode import coder

You will need to load the JSON mapping file once, and it may take from several seconds to over a minute, depending on your environment:

    coder.load_name_map("name-map.lines.json") # substitute the actual filename

After that, use the _coder.geocode_ function to geocode each string. The return value will be a JSON object, including the following properties:

*text* - the original text being geocoded
*status* - true for success, or false if no matches were found
*score* - the score of the best matches (higher is better; scores below 3 are unreliable)
*countries* - a list of zero or more matching ISO3 country codes (with the best score)

### Library examples

    result = coder.code("Ottawa") # ['CAN']
    result = coder.code("Ottawa KS") # ['USA']
    result = coder.code("Winnipeg") # ['CAN']
    result = coder.code("Belleville") # ['CAN', 'FRA', 'USA']
    result = coder.code("Belleville, ON") # ['CAN']

See "Command-line examples," above, for an explanation of the results.

# License

Started by David Megginson, 2019-09.

This Python module is in the Public Domain. See UNLICENSE.md for details.
