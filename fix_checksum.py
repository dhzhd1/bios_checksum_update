import subprocess
import argparse


def get_args():
    params = argparse.ArgumentParser()
    params.add_argument('--rom', help="specified modified BIOS rom", required=True)
    params.add_argument('--extractor', help='specified Modified version UEFIExtract path')
    return params.parse_args()


def get_digests(cmd):
    # Get the string of digits
    dict_digests = {}
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode('utf-8').split('\n')

    str_ibb_digest_new = list(filter(lambda a: 'BG-Protect Hash Calculated: ' in a, output))[0].split(": ")[1].lower()
    bytes_ibb_digest_new = bytearray.fromhex(str_ibb_digest_new)
    dict_digests['str_ibb_new'] = str_ibb_digest_new
    dict_digests['bytes_ibb_new'] = bytes_ibb_digest_new

    str_ibb_digest_old = list(filter(lambda a: 'BG-Protect Hash Existing: ' in a, output))[0].split(": ")[1].lower()
    bytes_ibb_digest_old = bytearray.fromhex(str_ibb_digest_old)
    dict_digests['str_ibb_old'] = str_ibb_digest_old
    dict_digests['bytes_ibb_old'] = bytes_ibb_digest_old

    str_ami_digest_new = list(filter(lambda a: 'AMI Hash Calculated: ' in a, output))[0].split(": ")[1].lower()
    bytes_ami_digest_new = bytearray.fromhex(str_ami_digest_new)
    dict_digests['str_ami_new'] = str_ami_digest_new
    dict_digests['bytes_ami_new'] = bytes_ami_digest_new

    str_ami_digest_old = list(filter(lambda a: 'AMI Hash Existing: ' in a, output))[0].split(": ")[1].lower()
    bytes_ami_digest_old = bytearray.fromhex(str_ami_digest_old)
    dict_digests['str_ami_old'] = str_ami_digest_old
    dict_digests['bytes_ami_old'] = bytes_ami_digest_old

    return dict_digests


def replace_digest(b_old_digest, b_new_digest, rom_path):
    with open(rom_path, "rb") as bf:
        rom_bytes = bf.read()
    rom_bytes_new_crc = rom_bytes.replace(b_old_digest, b_new_digest)

    with open(rom_path, "wb") as bf:
        bf.write(rom_bytes_new_crc)


def main():
    args = get_args()
    # Build digest extract command
    UEFIExtract = args.extractor
    ROM_Path = args.rom
    UEFIExtract_CMD = "{uefiextract_cmd} {rom} report".format(uefiextract_cmd=UEFIExtract, rom=ROM_Path)

    # get digests
    digest = get_digests(UEFIExtract_CMD)

    while digest['str_ami_new'] != digest['str_ami_old'] or digest['str_ibb_new'] != digest['str_ibb_old']:
        if digest['str_ami_new'] != digest['str_ami_old']:
            print("AMI Hash  should be {}, but detected as {} in rom".format(digest['str_ami_new'], digest['str_ami_old']))
            print("Replacing ...")
            replace_digest(digest['bytes_ami_old'], digest['bytes_ami_new'], ROM_Path)

        if digest['str_ibb_new'] != digest['str_ibb_old']:
            print("BG-Protected Hash should be {}, but detected as {} in rom".format(digest['str_ibb_new'], digest['str_ibb_old']))
            print("Replacing ...")
            replace_digest(digest['bytes_ibb_old'], digest['bytes_ibb_new'], ROM_Path)

        digest = get_digests(UEFIExtract_CMD)
    else:
        print("AMI and BG-Protected Hash are correct!")
        print("The updated BIOS file could be found at {}".format(ROM_Path))


if __name__ == '__main__':
    main()

