from PIL import Image

import os
import sys
import log
import shutil
import random
import json
import glob
from pprint import pprint
from utils import upload

logger = log.get_logger("pablo")

OUTPUT_DIR = 'output'
fileupload = upload.FileUpload()

from dotenv import load_dotenv
load_dotenv()

API_URL = os.environ.get('API_URL')
S3_URL = os.environ.get('AWS_BUCKET_NAME')

class Pablo:
    def __init__(self, config):

        self.config=config
        self.collection = config['collection']['name']
        self.image_folder = config['collection']['input_dir']
        self.accessory_list = config['traits']['accessories']
        self.background_list = config['traits']['backgrounds']
        self.outputs_folder = config["collection"]["output_dir"] +  config["collection"]["sname"] + '/'

        self.force_accessory = []
        self.accessory_versions = {}

        #  if self.collection.lower() == 'tarantino':
            #  self.image_folder = 'Quentin Tarantino/'
            #  self.accessory_list = ['Eyes', 'Hat']
            #  self.background_list = ['Circular Gradient', 'Solid Color', 'Tarantino Films']
        #  elif self.collection.lower() == 'unicorn':
            #  self.image_folder = 'Project Unicorn V1/'
            #  self.accessory_list = ['Horn', 'Mark']
            #  self.background_list = ['Circular Gradient', 'Solid Color', 'Fine Art']
        #  elif self.collection.lower() == 'unicorn2':
            #  self.image_folder = 'Project Unicorn V2/'
            #  self.accessory_list = ['Eyes', 'Horn', 'Hoodie', 'Head', 'Mane', 'Logo']
            #  self.background_list = ['Solid Color', 'Tech Unicorns']

        #self.base_image_folder = self.image_folder + 'base_images/'
        #self.cropped_base_folder = self.image_folder + 'base_images_cropped/'
        self.accessory_image_folder = self.image_folder + 'accessory_images/'
        self.style_image_folder = self.image_folder + 'style_images/'
        self.background_folder = self.image_folder + 'background_images/'


        self.styleRarities = {'Improvisation %': '', \
                              'Style %': '', \
                              '2nd Style': .1, \
                              '2nd Style %': '', \
                              '3rd Style': .1, \
                              '3rd Style %': '' }

        self.accessory_traits = {'Eyes': {'Rarity': .95, \
                                           'Supersedes': ['Horn'], \
                                           'Subsedes': ['Hat'], \
                                           'Collection': ['Tarantino', 'Unicorn2']}, \
                                 'Hat': {'Rarity': .75, \
                                         'Supersedes': ['Horn', 'Eyes'], \
                                         'Subsedes': [], \
                                         'Collection': ['Tarantino']}, \

                                 'Horn': {'Rarity': .95, \
                                          'Supersedes': ['Head'], \
                                          'Subsedes': ['Mane', 'Eyes', 'Hat'], \
                                          'Collection': ['Unicorn', 'Unicorn2']}, \
                                 'Mark': {'Rarity': .75, \
                                          'Supersedes': [], \
                                          'Subsedes': [], \
                                          'Collection': ['Unicorn']}, \

                                 'Hoodie': {'Rarity': 1, \
                                            'Supersedes': [], \
                                            'Subsedes': ['Head', 'Eyes', 'Horn', 'Hat', 'Mane'], \
                                            'Collection': ['Unicorn2']}, \

                                 'Head': {'Rarity': 1, \
                                          'Supersedes': ['Hoodie'], \
                                          'Subsedes': ['Mane', 'Eyes', 'Hat', 'Horn', 'Mark'], \
                                          'Collection': ['Unicorn2']}, \
                                 'Mane': {'Rarity': 1, \
                                          'Supersedes': ['Hoodie', 'Head', 'Horn'], \
                                          'Subsedes': ['Eyes', 'Hat', 'Mark'], \
                                          'Collection': ['Unicorn2']}, \

                                 'Logo': {'Rarity': 1, \
                                          'Supersedes': ['Hoodie'], \
                                          'Subsedes': ['Head'], \
                                          'Collection': ['Unicorn2']}}

        self.background_traits = {'Circular Gradient': {'Rarity': .3, \
                                                        'Collection': ['Unicorn', 'Tarantino']}, \
                                  'Fine Art': {'Rarity': .3, \
                                                'Collection': ['Unicorn', 'Unicorn2']}, \
                                  'Solid Color': {'Rarity': .1, \
                                                  'Collection': ['all']}, \

                                  'Tarantino Films': {'Rarity': .2, \
                                                      'Collection': ['Tarantino']}, \
                                  'Tech Unicorns': {'Rarity': .9, \
                                                    'Collection': ['Unicorn2']}}
        self.NFTs_Master = {}

    def generateBatch(self, quantity):

        for num in range(0, quantity):
            self.generate(num + 1)

    def generate(self, image_number=''):
        self.traits = {}

        # Background
        self.setBackground()

        # Accessories
        sorted_accessory_list = []

        for accessory in self.accessory_list:
            accessory_position = len(sorted_accessory_list)

            if len(self.accessory_traits[accessory]['Subsedes']) > 0:

                for sorted_accessory in sorted_accessory_list:

                    if sorted_accessory in self.accessory_traits[accessory]['Subsedes']:
                        if sorted_accessory_list.index(sorted_accessory) < accessory_position:
                            accessory_position = sorted_accessory_list.index(sorted_accessory)
            sorted_accessory_list.insert(accessory_position, accessory)


        unique = False
        while not(unique):
            for accessory in sorted_accessory_list:
                #if self.collection in self.accessory_traits[accessory]['Collection']:
                self.chooseAccessory(self.new_image, accessory)
            unique = True
            for NFT_number in self.NFTs_Master:
                if self.NFTs_Master[NFT_number]['Traits'] == self.traits:
                    unique = False

        print('\n\n-------- Unicorn #' + str(image_number) + ' Traits--------')


        #  imagepath = API_URL + '/metadata/collections/'+ self.config["collection"]["sname"] + '/' + str(image_number)

        #  https://metadata-ecoverse.s3.amazonaws.com/unicorns/3.png",

        imagepath = 'https://' + S3_URL + '.s3.amazonaws.com/' + self.config["collection"]["sname"] + '/' + str(image_number) + '.png'

        trait_file_lines = self.initializeTraitFile(
            'Unicorn #' + str(image_number),
            self.config['collection']['description'],
            imagepath
        )

        count = 0
        last_trait = False

        for trait in self.traits:
            count += 1
            print('    ' + str(count) + '. ' + trait + ': ' + self.traits[trait])
            if count == len(self.traits):
                last_trait = True
            else:
                last_trait = False
            trait_file_lines = self.addTraitToFile(trait_file_lines, trait, self.traits[trait], last_trait)

        print('\n')
        #self.new_image.show()
        self.NFTs_Master[image_number] = {}
        self.NFTs_Master[image_number]['Traits'] = self.traits
        #now = GCT.getDateTimeString()
        #self.new_image.save(self.outputs_folder + 'NewImage' + str(image_number) + '_' + now + '.png', 'PNG')
        self.new_image.save(self.outputs_folder + str(image_number) + '.png', 'PNG')
        self.finalizeTraitFile(trait_file_lines, image_number)

    def finalizeTraitFile(self, trait_file_lines, image_number):
        trait_file = open(self.outputs_folder + str(image_number) + '.json', 'w')
        # trait_file = open(self.outputs_folder + str(image_number) + '.json', 'w')
        for line in trait_file_lines:
            trait_file = self.addLine(trait_file, line)
        trait_file.close()

    def initializeTraitFile(self, name, description, image='None'):
        trait_file_lines = []
        trait_file_lines.append('{')
        trait_file_lines.append('    "name": "' + name + '",')
        trait_file_lines.append('    "description": "' + description + '",')
        trait_file_lines.append('    "image": "' + image + '",')
        trait_file_lines.append('    "attributes": [')
        return(trait_file_lines)

    def addTraitToFile(self, trait_file_lines, trait_type, value, last_trait=False):
        value = value.split('.')[0]
        trait_file_lines.append('        {')
        trait_file_lines.append('              "trait_type": "' + trait_type + '",')
        trait_file_lines.append('              "value": "' + value + '"')
        if last_trait:
            trait_file_lines.append('        }]}')
        else:
            trait_file_lines.append('        },')
        return(trait_file_lines)


    def addLine(self, trait_file, line):
        trait_file.write(line + '\n')
        return(trait_file)


    def chooseAccessory(self, image, accessory_type):
        accessory_rarity = self.accessory_traits[accessory_type]['Rarity']

        if accessory_type in self.force_accessory:
            if self.accessory_versions.get(accessory_type):
                accessory_folder = self.accessory_image_folder + '_' + accessory_type + ' ' + self.accessory_versions.get(accessory_type)
            else:
                accessory_folder = self.accessory_image_folder + '_' + accessory_type
        else:
            if self.accessory_versions.get(accessory_type):
                accessory_folder = self.accessory_image_folder + accessory_type + ' ' + self.accessory_versions.get(accessory_type)
            else:
                accessory_folder = self.accessory_image_folder + accessory_type

        file_choice = 'None'
        random_float = random.random()

        if random_float < accessory_rarity:
            image_list = []

            for file_name in os.listdir(accessory_folder):

                if '.jpg' in file_name or '.png' in file_name:
                    image_list.append(file_name)

            if len(image_list) <= 0:
                print(accessory_type + ' folder is EMPTY!')
            else:
                random_integer = random.randint(0, len(image_list) - 1)
                file_choice = image_list[random_integer]
                accessory_image = Image.open(accessory_folder + '/' + file_choice)
                self.new_image.paste(accessory_image, (0, 0), accessory_image)

        self.traits[accessory_type] = file_choice
        #self.new_image.save(self.outputs_folder + accessory_type + '.png', 'PNG')
        return(self.new_image)

    def setBackground(self):

        random_float = random.random()
        background_image = None

        rarity_total = 0
        for background in self.background_list:
            if not(background_image):
                #if self.collection in self.background_traits[background]['Collection'] or 'all' in self.background_traits[background]['Collection']:
                rarity_total += self.background_traits[background]['Rarity']
                if random_float <= rarity_total:
                    image_list = []
                    for file_name in os.listdir(self.background_folder + background + '/'):
                        if '.jpg' in file_name or '.png' in file_name:
                            image_list.append(file_name)
                    if len(image_list) <= 0:
                        print('Background folder is EMPTY!')
                    else:
                        random_integer = random.randint(0, len(image_list) - 1)
                        file_choice = image_list[random_integer]
                        background_image = Image.open(self.background_folder + background + '/' + file_choice)
        if not(background_image):
            background_image = Image.open(self.background_folder + 'Blank Image.png')
            file_choice = 'None'
        self.traits['Background'] = file_choice
        self.new_image = background_image
        #self.new_image.save(self.outputs_folder + 'bg.png', 'PNG')
        return(self.new_image)


