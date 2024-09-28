# pokeemerald-expansion-add-tms
Script for inserting the C code necessary to add new TMs into a given pokeemerald-expansion code base.

## How to use

```
python main.py "move name" <generation number> <pokeemerald directory>
```

(Currently, only generation number 8 is implemented. This should be easy to change if you need to.)

Write a description of the move in `.../src/data/text/item_descriptions.h` in your game's source code.
Make sure the description's formatting matches the others in the file.

**If you change the content of the used files (see below), this script might not work as it expects specific contents.**

## What the script does in detail

First, we need to decide which mons can learn the TM.
I have chosen that any mon who can learn the attack (via TM or other methods, including breeding) as listed by pokemondb.net will be allowed to learn the TM.
The needed info is scraped from https://pokemondb.net/move/\<move-name\>.

Mons with an ID above 905 are ignored, so this is done only for mons up to generation 8.
**You will need to edit the script if you want to use other generations.**
It is ensured that every mon referenced by the script actually exists in the game's source code by checking that its ID exists in `.../include/constants/species.h`.
An error is thrown if this check fails.
If there is no mon up to gen 8 that can learn the move, an error is thrown as well.

Then we need to add the TM into the game's source code:
* The array `gItems` in `.../src/data/items.h` contains the existing TMs (among the other items) and placeholders where new TMs can be added. A placeholder is unused if its `secondaryId` has the value `MOVE_NONE`. We pick the first unused placeholder or print an error message and return if none is left.
* **The item's description in `.../src/data/text/item_descriptions.h` is not changed because the user is expected to set this value themselves.**
* Set the item icon for the TM in `.../src/data/item_icon_table.h`. The move type determines the the icon used. **TODO: scraping of the move type is not implemented yet.**
* Add the move to the list of moves the corresponding mons can learn via TM. This is done by adding the move's ID to the mon's `s<...>TeachableLearnset` array in `.../src/data/pokemon/teachable_learnsets.h`.
