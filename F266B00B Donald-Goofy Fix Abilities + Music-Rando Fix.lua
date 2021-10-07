--Donald & Goofy fix from Num's GoA ROM Edition
--Music fix for Num's Music-Rando

LUAGUI_NAME = "Donald & Goofy fix from Num's GoA ROM Edition + Music fix for Num's Music-Rando"
LUAGUI_AUTH = "Rikysonic (original work: Num)"
LUAGUI_DESC = "Donald & Goofy abilities fix + Music fix for Music-Rando, extracted from GoA ROM Edition. FOR PCSX2 ONLY"

function _OnInit()
    if ENGINE_VERSION < 3.0 then
        print("LuaEngine is Outdated. Things might not work properly.")
    end
    Now = 0x032BAE0 --Current Location
    Save = 0x032BB30 --Save File
    Sys3 = 0x1CCB300 --03system.bin
end

function Spawn(Type, Subfile, Offset, Value)
    local Subpoint = ARD + 0x08 + 0x10 * Subfile
    local Address
    if ReadInt(ARD) == 0x01524142 and Subfile <= ReadInt(ARD + 4) then
        --Exclusions on Crash Spots in PCSX2-EX
        Address = ReadInt(Subpoint) + Offset
        if Type == "Short" then
            WriteShort(Address, Value)
        elseif Type == "Float" then
            WriteFloat(Address, Value)
        elseif Type == "Int" then
            WriteInt(Address, Value)
        elseif Type == "String" then
            WriteString(Address, Value)
        end
    end
end

function _OnFrame()
    if true then --Define current values for common addresses
        Place = ReadShort(Now + 0x00)
        ARD = ReadInt(0x034ECF4) --Base ARD Address
    end
    DonaldGoofyFix()
    MusicFix()
end

function DonaldGoofyFix()
    --Donald's Staff Active Abilities
    if true then
        local Staff = ReadShort(Save + 0x2604)
        local Ability = false
        if Staff == 0x04B then --Mage's Staff
            Ability = 0x13F36
        elseif Staff == 0x094 then --Hammer Staff
            Ability = 0x13F46
        elseif Staff == 0x095 then --Victory Bell
            Ability = 0x13F56
        elseif Staff == 0x097 then --Comet Staff
            Ability = 0x13F76
        elseif Staff == 0x098 then --Lord's Broom
            Ability = 0x13F86
        elseif Staff == 0x099 then --Wisdom Wand
            Ability = 0x13F96
        elseif Staff == 0x096 then --Meteor Staff
            Ability = 0x13F66
        elseif Staff == 0x09A then --Rising Dragon
            Ability = 0x13FA6
        elseif Staff == 0x09C then --Shaman's Relic
            Ability = 0x13FC6
        elseif Staff == 0x258 then --Shaman's Relic+
            Ability = 0x14406
        elseif Staff == 0x09B then --Nobody Lance
            Ability = 0x13FB6
        elseif Staff == 0x221 then --Centurion
            Ability = 0x14316
        elseif Staff == 0x222 then --Centurion+
            Ability = 0x14326
        elseif Staff == 0x1E2 then --Save the Queen
            Ability = 0x14186
        elseif Staff == 0x1F7 then --Save the Queen+
            Ability = 0x142D6
        elseif Staff == 0x223 then --Plain Mushroom
            Ability = 0x14336
        elseif Staff == 0x224 then --Plain Mushroom+
            Ability = 0x14346
        elseif Staff == 0x225 then --Precious Mushroom
            Ability = 0x14356
        elseif Staff == 0x226 then --Precious Mushroom+
            Ability = 0x14366
        elseif Staff == 0x227 then --Premium Mushroom
            Ability = 0x14376
        elseif Staff == 0x0A1 then --Detection Staff
            Ability = 0x13FD6
        end
        if Ability then
            Ability = ReadShort(Sys3 + Ability)
            if Ability == 0x0A5 then --Donald Fire
                WriteShort(Save + 0x26F6, 0x80A5)
                WriteByte(Sys3 + 0x11F0B, 0)
            elseif Ability == 0x0A6 then --Donald Blizzard
                WriteShort(Save + 0x26F6, 0x80A6)
                WriteByte(Sys3 + 0x11F23, 0)
            elseif Ability == 0x0A7 then --Donald Thunder
                WriteShort(Save + 0x26F6, 0x80A7)
                WriteByte(Sys3 + 0x11F3B, 0)
            elseif Ability == 0x0A8 then --Donald Cure
                WriteShort(Save + 0x26F6, 0x80A8)
                WriteByte(Sys3 + 0x11F53, 0)
            else
                WriteShort(Save + 0x26F6, 0) --Remove Ability Slot 80
                WriteByte(Sys3 + 0x11F0B, 2) --Restore Original AP Costs
                WriteByte(Sys3 + 0x11F23, 2)
                WriteByte(Sys3 + 0x11F3B, 2)
                WriteByte(Sys3 + 0x11F53, 3)
            end
        end
    end
    --Goofy's Shield Active Abilities
    if true then
        local Shield = ReadShort(Save + 0x2718)
        local Ability = false
        if Shield == 0x031 then --Knight's Shield
            Ability = 0x13FE6
        elseif Shield == 0x08B then --Adamant Shield
            Ability = 0x13FF6
        elseif Shield == 0x08C then --Chain Gear
            Ability = 0x14006
        elseif Shield == 0x08E then --Falling Star
            Ability = 0x14026
        elseif Shield == 0x08F then --Dreamcloud
            Ability = 0x14036
        elseif Shield == 0x090 then --Knight Defender
            Ability = 0x14046
        elseif Shield == 0x08D then --Ogre Shield
            Ability = 0x14016
        elseif Shield == 0x091 then --Genji Shield
            Ability = 0x14056
        elseif Shield == 0x092 then --Akashic Record
            Ability = 0x14066
        elseif Shield == 0x259 then --Akashic Record+
            Ability = 0x14416
        elseif Shield == 0x093 then --Nobody Guard
            Ability = 0x14076
        elseif Shield == 0x228 then --Frozen Pride
            Ability = 0x14386
        elseif Shield == 0x229 then --Frozen Pride+
            Ability = 0x14396
        elseif Shield == 0x1E3 then --Save the King
            Ability = 0x14196
        elseif Shield == 0x1F8 then --Save the King+
            Ability = 0x142E6
        elseif Shield == 0x22A then --Joyous Mushroom
            Ability = 0x143A6
        elseif Shield == 0x22B then --Joyous Mushroom+
            Ability = 0x143B6
        elseif Shield == 0x22C then --Majestic Mushroom
            Ability = 0x143C6
        elseif Shield == 0x22D then --Majestic Mushroom+
            Ability = 0x143D6
        elseif Shield == 0x22E then --Ultimate Mushroom
            Ability = 0x143E6
        elseif Shield == 0x032 then --Detection Shield
            Ability = 0x14086
        elseif Shield == 0x033 then --Test the King
            Ability = 0x14096
        end
        if Ability then --Safeguard if none of the above (i.e. Main Menu)
            Ability = ReadShort(Sys3 + Ability)
            if Ability == 0x1A7 then --Goofy Tornado
                WriteShort(Save + 0x280A, 0x81A7)
                WriteByte(Sys3 + 0x11F6B, 0)
            elseif Ability == 0x1AD then --Goofy Bash
                WriteShort(Save + 0x280A, 0x81AD)
                WriteByte(Sys3 + 0x11F83, 0)
            elseif Ability == 0x1A9 then --Goofy Turbo
                WriteShort(Save + 0x280A, 0x81A9)
                WriteByte(Sys3 + 0x11F9B, 0)
            else
                WriteShort(Save + 0x280A, 0) --Remove Ability Slot 80
                WriteByte(Sys3 + 0x11F6B, 2) --Restore Original AP Costs
                WriteByte(Sys3 + 0x11F83, 2)
                WriteByte(Sys3 + 0x11F9B, 2)
            end
        end
    end
