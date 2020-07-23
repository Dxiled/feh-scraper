# Build Module
# 
# This module contains all web scraping functions used by the manager in performing tasks to build and update the JSON database

# Import module dependencies
import requests
from bs4 import BeautifulSoup

def getHeroList():
    url = "https://feheroes.gamepedia.com/Hero_list"
    response = requests.get(url)
    rawHTML = BeautifulSoup(response.text, "html.parser")
    lstHeroHTML = rawHTML("tr",{"class": "hero-filter-element"})
    print("Found " + str(len(lstHeroHTML)) + " heroes on Gamepedia")
    print("Building hero database")
    dctHeroes = {}
    for heroTag in lstHeroHTML:
        dctHero = {}
        heroName, heroTitle = heroTag.find("td").next_sibling.find("a").text.split(": ")
        heroKey = heroName.lower() + "_" + "".join(heroTitle.lower().split(" "))
        heroGPediaLink = "https://feheroes.gamepedia.com" + heroTag.find("td").next_sibling.find("a")["href"]
        dctHero.update({
            "id": heroKey,
            "name": heroName,
            "title": heroTitle,
            "movement": heroTag.get("data-move-type"),
            "weapon": heroTag.get("data-weapon-type"),
            "gpedia": heroGPediaLink
        })
        dctHeroes[heroKey] = dctHero
    print("Hero database build complete")
    return dctHeroes


def listStats(stringStats):
    if len(stringStats) >= 5:
        result = list(map(int,stringStats.split("/")))
    else:
        result = [int(stringStats)]
    return result


def getStats(statTable):
    stats = {}
    currentRarity = "0"
    for i,tblData in enumerate(statTable):
        if i % 7 == 0:
            currentRarity = str(int(tblData.contents[0].encode("utf-8")))
            stats.update({("rarity" + currentRarity): {}})
        elif i % 7 == 1:
            stats["rarity" + currentRarity].update({"HP": listStats(str(tblData.string))})
        elif i % 7 == 2:
            stats["rarity" + currentRarity].update({"ATK": listStats(str(tblData.string))})
        elif i % 7 == 3:
            stats["rarity" + currentRarity].update({"SPD": listStats(str(tblData.string))})
        elif i % 7 == 4:
            stats["rarity" + currentRarity].update({"DEF": listStats(str(tblData.string))})
        elif i % 7 == 5:
            stats["rarity" + currentRarity].update({"RES": listStats(str(tblData.string))})
        elif i % 7 == 6:
            pass
        else:
            print("OVERFLOW ERROR: Table has more than 7 columns.")
    return stats

def getSkills(skillTables):
    skills = []
    for skillTypes in skillTables:
        for i, skillRow in enumerate(skillTypes("tr")):
            if i > 0:
                try:
                    skills.append("".join(skillRow.find("a").string.lower().split(" ")))
                except:
                    pass
    return skills


def getHeroData(url):
    response = requests.get(url)
    print("...",end="",flush=True)
    soup = BeautifulSoup(response.text, "html.parser")
    heroData = {}
    lvl1Stats = getStats(soup.find("span",{"id": "Level_1_stats"}).parent.next_sibling.find_all("td"))
    lvl40Stats = getStats(soup.find("span",{"id": "Level_40_stats"}).parent.next_sibling.find_all("td"))
    defaultSkills = getSkills(soup("table",{"class": "skills-table"}))
    print(".",end="",flush=True)
    heroData.update({"lvl1stats": lvl1Stats,
                                     "lvl40stats": lvl40Stats,
                                     "defaultskills": defaultSkills})
    return heroData

def getWeaponList():
    url = "https://feheroes.gamepedia.com/Weapons_(full)"
    response = requests.get(url)
    rawHTML = BeautifulSoup(response.text,"html.parser")
    lstWeaponHTML = rawHTML("td",{"class":"field_Name"})
    print("Found " + str(len(lstWeaponHTML)) + " weapons on Gamepedia")
    print("Building weapon database")
    dctWeapons = {}
    for weaponTag in lstWeaponHTML:
        dctWeapon = {}
        weaponName = weaponTag.find("a")["title"]
        weaponGPediaLink = "https://feheroes.gamepedia.com" + weaponTag.find("a")["href"]
        dctWeapon.update({
            "id": weaponName.lower().replace(" ",""),
            "name": weaponName,
            "gpedia": weaponGPediaLink
        })
        dctWeapons[dctWeapon["id"]] = dctWeapon
    print("Weapon database build complete")
    return dctWeapons

