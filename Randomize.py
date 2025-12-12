import os
import random
import shutil
import sys
from glob import glob
from time import sleep

goa_type = 1  # Represents the GoA type, 1 for a new rando, 2 to 6 for meme-y runs
to_be_replaced: list[int] = []
random_bgm_list: list[int] = []
random_wd_list: list[int] = []
current_dir = ""
kh1_mode = False
ffx_mode = False
rando_bgm = True
rando_wd = False
meme_ok = False


def roll_bgm_seed():
    global to_be_replaced, random_bgm_list, music_list
    # If goa_type is 7, we already have our customized random_list, we should not shuffle it again
    if goa_type != 7:
        # Shuffle tracks
        random_bgm_list = music_list.copy()
        random.shuffle(random_bgm_list)
    # Ensure Field & Fight tracks are grouped together
    to_be_replaced = []  # Fields to be deleted in arif
    for fight_old in fight:
        # If fight_old is not in music_list, it means that that world pair is excluded from rando
        # (the bgm files were removed from the corresponding folder), we should skip this iteration entirely.
        # We still keep the field/fight pair in the list to correctly manage arif hack in case of meme option
        if fight_old not in music_list:
            continue

        field_old = fight[fight_old]
        index_field = music_list.index(field_old)
        index_fight = music_list.index(fight_old)
        field_new = random_bgm_list[index_field]
        fight_new = random_bgm_list[index_fight]

        paired = False
        # If it's "Wait... is this a boss fight?" meme option, there's no "pair" because the pool is not a simple
        # permutation and has lots of repetitions - we set all field tracks to be replaced, and
        # we skip directly to the last check
        if goa_type != 7:
            # Find out where the pair is located
            try:
                paired = field[fight_new]
            except:
                try:
                    paired = fight[fight_new]
                except:
                    pass
        if paired:  # Swap the field with the pair tracks
            index_paired = random_bgm_list.index(paired)
            random_bgm_list[index_field], random_bgm_list[index_paired] = paired, field_new
        else:
            # THIS COMMENTED BLOCK BELOW SEEMS TO BE UNNECESSARY IN "GOA ROM EDITION"
            # ---------------------------------------------------------------------------------------
            # STT is out of the pool for now, so I only check for 0x35 (TT) and not 0x77 (STT)
            # Due to how GoA PNACH forces music, TT/STT cannot have an event track
            # if fight_old in [0x35, 0x77]:  # Re-roll seed if trying to set single track to TT/STT
            # if fight_old == 0x35:  # Re-roll seed if trying to set single track to TT
            #     # print("TT/STT is a single track! Rolling new seed...")
            #     print("TT is a single track! Rolling new seed...")
            #     return False
            # ---------------------------------------------------------------------------------------

            # Check if fight_new is one of the problematic tracks
            # if fight_old in [0x77] and fight_new in problematic_tracks:
            #     print(f"[STT] Problematic track found! -> {fight_new}, rolling new seed...")
            #     return False
            # Swap fight with field and flag fight_old to be removed
            # random_list[index_field], random_list[index_fight] = fight_new, field_new
            to_be_replaced.append(field_old)
    # Check for problematic tracks set to GoA custom tracks
    # goa_custom_tracks = [0x72]  # Tension Rising is set to play in Old Mansion forced fights during TT3
    # for old in goa_custom_tracks:
    #     index_old = music_list.index(old)
    #     new = random_list[index_old]
    #     if new in problematic_tracks:
    #         print(f"[GoA Mod custom music] Problematic track found! -> {new}, rolling new seed...")
    #         return False
    # Verify that every KH2 track is randomized
    for bgm_old in music_list:
        # Only check KH2 tracks
        if bgm_old > 299:
            break
        index_old = music_list.index(bgm_old)
        bgm_new = random_bgm_list[index_old]
        if bgm_old == bgm_new:
            print(f"The track number {bgm_old} wasn't randomized, rolling new seed...")
            return False
    return True


def roll_wd_seed():
    global random_wd_list, wd_list
    random_wd_list = wd_list.copy()
    random.shuffle(random_wd_list)
    # Verify that every KH2 soundfont is randomized
    for wd_old in wd_list:
        # Only check KH2 tracks
        if wd_old > 299:
            break
        index_old = wd_list.index(wd_old)
        wd_new = random_wd_list[index_old]
        if wd_old == wd_new:
            print(f"The soundfont number {wd_old} wasn't randomized, rolling new seed...")
            return False
    return True


def yes_no(question):
    while True:
        try:
            answer = input(f"{question} [y/n]: ").lower()
            if answer == "y" or answer == "yes":
                return True
            elif answer == "n" or answer == "no":
                return False
        except ValueError:
            pass
        print("Input not valid.\n")


