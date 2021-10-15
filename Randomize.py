import os
import random
import sys

goa_type = 1  # Represents the GoA type, 1 for new rando, 2 for DARKNESS mode, 3 for Relaxed Mermaid mode
to_be_replaced = []
random_list = []
current_dir = ""


def roll_seed():
    global to_be_replaced, random_list
    # Shuffle tracks
    random_list = music_list.copy()
    random.shuffle(random_list)
    # Ensure Field & Fight tracks are grouped together
    to_be_replaced = []  # Fields to be deleted in arif
    # Exit here if DARKNESS or Relaxed Mermaid is selected
    if goa_type in [2, 3]:
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

# These are the biggest tracks in the game and cannot be assigned to any world music and some GoA custom music
problematic_tracks = [
    0x6B,  # Ursula's Revenge
    0x3D,  # Darkness of the Unknown II
    0x9C,  # Guardando nel buio (KH I)
    0xB9,  # The 13th Dilemma
    0x57,  # Disappeared
    0x3B,  # A Fight to the Death
    0x43,  # Rage Awakened
    0x6A  # Under the Sea
]

# Get music ID
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    current_dir = f"{os.path.dirname(sys.executable)}"
elif __file__:
    current_dir = f"{os.path.dirname(__file__)}"

files = os.listdir(f"{current_dir}/bgm")
music_list = []
for file in files:
    music_list.append(int(file[5:8]))

print("Select the desired option:")
print("1) Generate new music rando")
print("2) DARKNESS MODE")
print("3) Relaxed Mermaid Mode")
print("4) Exit\n")
while True:
    try:
        goa_type = int(input("Input number: "))
        if goa_type in [1, 2, 3]:
            break
        if goa_type == 4:
            sys.exit(0)
    except ValueError:
        pass
    print("Input not valid.\n")

valid = False
while not valid:
    valid = roll_seed()

# Write the mod.yml
f = open(f"{current_dir}/mod.yml", 'w')
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
        # Replace EVERY TRACK IN THE GAME with Isn't it Lovely?
        new = 0x81
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
        # If Relaxed Mermaid, always replace
        elif (goa_type == 2 and x in fight and x != 0x3E) or (goa_type == 3 and x in fight) or (x in to_be_replaced):
            data[i + j] = fight[x]
f = open(f"{current_dir}/arif.bin", 'wb')
f.write(data)
f.close()
