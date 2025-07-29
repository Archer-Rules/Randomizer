#!/usr/bin/env python
# coding: utf-8

import sys
import os
import random
import time
import pandas as pd
from pathlib import Path
import math

#Ah good old statistics. Helps calculate item drop rates in shops and probably in other places later we'll see. Good formula to have saved.
def per_item_chance(total_chance, item_count):
    return 1 - math.pow(1 - total_chance, 1 / item_count)

####################################################################
#          Path Finder for Files once I EXE Bundle                 #
####################################################################
def resource_path(relative_path):

    
    
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running from script
        return os.path.join(os.path.abspath("."), relative_path)



############################################################################################
#The shop randomizer option. Made to be a yes or no choice as I'll add more features later.#
############################################################################################
def shopRandomizer():
    #Basic Questions
    shopType = input("What kind of shopkeeper is it? (a = Armor, r = Ranged Weapons, m = Melee Weapons, h = Healing, j = Junk): ")
    itemString = input("How many items does the shopkeeper have: ")
    itemCount = int(itemString)


    ########################
    #      Output List     #
    ########################
    shopList = []


    ################################################
    #          Statistics Purgatory Booooo         #
    ################################################

    #Handling Party Levels and adjusting chances of items for such.
    tempLevel = input("Please enter the level of the party: ")
    partyLevel = int(tempLevel)
        # Percentage to Probability Conversions woo 
        #2% higher chance of each rarity per party level, it's the math that mathed the most sense to me
    target_uncommon = 0.50 + partyLevel * 0.02
    target_rare = 0.25 + partyLevel * 0.02
    target_extremely_rare = 0.10 + partyLevel * 0.01
    target_exotic = 0.05 + partyLevel * 0.01
        # Setting caps so at higher levels you don't only see uncommons or something
    target_uncommon = min(target_uncommon, 0.95)
    target_rare = min(target_rare, 0.95)
    target_extremely_rare = min(target_extremely_rare, 0.95)
    target_exotic = min(target_exotic, 0.95)
        # God I hate statistics
    p_uncommon = per_item_chance(target_uncommon, itemCount)
    p_rare = per_item_chance(target_rare, itemCount)
    p_extremely_rare = per_item_chance(target_extremely_rare, itemCount)
    p_exotic = per_item_chance(target_exotic, itemCount)
        #Converting back to 1000 because I honestly don't know how well python handles decimals
    exoticThreshold = int(p_exotic * 1000)
    extremelyRareThreshold = exoticThreshold + int(p_extremely_rare * 1000)
    rareThreshold = extremelyRareThreshold + int(p_rare * 1000)
    uncommonThreshold = rareThreshold + int(p_uncommon * 1000)

        #Did I say how much I hate statistics god this took me like 2 hours to figure out I hate statistics



##########################################################
#          Switch Cases For Different Vendors            #
#      DONE: R/E/M/A                    TODO: H/J        #
##########################################################
    match shopType:

############################################################
#     The Ranged Weapon Section WooHooooooooooooo          #
############################################################
        case 'r':

            local_path = Path('ranged_list.csv')

            if local_path.is_file():
                df = pd.read_csv(local_path, header=None,
                 names=["Weapon Name", "Weight", "Value", "Requirement", "Range",
                        "Type", "Damage", "AP Cost", "RoF", "Mag Size",
                        "Ammo Type", "Rarity", "Tier", "Page #"])
            else:
                
                csv_path = resource_path('ranged_list.csv')
                df = pd.read_csv(csv_path, header=None,
                 names=["Weapon Name", "Weight", "Value", "Requirement", "Range",
                        "Type", "Damage", "AP Cost", "RoF", "Mag Size",
                        "Ammo Type", "Rarity", "Tier", "Page #"])

            # Print headers once
            print(f"{'Weapon Name':<30} {'Weight':<8} {'Value':<8} {'Requirement':<12} {'Range':<8} {'Type':<8} {'Damage':<12} {'AP Cost':<8} {'RoF':<14} {'Mag Size':<8} {'Ammo Type':<18} {'Rarity':<15} {'Tier':<6} {'Page #':<8}")
            print("-" * 170)

            #Organizes list of ranged weapons by Rarity dynamically for any adjustments in the future
            commonList = df[df['Rarity'] == 'Common']
            uncommonList = df[df['Rarity'] == 'Uncommon']
            rareList = df[df['Rarity'] == 'Rare']
            extremelyRareList = df[df['Rarity'] == 'Extremely Rare']
            exoticList = df[df['Rarity'] == 'Exotic']

             #The actual item generator: Appends random sample, does not currently prevent dupe items, but should be easy enough to fix if it becomes a problem
             #The pool for items should be large enough though
            for i in range(itemCount):
                item = random.randint(1, 1000)

                if item <= exoticThreshold:
                    random_row = exoticList.sample(1)
                elif item <= extremelyRareThreshold:
                    random_row = extremelyRareList.sample(1)
                elif item <= rareThreshold:
                    random_row = rareList.sample(1)
                elif item <= uncommonThreshold:
                    random_row = uncommonList.sample(1)
                else:
                    random_row = commonList.sample(1)

                row = random_row.iloc[0]
                shopList.append(row)

                # Print each row with standardized column widths
                print(f"{str(row['Weapon Name']):<30} {str(row['Weight']):<8} {str(row['Value']):<8} {str(row['Requirement']):<12} {str(row['Range']):<8} {str(row['Type']):<8} {str(row['Damage']):<12} {str(row['AP Cost']):<8} {str(row['RoF']):<14} {str(row['Mag Size']):<8} {str(row['Ammo Type']):<18} {str(row['Rarity']):<15} {str(row['Tier']):<6} {str(row['Page #']):<8}")