def copy_all_files(src, dst, filter=""):
    # fetch all files
    for file_name in os.listdir(src):
        if filter in file_name:
            # construct full file path
            source = os.path.join(src, file_name)
            destination = os.path.join(dst, file_name)
            # copy only files
            if os.path.isfile(source):
                shutil.copy(source, destination)


def set_meme(meme_song, exclude=None):
    global random_bgm_list, to_be_replaced
    if exclude is None:
        exclude = []
    for i in range(len(music_list)):
        if music_list[i] in exclude:
            random_bgm_list.append(music_list[i])
        else:
            random_bgm_list.append(meme_song)
            if music_list[i] in field:
                to_be_replaced.append(music_list[i])


# This is yet another implementation needed for "Wait... is this a boss fight?" meme option...
# Because now the random_bgm_list contains duplicates of the same song, and because we are forced to set the WD ID
# in bgm files to fix crashes, we need different copies of the same files, so that for every copy, if it's assigned
# as field track to a world, we can set its WD ID independently of all other copies of the same song applied
# somewhere else. So, we simply need to copy again the songs from kh2/kh1 folders, but following the
# vanilla naming scheme e.g. if both 60 and 61 are mapped to 138, we copy 138 from kh2 to bgm twice, with both names.
# At the end, we set random_bgm_list as an exact copy of music_list, so that all duplicates are removed: this is
# because the files in bgm folder are already randomized, and they are already following the
# vanilla naming scheme, so there's no need to keep track of which are which, we just need to map every song to
# the same vanilla number in mod.yml

# We will use this method for every meme option and, in general, for every option
# that presents repetitions inside random_bgm_list
def fix_bgm_list():
    global random_bgm_list
    for i in range(len(music_list)):
        bgm_old = music_list[i]
        # Stop when all KH2 songs have been assigned
        if bgm_old > 299:
            break
        bgm_new = random_bgm_list[i]
        folder = "kh2"
        if bgm_new in [0xBD, 0xBE]:
            folder = "tr"
        elif bgm_new in range(256, 512):
            folder = "kh1"
        elif bgm_new in range(512, 768):
            folder = "ffx"
        shutil.copy(f"{current_dir}/{folder}/music{str(bgm_new).zfill(3)}.bgm",
                    f"{current_dir}/bgm/music{str(bgm_old).zfill(3)}.bgm")
    random_bgm_list = music_list


# Pair up Field & Fight theme
field = {
    0x32: 0x33,  # Dive into the Heart -Destati- & Fragments of Sorrow
    0x34: 0x35,  # The Afternoon Streets & Working Together
    0x36: 0x37,  # Sacred Moon & Deep Drive
    0x38: 0x39,  # Nights of the Cursed (Unused) & He's a Pirate (Unused)
    0x3C: 0x3E,  # Darkness of the Unknown I & Darkness of the Unknown III
    0x40: 0x41,  # What a Surprise?! & Happy Holidays!
    0x44: 0x45,  # Cavern of Remembrance & Deep Anxiety
    0x64: 0x66,  # The Underworld & What Lies Beneath
    0x65: 0x68,  # Waltz of the Damned & Dance of the Daring
    0x74: 0x70,  # The Home of Dragons & Fields of Honor
    0x76: 0x77,  # Lazy Afternoons & Sinister Sundowns
    0x7A: 0x7B,  # Let's Sing and Dance! I & Let's Sing and Dance! II
    0x7F: 0x80,  # A Day in Agrabah & Arabian Dream
    0x85: 0x86,  # Magical Mystery & Working Together
    0x87: 0x88,  # Space Paranoids & Byte Bashing
    0x8A: 0x8B,  # Shipmeister's Shanty & Gearing Up
    0x90: 0x95,  # This is Halloween & Spooks of Halloween Town
    0x98: 0x99,  # Reviving Hollow Bastion & Scherzo Di Notte
    0x9A: 0x9B,  # Nights of the Cursed & He's a Pirate
    0xBA: 0xBB,  # Adventures in the Savannah & Savannah Pride
    0xBD: 0xBE   # Monochrome Dreams & Old Friends, Old Rivals
}
fight = {}  # Basically reverse of pairs
for i in field:
    fight[field[i]] = i

# KH1 Field & Fight theme
kh1_field = {
    0x17A: 0x17B  # Blast Away Gummi Ship I & Blast Away Gummi Ship II
}

kh1_fight = {}  # Basically reverse of pairs
for i in kh1_field:
    kh1_fight[kh1_field[i]] = i

