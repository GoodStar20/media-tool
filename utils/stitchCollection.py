
import os
import sys
import shutil
import random
import json
import glob
from pprint import pprint
import log

logger = log. get_logger("pablo")

sys.path.append(os.path.abspath('../'))

def generateCollectionFile(path, output_nft_dir):
    # generate dictionary for export
    collection_dictionary = {}

    # for ./*.json in output dir read and add to collection dict
    files = glob.glob(os.path.join(output_nft_dir, '*.json'))
    files = sorted(files)

    logger.info('Found {0} json files:'.format(len(files)))

    for x, y in enumerate(files):
        logger.info("ITEM {0}:{1}".format(x, y))


    for filename in files:

        with open(filename, encoding='unicode-escape', mode='r') as currentFile:

            logger.info('reading file: {0}'.format(filename))

            data=currentFile.read().replace('\n', '')
            data = json.loads(data)
            basename = os.path.basename(filename).replace('.json', '')
            collection_dictionary[basename] = data



    # Serializing json
    return json.dumps(collection_dictionary, indent = 4)



if __name__ == "__main__":

    print("Stitching Collection File")

    if len(sys.argv) != 3:
        logger.error('Must supply 2 arguments, e.g. "stitchCollection.py <DIRECTORY> collection.json"')
        sys.exit(1)

    path = sys.argv[1]
    collection_filename = os.path.join(path, sys.argv[2])

    output_nft_dir = path

    logger.info('Creating collection file: {0} in output dir {1}'.format(collection_filename, path))

    json_string = generateCollectionFile(path, output_nft_dir)

    with open(collection_filename, 'w') as f:
        f.write(json_string)

    logger.info('Collection file {0} written successfully'.format(collection_filename))

