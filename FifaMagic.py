'''
File name: FifaMagic.py
Author: HeavenlyBerserker
Date created: 03/26/2019

-------------
Requirements:
-------------
This Python code runs using:
    -python IDLE 3.6.5 for Windows 10
    -selenium (from pip install as of 03/26/2019)
    -firefox(Quantum 62.0.2 64 bit)
    -geckodriver for firefox(from https://github.com/mozilla/geckodriver as of
        03/26/2019).
    
The program assumes you have theabove libraries and software and will error
out if you miss something.

------------
Description:
------------
The program uses geckodriver opened firefox browser to automate some trasfer
market actions on the FIFA web app.

--------------------------
Installation instructions:
--------------------------
Install python and firefox. Pip install selenium though python. Install
geckodriver for firefox from the github link. Preferably, use the same
versions of python, firefox, selenium and geckodriver.

-------------
Instructions:
-------------
Once everything is installed, you can write your code and run-test by the following:
    -Run script(the firefox browser will open, and you will have 10 seconds to
        click the install button to get FUT enhancer. Make sure FUT enhancer is
        running)
    -Login to your account (Do two step verification if required)
    -Press enter on python
    -Activate futbin integration on firefox
    -Press enter on python
    
-----------------------
Warning and disclaimer:
-----------------------
This code is very raw and was intended forpersonal use only. Please refrain
from any commercial use. Violate EA and FIFA guidelines at your own risk.
I take no reponsability for any bans or any other problems.

-------
Sources
-------
https://automatetheboringstuff.com/chapter11/
https://tampermonkey.net/
https://github.com/Mardaneus86/futwebapp-tampermonkey
https://github.com/mozilla/geckodriver

--------------------
Further development:
--------------------
I will not develop this code further. If you wish to modify/improve it, please
share with the community and give credit. Thank you.

Python Version: 3.6.5
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import os
import sys
import traceback

#------------------------
#Pushbullet functionality
#------------------------
import requests
import json

ACCESS_TOKEN = 'place PushBullet ACCESS_TOKEN here'
 
def send_notification_via_pushbullet(title, body):
    """ Sending notification via pushbullet.
        Args:
            title (str) : title of text.
            body (str) : Body of text.
    """
    data_send = {"type": "note", "title": title, "body": body}
 
    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Something wrong, did not send.')
    else:
        print('Sending Complete! Terminated well.')

def pushExit(mode, comment):
    if(mode == 0):
        title = "Exited with exception..."
        body = "Current time: " + str(datetime.datetime.now()) + "\nBought: " + str(statistics.bought) +"\nSold: " + str(statistics.sold) + "\nPractical Asset profit: " + str( statistics.coins + (statistics.bought-statistics.sold)*600 - statistics.startAssets) +"\nCurrt coins: " + str(statistics.coins) +"\n"
        send_notification_via_pushbullet(title, body)
    elif(mode == 1):
        title = "Unable to get FUTBIN..."
        body = "Current time: " + str(datetime.datetime.now()) + "\nBought: " + str(statistics.bought) +"\nSold: " + str(statistics.sold) + "\nPractical Asset profit: " + str( statistics.coins + (statistics.bought-statistics.sold)*600 - statistics.startAssets) +"\nCurrt coins: " + str(statistics.coins) +"\n"
        send_notification_via_pushbullet(title, body)

pushBullet = False

#--------
#Log file
#--------

tWrite = "#############################################\n Current Run:" + str(datetime.datetime.now()) + "\n#############################################\n"

print(tWrite)
with open("log.txt","a") as f:
    f.write(tWrite)

def writeTime():
    with open("log.txt","a") as f:
        f.write("Current time: " + str(datetime.datetime.now()) + "\n")

def writeNew(string):
    with open("log.txt","a") as f:
        f.write("\n--------------------------------------------------------------------------------------------------------------\n")
        f.write(string)

#----------------
#Global variables
#----------------
tlsize = 70
ttsize = 50
maxpricerelist = 10000
#Limit of the minutes
minuteLimit = 4
#Maximum times buying loop is ran
maxBuyLoop = 5
#Minimum amount of pages
minPage = 3
#Times try to do inputs
maxTime = 3
#low volume: true low players in market. false lots of players in market
low = False
#Amount of players bought to be considered low volume
lowThresh = 5
#Transfer market error check times >= 1, 2 best
tmCheck = 2
class g:
    #Is this the first run of the loop for log?
    firstRun = True

glob = g()

#-----------------
#Global Structures
#-----------------
class transferList:
    sold = []
    unsold = []
    available = []
    active = []
    avai = []
    count = 0

tl = transferList()

class transferTargets:
    activeBids = []
    watchedItems = []
    wonItems = []
    expiredItems = []
    avai = []
    count = 0

tt = transferTargets()

class marketPage:
    items = []
    count = 0

mp = marketPage()

class stats:
    bought = 0
    listed = 0
    sold = 0
    revenue = 0
    coins = 0
    startCoins = 0
    startAssets = 0

statistics = stats()

banlist = []

#-------------------
#Auxiliary functions
#-------------------

def writeStats():
    with open("log.txt","a") as f:
        f.write("------\n")
        f.write("Report\n")
        f.write("------\n")
        f.write("Current time: " + str(datetime.datetime.now()) + "\n")
        f.write("Currt coins: " + str(statistics.coins) +"\n")
        f.write("Start coins: " + str(statistics.startCoins) +"\n")
        f.write("Start asset: " + str(statistics.startAssets) +"\n")
        f.write("Asset coins: " + str(statistics.coins + (statistics.bought-statistics.sold)*600) +"\n")
        f.write("Bought: " + str(statistics.bought) +"\n")
        f.write("Listed: " + str(statistics.listed) +"\n")
        f.write("Sold: " + str(statistics.sold) +"\n")
        f.write("Revenue: " + str(statistics.revenue) +"\n")
        f.write("Expenses: " + str(statistics.bought * 700) +"\n")
        f.write("Min Profit: " + str( statistics.revenue - (statistics.bought * 700)) +"\n")
        f.write("Coin difference: " + str( statistics.coins - statistics.startCoins) +"\n")
        f.write("Practical Asset profit: " + str( statistics.coins + (statistics.bought-statistics.sold)*600 - statistics.startAssets) +"\n")
        f.write("Transfer List: " + str(tl.count - len(tl.sold)) +"\n")
        f.write("Transfer Targets: " + str(len(tt.wonItems)) +"\n")


def findAndRemove(s, text):
    i = text.find(s)
    if(i >= 0):
        start = i
        while(start < len(text) and text[start] != '>'):
            start+=1
        start+=1

        end = start
        while(end < len(text) and text[end] != '<'):
            end+=1
        
        return True, text[start:end], text[end+1:]
    else:
        return False, "", text

def beforeAfter(s1, s2, text):
    i = text.find(s1)
    j = text.find(s2)
    if(i >= 0 and j >= 0):
        if(i >= j):
            return 1
        else:
            return 0
    else:
        return -1

def printPlayer(player):
    print("\n")
    print(player)
    print("name = ", player[3])
    print("rating = ", player[1])
    print("quality = ", player[0])
    print("position = ", player[2])
    print(player[4], " = ", player[5])
    print(player[6], " = ", player[7])
    print(player[8], " = ", player[9])
    print(player[10], " = ", player[11])
    print(player[12], " = ", player[13])
    print(player[14], " = ", player[15])
    print("FUTBIN val = ", player[16])
    print("start val = ", player[17])
    print("bid val = ", player[18])
    print("buy val = ", player[19])
    print("listnum = ", player[20])

def printPlayerBasic(player):
    print("\n")
    print(player)
    print("name = ", player[3])
    print("rating = ", player[1])
    print("quality = ", player[0])
    print("listnum = ", player[20])

def printPlayerCondensed(player):
    print("name =", player[3], ";rating =", player[1], ";position =", player[2], ";FUTBIN val =", player[16], ";start val =", player[17], ";bid val =", player[18], ";buy val =", player[19], end = "")
    if(len(player) > 19):
        print(";Num =", player[20], ".")
    else:
        print(".")

def printTL():
    print("-----------\nSold\n-----------")
    for p in tl.sold:
        printPlayer(p)
    print("-----------\nUnsold\n-----------")
    for p in tl.unsold:
        printPlayer(p)
    print("-----------\nAvailable\n-----------")
    for p in tl.available:
        printPlayer(p)
    print("-----------\nActive\n-----------")
    for p in tl.active:
        printPlayer(p)

def printTT():
    print("-----------\nActive bids\n-----------")
    for p in tt.activeBids:
        printPlayer(p)
    print("-----------\nWatched Items\n-----------")
    for p in tt.watchedItems:
        printPlayer(p)
    print("-----------\nWon Items\n-----------")
    for p in tt.wonItems:
        printPlayer(p)
    print("-----------\nExpired Items\n-----------")
    for p in tt.expiredItems:
        printPlayer(p)

def printTLBasic():
    print("-----------\nSold\n-----------")
    for p in tl.sold:
        printPlayerBasic(p)
    print("-----------\nUnsold\n-----------")
    for p in tl.unsold:
        printPlayerBasic(p)
    print("-----------\nAvailable\n-----------")
    for p in tl.available:
        printPlayerBasic(p)
    print("-----------\nActive\n-----------")
    for p in tl.active:
        printPlayerBasic(p)

def printTLCondensed():
    print("-----------\nSold\n-----------")
    for p in tl.sold:
        printPlayerCondensed(p)
    print("-----------\nUnsold\n-----------")
    for p in tl.unsold:
        printPlayerCondensed(p)
    print("-----------\nAvailable\n-----------")
    for p in tl.available:
        printPlayerCondensed(p)
    print("-----------\nActive\n-----------")
    for p in tl.active:
        printPlayerCondensed(p)

def printTTBasic():
    print("-----------\nActive bids\n-----------")
    for p in tt.activeBids:
        printPlayerBasic(p)
    print("-----------\nWatched Items\n-----------")
    for p in tt.watchedItems:
        printPlayerBasic(p)
    print("-----------\nWon Items\n-----------")
    for p in tt.wonItems:
        printPlayerBasic(p)
    print("-----------\nExpired Items\n-----------")
    for p in tt.expiredItems:
        printPlayerBasic(p)

def printTTCondensed():
    print("-----------\nActive bids\n-----------")
    for p in tt.activeBids:
        printPlayerCondensed(p)
    print("-----------\nWatched Items\n-----------")
    for p in tt.watchedItems:
        printPlayerCondensed(p)
    print("-----------\nWon Items\n-----------")
    for p in tt.wonItems:
        printPlayerCondensed(p)
    print("-----------\nExpired Items\n-----------")
    for p in tt.expiredItems:
        printPlayerCondensed(p)

def readPlayer(transferHTML):
    player = []
    #Quality
    if(beforeAfter("common", "name", transferHTML) == 0):
        player.append("common")
    elif(beforeAfter("rare", "name", transferHTML) == 0):
        player.append("rare")
    elif(beforeAfter("specials", "name", transferHTML) == 0):
        player.append("specials")
    else:
        player.append("unknown")
        #print(transferHTML)

    rating = findAndRemove("rating", transferHTML)
    player.append(int(rating[1]))
    position = findAndRemove("position", transferHTML)
    player.append(position[1])
    name = findAndRemove("name", transferHTML)
    player.append(name[1])
    transferHTML = name[2]
    label = findAndRemove("label", transferHTML)
    value = findAndRemove("value", transferHTML)
    player.append(label[1])
    player.append(int(value[1]))
    transferHTML = value[2]
    label = findAndRemove("label", transferHTML)
    value = findAndRemove("value", transferHTML)
    player.append(label[1])
    player.append(int(value[1]))
    transferHTML = value[2]
    label = findAndRemove("label", transferHTML)
    value = findAndRemove("value", transferHTML)
    player.append(label[1])
    player.append(int(value[1]))
    transferHTML = value[2]
    label = findAndRemove("label", transferHTML)
    value = findAndRemove("value", transferHTML)
    player.append(label[1])
    player.append(int(value[1]))
    transferHTML = value[2]
    label = findAndRemove("label", transferHTML)
    value = findAndRemove("value", transferHTML)
    player.append(label[1])
    player.append(int(value[1]))
    transferHTML = value[2]
    label = findAndRemove("label", transferHTML)
    value = findAndRemove("value", transferHTML)
    player.append(label[1])
    player.append(int(value[1]))
    transferHTML = value[2]

    coins = findAndRemove("coins value", transferHTML)
    temp = coins[1].replace(',', '')
    if(temp != "---"):
        player.append(int(temp))
    else:
        player.append(900)
    transferHTML = coins[2]
    coins = findAndRemove("coins value", transferHTML)
    temp = coins[1].replace(',', '')
    if(temp != ""):
        player.append(int(temp))
    else:
        player.append(900)
    transferHTML = coins[2]
    coins = findAndRemove("coins value", transferHTML)
    temp = coins[1].replace(',', '')
    if(temp != ""):
        player.append(int(temp))
    else:
        player.append(900)
    transferHTML = coins[2]
    coins = findAndRemove("coins value", transferHTML)
    temp = coins[1].replace(',', '')
    if(temp != ""):
        player.append(int(temp))
    else:
        player.append(900)
    transferHTML = coins[2]
    return player, transferHTML

def getInfoFromSelected(browser):
    html = getTextByClass("listFUTItem has-auction-data selected",browser)
    return readPlayer(html)[0]

def parsTL(transferHTML):
    tl.avai = [0,0,0,0]
    tl.sold = []
    tl.unsold = []
    tl.available = []
    tl.active = []
    section = tl.sold
    count = 0
    if(transferHTML != "" and transferHTML.find("futbin") < 0):
        if(pushBullet):
            pushExit(1,"")
        print("FATAL ERROR: Futbin might be down or you don't have permission anymore.")
        sys.exit()
    while(1):
        if(beforeAfter("Sold Items", "name", transferHTML) == 0):
            section = tl.sold
        if(beforeAfter("Unsold Item", "name", transferHTML) == 0):
            section = tl.unsold
        if(beforeAfter("Available Items", "name", transferHTML) == 0):
            section = tl.available
        if(beforeAfter("Active Transfers", "name", transferHTML) == 0):
            section = tl.active
            
        if(beforeAfter("player item", "player item", transferHTML) >= 0):
            player,transferHTML = readPlayer(transferHTML)
            
            player.append(count)
            count = count + 1

            section.append(player)
        else:
            if(len(tl.sold) > 0):
                tl.avai[0] = 1
            if(len(tl.unsold) > 0):
                tl.avai[1] = 1
            if(len(tl.available) > 0):
                tl.avai[2] = 1
            if(len(tl.active) > 0):
                tl.avai[3] = 1
            tl.count = count
            break

def parsTT(transferHTML):
    tt.avai = [0,0,0,0]
    tt.activeBids = []
    tt.watchedItems = []
    tt.wonItems = []
    tt.expiredItems = []
    section = tt.activeBids
    count = 0
    while(1):
        if(beforeAfter("Active Bids", "name", transferHTML) == 0):
            section = tt.activeBids
        if(beforeAfter("Watched Items", "name", transferHTML) == 0):
            section = tt.watchedItems
        if(beforeAfter("Won Items", "name", transferHTML) == 0):
            section = tt.wonItems
        if(beforeAfter("Expired Items", "name", transferHTML) == 0):
            section = tt.expiredItems
            
        if(beforeAfter("player item", "player item", transferHTML) >= 0):
            player,transferHTML = readPlayer(transferHTML)
            
            player.append(count)
            count = count + 1

            if(player[19] <= player[17]):
                print("Warning: Futbin might be down or you don't have permission anymore.")
            
            section.append(player)
        else:
            if(len(tt.activeBids) > 0):
                tt.avai[0] = 1
            if(len(tt.watchedItems) > 0):
                tt.avai[1] = 1
            if(len(tt.wonItems) > 0):
                tt.avai[2] = 1
            if(len(tt.expiredItems) > 0):
                tt.avai[3] = 1
            tt.count = count
            break

def populateBanlist():
    banlist = []
    
    nameList = []
    ocList = []
    for p in tl.unsold:
        nameList.append(p[3])
    for p in tl.available:
        nameList.append(p[3])
    for p in tl.active:
        nameList.append(p[3])
    for p in tt.wonItems:
        nameList.append(p[3])

    for name in nameList:
        isIn = False
        for el in ocList:
            if(el[0] == name):
                el[1] = el[1] + 1
                isIn = True
        if(not isIn):
            ocList.append([name, 1])
    for oc in ocList:
        if(oc[1] >= 2):
            banlist.append(oc[0])
    print("Banlist:", banlist)

def inBanlist(name):
    return (name in banlist)

def clearExpired(browser):
    print("Clearing expired...")
    getTT(1,1,1,browser)
    if(len(tt.expiredItems)>0):
        button = browser.execute_script("return document.getElementsByClassName('btn-standard section-header-btn mini call-to-action')")
        button[3].click()
        time.sleep(1)
        getTT(1,1,1,browser)

def spinToClear(browser, wait):
    print("Waiting for bid players to expire...")
    if(wait):
        time.sleep(minuteLimit*30)
    wait = True
    while(wait):
        time.sleep(5)
        getTT(2,1,2,browser)
        if(len(tt.activeBids) == 0):
            wait = False
            
def redefineIndexesTT():
    count = 0
    for p in tt.activeBids:
        p[20] = count
        count = count + 1
    for p in tt.watchedItems:
        p[20] = count
        count = count + 1
    for p in tt.wonItems:
        p[20] = count
        count = count + 1
    for p in tt.expiredItems:
        p[20] = count
        count = count + 1
    tt.count = count

def getTL(w1,w2,w3,browser):
    text = getTextByClass("FUINavigation",browser)
    time.sleep(w1)
    if(text.find("Sold Items") < 0 and text.find("Unsold Items") < 0 and text.find("Available Items") < 0 and text.find("Active Transfers") < 0):
        clickTransfer(browser)
        time.sleep(1)
        clickClassNumPer('tile has-separator col-1-2 ut-tile-transfer-list',0,browser, 0)
        time.sleep(w2)
    getTransferListInfo(browser)
    time.sleep(w3)

def getTT(w1,w2,w3,browser):
    text = getTextByClass("FUINavigation",browser)
    time.sleep(w1)
    if(text.find("Active Bids") < 0 and text.find("Watched Items") < 0 and text.find("Won Items") < 0 and text.find("Expired Items") < 0):
        clickTransfer(browser)
        time.sleep(1)
        clickClass('tile has-separator col-1-2 ut-tile-transfer-targets',browser)
        time.sleep(w2)
    getTransferTargetsInfo(browser)
    time.sleep(w3)

#Wait wait time minutes
def waiting(waitTime,browser):
    waitTime = waitTime *60
    currtime = 0
    print("Waiting...", waitTime/60, "minutes","Current time: ", datetime.datetime.now(),".....")
    while(currtime < waitTime):
        print("Current time: ", datetime.datetime.now(), "... Last update: ", currtime/60, " minutes ago...")
        time.sleep(60)
        currtime = currtime + 60
        clickClass("view-tab-bar-item icon-home", browser)
        time.sleep(60)
        currtime = currtime + 60
        clickTransfer(browser)

#------------
#Multipurpose
#------------
def spinShield(browser, times):
    #shield = browser.execute_script("return document.getElementById('ClickShield"')")
    shield = browser.find_element_by_id('ClickShield')
    if(not shield.is_displayed()):
        return
    else:
        if(times <= 0):
            return
        time.sleep(2)
        spinShield(browser, times-1)
        return
    #shield = browser.execute_script("return document.getElementsById('ClickShield"')[0]")

def clickClass(clss,browser):
    spinShield(browser, 10)
    button = browser.execute_script("return document.getElementsByClassName('" + clss + "')")
    button = button[0]
    button.click()

def clickClassNum(clss,num,browser):
    spinShield(browser, 10)
    button = browser.execute_script("return document.getElementsByClassName('" + clss + "')")
    button = button[num]
    button.click()

def clickClassNumPer(clss,num,browser,times):
    try:
        button = browser.execute_script("return document.getElementsByClassName('" + clss + "')")
        button = button[num]
        button.click()
    except:
        if(times < maxTime):
            time.sleep(4)
            clickClassNumPer(clss,num,browser,times + 1)
        else:
            clickClassNum(clss,num,browser)

def getTextByClass(clss,browser):
    spinShield(browser, 10)
    try:
        content = browser.execute_script("return document.getElementsByClassName('" + clss +"') [0].innerHTML")
        return content
    except:
        return ""

def getTextByClassNum(clss,num, browser):
    spinShield(browser, 10)
    content = browser.execute_script("return document.getElementsByClassName('" + clss +"') ["+ str(num) +"].innerHTML")
    return content
    
#--------------
#Limited
#--------------
#Out of transfer tab
def clickTransfer(browser):
    '''
    transferButton = browser.execute_script("return document.getElementsByClassName('view-tab-bar-item icon-transfer')")
    transferButton = transferButton[0]
    transferButton.click()
    '''
    clickClassNum('view-tab-bar-item icon-transfer',0,browser)

#---------------
#In trasfers tab
#---------------
def getTransferTargetsInfo(browser):
    print("Getting Transfer Targets Info...")
    time.sleep(4)
    letgo = 0
    times = 0
    text = getTextByClass('nativeScrolling panel-list WatchList ui-layout-left',browser)
    while(letgo == 0):
        if(text.find("futbin") >= 0 or text == ""):
            letgo = 1
        else:
            if(times > maxTime):
                letgo = 1
            print("Error: Empty or no futbin.")
            times = times + 1
            time.sleep(5)
            text = getTextByClass('nativeScrolling panel-list WatchList ui-layout-left',browser)
    parsTT(text)

#Gets transfer list players info into transfer list struct tl
def getTransferListInfo(browser):
    print("Getting Transfer List Info...")
    time.sleep(4)
    letgo = 0
    times = 0
    text = getTextByClass('panel-list layout-sectioned-list ui-layout-left',browser)
    while(letgo == 0):
        if(text.find("futbin") >= 0 or text == ""):
            letgo = 1
        else:
            if(times > maxTime):
                letgo = 1
            print("Error: Empty or no futbin.")
            times = times + 1
            time.sleep(5)
            text = getTextByClass('panel-list layout-sectioned-list ui-layout-left',browser)
    parsTL(text)
    
    

#------------------
#In trasfer targets
#------------------


def listPlayer(num, ind, bid, buynow, browser):
    if(tl.count >= tlsize):
        print("ERROR: Trasfer List size limit has been reached.")
    else:
        time.sleep(0.5)
        '''
        buttons = browser.execute_script("return document.getElementsByClassName('listFUTItem has-auction-data')")
        buttons[num].click()
        '''
        clickClassNumPer('listFUTItem has-auction-data',num,browser,0)
        time.sleep(2.5)
        
        #Listing player number num
        clickClass("accordian",browser)
        time.sleep(2.5)
        inputs = browser.execute_script("return document.getElementsByClassName('numericInput filled')")
        inputs[0].click()
        inputs[0].send_keys(str(bid))
        time.sleep(1)
        inputs[1].click()
        time.sleep(0.5)
        inputs[1].send_keys(str(buynow))
        time.sleep(0.2)
        inputs[0].click()
        time.sleep(2)
        clickClassNumPer("btn-standard call-to-action",4,browser,0)
        time.sleep(1)
        statistics.listed = statistics.listed + 1

        tt.wonItems.pop(ind)
        redefineIndexesTT()
        
        time.sleep(1)
        tl.count = tl.count+1
        tt.count = tt.count-1

#Policy
def listingLoop(browser):
    getTT(0,2,1,browser)
    goods = 0
    for i in range(len(tt.wonItems)):
        if(tt.wonItems[i][16] >= 750):
            goods = goods + 1

    needed = min(tlsize - tl.count, len(tt.wonItems))
        
    print("-------------------\nTrying to list ", needed, " players. Good players:", goods ,'/',len(tt.wonItems) ,". Needed:",tlsize - tl.count,"\n-------------------")
    
    for i in range(needed):
        maxifutbin = tt.wonItems[0][16]
        maxi = 0
        for j in range(len(tt.wonItems)):
            if(tt.wonItems[j][16] > maxifutbin):
                maxifutbin = tt.wonItems[j][16]
                maxi = j

        
        p = tt.wonItems[maxi]
        
        if(p[16] >= 800):
            print("Listing player: ", p[3], end = '')
            try:
                if(p[16] >= 700 and p[16] <= 800):
                    listPlayer(p[20],maxi, 850, 900, browser)
                    print(" for B = 850 BN = 900.")
                elif(p[16] == 850):
                    listPlayer(p[20],maxi, 850, 900, browser)
                    print(" for B = 850 BN = 900.")
                elif(p[16] >= 850 and p[16] <= 950):
                    listPlayer(p[20],maxi, p[16] - 50, p[16] + 50, browser)
                    print(" for B = ",p[16] - 50," BN = ", p[16] + 50)
                elif(p[16] > 950 and p[16] <= 1200):
                    listPlayer(p[20],maxi, p[16] - 100, p[16], browser)
                    print(" for B = ",p[16] - 100," BN = ", p[16])
                elif(p[16] > 1200 and p[16] <= 2000):
                    listPlayer(p[20],maxi, p[16] - 200, p[16], browser)
                    print(" for B = ",p[16] - 200," BN = ", p[16])
                elif(p[16] > 2000 and p[16] <= 10000):
                    listPlayer(p[20],maxi, p[16] - 300, p[16], browser)
                    print(" for B = ",p[16] - 300," BN = ", p[16])
                print("Done")
            except:
                print("Transfer list reading error: Probably full. Please check.")
                    

#---------------
#In trasfer list
#---------------

def redefineIndexesTL():
    count = 0
    for p in tl.sold:
        p[20] = count
        count = count + 1
    for p in tl.unsold:
        p[20] = count
        count = count + 1
    for p in tl.available:
        p[20] = count
        count = count + 1
    for p in tl.active:
        p[20] = count
        count = count + 1
    tl.count = count

def relistPlayer(num, ind, bid, buynow, browser):
    buttons = browser.execute_script("return document.getElementsByClassName('listFUTItem has-auction-data')")
    buttons[num].click()
    time.sleep(2)

    p = getInfoFromSelected(browser)
    if(p[3] == tl.unsold[ind][3]):
    
        #Listing player number num
        clickClass("accordian",browser)
        time.sleep(1.5)
        inputs = browser.execute_script("return document.getElementsByClassName('numericInput filled')")
        inputs[0].click()
        inputs[0].send_keys(str(bid))
        time.sleep(1)
        inputs[1].click()
        time.sleep(0.5)
        inputs[1].send_keys(str(buynow))
        time.sleep(0.5)
        inputs[0].click()
        time.sleep(1)
        clickClassNum("btn-standard call-to-action",4,browser)
        time.sleep(2)

        tl.active.append(tl.unsold[ind])
        tl.unsold.pop(ind)
        redefineIndexesTL()
        time.sleep(1)
    else:
        print("Error, changed ", p[3], tl.unsold[ind][3])
        time.sleep(1)
        clickTransfer(browser)
        time.sleep(2)
        getTL(1,1,1,browser)

#Policy
def relistingLoop(browser):
    getTL(1,1,1,browser)
    goods = 0
    for i in range(len(tl.unsold)):
        p = tl.unsold[i]
        if((p[16] + 50 < p[19] or p[16] > p[19]+100) and p[19] <= maxpricerelist):
            goods = goods + 1
            
    print("-------------------\nTrying to relist ", goods, " players for a different price.\n-------------------")
    
    for i in range(goods):
        maxi = 0
        for j in range(len(tl.unsold)):
            if((tl.unsold[j][16] + 50 < tl.unsold[j][19] or tl.unsold[j][16] > tl.unsold[j][19] + 100) and tl.unsold[j][19] <= maxpricerelist):
                maxi = j
                break
        try:
            p = tl.unsold[maxi]

            if(p[16] >= 850):
                print("Relisting player: ", p[3], end = '')
                if(p[16] == 850):
                    relistPlayer(p[20],maxi, 850, 900, browser)
                    print(" for B = 850 BN = 900.")
                elif(p[16] >= 850 and p[16] <= 950):
                    relistPlayer(p[20],maxi, p[16] - 50, p[16] + 50, browser)
                    print(" for B = ",p[16] - 50," BN = ", p[16] + 50)
                elif(p[16] > 950 and p[16] <= 1200):
                    relistPlayer(p[20],maxi, p[16] - 100, p[16], browser)
                    print(" for B = ",p[16] - 100," BN = ", p[16])
                elif(p[16] > 1200 and p[16] <= 2000):
                    relistPlayer(p[20],maxi, p[16] - 200, p[16], browser)
                    print(" for B = ",p[16] - 200," BN = ", p[16])
                elif(p[16] > 2000 and p[16] <= 10000):
                    relistPlayer(p[20],maxi, p[16] - 300, p[16], browser)
                    print(" for B = ",p[16] - 300," BN = ", p[16])
                print("Done")
            else:
                print("Relisting player: ", p[3], end = '')
                if(p[16] >= 650):
                    relistPlayer(p[20], maxi, p[16], p[16] + 50, browser)
                    print(" for B = ",p[16] , " BN = ",p[16] + 50 ,".")
                else:
                    print("Under 650, please relist manually.")
                    time.sleep(1)
                    
                print("Done")
        except:
            traceback.print_exc()
            print("Error: Expired while relisting. Retrying")
            getTL(1,2,2,browser)
            relistingLoop(browser)
            break
    time.sleep(1)
            
    
#Clears and relists players
def clearAndRelist(browser):
    getTL(1,1,0.3,browser)
    print("Clearing sold and relisting on transfer list...")
    if(tl.avai[0] != 0):
        statistics.sold = statistics.sold + len(tl.sold)
        for p in tl.sold:
            statistics.revenue = statistics.revenue + p[18]
        statistics.coins = int(getTextByClass("view-navbar-currency-coins",browser).replace(',', ''))
        writeStats()
        button = browser.execute_script("return document.getElementsByClassName('btn-standard section-header-btn mini call-to-action')")
        if(tl.avai[1] != 0):
            button[0].click()
            time.sleep(1)
            clickTransfer(browser)
            time.sleep(2)
            clickClass('tile has-separator col-1-2 ut-tile-transfer-list',browser)
            time.sleep(2)
            spinShield(browser, 10)
            rel = browser.execute_script("return document.getElementsByClassName('btn-standard section-header-btn mini call-to-action')")
            rel[1].click()
            time.sleep(2)
            yes = browser.execute_script("return document.getElementsByClassName('flat')")
            yes = yes[1]
            yes.click()
        else:
            button[0].click()
    elif(tl.avai[1] != 0):
        button = browser.execute_script("return document.getElementsByClassName('btn-standard section-header-btn mini call-to-action')")
        button[1].click()
        time.sleep(2)
        yes = browser.execute_script("return document.getElementsByClassName('flat')")
        yes = yes[1]
        yes.click()
    getTL(1,1,1,browser)

#-----------
#From market
#-----------
def parsMp(transferHTML):
    mp.items = []
    count = 0
    if(transferHTML != "" and transferHTML.find("futbin") < 0):
        if(pushBullet):
            pushExit(1,"")
        print("FATAL ERROR: Futbin might be down or you don't have permission anymore.")
        sys.exit()
    while(1):
        if(beforeAfter("player item", "player item", transferHTML) >= 0):
            player,transferHTML = readPlayer(transferHTML)
            
            player.append(count)
            count = count + 1

            mp.items.append(player)
        else:
            mp.count = count
            break

#Gets transfer market page html
def getTransferMarketInfo(browser):
    time.sleep(2)
    letgo = 0
    times = 0
    text = getTextByClass('paginated-item-list',browser)
    while(letgo == 0):
        if(text.find("futbin") >= 0 or text == ""):
            letgo = 1
        else:
            if(times > maxTime):
                letgo = 1
            print("Error: Empty or no futbin.")
            times = times + 1
            time.sleep(5)
            text = getTextByClass('paginated-item-list',browser)
    parsMp(text)

#Bids on Player
#Outputs
# 1 = bid and continue
# 0 = bid but stop
# -1 = not listed because expired
# -2 = not listed because already had a bid
# -3 = changed while listing
def bidPlayer(num, maxBid, futbin, browser):
    #buttons = browser.execute_script("return document.getElementsByClassName('listFUTItem has-auction-data')")
    #buttons[num].click()
    clickClassNumPer("listFUTItem has-auction-data",num,browser,0)
    time.sleep(0.5)

    sorc = getTextByClassNum("secondary subHeading",1, browser)
    t = getTextByClass("subContent", browser)
    coins = int((getTextByClass("coins subContent", browser).replace(",", "")))
    if(sorc == "Start Price:"):
        print("Start Price: ", coins)
    else:
        print("Current bid: ", coins)
    parts = t.split()
    parts[0] = parts[0].strip('&lt;')
    if(parts[0] == "Expired" or parts[0] == "Processing..."):
        return -1
    parts[0] = int(parts[0])
    #print("Sorc|", sorc, "|parts", parts)
    time.sleep(0.5)
    w = getTextByClass("btn-toggle mini watch", browser)

    if(w == "Watch" and (sorc == "Start Price:" or (coins == 650 and futbin >= 1000))):
        if(t != "1 Second" and t != "Processing..." and t != "Expired"):
            clickClass("btn-standard call-to-action bidButton", browser)
            time.sleep(2.5)
            w = getTextByClass("btn-toggle mini watch", browser)
            if(w == "Watch"):
                time.sleep(3)
                w = getTextByClass("btn-toggle mini watch", browser)
                if(w == "Watch"):
                    return -3
            if(parts[1] == "Hour" or parts[1] == "Hours" or parts[1] == "Day" or parts[1] == "Days"):
                return 0
            elif(parts[1] == "Minute" or parts[1] == "Minutes"):
                if(parts[0] >= minuteLimit):
                    return 0
                else:
                    return 1
            return 1
        else:
            return -1
    else:
        return -2
    
    
#--------------------
#Pretty much anywhere
#--------------------    
    

def search600(browser):
    time.sleep(1)
    clickTransfer(browser)
    time.sleep(2)
    clickClass("tile col-1-1 ut-tile-transfer-market", browser)
    time.sleep(3)
    clickClass("inline-list-select ut-search-filter-control has-default has-image", browser)
    time.sleep(0.5)
    clickClassNum("with-icon", 3, browser)
    time.sleep(0.5)
    
    inputs = browser.execute_script("return document.getElementsByClassName('numericInput')")
    inputs[0].click()
    inputs[0].send_keys("600")
    time.sleep(0.5)
    inputs[1].click()
    time.sleep(0.5)
    inputs[1].send_keys("650")
    time.sleep(0.5)
    inputs[0].click()
    time.sleep(0.5)

    clickClass("btn-standard call-to-action",browser)
    time.sleep(3)

def bidAndBuy600Opt(browser, looking, times):
    populateBanlist()
    search600(browser)
    bidon = 0
    print("-------------------\nLooking for", looking, "players.\n-------------------")
    numBid = 0
    page = 0

    if(times > 0):
        while(bidon < looking):
            getTransferMarketInfo(browser)
            print("Gotten", bidon, "/", looking, ".")
            for p in mp.items:
                if(bidon >= looking):
                    break
                if(not inBanlist(p[3]) and p[0] == "rare" and p[1] >= 78 and p[16] >= 850 and p[18] <= 650):
                    val = bidPlayer(p[20], 650, p[16], browser)
                    if(val == 1):
                        bidon = bidon + 1
                        numBid = numBid + 1
                        print("Bid on", p[3], "for 650, Futbin", p[16])
                    elif(val == 0):
                        bidon = bidon + 1
                        numBid = numBid + 1
                        print("Bid on", p[3], "for 650, Futbin", p[16])
                        if(page < minPage):
                            numBid = numBid + bidAndBuy600Opt(browser, looking-numBid, times -1)
                            print("Transfer market page error, rechecking.")
                        bidon = looking
                        break
                    elif(val == -1):
                        print("Tried to bid on", p[3], "for 650, Futbin", p[16], "but expired.")
                    elif(val == -2):
                        print("Tried to bid on", p[3], "for 650, Futbin", p[16], "but current bid too high.")
                    elif(val == -3):
                        print("Tried to bid on", p[3], "for 650, Futbin", p[16], "but it changed while listing.")
                    
            #Check if last player over aloted time
            p = mp.items[len(mp.items) - 1]
            time.sleep(0.5)
            buttons = browser.execute_script("return document.getElementsByClassName('listFUTItem has-auction-data')")
            buttons[p[20]].click()
            time.sleep(0.5)

            t = getTextByClass("subContent", browser)
            parts = t.split()
            parts[0] = parts[0].strip('&lt;')
            if(parts[0] == "Expired" or parts[0] == "Processing..."):
                parts[0] = 1
                parts.append("Seconds")
            else:
                parts[0] = int(parts[0])

            if(parts[1] == "Hour" or parts[1] == "Hours" or parts[1] == "Day" or parts[1] == "Days"):
                if(page < minPage):
                    numBid = numBid + bidAndBuy600Opt(browser, looking-numBid, times -1)
                    print("Transfer market page error, rechecking.")
                bidon = looking
                break
            elif(parts[1] == "Minute" or parts[1] == "Minutes"):
                if(parts[0] >= minuteLimit):
                    if(page < minPage):
                        numBid = numBid + bidAndBuy600Opt(browser, looking-numBid, times - 1)
                        print("Transfer market page error, rechecking.")
                    bidon = looking
                    break
                
            #Next page
            clickClass("flat pagination next", browser)
            page = page + 1
            print("Page", page)
            time.sleep(2)
        
    return numBid    

def bidAndBuy600(browser):
    populateBanlist()
    search600(browser)
    bidon = 0
    looking = 50 - tt.count
    print("-------------------\nLooking for", looking, "players.\n-------------------")
    numBid = 0
    page = 3
    
    while(bidon < looking):
        getTransferMarketInfo(browser)
        for p in mp.items:
            if(bidon >= looking):
                break
            if(not inBanlist(p[3]) and p[0] == "rare" and p[1] >= 78 and p[16] >= 850 and p[18] <= 650):
                val = bidPlayer(p[20], 650, p[16], browser)
                if(val == 1):
                    bidon = bidon + 1
                    numBid = numBid + 1
                    print("Bid on", p[3], "for 650, Futbin", p[16])
                elif(val == 0):
                    bidon = bidon + 1
                    numBid = numBid + 1
                    print("Bid on", p[3], "for 650, Futbin", p[16])
                    bidon = looking
                    break
                elif(val == -1):
                    print("Tried to bid on", p[3], "for 650, Futbin", p[16], "but expired.")
                elif(val == -2):
                    print("Tried to bid on", p[3], "for 650, Futbin", p[16], "but current bit too high.")
                
        #Check if last player over aloted time
        p = mp.items[len(mp.items) - 1]
        buttons = browser.execute_script("return document.getElementsByClassName('listFUTItem has-auction-data')")
        buttons[p[20]].click()
        time.sleep(0.5)

        t = getTextByClass("subContent", browser)
        parts = t.split()
        parts[0] = parts[0].strip('&lt;')
        if(parts[0] != "Expired" or parts[0] != "Processing..."):
            parts[0] = int(parts[0])
            if(parts[1] == "Hour" or parts[1] == "Hours" or parts[1] == "Day" or parts[1] == "Days"):
                bidon = looking
                break
            elif(parts[1] == "Minute" or parts[1] == "Minutes"):
                if(parts[0] >= minuteLimit):
                    bidon = looking
                    break
            
        #Next page
        clickClass("flat pagination next", browser)
        page = page + 1
        time.sleep(2)
        
    return numBid        
    

#Clear and relist loop
#Updates every updateFrame minutes
#Does this for maxI iterations
    #Run where home button is available
def updateLoop(updateFrame, maxI, browser):
    updateFrame = updateFrame*60
    if(maxI == -1):
        maxI = 2147483647
    print("------------------------\nRelisting every ", updateFrame/60, " minutes.\n------------------------")
    iterations = 0
    
    while(iterations < maxI):
        currtime = 0
        while(currtime < updateFrame):
            print("Current time: ", datetime.datetime.now(), "\nLast update: ", currtime/60, " minutes ago.\n")
            time.sleep(60)
            currtime = currtime + 60
            clickClass("view-tab-bar-item icon-home", browser)
            time.sleep(60)
            currtime = currtime + 60
        time.sleep(5)
        getTL(1,1,1,browser)
        time.sleep(1)
        printTLCondensed()
        time.sleep(3)
        clearAndRelist(browser)
        iterations = iterations + 1



#++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Clear, relist, list from targets, and buys optimized loop
#Updates every updateFrame minutes
#Does this for maxI iterations
    #Run where home button is available
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def updateLoopTargetsBuy(updateFrame, maxI, browser):
    updateFrame = updateFrame*60
    global low
    global minuteLimit
    global maxBuyLoop
    global minPage
    global tmCheck
    if(maxI == -1):
        maxI = 2147483647
    print("------------------------------------------------------\nRelisting every", updateFrame/60, "minutes.\n------------------------------------------------------")
    iterations = 0
    buyCount = 0

    
    while(iterations < maxI):
        currtime = 0
        print("------------------------\nStage 0: Waiting.\n------------------------")
        if(iterations > 0):
            print("--------\nWaiting...", updateFrame/60, "minutes","Current time: ", datetime.datetime.now(),".\n--------")
            while(currtime < updateFrame and tt.count > 30):
                print("Current time: ", datetime.datetime.now(), "\nLast update: ", currtime/60, " minutes ago.\n")
                time.sleep(60)
                currtime = currtime + 60
                clickClass("view-tab-bar-item icon-home", browser)
                time.sleep(60)
                currtime = currtime + 60
                clickTransfer(browser)

        print("------------------------\nStage 1: relisting, and clearing expired.\n------------------------")
        #Relist transfers
        relistingLoop(browser)
        if(glob.firstRun and iterations == 0):
            statistics.bought = tl.count
            statistics.startCoins = int(getTextByClass("view-navbar-currency-coins",browser).replace(',', ''))
            statistics.startAssets = statistics.startCoins + (statistics.bought-statistics.sold)*600
            glob.firstRun = False
        time.sleep(1)

        #Clears and relists the rest
        clearAndRelist(browser)
        time.sleep(1)

        #Clears expired
        clearExpired(browser)
        
        lis = True

        #-----------
        #Bid and buy
        #-----------
        if(iterations == 0 or len(tt.wonItems) <= 30):
            bids = 0
            loops = 0
            while(tt.count + bids < 40 and loops < maxBuyLoop):
                print("------------------------\nStage 2: Buying, relisting, waiting, listing, and cleaning.\n------------------------")
                buyCount = 0
                ttwon = len(tt.wonItems)
                
                #Bid and buy
                bids = bidAndBuy600Opt(browser,50 - tt.count, 2)
                print(bids,"players bid on.")
                if(bids > 0):
                    lis = False

                    #Relist transfers
                    relistingLoop(browser)
                    time.sleep(1)

                    #Clears and relists the rest
                    clearAndRelist(browser)
                    time.sleep(1)
                    
                    spinToClear(browser,False)

                    #Calculating won players
                    ttwonnow = len(tt.wonItems) - ttwon
                    print("Won: ", ttwonnow, "/", bids, ".")
                    statistics.bought = statistics.bought + ttwonnow

                    #Determining if volume change
                    if(not low and len(tt.wonItems) <= lowThresh):
                        print("===========================\nSwitched to low volume\n===========================")
                        low = True
                        minuteLimit = 5
                        maxBuyLoop = 10
                        minPage = 2
                        tmCheck = 1
                    elif(low and len(tt.wonItems) > lowThresh):
                        print("===========================\nSwitched to notmal volume\n===========================")
                        low = False
                        minuteLimit = 4
                        maxBuyLoop = 5
                        minPage = 3
                        tmCheck = 2

                    #List trasfers
                    listingLoop(browser)

                    #Gets current transfer target and info
                    time.sleep(1)
                    clearExpired(browser)

                    #Gets current transfer target and info
                    getTL(1,2,1,browser)
                else:
                    lis = True

                if(low):
                    waiting(0.5,browser)
                    
                loops = loops + 1
        #-----------

        print("------------------------\nStage 3: Wrap up cycle.\n------------------------")
        if(lis or tl.count <= 60):
            #List trasfers
            listingLoop(browser)

        time.sleep(1)
        clearExpired(browser)
        time.sleep(1)
        
        iterations = iterations + 1

def failSafeCompleteUpdate(updateFrame, maxI, browser, failNum):
    try:
        updateLoopTargetsBuy(updateFrame, maxI, browser)
    except:
        if(pushBullet):
            traceback.print_exc()
            pushExit(0,"")
        '''
        if(failNum > 0):
            print("##############################\nERROR: Trying again\n##############################")
            failSafeCompleteUpdate(updateFrame, maxI, buyInterval,browser, failNum-1)
        else:
            try:
                print("##############################\nERROR: Trying basic loop\n##############################")
                updateLoop(updateFrame, maxI, browser)
            except:
                print("##############################\nFATAL ERROR\n##############################")
        '''
    

###############
#Main function#
###############
def main():
    browser = webdriver.Firefox()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    extensions = [
    '\\tampermonkey-4.8.5847-an+fx.xpi',
    ]
 
    for extension in extensions:
        browser.install_addon(dir_path + extension, temporary=True)

    #https://openuserjs.org/install/Mardaneus86/FUT_Enhancer.user.js
    #https://openuserjs.org/scripts/Mardaneus86/FUT_Enhancer
    browser.get('https://openuserjs.org/install/Mardaneus86/FUT_Enhancer.user.js')
    time.sleep(10)

    print("Openning FIFA")
    browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    browser.get('https://www.easports.com/fifa/ultimate-team/web-app/')

    input("Press Enter once you're logged in...")

    clickClass("futsettings-toggle standard mini call-to-action",browser)
    time.sleep(0.5)
    input("Press Enter after clicking FUTBIN integration")
    clickClass("futsettings-toggle standard mini call-to-action",browser)

    browser.execute_script("document.getElementsByClassName('view-tab-bar-item icon-transfer') [0].click()") #browser.find_element_by_class_name("view-tab-bar-item icon-transfer")

    #Relist loop
    failSafeCompleteUpdate(8, -1, browser,5)
    #failSafeCompleteUpdate(12, -1, 120, browser, 0)
    #updateLoop(20, 40, browser)

    print("Loop finished or terminated. \n Please provide command.\n 1 when you are ready try again (At home of web app), or 0 to exit.")
    cmdType = 1
    command = ""
    while(command != 0):
        cmdType = input("Input command type: ")
        if(cmdType == ""):
            cmdType = 1
        else:
            cmdType = int(cmdType)
        
        
        if(cmdType == 1):
            failSafeCompleteUpdate(8, -1, browser,5)
            print("Restarting run...\n")
        elif(cmdType == 0):
            print("Exiting...")
    
    input("Prigram ended. Press Enter to exit...")


main()
