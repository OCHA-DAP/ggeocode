""" Compile a name map from GeoNames data

Usage:

    python parse_geonames.py allCountries.txt > name-map.lines.json

The geocode.py module uses the output.

Started 2019-09 by David Megginson
This code is in the public domain
"""

import fileinput, json, logging, re, sys
import ggeocode.iso3
from ggeocode.coder import normalise


#
# Global variables
#

logger = logging.getLogger("parse-geonames")

keys = (
    "geonameid",
    "name",
    "asciiname",
    "alternatenames",
    "latitude",
    "longitude",
    "feature_class",
    "feature_code",
    "country_code",
    "cc2",
    "admin1_code",
    "admin2_code",
    "admin3_code",
    "admin4_code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification_date",
)
""" Column keys for the tab-separated GeoNames data """


FEATURE_WEIGHTS = {
    # countries and country-like things
    'PCL': 3,
    'PCLD': 3,
    'PCLF': 3,
    'PCLI': 3,
    'PCLIX': 3,
    'PCLS': 3,
    # administrative subdivisions
    'ADM1': 2,
    # national or admin1 capital
    'PPLC': 2,
    'PPLA': 2,
}
""" GeoNames feature names that get extra weight """


#
# Main entry point
#

def read_geonames (input=None):
    """ Parse the GeoNames allCountries.txt file into a Python dict.
    Warning: the dict will be large (hundreds of megabytes)
    @param input: the input stream (defaults to standard input)
    @returns: a dict of geo names and country-weight maps
    @see write_geonames
    """
    if input is None:
        input = sys.stdin
        
    mapping_table = {} # the mapping table we'll return
    
    country_codes_seen = set() # keep track of the ones we've seen, for progress reporting

    # Iterate through the tab-separated input text, row by row, and extract the info
    for row in input:

        # Make a dict out of the fields
        record = dict(zip(keys, row.split("\t")))

        # Look up the ISO3 country code
        country_code = ggeocode.iso3.MAP.get(record['country_code'])
        
        if country_code is not None:
            # Extract the alternate names as well as the normative ones
            # (Note: these will be in multiple languages)
            alternate_names = record['alternatenames'].split(",")
            names = [record['name']] + alternate_names

            # We're interested only in administrative subdivisions and populated places
            # (Not parks, rivers, etc)
            if record['feature_class'] in ('A', 'P',):

                # Keep the user updated, since this runs for a while
                if country_code not in country_codes_seen:
                    logger.info("Processing %s", country_code)
                    country_codes_seen.add(country_code)

                # Add all the names to the mapping table with this country code
                for name in names:
                    if name:

                        # lower case and normalise all non-word characters into a single space
                        name = normalise(name)

                        # create the country weight table, if it doesn't already exist
                        if not mapping_table.get(name):
                            mapping_table[name] = dict()

                        # raise to the appropriate weight for the feature type
                        weight = FEATURE_WEIGHTS.get(record['feature_code'], 1) # default weight is 1

                        # add a prominance bonus if there are lots of translations
                        if len(alternate_names) > 5:
                            weight += 1

                        # save the new weight if it's not lower than the existing one
                        current_weight = mapping_table[name].get(country_code, 1)
                        if current_weight <= weight:
                            mapping_table[name][country_code] = weight

    return mapping_table


def write_geonames (mapping_table, output=None):
    """ Write the mapping table out to line-oriented JSON.
    @param mapping_table: the mapping table to write
    @param output: the output stream (defaults to standard output)
    @see read_geonames
    """
    
    if output is None:
        output = sys.stdout
        
    entries_written = 0

    for entry in mapping_table.items():
        json.dump(list(entry), output)
        print('', file=output)
        entries_written += 1
        if (entries_written % 1000000) == 0:
            logger.info("Wrote %d entries", entries_written)


#
# Command-line script entry point: read all files named as arguments and write to standard output
#

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 2:
        logging.error("Usage: python %s allCountries.txt > name-map.lines.json")
        sys.exit(2)

    with open(sys.argv[1]) as input:
        mapping_table = read_geonames(input)
        
    write_geonames(mapping_table, sys.stdout)

# end
