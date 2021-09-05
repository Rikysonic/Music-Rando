import os
import random

#Pair up Field & Fight theme
dotk = [0x3C,0x3D,0x3E] #Darkness of the Unknown
random.shuffle(dotk)
field = {dotk[0]:dotk[1],
         dotk[1]:dotk[2],
         dotk[2]:dotk[0],
         0x32:0x33, #Dive into the Heart -Destati- & Fragments of Sorrow
         0x34:0x35, #The Afternoon Streets & Working Together
         0x36:0x37, #Sacred Moon & Deep Drive
         0x40:0x41, #What a Surprise?! & Happy Holidays!
         0x44:0x45, #Cavern of Remembrance & Deep Anxiety
         0x64:0x66, #The Underworld & What Lies Beneath
         0x65:0x68, #Waltz of the Damned & Dance of the Daring
         0x74:0x70, #The Home of Dragons & Fields of Honor
         0x76:0x77, #Lazy Afternoons & Sinister Sundowns
         0x7A:0x7B, #Let's Sing and Dance! I & Let's Sing and Dance! II
         0x7F:0x80, #A Day in Agrabah & Arabian Dream
         0x85:0x86, #Magical Mystery & Working Together
         0x87:0x88, #Space Paranoids & Byte Bashing
         0x8A:0x8B, #Shipmeister's Shanty & Gearing Up
         0x90:0x95, #This is Halloween & Spooks of Halloween Town
         0x98:0x99, #Reviving Hollow Bastion & Scherzo Di Notte
         0x9A:0x9B, #Nights of the Cursed & He's a Pirate
         0xBA:0xBB, #Adventures in the Savannah & Savannah Pride
         0xBD:0xBE} #Monochrome Dreams & Old Friends, Old Rivals
fight = {} #Basically reverse of pairs
for i in field:
    fight[field[i]] = i

#Get music ID
currentDir = os.path.realpath(__file__).replace(os.path.basename(__file__),'')
files = os.listdir(currentDir+'bgm')
musiclist = []
for file in files:
    musiclist.append(int(file[5:8]))
#Remove unwanted tracks
musiclist.remove(0x84) #Beauty and the Beast (No Loop)

#Shuffle tracks
randomlist = musiclist.copy()
random.shuffle(randomlist)

#Ensure Field & Fight tracks are grouped together
tobereplaced = []
for fightold in fight:
    fieldold = fight[fightold]
    indexfield = musiclist.index(fieldold)
    indexfight = musiclist.index(fightold)
    fieldnew = randomlist[indexfield]
    fightnew = randomlist[indexfight]
    paired = False
    #Find out where the pair is located
    try:
        paired = field[fightnew]
    except:
        try:
            paired = fight[fightnew]
        except:
            pass
    if paired: #Swap the field with the pair tracks
        indexpaired = randomlist.index(paired)
        randomlist[indexfield],randomlist[indexpaired] = paired, fieldnew
    else:
        tobereplaced.append([indexfield,fightnew])
#Replace the field with the fight track
for i in tobereplaced:
    randomlist[i[0]] = i[1]

#Write the mod.yml
f = open(currentDir+"mod.yml", "w")
f.write('assets:\n')
for i in range(len(musiclist)):
    old = musiclist[i]
    new = randomlist[i]
    old = 'bgm/music'+str(old).zfill(3)+'.bgm'
    new = 'bgm/music'+str(new).zfill(3)+'.bgm'
    f.write('- name: '+old+'\n  method: copy\n  source:\n  - name: '+new+'\n')
f.close()
