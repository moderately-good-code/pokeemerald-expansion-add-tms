#!/usr/bin/env python

import datetime
import re
import shutil
from typing import List

def get_moves_h_path(pe_dir: str) -> str:
    return pe_dir + "include/constants/moves.h"

def get_species_h_path(pe_dir: str) -> str:
    return pe_dir + "include/constants/species.h"

def get_items_h_path(pe_dir: str) -> str:
    return pe_dir + "src/data/items.h"

def get_itemicontable_h_path(pe_dir: str) -> str:
    return pe_dir + "src/data/item_icon_table.h"

def get_teachablelearnsets_h_path(pe_dir: str) -> str:
    return pe_dir + "src/data/pokemon/teachable_learnsets.h"

def pokemondb_mon_name_to_pokeemerald_mon_name(db_name: str) -> str:
    pe_name = "SPECIES_" + db_name.upper().strip()

    # basic formatting to get a valid C macro name
    pe_name = pe_name.replace(" ", "_")
    pe_name = pe_name.replace(".", "")
    pe_name = pe_name.replace("-", "_")
    pe_name = pe_name.replace("%", "")
    pe_name = pe_name.replace("'", "")
    pe_name = pe_name.replace("É", "E")

    # remove double name of base species
    # (some strings have the form "<base species> <specifier> <base species>")
    for separator in [
            # regional forms
            "_GALARIAN", "_ALOLAN", "_HISUIAN",
            # Kyurem forms
            "_KYUREM_BLACK", "_KYUREM_WHITE",
            # Rotom forms
            "_ROTOM_HEAT", "_ROTOM_WASH", "_ROTOM_FROST", "_ROTOM_FAN", "_ROTOM_MOW",
            # others
            "_GRENINJA_ASH"]:
        base1, variation, base2 = pe_name.partition(separator)
        pe_name = base1 + variation

    # remove suffixes that are not used in macro names
    for suffix in [
            # suffixes designating the "normal" form of a pokemon
            "_HERO_OF_MANY_BATTLES", "_NORMAL_FORME", "_INCARNATE_FORME",
            "_HOOPA_CONFINED", "_ORDINARY_FORM", "_MIDDAY_FORM",
            "_AMPED_FORM", "_LAND_FORME", "_ALTERED_FORME", "_BAILE_STYLE",
            "_ARIA_FORME", "_RED_STRIPED_FORM", "_METEOR_FORM",
            "_MALE", # kind of misogynistic that they made this the "normal" form...
            # remove these AFTER the ones above!
            "_FORME", "_FORM", "_STYLE"]:
        if pe_name.endswith(suffix):
            pe_name = pe_name.replace(suffix, "")

    # special cases
    pe_name = pe_name.replace("HOOPA_HOOPA", "HOOPA")
    return pe_name

def pokemondb_move_name_to_pokeemerald_move_name(db_name: str) -> str:
    return "MOVE_" + db_name.replace(" ", "_").upper()

def is_valid_move(db_move_name: str, pe_dir: str) -> bool:
    move_name = " " + pokemondb_move_name_to_pokeemerald_move_name(db_move_name) + " "
    # (spaces around name to make sure we're matching the full name)
    file_path = get_moves_h_path(pe_dir)
    with open(file_path, "r") as move_file:
        for line in move_file:
            if move_name in line:
                return True
    return False

def is_valid_species_id_macro(macro: str, pe_dir: str) -> bool:
    macro_spaces = " " + macro + " "
    # (spaces around name to make sure we're matching the full name)
    file_path = get_species_h_path(pe_dir)
    with open(file_path, "r") as move_file:
        for line in move_file:
            if macro_spaces in line:
                return True
    return False

def create_backup(file_path: str) -> str:
    time_str = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
    backup_path = file_path + "." + time_str + "_BACKUP"
    shutil.copyfile(file_path, backup_path)
    return backup_path
    # with open(file_path, 'r') as file:
    #     data = file.read()
    # time_str = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")
    # backup_path = file_path + "." + time_str + "_BACKUP"
    # with open(backup_path, 'x') as file:
    #     file.write(data)
    # return backup_path

