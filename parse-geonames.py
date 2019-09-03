""" Compile a name map from GeoNames data

Usage:

    python parse_geonames.py allCountries.txt > name-map.lines.json

The geocode.py module uses the output.

Started 2019-09 by David Megginson
This code is in the public domain
"""

import fileinput, json, logging, re, sys
import iso3

logging.basicConfig(level=logging.INFO)
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


WS_PATTERN = re.compile('\W+')

def normalise (s):
    """ Generate a normalised version of a string """
    return WS_PATTERN.sub(' ', s).lower().strip()

def parse_geonames (input, output):
    mapping_table = dict()
    country_codes_seen = set()

    for row in input:
        record = dict(zip(keys, row.split("\t")))
        country_code = iso3.MAP.get(record['country_code'])
        if country_code is not None:
            alternate_names = record['alternatenames'].split(",")
            names = [record['name']] + alternate_names
            if record['feature_class'] in ('A', 'P',):
                if country_code not in country_codes_seen:
                    logger.info("Processing %s", country_code)
                    country_codes_seen.add(country_code)
                for name in names:
                    if name:
                        name = normalise(name)

                        # create the map of country codes, if it doesn't already exist
                        if not mapping_table.get(name):
                            mapping_table[name] = dict()

                        # raise to the appropriate weight for the feature type
                        weight = FEATURE_WEIGHTS.get(record['feature_code'], 1)
                        if len(alternate_names) > 5:
                            weight += 1 # prominance bonus for many translations
                        current_weight = mapping_table[name].get(country_code)
                        if current_weight is None or current_weight < weight:
                            mapping_table[name][country_code] = weight

    entries_written = 0
    for entry in mapping_table.items():
        json.dump(list(entry), output)
        print('', file=output)
        entries_written += 1
        if (entries_written % 1000000) == 0:
            logger.info("Wrote %d entries", entries_written)


if __name__ == "__main__":
    parse_geonames(fileinput.input(), sys.stdout)
