import os
import random
import shutil
import sys
from glob import glob

goa_type = 1  # Represents the GoA type, 1 for a new rando, 2 to 6 for meme-y runs
to_be_replaced = []
random_list = []
current_dir = ""
kh1_mode = False
ffx_mode = False
meme_copied = False


def roll_seed():
    global to_be_replaced, random_list
    # Shuffle tracks
    random_list = music_list.copy()
    random.shuffle(random_list)
    # Ensure Field & Fight tracks are grouped together
    to_be_replaced = []  # Fields to be deleted in arif
    # Exit here if DARKNESS, DARKNESS - KH1 Edition, Relaxed Mermaid, Traverse Town, or In Zanarkand is selected
    if goa_type in range(2, 7):
        return True
    for fight_old in fight:
        field_old = fight[fight_old]
        index_field = music_list.index(field_old)
        index_fight = music_list.index(fight_old)
        field_new = random_list[index_field]
        fight_new = random_list[index_fight]
        paired = False
        # Find out where the pair is located
        try:
            paired = field[fight_new]
        except:
            try:
                paired = fight[fight_new]
            except:
                pass
        if paired:  # Swap the field with the pair tracks
            index_paired = random_list.index(paired)
            random_list[index_field], random_list[index_paired] = paired, field_new
        else:
            # Due to how GoA PNACH forces music, TT/STT cannot have an event track
            if fight_old in [0x35, 0x77]:  # Re-roll seed if trying to set single track to TT/STT
                print("TT/STT is a single track! Rolling new seed...")
                return False
            # Check if fight_new is one of the problematic tracks
            if fight_new in problematic_tracks:
                print(f"[World music] Problematic track found! -> {fight_new}, rolling new seed...")
                return False
            # Swap fight with field and flag fight_old to be removed
            random_list[index_field], random_list[index_fight] = fight_new, field_new
            to_be_replaced.append(fight_old)
    # Check for problematic tracks set to GoA custom tracks
    goa_custom_tracks = [0x72]  # Tension Rising is set to play in Old Mansion forced fights during TT3
    for old in goa_custom_tracks:
        index_old = music_list.index(old)
        new = random_list[index_old]
        if new in problematic_tracks:
            print(f"[GoA Mod custom music] Problematic track found! -> {new}, rolling new seed...")
            return False
    return True


def yes_no(question):
    while True:
        try:
            answer = input(f"{question} [y/n]: ")
            if answer == "y" or answer == "yes":
                return True
            elif answer == "n" or answer == "no":
                return False
        except ValueError:
            pass
        print("Input not valid.\n")


def copy_all_files(src, dst):
    # fetch all files
    for file_name in os.listdir(src):
        # construct full file path
        source = os.path.join(src, file_name)
        destination = os.path.join(dst, file_name)
        # copy only files
        if os.path.isfile(source):
            shutil.copy(source, destination)


# Pair up Field & Fight theme
field = {
    0x32: 0x33,  # Dive into the Heart -Destati- & Fragments of Sorrow
    0x34: 0x35,  # The Afternoon Streets & Working Together
    0x36: 0x37,  # Sacred Moon & Deep Drive
    0x3C: 0x3E,  # Darkness of the Unknown I & Darkness of the Unknown III
    0x40: 0x41,  # What a Surprise?! & Happy Holidays!
    0x44: 0x45,  # Cavern of Remembrance & Deep Anxiety
    0x64: 0x66,  # The Underworld & What Lies Beneath
    0x65: 0x68,  # Waltz of the Damned & Dance of the Daring
    0x74: 0x70,  # The Home of Dragons & Fields of Honor
    0x76: 0x77,  # Lazy Afternoons & Sinister Sundowns
    # 0x7A: 0x7B,  # Let's Sing and Dance! I & Let's Sing and Dance! II
    0x7F: 0x80,  # A Day in Agrabah & Arabian Dream
    0x85: 0x86,  # Magical Mystery & Working Together
    0x87: 0x88,  # Space Paranoids & Byte Bashing
    0x8A: 0x8B,  # Shipmeister's Shanty & Gearing Up
    0x90: 0x95,  # This is Halloween & Spooks of Halloween Town
    0x98: 0x99,  # Reviving Hollow Bastion & Scherzo Di Notte
    0x9A: 0x9B,  # Nights of the Cursed & He's a Pirate
    0xBA: 0xBB,  # Adventures in the Savannah & Savannah Pride
    0xBD: 0xBE  # Monochrome Dreams & Old Friends, Old Rivals
}
fight = {}  # Basically reverse of pairs
for i in field:
    fight[field[i]] = i

