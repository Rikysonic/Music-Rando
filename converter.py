import os
from glob import glob

offset = 0x02  # Change it to the number you want - for now KH1 uses 01 as offset


def rename_bgm():
    current_dir = os.path.dirname(__file__) or '.'
    files = glob(f"{current_dir}/*.bgm")
    for file in files:
        with open(file, 'rb') as f:
            data = bytearray(f.read())
        data[0x05] = offset
        data[0x07] = offset
        old_filename = os.path.basename(file)
        old_number = old_filename[5:8]
        new_number = offset * 0x100 + data[0x04]
        new_file = str(file).replace(old_number, str(new_number).rjust(3, '0'))
        with open(f"converted/{os.path.basename(new_file)}", 'wb') as f:
            f.write(data)


def rename_wd():
    current_dir = os.path.dirname(__file__)  or '.'
    files = glob(f"{current_dir}/*.wd")
    for file in files:
        with open(file, 'rb') as f:
            data = bytearray(f.read())
        data[0x03] = offset
        old_filename = os.path.basename(file)
        old_number = old_filename[4:8]
        new_number = offset * 0x100 + data[0x02]
        new_file = str(file).replace(old_number, str(new_number).rjust(4, '0'))
        with open(f"converted/{os.path.basename(new_file)}", 'wb') as f:
            f.write(data)


if __name__ == '__main__':
    rename_bgm()
    rename_wd()