############################################################
#     The Melee Weapon Section WooHooooooooooooo           #
############################################################

        case 'm':
            #Reads CSV, could probably be cleaner but I'm just gonna do it on a case by case basis.
            csv_path = resource_path('melee_list.csv')

            df = pd.read_csv(csv_path, header=None,
                 names=["Weapon Name", "Weight", "Value", "Requirement", "Range",
                        "Type", "Damage", "AP Cost", "RoF", "Mag Size",
                        "Ammo Type", "Rarity", "Tier", "Page #"])

            # Print headers once
            print(f"{'Weapon Name':<30} {'Weight':<8} {'Value':<8} {'Range (Yards)':<14} {'Damage':<12} {'AP Cost':<8} {'Rarity':<15} {'Tier':<6} {'Page #':<8}")
            print("-" * 125)

            #Organizes list of ranged weapons by Rarity dynamically for any adjustments in the future
            commonList = df[df['Rarity'] == 'Common']
            uncommonList = df[df['Rarity'] == 'Uncommon']
            rareList = df[df['Rarity'] == 'Rare']
            extremelyRareList = df[df['Rarity'] == 'Extremely Rare']
            exoticList = df[df['Rarity'] == 'Exotic']

            #The actual item generator: Appends random sample, does not currently prevent dupe items, but should be easy enough to fix if it becomes a problem
            #The pool for items should be large enough though
            for i in range(itemCount):
                item = random.randint(1, 1000)

                if item <= exoticThreshold:
                    random_row = exoticList.sample(1)
                elif item <= extremelyRareThreshold:
                    random_row = extremelyRareList.sample(1)
                elif item <= rareThreshold:
                    random_row = rareList.sample(1)
                elif item <= uncommonThreshold:
                    random_row = uncommonList.sample(1)
                else:
                    random_row = commonList.sample(1)

                row = random_row.iloc[0]
                shopList.append(row)

                # Print each row with standardized column widths
                print(f"{str(row['Weapon Name']):<30} {str(row['Weight']):<8} {str(row['Value']):<8} {str(row['Range (Yards)']):<14} {str(row['Damage']):<12} {str(row['AP Cost']):<8} {str(row['Rarity']):<15} {str(row['Tier']):<6} {str(row['Page #']):<8}")

