"""
TODO Split up multiple observers
"""
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import numpy as np
from bs4 import BeautifulSoup
#try:
#    from urllib import urlopen
#except:
#    from urllib.request import urlopen
from urllib.request import urlopen
import ssl
import pandas as pd

from datetime import datetime
from astropy.time import Time

month2int = dict(zip(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                       range(1,13)))

def parse_date(items, year):
    month, day = items[0].get_text().split()
    #day  = items[1].get_text()
    dark_frac = float(items[2].get_text())
    dt = Time(datetime(year, month2int[month], int(day)))

    return dt, dark_frac

def add_line(prev, institution, observer, instruments):
    institution = institution.get_text().strip()
    observer = observer.get_text().strip()
    instruments = [x.get_text().strip() for x in instruments]
    while True:
        try:
            instruments.remove('')
        except:
            break
    instruments = "/".join(instruments)

    # Fill in quotation marks
    if institution == '"':
        try:
            institution = prev[-1][0]
        except IndexError as e:
            print("Error reading institution")
            print(e)
            institution = "error"
    if observer == '"':
        try:
            observer = prev[-1][1]
        except IndexError as e:
            print("Error reading observer")
            print(e)
            observer = "error"
    if '"' in instruments or u"\u201c" in instruments:
        if prev == []:
            instruments = "[Error]"
        else:
            instruments = prev[-1][2]
    
    prev.append([institution, observer, instruments])
    return

def parse_address(address):
    r = urlopen(address,context=ssl._create_unverified_context()).read()
    soup = BeautifulSoup(r)
    
    ## Lists to store data
    dates  = []
    dfracs = []
    baade  = []
    clay   = []
    dupont = []
    swope  = []
    

    rows = soup.find_all("tr")
    year = int(rows[0].find_all("td")[0].get_text())
    N = len(rows[0].find_all("td"))
    print(address,N)
    N_expected = 20
    
    # Hardcode May 2023 for LLAMAS
    if "2023_05" in address:
        print("Detected 2023_05, assuming LLAMAS")
        baade_has_fp2 = True
    else:
        baade_has_fp2 = False
    
    if N == 21 and not baade_has_fp2:
        clay_has_cassegrain = True
    else:
        clay_has_cassegrain = False
    
    for i,row in enumerate(rows):
        items = row.find_all("td")
        try:
            date, dark_frac = parse_date(items, year)
        except:
            #print("Skipping row {} = {}".format(i,row))
            continue
        dates.append(date)
        dfracs.append(dark_frac)
        claystart = 0
        if baade_has_fp2:
            add_line(baade, items[3], items[4], items[5:10])
            claystart = 1
        else:
            add_line(baade, items[3], items[4], items[5:9])
        if clay_has_cassegrain:
            add_line(clay,  items[claystart+10], items[claystart+11],items[claystart+12:claystart+15])
            add_line(dupont,items[claystart+16], items[claystart+16],[items[claystart+17]])
            add_line(swope, items[claystart+19], items[claystart+19],[items[claystart+20]])
        else:
            add_line(clay,  items[claystart+10], items[claystart+11],items[claystart+12:claystart+14])
            add_line(dupont,items[claystart+15], items[claystart+15],[items[claystart+16]])
            add_line(swope, items[claystart+18], items[claystart+18],[items[claystart+19]])
    return dates, dfracs, baade, clay, dupont, swope

if __name__=="__main__":
    addresses = []
    addresses += ["https://schedule.obs.carnegiescience.edu/2015/sch2015_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2016/sch2016_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2017/sch2017_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2018/sch2018_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2019/sch2019_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2020/sch2020_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2021/sch2021_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2022/sch2022_{:02}.html".format(num)
                 for num in range(1,13)]
    addresses += ["https://schedule.obs.carnegiescience.edu/2023/sch2023_{:02}.html".format(num)
                 for num in range(1,7)]
    
    dates  = []
    dfracs = []
    baade  = []
    clay   = []
    dupont = []
    swope  = []
    
    for address in addresses:
        out = parse_address(address)
        dates  += out[0]
        dfracs += out[1]
        baade  += out[2]
        clay   += out[3]
        dupont += out[4]
        swope  += out[5]
        
    index = list(map(lambda x: x.iso.split()[0], dates))
    
    baade = pd.DataFrame(baade, index=index, columns=['Institution','Observer','Instruments'])
    clay  = pd.DataFrame(clay,  index=index, columns=['Institution','Observer','Instruments'])
    dupont= pd.DataFrame(dupont,index=index, columns=['Institution','Observer','Instruments'])
    swope = pd.DataFrame(swope, index=index, columns=['Institution','Observer','Instruments'])
    
    baade["DarkFrac"] = dfracs
    clay["DarkFrac"] = dfracs

    magellan = pd.concat([baade,clay], axis=0)
    magellan["Telescope"] = "     "
    magellan["Telescope"].iloc[0:len(baade)] = "Baade"
    magellan["Telescope"].iloc[len(baade):] = "Clay"

    myname = "Ji"
    meclay = np.array([myname in x for x in clay["Observer"]])
    mebaade = np.array([myname in x for x in baade["Observer"]])
    medupont = np.array([myname in x for x in dupont["Observer"]])
    
    print("=====Clay=====")
    print(clay[meclay])
    
    print("\n=====Baade=====")
    print(baade[mebaade])

    print("\n=====DuPont=====")
    print(dupont[medupont])
    #carnegie_ii = magellan["Institution"]=="Carnegie"
    #print(magellan[carnegie_ii]["Observer"].value_counts())
    
    
