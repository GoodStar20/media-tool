import os
import sys


class FixTraits:
    def __init__(self):
        test = True
        if test:
            self.destination_folder = '________ALL _FIXED_ Traits Mixed TEST'
            self.starting_folder = '________ALL Traits Mixed TEST' 
        else:
            self.destination_folder = '____All _FIXED_ Traits - Renamed'
            self.starting_folder = '____All Final Traits - Renamed'

    def fix_traits(self):
        count = 0
        self.no_logo_count = 0
        self.day_zero_count = 0
        for file_name in os.listdir(self.starting_folder):
            self.append_legendary = False
            self.append_class = False
            count += 1
            if count <= 2000 or count == 276:
                file = open(self.starting_folder + '/' + file_name, 'r')
                line_list = []
                next_line = 'None'
                for line in file:
##                    # add "Class: 2022" trait to hoodies with trait "Edition: Day 0" (275 total)
##                    if 'edition' in line.lower():
##                        next_line = 'Edition Value'
##                    elif next_line == 'Edition Value':
##                        if 'Day 0' in line:
##                            print(line)
##                            self.day_zero_count += 1
##                            self.append_class = True
##                        next_line = 'None'
                    # add "Class: 2022" trait to all hoodies (1111 total)
                    self.day_zero_count += 1
                    self.append_class = True
                    # add "Legendary: Customizable" trait to hoodies without logos (11 total)
                    if 'logo' in line.lower():
                        next_line = 'Logo Value'
                    elif next_line == 'Logo Value':
                        if 'None' in line:
                            print(line)
                            self.no_logo_count += 1
                            self.append_legendary = True
                        next_line = 'None'
                    # detects end of file
                    if '}]}' in line:
                        if self.append_class:
                            line_list = self.addTraitToFile(line_list, 'Class', '2022', not(self.append_legendary))
                        if self.append_legendary:
                            line_list = self.addTraitToFile(line_list, 'Legendary', 'Customizable', True)
                    else:
                        line_list.append(line)
                image_number = file_name.split('.')[0]
                if self.append_legendary:
                    print(image_number)
                self.finalizeTraitFile(line_list, image_number)
                file.close()
        print(self.no_logo_count)
        print(self.day_zero_count)


    def finalizeTraitFile(self, trait_file_lines, image_number):
        trait_file = open(self.destination_folder + '/' + str(image_number) + '.json', 'w')
        for line in trait_file_lines:
            line_title = 'None'
            if '"' in line:
                line_title = line.split('"')[1]
                # fix the number in the name
                if line_title == 'name':
                    line = '    "name": "Unicorn #' + image_number + '",\n'
                # adds a description
                if line_title == 'description':
                    # check if Legendary unicorn
                    legendary_unicorn = False
                    for line in trait_file_lines:
                        if 'Legendary' in line:
                            legendary_unicorn = True
                    if legendary_unicorn:
                        line = '    "description": "Join the Day Zero Project Unicorn Class of 2022 with the purchase of this Legendary Unicorn with the coveted Blank Hoodie trait. Holders of these 11 Legendary tokens can burn 1 to receive 11 new Unicorns minted with their organization’s logo printed on their hoodies. With only 11 available, this Legendary trait provides unique membership to the Day Zero Project Unicorn Class of 2022. #LFG",\n'
                    else:
                        line = '    "description": "Welcome to Project Unicorn: An NFTs for Recognition Production; celebrating the BRIGHTEST MINDS in the room.  Inspired by Tech Unicorns, your Unicorn serves as membership to a first-of-its-kind NFT Crew that gathers to solve real world problems throughout the year.  Project Unicorn is recruiting unknown, struggling artists for our future drops. Join our Discord to learn how to submit your art!  Unique events for Unicorn NFT holders are being planned each month, plus an annual global event for recognizing the most brilliant Unicorns of the year! #WAGMI",\n'
                # find backgrounds with watermark
                elif 'angular math' in line.lower():
                    print(line)
                    print(image_number)
            trait_file = self.addLine(trait_file, line)
        trait_file.close()

    def addLine(self, trait_file, line):
        trait_file.write(line)
        return(trait_file)

    def addTraitToFile(self, trait_file_lines, trait_type, value, last_trait=False):
        value = value.split('.')[0]
        trait_file_lines.append('        },\n')
        trait_file_lines.append('        {\n')
        trait_file_lines.append('              "trait_type": "' + trait_type + '",\n')
        trait_file_lines.append('              "value": "' + value + '"\n')
        if last_trait:
            trait_file_lines.append('        }]}\n')
##        else:
##            trait_file_lines.append('        },\n')
        return(trait_file_lines)



FT = FixTraits()
FT.fix_traits()
