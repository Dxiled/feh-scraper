# Fire Emblem Heroes - Hero Database Manager
# Main App Module
# Author: Dxiled
# Modified from https://github.com/vwstang/feh-scraper
# Controls tasks to run based on user input

# Import module dependencies
from pprint import pprint
import time
import json
import build


def dbComparer(currDB,updtDB):
    updtHeroes = {k:v for k,v in updtDB.items() if k not in currDB or v != currDB[k]}
    print(updtHeroes)


def comparing():
    with open("./tests/currentdb.json") as file:
        currentHeroList = json.load(file)
    with open("./tests/newupdates.json") as file:
        updatedHeroList = json.load(file)
    dbComparer(currentHeroList,updatedHeroList)


def writeToJSON(dictionary,name):
    filename = str(name) + ".json"
    with open(filename,"w") as outfile:
        json.dump(dictionary,outfile,indent=4)
    print("Output to " + filename + " complete")


def runHeroes():
    heroList = build.getHeroList()
    for hero in heroList:
        #time.sleep(1)
        print("Fetching data for " + hero,end="",flush=True)
        heroList[hero].update(build.getHeroData(heroList[hero]["gpedia"]))
        print("Done")
    writeToJSON(heroList,"herodb")
    print("Task complete")

def runWeapons():
    weaponList = build.getWeaponList()
    for weapon in weaponList:
        print("Fetching data for " + weapon,end="",flush=True)
        weaponList[weapon].update(build.getWeaponData(weaponList[weapon]["gpedia"]))
        print("Done")
    writeToJSON(weaponList, "weapondb")
    print("Task complete")

def runSkills():
    ASkillList = build.getASkillData()
    BSkillList = build.getBSkillData()
    CSkillList = build.getCSkillData()
    SacredSealList = build.getSacredSeals()
    SpecialList = build.getSpecials()
    AssistList = build.getAssists()
    writeToJSON(ASkillList, "askilldb")
    writeToJSON(BSkillList, "bskilldb")
    writeToJSON(CSkillList, "cskilldb")
    writeToJSON(SacredSealList, "sacredsealdb")
    writeToJSON(SpecialList, "specialdb")
    writeToJSON(AssistList, "assistdb")

def runExit():
    print("Exiting manager")


def runDebug():
    print("I'm in the (hidden) runDebug!")


def main():
    welcomemsg = """
******************************************************
***** FIRE EMBLEM HEROES - HERO DATABASE MANAGER *****
******************************************************

v0.0.2

=== Available tasks ===

heroes            build new database of heroes
weapons           build new database of weapons
skills            build new database of passive skills
exit              don't run any tasks and exit

===
"""
    task = {
        "heroes": runHeroes,
        "weapons": runWeapons,
        "skills": runSkills,
        "exit": runExit,
        "debug": runDebug
    }
    print(welcomemsg)
    userTask = input("What task would you like to run? ").lower()
    try:
        task[userTask]()
    except KeyError:
        print("INVALID COMMAND: Please rerun the script and enter a valid command")

main()