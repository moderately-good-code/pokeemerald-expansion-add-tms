#!/usr/bin/env python

import os
import sys

import pokeemerald_utils as peutils
import scrape_move_info as scrpmi

def main(move_name: str, gen_nr: int, pe_dir: str) -> None:
    # check that pokeemerald directory is valid
    if not pe_dir.endswith("/"):
        pe_dir += "/"
    if not os.path.isdir(pe_dir):
        raise RuntimeError(f"'{pe_dir}' is not a valid directory.")
    print(f"Directory '{pe_dir}' is valid!")

    # check that move name is valid
    if not peutils.is_valid_move(move_name, pe_dir):
        raise RuntimeError(f"'{move_name}' is not a valid move.")
    print(f"Move name '{move_name}' is valid!")

    # get names of teachable mons
    print("Scraping teachable mons...")
    db_teachable = scrpmi.scrape_teachable_mons(move_name, gen_nr)
    if len(db_teachable) == 0:
        raise RuntimeError("No teachable mons were found.")
    db_teachable = {mon for mon in db_teachable}
    print("Done!")

    # discard these variations for now - might need to be changed for higher gens
    for variation_str in ["Breed", "Bloodmoon", "Paldean"]:
        db_teachable = {elem for elem in db_teachable if (not variation_str in elem)}

    # convert to names used in pokeemerald
    pe_teachable = {peutils.pokemondb_mon_name_to_pokeemerald_mon_name(name) for name in db_teachable}

    # check that all names are valid
    print("Checking that all created species ID macro names are valid...")
    for mon_name in pe_teachable:
        if not peutils.is_valid_species_id_macro(mon_name, pe_dir):
            raise RuntimeError(f"Expected macro '{mon_name}' to exist, but didn't find it.")
    print("Done!")

    # add TM to global array of items
    print("Adding the TM to the gItems array...")
    new_tm_name = peutils.add_tm_to_items(pe_dir, move_name)
    if not new_tm_name:
        print("Failed to insert the new TM into the items.")
        return
    print(f"Done! (Move was assigned to TM '{new_tm_name}')")

    # set TM item icon
    print("Setting the item icon for the new TM...")
    succ = peutils.set_tm_icon(pe_dir, new_tm_name, "TODO")
    if not succ:
        print("Failed to set icon for the TM.")
        return
    print("Done!")

    # update mon learnsets
    print("Updating mon learnsets...")
    succ = peutils.update_learnsets(pe_dir, move_name, db_teachable)
    if not succ:
        print("Failed to update the learnsets.")
        return
    print("Done!")

if __name__=="__main__":
    if len(sys.argv) != 4:
        raise ValueError("Expected exactly 3 arguments (move name, generation number, pokeemerald directory).")
    move_name = sys.argv[1]
    gen_nr = int(sys.argv[2])
    pe_dir = sys.argv[3]
    main(move_name, gen_nr, pe_dir)
