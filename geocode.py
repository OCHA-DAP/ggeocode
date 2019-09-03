import json, logging, re, sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("geocode")

WS_PATTERN = re.compile('\W+')

def normalise (s):
    """ Generate a normalised version of a string """
    return WS_PATTERN.sub(' ', s).lower().strip()

name_map = {}

loaded_count = 0
with open('working/name-country-map.lines.json') as input:
    logger.info("Loading database...")
    for line in input:
        entry = json.loads(line)
        name_map[entry[0]] = entry[1]
        loaded_count += 1
        if (loaded_count % 1000000) == 0:
            logger.info("Read %d entries", loaded_count)

for name in sys.argv[1:]:
    entries = name_map.get(normalise(name))
    max_score = 0
    max_keys = []
    if entries:
        for key in entries:
            if entries[key] > max_score:
                max_keys = [key]
                max_score = entries[key]
            elif entries[key] == max_score:
                max_keys.append(key)
        print(name, max_keys)
    else:
        print("No entries for", name)