def getWeaponData(url):
    response = requests.get(url)
    print("...", end="", flush=True)
    soup = BeautifulSoup(response.text, "html.parser")
    weaponData = {}
    attributeList = []
    raw = soup.find("div",{"class": "hero-infobox"}).find_all("td")
    keys = soup.find("div",{"class": "hero-infobox"}).find_all("th")
    for key in keys:
        attributeList.append(key.text.strip('\n'))
    if len(raw) != len(keys):
        attributeList = attributeList[1:]
    weaponData["type"] = raw[attributeList.index("Weapon type")].find("a")["title"].lower()
    if ("red" in weaponData["type"]) and (weaponData["type"] != "red tome"):
        weaponData["type"] = weaponData["type"].strip("red ")
    weaponData["might"] = int(raw[attributeList.index("Might")].text)
    weaponData["range"] = int(raw[attributeList.index("Range")].text)
    weaponData["sp"] = int(raw[attributeList.index("SP")].text)
    try:
        weaponData["description"] = raw[attributeList.index("Description")].text.strip("\n")
    except:
        weaponData["description"] = ''
    try:
        raw = soup.find("span",{"id": "Upgrades"}).parent.next_sibling.next_sibling.next_sibling.next_sibling.find_all("td")[2]
        weaponData["refinable"] = 1
        try:
            refineDescription = raw.find("div").text.replace(raw.find("span").text,'')
            if refineDescription != weaponData["description"]:
                weaponData["refinedescription"] = raw.find("div").text.replace(raw.find("span").text,'')
            if weaponData["type"] != "staff":
                weaponData["specialrefine"] = raw.find("span").text
        except:
            pass
    except:
        weaponData["refinable"] = 0
    return weaponData

def getASkillData():
    print("Getting A Skills...")
    url = "https://feheroes.gamepedia.com/Passives"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    AskillData = {}
    raw = soup.find("span",{"id":"List_of_Type_A"}).parent.next_sibling.next_sibling.find("tbody")
    nameList = raw.find_all("td",{"class":"field_Name"})
    descList = raw.find_all("td",{"class":"field_Description"})
    spList = raw.find_all("td",{"class":"field_SP"})
    for i in range(len(nameList)):
        skillID = nameList[i].find("a").text.lower().replace(" ","_")
        AskillData[skillID] = {}
        AskillData[skillID]["id"] = skillID
        AskillData[skillID]["name"] = nameList[i].find("a").text
        AskillData[skillID]["description"] = descList[i].text
        AskillData[skillID]["sp"] = int(spList[i].text)
    for skill in AskillData:
        url = "https://feheroes.gamepedia.com/" + AskillData[skill]["name"].strip(" 1234").replace(" ","_")
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        restrictionsRaw = soup.find("td",{"colspan":"6"})
        AskillData[skill]["restrictions"] = []
        try:
            if "staff" in restrictionsRaw.text:
                AskillData[skill]["restrictions"].append("staffonly")
            elif "original unit" in restrictionsRaw.text:
                AskillData[skill]["restrictions"].append("unique")
            else:
                AskillData[skill]["restrictions"].append(img["alt"])
        except:
            pass
    return AskillData

def getBSkillData():
    print("Getting B Skills...")
    url = "https://feheroes.gamepedia.com/Passives"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    BskillData = {}
    raw = soup.find("span",{"id":"List_of_Type_B"}).parent.next_sibling.next_sibling.find("tbody")
    nameList = raw.find_all("td",{"class":"field_Name"})
    descList = raw.find_all("td",{"class":"field_Description"})
    spList = raw.find_all("td",{"class":"field_SP"})
    for i in range(len(nameList)):
        skillID = nameList[i].find("a").text.lower().replace(" ","_")
        BskillData[skillID] = {}
        BskillData[skillID]["id"] = skillID
        BskillData[skillID]["name"] = nameList[i].find("a").text
        BskillData[skillID]["description"] = descList[i].text
        BskillData[skillID]["sp"] = int(spList[i].text)
    for skill in BskillData:
        url = "https://feheroes.gamepedia.com/" + BskillData[skill]["name"].strip(" 1234").replace(" ","_")
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        restrictionsRaw = soup.find("td",{"colspan":"6"})
        BskillData[skill]["restrictions"] = []
        try:
            if "staff" in restrictionsRaw.text:
                BskillData[skill]["restrictions"].append("staffonly")
            elif "original unit" in restrictionsRaw.text:
                BskillData[skill]["restrictions"].append("unique")
            else:
                AskillData[skill]["restrictions"].append(img["alt"])
        except:
            pass
    return BskillData

def getCSkillData():
    print("Getting C Skills...")
    url = "https://feheroes.gamepedia.com/Passives"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    CskillData = {}
    raw = soup.find("span",{"id":"List_of_Type_C"}).parent.next_sibling.next_sibling.find("tbody")
    nameList = raw.find_all("td",{"class":"field_Name"})
    descList = raw.find_all("td",{"class":"field_Description"})
    spList = raw.find_all("td",{"class":"field_SP"})
    for i in range(len(nameList)):
        skillID = nameList[i].find("a").text.lower().replace(" ","_")
        CskillData[skillID] = {}
        CskillData[skillID]["id"] = skillID
        CskillData[skillID]["name"] = nameList[i].find("a").text
        CskillData[skillID]["description"] = descList[i].text
        CskillData[skillID]["sp"] = int(spList[i].text)
    for skill in CskillData:
        url = "https://feheroes.gamepedia.com/" + CskillData[skill]["name"].strip(" 1234").replace(" ","_")
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        restrictionsRaw = soup.find("td",{"colspan":"6"})
        CskillData[skill]["restrictions"] = []
        try:
            if "staff" in restrictionsRaw.text:
                CskillData[skill]["restrictions"].append("staffonly")
            elif "original unit" in restrictionsRaw.text:
                CskillData[skill]["restrictions"].append("unique")
            else:
                CskillData[skill]["restrictions"].append(img["alt"])    
        except:
            pass
    return CskillData

