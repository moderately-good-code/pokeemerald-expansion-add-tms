#!/usr/bin/env python

from typing import List

from lxml import html
import requests

MAX_MON_NUMBER_GEN_8    = 905

POKEMON_DB_URL          = "https://www.pokemondb.net/"

def move_name_to_website_url(move_name: str) -> str:
    return POKEMON_DB_URL + "move/" + move_name.replace(" ", "-")

def get_mon_national_number(mon_name: str) -> str:
    return -1

def scrape_teachable_mons(move_name: str, gen_nr: int) -> List[str]:
    if gen_nr != 8:
        raise NotImplementedError("Only generation 8 is implemented.")

    # find all pokemon info cards as these represent all mons that can learn the move
    url = move_name_to_website_url(move_name)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    # teachable = tree.find_class("img-fixed icon-pkmn")
    teachable = tree.find_class("infocard")

    # get the text from the info card
    teachable = {elem.getchildren()[1].text_content() for elem in teachable}

    # text has the format "<name> #<number> ..."
    teachable = [elem.split("#") for elem in teachable]
    for elem in teachable:
        elem[1] = int(elem[1].split()[0])
    # print(teachable)

    # filter out mons whose numbers are too high for selected generation
    teachable = [elem[0].strip() for elem in teachable if (elem[1] < MAX_MON_NUMBER_GEN_8)]
    print(teachable)

    # the pokemon names are in the alt field of the icon images
    # teachable = {elem.attrib["alt"] for elem in teachable}
    # print(teachable)

    return teachable