# These are the biggest tracks in the game and cannot be assigned to STT (last day crash)
# and TR (3rd and 4th mini-windows crash).
# STT and TR are already removed from rando, so this list is here just for reference (and it's also incomplete)
problematic_tracks = [
    0x6B,  # Ursula's Revenge
    0x3D,  # Darkness of the Unknown II
    0x9C,  # Guardando nel buio (KH I)
    0xB9,  # The 13th Dilemma
    0x57,  # Disappeared
    0x3B,  # A Fight to the Death
    0x43,  # Rage Awakened
    0x6A,  # Under the Sea
    0x3F,  # The 13th Reflection
    0x79,  # Desire for All That is Lost
    0x95,  # Spooks of Halloween Town
    0xBC,  # One Winged Angel
    # KH1 songs
    0x1C5,  # Night On Bald Mountain
    # 0x163,  # Disappeared (removed from bgm folder)
    0x1B9,  # Forze Del Male
    # 0x161,  # Disappeared (No Intro) (removed from bgm folder)
    # 0x1C2,  # Guardando Nel Buio (No Intro) (removed from bgm folder)
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

print("--------------------------------------------")
print("       KH2 Music-Rando - By Rikysonic")
print("--------------------------------------------")
print("\nSelect the desired option:")
print("1) Generate new music rando...")
print("2) DARKNESS MODE")
print("3) DARKNESS MODE - KH1 Edition")
print("4) Relaxed Mermaid Mode")
print("5) I Love Traverse Town!")
print("6) In Zanarkand Everywhere You Go")
print("7) Wait... is this a boss fight?")
print("8) Exit\n")
while True:
    try:
        goa_type = int(input("Input number: "))
        if goa_type in range(2, 7):
            break
        if goa_type == 1:
            # Set the rando type
            print("\nSelect the desired option:")
            print("1) Randomized music, vanilla soundfonts")
            print("2) Vanilla music, randomized soundfonts")
            print("3) Randomized music, randomized soundfonts\n")
            descr = "songs"
            while True:
                try:
                    rando_type = int(input("Input number: "))
                    if rando_type == 1:
                        rando_bgm = True
                        rando_wd = False
                        break
                    if rando_type == 2:
                        rando_bgm = False
                        rando_wd = True
                        descr = "soundfonts"
                        break
                    if rando_type == 3:
                        rando_bgm = True
                        rando_wd = True
                        descr = "songs and soundfonts"
                        break
                except ValueError:
                    pass
                print("Input not valid.\n")
            kh1_mode = yes_no(f"Do you want KH1 {descr} in the rando?")
            ffx_mode = yes_no(f"Do you want FFX {descr} in the rando?")
            break
        if goa_type == 7:
            # Adding KH1 songs to bgm folder, because some of them are inside both boss-fight and silly tracklists
            kh1_mode = True
            break
        if goa_type == 8:
            print("\nOk! Bye!")
            sleep(2)
            sys.exit(0)
    except ValueError:
        pass
    print("Input not valid.\n")

# Create bgm folder
if os.path.exists(f"{current_dir}/bgm"):
    shutil.rmtree(f"{current_dir}/bgm")
os.makedirs(f"{current_dir}/bgm")

# Copy all KH2 songs
copy_all_files(f"{current_dir}/kh2", f"{current_dir}/bgm", filter=".bgm")
if rando_wd:
    # If rando_wd, add also KH2 wd files
    copy_all_files(f"{current_dir}/kh2", f"{current_dir}/bgm", filter=".wd")

# Copy all KH1 songs and add the KH1 field/fight pairs to global field/fight dictionary if KH1 was selected
if kh1_mode:
    copy_all_files(f"{current_dir}/kh1", f"{current_dir}/bgm")
    fight.update(kh1_fight)
    field.update(kh1_field)

# Copy all FFX songs and add the FFX field/fight pairs to global field/fight dictionary if FFX was selected
if ffx_mode:
    copy_all_files(f"{current_dir}/ffx", f"{current_dir}/bgm")

music_list: list[int] = []

# If meme, add EVERY KH2 SONG to the pool
if goa_type != 1:
    with open(f"{current_dir}/kh2-bgm-list.txt", "r") as bgm_file:
        music_list = [int(line.strip()) for line in bgm_file]
else:
    # Create music_list
    files = glob(f"{current_dir}/bgm/*.bgm")
    for file in files:
        file = os.path.basename(file)
        music_list.append(int(file[5:8]))

# Get all the wd files in bgm
files = glob(f"{current_dir}/bgm/*.wd")
wd_list = []
for file in files:
    file = os.path.basename(file)
    wd_list.append(int(file[4:8]))

bgm_valid = False
wd_valid = False

# If meme except for "Wait... is this a boss fight?", don't roll a seed
if goa_type != 1 and goa_type != 7:
    bgm_valid = True

# If not rando_bgm, no need to roll a seed
if rando_bgm:
    while not bgm_valid:
        # For the "Wait... is this a boss fight?" meme option, we need to create a custom random_list with following rules:
        # - All boss fight songs must become one of the silly songs
        # - All other songs must become one of the boss fight songs
        # - Roxas boss fight song is forced to Roxas theme
        # - TR is forced to Rowdy Rumble (to prevent 3rd and 4th mini-windows crashes)
        # - STT is forced to Roxas boss theme (to prevent last day crash)
        if goa_type == 7:
            with open(f"{current_dir}/boss-music.txt", "r") as boss_file:
                boss_music_list = [int(line.strip()) for line in boss_file]
            with open(f"{current_dir}/silly-music.txt", "r") as silly_file:
                silly_music_list = [int(line.strip()) for line in silly_file]
            random_bgm_list = []
            for song in music_list:
                random_song = 0
                if song == 0x42:
                    random_song = 0x92
                elif song in [0xBD, 0xBE]:
                    random_song = 0x75
                elif song in [0x76, 0x77]:
                    random_song = 0x42
                elif song in boss_music_list:
                    random_song = random.choice(silly_music_list)
                else:
                    random_song = random.choice(boss_music_list)
                random_bgm_list.append(random_song)
        bgm_valid = roll_bgm_seed()

# If not rando_wd, no need to roll a seed
if rando_wd:
    while not wd_valid:
        wd_valid = roll_wd_seed()

# Write the mod.yml
mod = open(f"{current_dir}/mod.yml", 'w')
mod.write('''title: Music-Rando (now with KH1 and FFX music!)
originalAuthor: Rikysonic (original repo by Num)
game: kh2
description: A Music Randomizer for KH2 (original work by Num). It supports KH2, KH1 and FFX music.\
 Make sure to run Randomizer.exe in openkh/mods/kh2/Rikysonic/Music-Rando to generate a new rando.\
 Big thanks to Necrofitz for working on FFX music and helping a lot on brainstorming and testing critical\
 music combinations. Thanks to CoreySG9 for his beautiful idea of soundfonts rando.
''')
mod.write('assets:\n')

# If not rando_bgm, no need to set bgm files
if rando_bgm:
    # Load the dummy bgm file
    dummy = open(f"{current_dir}/dummy.bgm", 'rb').read()
    dummy = bytearray(dummy)

    for i in range(len(music_list)):
        bgm_old = music_list[i]
        # Stop when all KH2 songs have been assigned
        if bgm_old > 299:
            break
        if goa_type == 2:
            # Replace EVERY TRACK IN THE GAME with The 13th Struggle
            # except DARKNESS OF THE UNKNOWN I (doesn't play in rando) and DARKNESS OF THE UNKNOWN III
            if not meme_ok:
                set_meme(0x97, exclude=[0x3C, 0x3E])
                fix_bgm_list()
                meme_ok = True
            # bgm_new = 0x3E if bgm_old == 0x3E else 0x3C
        elif goa_type == 3:
            # Replace EVERY TRACK IN THE GAME with Night of Fate from KH1
            if not meme_ok:
                # Copy meme song to bgm
                # shutil.copy(f"{current_dir}/kh1/music387.bgm", f"{current_dir}/bgm/music387.bgm")
                shutil.copy(f"{current_dir}/kh1/wave0387.wd", f"{current_dir}/bgm/wave0387.wd")
                wd_list.append(387)
                # Add meme song to every slot in random_bgm_list
                set_meme(0x183)
                fix_bgm_list()
                meme_ok = True
            # bgm_new = 0x183
        elif goa_type == 4:
            # Replace EVERY TRACK IN THE GAME with Isn't it Lovely?
            if not meme_ok:
                set_meme(0x81)
                fix_bgm_list()
                meme_ok = True
            # bgm_new = 0x81
        elif goa_type == 5:
            # Replace EVERY TRACK IN THE GAME with Traverse Town
            if not meme_ok:
                # Copy meme song to bgm
                # shutil.copy(f"{current_dir}/kh1/music360.bgm", f"{current_dir}/bgm/music360.bgm")
                shutil.copy(f"{current_dir}/kh1/wave0360.wd", f"{current_dir}/bgm/wave0360.wd")
                wd_list.append(360)
                set_meme(0x168)
                fix_bgm_list()
                meme_ok = True
            # bgm_new = 0x168
        elif goa_type == 6:
            # Replace EVERY TRACK IN THE GAME with In Zanarkand
            if not meme_ok:
                # Copy meme song to bgm
                # shutil.copy(f"{current_dir}/ffx/music642.bgm", f"{current_dir}/bgm/music642.bgm")
                shutil.copy(f"{current_dir}/ffx/wave0642.wd", f"{current_dir}/bgm/wave0642.wd")
                wd_list.append(642)
                set_meme(0x282)
                fix_bgm_list()
                meme_ok = True
            # bgm_new = 0x282
        elif goa_type == 7:
            if not meme_ok:
                fix_bgm_list()
                meme_ok = True

        if bgm_old in to_be_replaced:
            # This block fixes the impossible assignment of problematic tracks to worlds, caused by forced fights
            # loading both field and fight files regardless of arif hack. In this way, you will always have
            # a real fight bgm file (small or big) + 1kb fake field bgm file in memory, both pointing to the same WD file,
            # ensuring RAM is never overloaded with useless big tracks, preventing crashes.
            # Before this change, if a problematic track was assigned e.g. to Agrabah, entering it on the 1st visit
            # caused an immediate crash, because the big track was being loaded twice in RAM (as both field and fight).
            # Now it will always have 1kb dummy as field + the big track as fight, preventing crashes.

            # Set the field track to a dummy 1kb bgm file, having its WD ID set to the same value as the fight track
            fight_old = field[bgm_old]
            index_fight = music_list.index(fight_old)
            fight_new = random_bgm_list[index_fight]
            data = open(f"{current_dir}/bgm/music{str(fight_new).zfill(3)}.bgm", 'rb').read()
            data = bytearray(data)
            # 7th and 8th byte contain the WD ID for the new randomized fight track, so we set those same values
            # as WD ID for the dummy track - in this way the corresponding WD file is always loaded once in memory
            dummy[6] = data[6]
            dummy[7] = data[7]
            # We now save this modified dummy bgm as the new field track
            open(f"{current_dir}/bgm/music{str(random_bgm_list[i]).zfill(3)}.bgm", "wb").write(dummy)
            bgm_new = random_bgm_list[i]
        else:
            bgm_new = random_bgm_list[i]
        bgm_old = f"bgm/music{str(bgm_old).zfill(3)}.bgm"
        bgm_new = f"bgm/music{str(bgm_new).zfill(3)}.bgm"
        mod.write(f"- name: {bgm_old}\n  method: copy\n  source:\n  - name: {bgm_new}\n")

# Load all the wd files in bgm folder
for i in range(len(wd_list)):
    wd_old = wd_list[i]
    # If not rando_bgm, stop when all KH2 soundfonts have been assigned
    if not rando_bgm and wd_old > 299:
        break
    # We start setting new wd same as old wd - we will update it if rando_wd
    wd_new = wd_old
    # If not rando_wd, no need to hack WD ID inside wd files
    if rando_wd:
        wd_new = random_wd_list[i]
        byte_2 = bytes([wd_old % 256])
        byte_3 = bytes([wd_old // 256])
        with open(f"{current_dir}/bgm/wave{str(wd_new).zfill(4)}.wd", 'r+b') as wd_file:
            wd_file.seek(2)
            wd_file.write(byte_2)
            wd_file.write(byte_3)
    bgm_old = f"bgm/wave{str(wd_old).zfill(4)}.wd"
    bgm_new = f"bgm/wave{str(wd_new).zfill(4)}.wd"
    mod.write(f"- name: {bgm_old}\n  method: copy\n  source:\n  - name: {bgm_new}\n")

# If not rando_bgm, no need to set arif hack
if rando_bgm:
    # Replace the field with the fight track
    mod.write('- name: 03system.bin\n  method: binarc\n  source:\n')
    mod.write('  - name: arif\n    type: list\n    method: copy\n    source:\n')
    mod.write('    - name: arif.bin')
    data = open(f"{current_dir}/arifbackup.bin", 'rb').read()
    data = bytearray(data)
    for i in range(0x64, 0x5865, 0x40):
        for j in range(0, 0x10, 2):
            x = data[i + j]
            if x == 0:
                continue
            # If meme, always replace (because to_be_replaced always contains all field tracks)
            if x in to_be_replaced:
                data[i + j] = field[x]
    arif = open(f"{current_dir}/arif.bin", 'wb')
    arif.write(data)
    arif.close()

mod.close()
print("\nFinished! Enjoy your randomized music!")
print("\nBye!", end="")
sleep(2)