end

function MusicFix()
    --Simulated Twilight Town Adjustments
    if ReadByte(Save + 0x1CFF) == 13 then --STT Removals
        if ReadByte(Save + 0x3FF5) == 6 and ReadByte(Save + 0x1CFE) == 0 then --Day 6 & STT Not Cleared
            WriteByte(Save + 0x23EE, 2) --STT Music: Sinister Sundowns (No Field Music)
        else
            WriteByte(Save + 0x23EE, 0) --STT Music: Lazy Afternoons & Sinister Sundowns
        end
    else --Restore Outside STT
        WriteByte(Save + 0x23EE, 1) --TT Music: The Afternoon Streets & Working Together
    end
    --Station of Calling Spawns
    if true then
        --Music Change - Final Fights
        if Place == 0x1212 then --The Altar of Naught
            Path = 1
        elseif Place == 0x1A04 then --Garden of Assemblage
            Path = 15
        end
        if Path then
            WriteShort(Save + 0x03D6, Path) --Station of Calling MAP
            WriteShort(Save + 0x03D8, 0x00) --Station of Calling BTL
        end
    end
    if ReadShort(Save + 0x03D6) == 15 --[[and Platform == 0--]] then
        if Place == 0x1B12 then --Part I
            Spawn("Short", 0x06, 0x0A4, 0x09C) --Guardando nel buio
            Spawn("Short", 0x06, 0x0A6, 0x09C)
        elseif Place == 0x1C12 then --Part II
            Spawn("Short", 0x07, 0x008, 0x09C)
            Spawn("Short", 0x07, 0x00A, 0x09C)
        elseif Place == 0x1A12 then --Cylinders
            Spawn("Short", 0x07, 0x008, 0x09C)
            Spawn("Short", 0x07, 0x00A, 0x09C)
        elseif Place == 0x1912 then --Core
            Spawn("Short", 0x07, 0x008, 0x09C)
            Spawn("Short", 0x07, 0x00A, 0x09C)
        elseif Place == 0x1812 then --Armor Xemnas I
            Spawn("Short", 0x06, 0x008, 0x09C)
            Spawn("Short", 0x06, 0x00A, 0x09C)
            Spawn("Short", 0x06, 0x034, 0x09C)
            Spawn("Short", 0x06, 0x036, 0x09C)
        elseif Place == 0x1D12 then --Pre-Dragon Xemnas
            Spawn("Short", 0x03, 0x010, 0x09C)
            Spawn("Short", 0x03, 0x012, 0x09C)
        end
    end
end