def add_tm_to_items(pe_dir: str, db_move_name: str) -> str:
    """Returns the name of the new TM."""
    # create backup of items file
    file_path = get_items_h_path(pe_dir)
    backup_path = create_backup(file_path)

    # now read from backup file into items file while adding the TM
    tm_added = False
    new_tm_name = None
    with open(backup_path, "r") as backup_file:
        with open(file_path, "w") as items_file:
            # get to start of gItems
            while True:
                line = backup_file.readline()
                items_file.write(line)
                if not line or line.startswith("const struct Item gItems[] ="):
                    break

            while not tm_added:
                # find next placeholder TM item
                while True:
                    line = backup_file.readline()
                    items_file.write(line)
                    if not line:
                        return None
                    # preset TMs have names like ITEM_TM_<name>
                    # placeholder TMs have names like ITEM_TM<number>
                    if "ITEM_TM" in line and not "ITEM_TM_" in line:
                        break

                # extract name of new TM
                tm_regex_match = re.search(r"\[(.*?)\]", line)
                if tm_regex_match:
                    new_tm_name = tm_regex_match.group(0)[1:-1]
                else:
                    return None

                # next 8 lines do not need to be modified (general TM item stuff)
                for i in range(8):
                    line = backup_file.readline()
                    items_file.write(line)
                    if not line:
                        return None

                # next line will reference the actual move
                # (if it is MOVE_NONE, the placeholder is free, otherwise used already)
                line = backup_file.readline()
                if not line:
                    return None
                if "MOVE_NONE," in line:
                    # placeholder is free
                    new_move = pokemondb_move_name_to_pokeemerald_move_name(db_move_name)
                    line = line.replace("MOVE_NONE", new_move)
                    tm_added = True
                items_file.write(line)

            # TM has been added, let's just copy the remaining lines directly
            data = backup_file.read()
            items_file.write(data)

    return new_tm_name

def set_tm_icon(pe_dir: str, pe_tm_name: str, move_type: str) -> bool:
    # create backup of items file
    file_path = get_itemicontable_h_path(pe_dir)
    backup_path = create_backup(file_path)

    # now read from backup file into items file while adding the TM
    icon_set = False
    with open(backup_path, "r") as backup_file:
        with open(file_path, "w") as icons_file:
            # find line defining the icon
            searched_substr = f"[{pe_tm_name}]"
            while not icon_set:
                line = backup_file.readline()
                if not line:
                    return False
                if searched_substr in line:
                    # this is the line where we need to add the correct icon
                    line = line.replace("Normal", move_type)
                    icon_set = True
                icons_file.write(line)

            # icon has been set, let's copy the remaining lines directly
            data = backup_file.read()
            icons_file.write(data)

    return icon_set

def update_learnsets(pe_dir: str, db_move_name, db_teachable_names: List[str]) -> bool:
    pe_move_name = pokemondb_move_name_to_pokeemerald_move_name(db_move_name)
    pe_teachable_names = [pokemondb_mon_name_to_pokeemerald_mon_name(name)\
            .replace("_", "").replace("SPECIES", "").lower() \
            for name in db_teachable_names]

    # special forms use the same learnset as the standard forms and can be removed
    def is_mon_special_form(name: str) -> bool:
        for suffix in ["greninjaash", "striped", "decidueyehisuian", "oricoriopau",
                "shayminsky", "oricoriosensu", "oricoriopompom", "therian", "origin",
                "avalugghisuian"]:
            if name.endswith(suffix):
                return True
        return False
    pe_teachable_names[:] = [mon for mon in pe_teachable_names if (not is_mon_special_form(mon))]

    # create backup of items file
    file_path = get_teachablelearnsets_h_path(pe_dir)
    backup_path = create_backup(file_path)

    # now read from backup file into items file while adding the TM
    learnsets_updated = False
    with open(backup_path, "r") as backup_file:
        with open(file_path, "w") as learnsets_file:
            while not learnsets_updated:
                # find beginning of the next learnset definition
                while True:
                    line = backup_file.readline()
                    learnsets_file.write(line)
                    if not line:
                        print("Unexpected end of file. No learnsets found for these mons:", pe_teachable_names)
                        return False
                    mon_regex_match = re.search(r"s(\w+?)Teachable", line)
                    if mon_regex_match:
                        mon_name = mon_regex_match.group(0)[1:-9].lower()
                        break

                # new learnset found, check if the corresponding mon is in our list
                if not mon_name in pe_teachable_names:
                    continue

                # check if move is already in learnset, add if it is not
                already_teachable = False
                while True:
                    line = backup_file.readline()
                    if not line:
                        print("Unexpected end of file.")
                        return False
                    if pe_move_name in line:
                        already_teachable = True
                    if "MOVE_UNAVAILABLE" in line:
                        break
                    learnsets_file.write(line)
                if not already_teachable:
                    inserted_line = f"    {pe_move_name},\n"
                    learnsets_file.write(inserted_line)
                learnsets_file.write(line)

                pe_teachable_names.remove(mon_name)
                print(f"Successfully udated learnset for {mon_name}!")
                if len(pe_teachable_names) == 0:
                    learnsets_updated = True

            # learnsets have been updated, let's copy the remaining lines directly
            data = backup_file.read()
            learnsets_file.write(data)

    if not learnsets_updated:
        print("No learnsets found for these mons:", pe_teachable_names)

    return learnsets_updated