def writeCollectionFile(output_dir, config):

    collection_filename = os.path.join(os.getcwd(), output_dir, 'collection.json')

    logger.info('creating collection file: {0} in output dir {1}'.format(collection_filename, path))

    # generate dictionary for export
    collection_dictionary = {}

    ## for ./*.json in output dir read and add to collection dict
    for filename in glob.glob(os.path.join(output_dir, '*.json')):
        with open(filename, encoding='utf-8', mode='r') as currentFile:

            data=currentFile.read().replace('\n', '')
            data = json.loads(data)
            basename = os.path.basename(filename).replace('.json', '')
            collection_dictionary[basename] = data

    # Serializing json
    json_string = json.dumps(collection_dictionary, indent = 4)

    with open(collection_filename, 'w') as f:
        f.write(json_string)

    logger.info('Collection file {0} written successfully'.format(collection_filename))


def writeContractFile(output_dir, config):

    output_filename = os.path.join(os.getcwd(), output_dir, 'contract.json')

    out_dict = {}

    banner_img = 'https://'+ S3_URL +'.s3.amazonaws.com/'+ config["collection"]["sname"] + '/banner.png'

    out_dict["name"] = config["collection"]["name"]
    out_dict["description"] = config["collection"]["description"]

    out_dict["image"] = banner_img

    # No need for these tags if they're all the same
    #  out_dict["image"] = config["collection"]["image"]
    #  out_dict["image_url"] = config["collection"]["image_url"]
    #  out_dict["banner_image_url"] = config["collection"]["banner_image_url"]
    out_dict["seller_fee_basis_points"] = config["collection"]["seller_fee_basis_points"]
    out_dict["fee_recipient"] = config["collection"]["fee_recipient"]


    json_string = json.dumps(out_dict, indent = 4)

    with open(output_filename, 'w') as f:
        f.write(json_string)
    return

