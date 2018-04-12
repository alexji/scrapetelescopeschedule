"""
TODO Split up multiple observers
"""

from bs4 import BeautifulSoup
import urllib
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
    institution = institution.get_text()
    observer = observer.get_text()
    instruments = [x.get_text() for x in instruments]
    while True:
        try:
            instruments.remove('')
        except:
            break
    instruments = "/".join(instruments)

    # Fill in quotation marks
    if institution == '"':
        institution = prev[-1][0]
    if observer == '"':
        observer = prev[-1][1]
    if '"' in instruments:
        instruments = prev[-1][2]
    
    prev.append([institution, observer, instruments])
    return

def parse_address(address):
    r = urllib.urlopen(address).read()
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
    for i,row in enumerate(rows):
        items = row.find_all("td")
        try:
            date, dark_frac = parse_date(items, year)
        except:
            #print "Skipping row {}".format(i)
            continue
        dates.append(date)
        dfracs.append(dark_frac)
        add_line(baade, items[3], items[4], items[5:9])
        add_line(clay,  items[10], items[11],items[12:14])
        add_line(dupont,items[15], items[15],[items[16]])
        add_line(swope, items[18], items[18],[items[19]])
    return dates, dfracs, baade, clay, dupont, swope

if __name__=="__main__":
    addresses = ["https://schedule.obs.carnegiescience.edu/2017/sch2017_{:02}.html".format(num)
                 for num in range(7,13)]
    
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
        
    index = map(lambda x: x.iso.split()[0], dates)
    
    baade = pd.DataFrame(baade, index=index, columns=['Institution','Observer','Instruments'])
    clay  = pd.DataFrame(clay,  index=index, columns=['Institution','Observer','Instruments'])
    dupont= pd.DataFrame(dupont,index=index, columns=['Institution','Observer','Instruments'])
    swope = pd.DataFrame(swope, index=index, columns=['Institution','Observer','Instruments'])