# KH1 Field & Fight theme
kh1_field = {
    0x17A: 0x17B,  # Blast Away Gummi Ship I & Blast Away Gummi Ship II
}

kh1_fight = {}  # Basically reverse of pairs
for i in kh1_field:
    kh1_fight[kh1_field[i]] = i

# These are the biggest tracks in the game and cannot be assigned to any world music and some GoA custom music
problematic_tracks = [
    0x6B,  # Ursula's Revenge
    0x3D,  # Darkness of the Unknown II
    0x9C,  # Guardando nel buio (KH I)
    0xB9,  # The 13th Dilemma
    0x57,  # Disappeared
    0x3B,  # A Fight to the Death
    0x43,  # Rage Awakened
    0x6A,  # Under the Sea
    # KH1 songs
    0x1C5,  # Night On Bald Mountain
    # 0x163,  # Disappeared (removed from bgm folder)
    0x1B9,  # Forze Del Male
    0x161,  # Disappeared (No Intro)
    0x1C2,  # Guardando Nel Buio (No Intro)
    # FFX Songs
    0x2B5,  # Assault
    0x232,  # Decisive Battle
    0x2B0,  # Aeon Battle
    0x21B,  # Blitz Off
    0x22A,  # Seymour Battle
    0x291,  # Challenge
    0x281  # The Splendid Performance
]

# Get music ID
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    current_dir = f"{os.path.dirname(sys.executable)}"
elif __file__:
    current_dir = f"{os.path.dirname(__file__)}"

print("Select the desired option:")
print("1) Generate new music rando...")
print("2) DARKNESS MODE")
print("3) DARKNESS MODE - KH1 Edition")
print("4) Relaxed Mermaid Mode")
print("5) I Love Traverse Town!")
print("6) In Zanarkand Everywhere You Go")
print("7) Exit\n")
while True:
    try:
        goa_type = int(input("Input number: "))
        if goa_type in range(2, 7):
            break
        if goa_type == 1:
            kh1_mode = yes_no("Do you want KH1 songs in the rando?")
            ffx_mode = yes_no("Do you want FFX songs in the rando?")
            break
        elif goa_type == 7:
            print("Exited!")
            sys.exit(0)
    except ValueError:
        pass
    print("Input not valid.\n")

# Create bgm folder
if os.path.exists("bgm"):
    shutil.rmtree("bgm")
os.makedirs("bgm")

# Copy all KH2 songs
copy_all_files(f"{current_dir}/kh2", f"{current_dir}/bgm")

# Copy all KH1 songs and add the KH1 field/fight pairs to global field/fight dictionary if KH1 was selected
if kh1_mode:
    copy_all_files(f"{current_dir}/kh1", f"{current_dir}/bgm")
    fight.update(kh1_fight)
    field.update(kh1_field)

# Copy all FFX songs and add the FFX field/fight pairs to global field/fight dictionary if FFX was selected
if ffx_mode:
    copy_all_files(f"{current_dir}/ffx", f"{current_dir}/bgm")

files = glob(f"{current_dir}/bgm/*.bgm")
music_list = []
for file in files:
    file = os.path.basename(file)
    music_list.append(int(file[5:8]))

# Get all the wd files in bgm
files = glob(f"{current_dir}/bgm/*.wd")
wd_list = []
for file in files:
    wd_list.append(os.path.basename(file))

valid = False
while not valid:
    valid = roll_seed()