def writeSettingsFile(output_dir, config):

    output_filename = os.path.join(os.getcwd(), output_dir, 'settings.json')
    out_dict = config["settings"]

    collection_url = API_URL + '/metadata/contracts/'+ config["collection"]["sname"] + '/'
    base_api_url = API_URL + '/metadata/collections/'+ config["collection"]["sname"] + '/'


    out_dict["collection_url"] = collection_url
    out_dict["base_api_url"] = base_api_url


    # write file out
    json_string = json.dumps(out_dict, indent = 4)
    with open(output_filename, 'w') as f:
        f.write(json_string)
    return



if __name__ == '__main__':

    logger.info('Starting Pablo the pfp generator.')

    if len(sys.argv) != 2:
        logger.error('must supply 2 arguments, e.g. "pablo.py unicorn.json"')
        sys.exit(1)

    config = json.load(open(sys.argv[1]))

    output_dir = config["collection"]["output_dir"]
    output_collection_dir = config["collection"]["output_dir"] + config["collection"]["sname"] + '/'

    # Path
    path = os.path.join(os.getcwd(), output_collection_dir)
    output_path = os.path.join(os.getcwd(), output_dir)

    # wipe and remake the output directory
    try:
        shutil.rmtree(output_collection_dir)
        logger.info("Cleared the output directory.")
    except OSError as e:
        logger.error("Error: %s : %s" % (path, e.strerror))

    try:
        os.makedirs(path, exist_ok = True)
        os.makedirs(output_path, exist_ok = True)
        logger.info("Directory '%s' created successfully" % path)
    except OSError as error:
        logger.error("Directory '%s' can not be created" % path)


    num_nfts = int(config.get("collection").get("number"))

    # Set a rng seed to make the generation reproducible
    random.seed(config['collection']['seed'])

    Pablo = Pablo(config)
    Pablo.generateBatch(num_nfts)

    # TODO generate image banner after run?
    collection_dir = config['collection']['output_dir'] + config['collection']['sname']

    # generate contract metadata
    writeCollectionFile(collection_dir, config)
    writeContractFile(collection_dir, config)
    writeSettingsFile(collection_dir, config)

    #  fileupload.upload_files()
    logger.info("Generation Complete.")
