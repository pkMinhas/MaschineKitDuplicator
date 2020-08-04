# The Maschine Kit Duplicator
# Author: Preet Kamal Singh Minhas (https://marchingbytes.com)
# License : MIT
# Requirements: python v3.8

import os
import glob
from enum import Enum
from shutil import copyfile


def all_kit_names(expansion_path):
    kits_dir = f"{expansion_path}{os.sep}Groups/Kits"
    print(f"Evaluating Kits at {kits_dir}")

    kit_names = []
    for kit in os.listdir(kits_dir):
        if kit.endswith(".mxgrp"):
            kit_names.append(kit.split(".mxgrp")[0])

    print(f"Found {len(kit_names)} kits")
    return kit_names


def wav_files_for_kit(expansion_path, kit_name):
    print(f"Searching files in kit {kit_name}")
    # remove the trailing " Kit" from kit name to get the wav files
    kit_name = kit_name.replace(" Kit", "")
    search_string = f"{expansion_path}/**/*{kit_name}*.wav"
    all_waves = glob.glob(search_string, recursive=True)
    print(f"Found {len(all_waves)} files")
    return all_waves


def is_maschine_expansion(expansion_path):
    """Rough check for whether the given library is a maschine expansion.
    As per analysis, all maschine expansions have a Groups folder. Thats what we check for!
    """
    groups_dir = f"{expansion_path}{os.sep}Groups"
    return os.path.exists(groups_dir) and os.path.isdir(groups_dir)


def all_expansions(base_dir):
    all_libraries = glob.glob(f"{base_dir}/* Library", recursive=False)
    expansions = []
    for path in all_libraries:
        if is_maschine_expansion(path):
            expansions.append(path)
    return expansions


def process_expansion_kits(expansion_path, expansion_output_dir, run_mode):
    kit_names = all_kit_names(expansion_path)
    for kit in kit_names:
        # print(f"Processing kit: {kit}")
        waves = wav_files_for_kit(expansion_path, kit)
        # skip the kit if the output directory already exists OR if the kit has 0 wav files
        kit_output_dir = f"{expansion_output_dir}{os.sep}{kit}"
        if os.path.exists(kit_output_dir) == False and len(waves) > 0:
            # create dir for kit
            os.mkdir(kit_output_dir)
            # print(f"Created kit output directory: {kit_output_dir}")

            # create a link to the wav file (space savings!!!)
            for wav in waves:
                src = wav
                file_name = os.path.split(wav)[1]
                dest = f"{kit_output_dir}{os.sep}{file_name}"
                if not os.path.exists(dest):
                    if run_mode == RunMode.SYMLINKS:
                        os.symlink(src, dest)
                    elif run_mode == RunMode.COPY:
                        copyfile(src, dest)
                    else:
                        raise Exception(f"Invalid run mode: {run_mode}")
        else:
            if len(waves) == 0:
                print(f"Skipping kit {kit} as it has 0 wav files")
            else:
                # directory already exists, skip processing the kit
                print(f"Skipping kit as output directory already exists: {kit_output_dir}")


class RunMode(Enum):
    NONE = -1
    SYMLINKS = 0
    COPY = 1


if __name__ == "__main__":
    output_dir = f"{os.path.expanduser('~')}/Music/MKD Kits"
    maschine_expansion_base_dir = "/Users/Shared"
    run_mode = RunMode.NONE

    user_input = input(f"Enter Maschine data installation directory [{maschine_expansion_base_dir}]: ")
    if user_input is not None and len(user_input) > 0:
        maschine_expansion_base_dir = user_input

    if not os.path.isdir(maschine_expansion_base_dir):
        raise Exception("Maschine data installation path is not a valid directory!")

    # get output dir
    user_input = input(f"Enter output directory [{output_dir}]: ")
    if user_input is not None and len(user_input) > 0:
        output_dir = user_input
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # get mode - symlink or copy
    while run_mode == RunMode.NONE:
        user_input = input(f"Create links (saves disk space) or copy wav to destination? [symlinks / copy]: ")
        if user_input == "symlinks":
            run_mode = RunMode.SYMLINKS
        elif user_input == "copy":
            run_mode = RunMode.COPY
        else:
            print(f"Please enter either 'symlinks' or 'copy'")


    expansions = all_expansions(maschine_expansion_base_dir)
    print(f"Found {len(expansions)} maschine expansions")

    for expansion_path in expansions:
        expansion_name = os.path.split(expansion_path)[1]
        expansion_name = expansion_name.replace(" Library","")

        print(f"Processing {expansion_name}. This might take a while...")
        # create directory for the expansion
        expansion_output_dir = f"{output_dir}{os.sep}{expansion_name}"
        if os.path.isdir(expansion_output_dir) == False:
            os.makedirs(expansion_output_dir)
            print(f"Created output dir: {expansion_output_dir}")

        process_expansion_kits(expansion_path, expansion_output_dir, run_mode)
        print("Done!")