#############################################################
#               The Explosives Weapon Section               #
#############################################################

        case 'e':
             #Reads CSV, could probably be cleaner but I'm just gonna do it on a case by case basis.
            csv_path = resource_path('explosive_list.csv')

            df = pd.read_csv(csv_path, header=None,
                 names=["Weapon Name", "Weight", "Value", "Requirement", "Range",
                        "Type", "Damage", "AP Cost", "RoF", "Mag Size",
                        "Ammo Type", "Rarity", "Tier", "Page #"])

            # Print headers once
            print(f"{'Weapon Name':<30} {'Weight':<8} {'Value':<8} {'Range (Yards)':<14} {'Damage':<12} {'AP Cost':<8} {'Rarity':<15} {'Tier':<6} {'Page #':<8}")
            print("-" * 120)


                        #Organizes list of ranged weapons by Rarity dynamically for any adjustments in the future
            commonList = df[df['Rarity'] == 'Common']
            uncommonList = df[df['Rarity'] == 'Uncommon']
            rareList = df[df['Rarity'] == 'Rare']
            extremelyRareList = df[df['Rarity'] == 'Extremely Rare']
            exoticList = df[df['Rarity'] == 'Exotic']


            #The actual item generator: Appends random sample, does not currently prevent dupe items, but should be easy enough to fix if it becomes a problem
            #The pool for items should be large enough though
            for i in range(itemCount):
                item = random.randint(1, 1000)

                if item <= exoticThreshold:
                    random_row = exoticList.sample(1)
                elif item <= extremelyRareThreshold:
                    random_row = extremelyRareList.sample(1)
                elif item <= rareThreshold:
                    random_row = rareList.sample(1)
                elif item <= uncommonThreshold:
                    random_row = uncommonList.sample(1)
                else:
                    random_row = commonList.sample(1)

                row = random_row.iloc[0]
                shopList.append(row)



                print(f"{str(row['Weapon Name']):<30} {str(row['Weight']):<8} {str(row['Value']):<8} {str(row['Range (Yards)']):<14} {str(row['Damage']):<12} {str(row['AP Cost']):<8} {str(row['Rarity']):<15} {str(row['AoE']):<4} {str(row['Tier']):<6} {str(row['Page #']):<8}")

#############################################################
#                      The Armor Section                    #
#############################################################

        case 'a':
            #Reads CSV, could probably be cleaner but I'm just gonna do it on a case by case basis.
            csv_path = resource_path('armor_list.csv')

            df = pd.read_csv(csv_path, header=None,
                 names=["Armor Name", "DT", "Weight", "Value", "Faction",
                        "Effect", "Rarity", "Type", "Page #"])

            # Print headers once
            print(f"{'Armor Name':<40} {'DT':<4} {'Weight':<8} {'Value':<8} {'Faction':<12} {'Effect':<35} {'Rarity':<15} {'Type':<20} {'Page #':<6}")
            print("-" * 120)

            #Organizes list of ranged weapons by Rarity dynamically for any adjustments in the future
            commonList = df[df['Rarity'] == 'Common']
            uncommonList = df[df['Rarity'] == 'Uncommon']
            rareList = df[df['Rarity'] == 'Rare']
            extremelyRareList = df[df['Rarity'] == 'Extremely Rare']
            exoticList = df[df['Rarity'] == 'Exotic']


            #The actual item generator: Appends random sample, does not currently prevent dupe items, but should be easy enough to fix if it becomes a problem
            #The pool for items should be large enough though
            for i in range(itemCount):
                item = random.randint(1, 1000)

                if item <= exoticThreshold:
                    random_row = exoticList.sample(1)
                elif item <= extremelyRareThreshold:
                    random_row = extremelyRareList.sample(1)
                elif item <= rareThreshold:
                    random_row = rareList.sample(1)
                elif item <= uncommonThreshold:
                    random_row = uncommonList.sample(1)
                else:
                    random_row = commonList.sample(1)

                row = random_row.iloc[0]
                shopList.append(row)



                print(f"{str(row['Armor Name']):<40} {str(row['DT']):<4} {str(row['Weight']):<8} {str(row['Value']):<8} {str(row['Faction']):<12} {str(row['Effect']):<35} {str(row['Rarity']):<15} {str(row['Type']):<20} {str(row['Page #']):<6}")



    #Debug Message
    print(f"\nShop contains {len(shopList)} items total.")


################################################################################################################################################################################
################################################################################################################################################################################
# Beginning of Main Here. Current Features: Shop Randomizer (Ranged, Melee)               Upcoming: Shop Randomizer (Explosives, Medicine, Junk), Perk/Trait/Character Creator #
################################################################################################################################################################################
################################################################################################################################################################################

