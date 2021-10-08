import os
import random

# import sys

# goa_type = 1  # Represents the GoA type, 1 for original PNACH, 2 for modded PNACH + Lua for Music-Rando fix
goa_type = 1  # Represents the GoA type, 1 for original PNACH, 2 for DARKNESS
to_be_replaced = []
random_list = []


def roll_seed():
    global to_be_replaced, random_list
    # Shuffle tracks
    random_list = music_list.copy()
    random.shuffle(random_list)
    # Ensure Field & Fight tracks are grouped together
    to_be_replaced = []  # Fields to be deleted in arif
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
            if goa_type == 1:  # If classic rando, then TT/STT cannot be in to_be_replaced
                if fight_old in [0x35, 0x77]:  # Re-roll seed if trying to set single track to TT/STT
                    print("TT/STT is a single track! Rolling new seed...")
                    return False
            # Swap fight with field and flag fight_old to be removed
            random_list[index_field], random_list[index_fight] = fight_new, field_new
            to_be_replaced.append(fight_old)
    # Exit here if DARKNESS is selected
    if goa_type == 2:
        return True
    # Validate shuffled list
    print(to_be_replaced)
    for old in to_be_replaced:
        # new = 0x92  # Roxas theme is 2nd lowest filesize
        # Link both the field and the fight track to the same bgm file
        field_old = fight[old]
        index_field = music_list.index(field_old)
        new = random_list[index_field]
        if new in problematic_songs:
            print(f"Problematic song found! -> {new}, rolling new seed...")
            # new = 0x92  # Roxas theme is 2nd lowest filesize
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

problematic_songs = [
    0x6B,
    0x3D,
    0x9C,
    0xB9,
    0x57,
    0x3B,
    0x43,
    0x6A
]

# Get music ID
current_dir = os.path.realpath(__file__).replace(os.path.basename(__file__), '')
# current_dir = os.path.dirname(sys.executable) + "\\"
files = os.listdir(current_dir + 'bgm')
music_list = []
for file in files:
    music_list.append(int(file[5:8]))

print("Select the desired option:")
print("1) Generate new music rando")
print("2) Generate DARKNESS")
print("3) Exit\n")
while True:
    goa_type = int(input("Input number: "))
    if goa_type in [1, 2]:
        break
    if goa_type == 3:
        exit(0)
    print("Input not valid.\n")

valid = False
while not valid:
    valid = roll_seed()

# Write the mod.yml
f = open(current_dir + 'mod.yml', 'w')
f.write('assets:\n')
for i in range(len(music_list)):
    old = music_list[i]
    if goa_type == 2:
        # Replace EVERY SONG IN THE GAME with DARKNESS OF THE UNKNOWN I except DARKNESS OF THE UNKNOWN III
        if old == 0x3E:
            new = 0x3E
        else:
            new = 0x3C
    elif old in to_be_replaced:
        # new = 0x92  # Roxas theme is 2nd lowest filesize
        # Link both the field and the fight track to the same bgm file
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
data = open(current_dir + 'arifbackup.bin', 'rb').read()
data = bytearray(data)
for i in range(0x64, 0x5865, 0x40):
    for j in range(0, 0x10, 2):
        x = data[i + j]
        if x == 0:
            continue
        # If DARNESS, replace every fight occurrence with the field except the Final Fight
        elif (goa_type == 2 and x != 0x3E and x in fight) or (x in to_be_replaced):
            data[i + j] = fight[x]
f = open(current_dir + 'arif.bin', 'wb')
f.write(data)
f.close()