# Write the mod.yml
f = open(f"{current_dir}/mod.yml", 'w')
f.write('''title: Music-Rando (now with KH1 and FFX music!)
originalAuthor: Rikysonic (original repo by Num), big thanks to Necrofitz for working on FFX music and helping a lot on\
 brainstorming and testing critical music combinations
game: kh2
description: A Music Randomizer for KH2. It supports KH2, KH1 and FFX music. Make sure to run Randomizer.exe in openkh/\
mods/Rikysonic/Music-Rando to generate a new rando.
''')
f.write('assets:\n')
for i in range(len(music_list)):
    old = music_list[i]
    if goa_type == 2:
        # Replace EVERY TRACK IN THE GAME with DARKNESS OF THE UNKNOWN I except DARKNESS OF THE UNKNOWN III
        if old == 0x3E:
            new = 0x3E
        else:
            new = 0x3C
    elif goa_type == 3:
        # Copy meme song to bgm
        if not meme_copied:
            shutil.copy(f"{current_dir}/kh1/music387.bgm", f"{current_dir}/bgm/music387.bgm")
            music_list.append(387)
            shutil.copy(f"{current_dir}/kh1/wave0387.wd", f"{current_dir}/bgm/wave0387.wd")
            wd_list.append("wave0387.wd")
            meme_copied = True
        # Replace EVERY TRACK IN THE GAME with Night of Fate from KH1
        new = 0x183
    elif goa_type == 4:
        # Replace EVERY TRACK IN THE GAME with Isn't it Lovely?
        new = 0x81
    elif goa_type == 5:
        # Copy meme song to bgm
        if not meme_copied:
            shutil.copy(f"{current_dir}/kh1/music360.bgm", f"{current_dir}/bgm/music360.bgm")
            music_list.append(360)
            shutil.copy(f"{current_dir}/kh1/wave0360.wd", f"{current_dir}/bgm/wave0360.wd")
            wd_list.append("wave0360.wd")
            meme_copied = True
        # Replace EVERY TRACK IN THE GAME with Traverse Town
        new = 0x168
    elif goa_type == 6:
        # Copy meme song to bgm
        if not meme_copied:
            shutil.copy(f"{current_dir}/ffx/music642.bgm", f"{current_dir}/bgm/music642.bgm")
            music_list.append(642)
            shutil.copy(f"{current_dir}/ffx/wave0642.wd", f"{current_dir}/bgm/wave0642.wd")
            wd_list.append("wave0642.wd")
            meme_copied = True
        # Replace EVERY TRACK IN THE GAME with In Zanarkand
        new = 0x282
    elif old in to_be_replaced:
        # Set the fight track to be a copy of the corresponding new field track
        field_old = fight[old]
        index_field = music_list.index(field_old)
        new = random_list[index_field]
    else:
        new = random_list[i]
    old = 'bgm/music' + str(old).zfill(3) + '.bgm'
    new = 'bgm/music' + str(new).zfill(3) + '.bgm'
    f.write('- name: ' + old + '\n  method: copy\n  source:\n  - name: ' + new + '\n')

# Load all the wd files in bgm folder
for wd in wd_list:
    old = f'bgm/{wd}'
    new = f'bgm/{wd}'
    f.write('- name: ' + old + '\n  method: copy\n  source:\n  - name: ' + new + '\n')

# Replace the fight with the field track
f.write('- name: 03system.bin\n  method: binarc\n  source:\n')
f.write('  - name: arif\n    type: list\n    method: copy\n    source:\n')
f.write('    - name: arif.bin')
f.close()
data = open(f"{current_dir}/arifbackup.bin", 'rb').read()
data = bytearray(data)
for i in range(0x64, 0x5865, 0x40):
    for j in range(0, 0x10, 2):
        x = data[i + j]
        if x == 0:
            continue
        # If DARKNESS, replace every fight occurrence with the field except the Final Fight
        # If Relaxed Mermaid, DARKNESS - KH1 Edition or Traverse Town, always replace
        elif (goa_type == 2 and x in fight and x != 0x3E) or (goa_type in range(3, 10) and x in fight) or \
                (x in to_be_replaced):
            data[i + j] = fight[x]
f = open(f"{current_dir}/arif.bin", 'wb')
f.write(data)
f.close()
print("\nFinished! Enjoy your randomized music!")