print("""⠀
      ⠀⠀   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀ ⢀⣠⡆⠀⠀⢤⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠖⠉⠘⡇⠀⠀⡸⠙⢧⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡠⢤⡴⠋⣀⡤⠶⠛⠛⠛⠿⣥⡀⠀⠻⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡜⠁⡰⢋⣔⠜⠃⠀⢀⠀⠂⠤⡀⠠⣙⢦⡴⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠀⡞⠍⠙⢦⡀⠀⠀⠀⠁⠢⡀⠙⡄⠘⣟⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡅⡼⢸⠀⠀⠀⠱⠀⣀⠰⣄⠀⠈⢦⡈⠦⡈⠳⠶⢶⡎
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠁⠸⡀⢇⠀⢀⠀⢀⣉⣀⠉⠑⢠⠘⡦⣈⢩⡶⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠀⢠⣷⡈⠸⣾⡲⠉⠁⢉⣽⣦⠀⠠⣯⢻⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀⢸⠀⡑⠀⠛⢃⠀⠀⢮⠁⣹⡆⠀⢿⣾⠃⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣀⡤⠤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠸⡄⡞⠀⠇⠀⢼⣧⠢⡀⢮⣾⣿⠇⠀⠠⡙⢲⠀⠀⠀
⠀⠀⠀⢀⡔⢟⡩⠐⠂⠀⠉⠑⠪⣗⢄⠀⠀⠀⠀⠀⢹⠂⠀⠈⢆⠀⠀⠀⠀⠉⠉⠁⠀⠘⣗⠴⠋⠀⠀⠀    War. War never Changes.
⠀⠀⣴⠏⡰⠋⠀⢀⠀⠀⠀⠀⠠⢀⡱⣥⣠⠤⣤⣤⠋⢠⠀⠀⠀⢣⠀⠀⡏⠒⠒⠒⠒⠊⠉⠀⠀⠀⠀⠀
⠀⣸⠃⡜⠀⠀⠰⠁⠀⣠⠶⠐⠒⠒⡷⣿⠀⠀⠀⢈⢢⡈⠣⣀⡀⡜⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢰⡇⡸⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⣼⣌⣿⠀⠀⠀⠈⠒⠤⢩⠋⠁⠀⠈⠑⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    Deadtree Shop/Eventually NPC Randomizer V0.0
⠈⠀⠃⠀⠀⠀⢠⠀⢱⠀⠀⠀⢰⡏⠃⠉⡀⠀⠀⠀⠀⢀⢨⠢⠤⠄⠀⢀⣭⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⠀⠀⠀⠀⠈⢆⠸⡄⠀⠀⠈⡇⠀⠀⢳⡀⠀⠀⠀⠀⠵⠲⠮⡒⣧⣞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ASCII art came from emojicombos.com (First one I could find)
⢸⡀⡄⠀⠀⠀⠀⠈⠆⢹⠀⣠⠖⠇⠀⣰⠃⢈⡗⢲⠇⠀⢸⠖⢺⡉⠀⠀⠈⢢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠘⡥⢧⠀⠀⠀⠀⠀⡀⣸⣰⠋⠀⠀⡼⠁⢀⡞⠀⡞⠀⠀⢸⠀⠀⠉⠓⡦⠀⠘⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠫⣢⢀⣀⢀⢜⡴⢻⠇⠀⠀⣰⠃⠀⢸⠃⢰⠇⠀⠀⠀⠀⠀⠀⣼⠁⠀⠀⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀    For any questions or suggestions or issues, shoot me a dm on discord (archer_rules)
⡔⣴⠉⡍⠛⠀⢿⠁⠀⡟⠀⠀⠀⡟⠀⠀⢸⠀⣾⠀⠀⠀⢸⡀⠀⠀⢹⡀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠹⣫⡤⠵⠀⣸⣆⠅⢸⠁⠀⠀⠀⡇⠀⠀⠸⡄⣿⠀⠀⠀⠘⡇⠀⠀⠀⠳⢤⡜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    Please press "Enter" to continue to the rest of the randomizer!
⠀⠓⠦⠖⠊⠁⠉⠀⢼⠀⠀⠀⠀⢛⠤⠤⠦⠇⣿⠀⠀⠀⠀⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠛⠋⠀⠀⠀⠀⠹⠤⢤⣀⣠⣬⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ """)

input("")
print("Welcome to the Randomizer!\n")
print("Please DO NOT enter silly inputs I don't want to code fallbacks for them.\n")
print()
print("Loading Data now... Please hold")
print()

#Gives user time to read the "dont be silly" line
#Also gives the chance in the future to release the funny patch of "Reduced load times" and just lower the number lmao
time.sleep(3)

randomizerCheck = input("Would you like a shop randomizer? (y/n): ")

if (randomizerCheck == 'y'):
    shopRandomizer()


npcBuilderCheck = input("Would you like a randomized NPC? (NOT IMPLEMENTED YET): ")

if (npcBuilderCheck == 'y'):
    print ("I said it wasn't implemented nerd")



print("Script has finished Running!")
input("Press Enter to exit...")

#Debug Message
print("DEBUG MESSAGE: Gaming")