def getSacredSeals():
    print("Getting Sacred Seals...")
    url = "https://feheroes.gamepedia.com/Sacred_Seals"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    SacredSealData = {}
    raw = soup.find("span",{"id":"List_of_Sacred_Seals"}).parent.next_sibling.next_sibling
    nameList = raw.find_all("td",{"class":"field_Name"})
    descList = raw.find_all("td",{"class":"field_Description"})
    spList = raw.find_all("td",{"class":"field_SP"})
    for i in range(len(nameList)):
        sealID = nameList[i].find("a").text.lower().replace(" ","_")
        SacredSealData[sealID] = {}
        SacredSealData[sealID]["id"] = sealID
        SacredSealData[sealID]["name"] = nameList[i].find("a").text
        SacredSealData[sealID]["description"] = descList[i].text
        SacredSealData[sealID]["sp"] = int(spList[i].text)
    for skill in SacredSealData:
        url = "https://feheroes.gamepedia.com/" + SacredSealData[skill]["name"].strip(" 1234").replace(" ","_")
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        restrictionsRaw = soup.find("td",{"colspan":"6"})
        SacredSealData[skill]["restrictions"] = []
        try:
            if "staff" in restrictionsRaw.text:
                SacredSealData[skill]["restrictions"].append("staffonly")
            elif "original unit" in restrictionsRaw.text:
                SacredSealData[skill]["restrictions"].append("unique")
            else:
                SacredSealData[skill]["restrictions"].append(img["alt"])    
        except:
            pass
    return SacredSealData

def getSpecials():
    print("Getting Specials...")
    url = "https://feheroes.gamepedia.com/Specials"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    SpecialData = {}
    nameList = soup.find_all("td",{"class":"field_Name"})
    descList = soup.find_all("td",{"class":"field_Description"})
    spList = soup.find_all("td",{"class":"field_SP"})
    cooldownList = soup.find_all("td",{"class":"field_Cooldown"})
    for i in range(len(nameList)):
        specialID = nameList[i].find("a").text.lower().replace(" ","")
        SpecialData[specialID] = {}
        SpecialData[specialID]["id"] = specialID
        SpecialData[specialID]["name"] = nameList[i].find("a").text
        SpecialData[specialID]["description"] = descList[i].text
        SpecialData[specialID]["sp"] = int(spList[i].text)
        SpecialData[specialID]["cooldown"] = int(cooldownList[i].text)
    for special in SpecialData:
        url = "https://feheroes.gamepedia.com/" + SpecialData[special]["name"].replace(" ","_")
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        restrictionRaw = soup.find("td",{"colspan":"5"})
        SpecialData[special]["restrictions"] = []
        if "original unit" in restrictionRaw.text:
            SpecialData[special]["restrictions"].append("unique")
        elif "staff" in restrictionRaw.text:
            SpecialData[special]["restrictions"].append("staffonly")
        else:
            imgs = restrictionRaw.find_all("img")
            for img in imgs:
                SpecialData[special]["restrictions"].append(img["alt"])
    return SpecialData

def getAssists():
    print("Getting Assists...")
    url = "https://feheroes.gamepedia.com/Assists"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    AssistData = {}
    nameList = soup.find_all("td",{"class":"field_Name"})
    descList = soup.find_all("td",{"class":"field_Description"})
    spList = soup.find_all("td",{"class":"field_SP"})
    for i in range(len(nameList)):
        assistID = nameList[i].find("a").text.lower().replace(" ","")
        AssistData[assistID] = {}
        AssistData[assistID]["id"] = assistID
        AssistData[assistID]["name"] = nameList[i].find("a").text
        AssistData[assistID]["description"] = descList[i].text
        AssistData[assistID]["sp"] = int(spList[i].text)
    for assist in AssistData:
        url = "https://feheroes.gamepedia.com/" + AssistData[assist]["name"].replace(" ","_")
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        restrictionRaw = soup.find("td",{"colspan":"5"})
        AssistData[assist]["restrictions"] = []
        try:
            if "original unit" in restrictionRaw.text:
                AssistData[assist]["restrictions"].append("unique")
            elif "staff" in restrictionRaw.text:
                AssistData[assist]["restrictions"].append("staffonly")
            else:
                imgs = restrictionRaw.find_all("img")
                for img in imgs:
                    AssistData[assist]["restrictions"].append(img["alt"])
        except:
            AssistData[assist]["restrictions"].append("error")
    return AssistData