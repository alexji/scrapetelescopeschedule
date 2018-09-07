""" A stub of a script to scrape LCO weather """
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import urllib2
import json
import time

seeing_url_1 = "http://weather.lco.cl/clima/weather/Magellan/PHP/grabMag1.php"
seeing_url_2 = "http://weather.lco.cl/clima/weather/Magellan/PHP/grabMag2.php"
seeing_url_3 = "http://weather.lco.cl/clima/weather/Magellan/PHP/grabDimm.php"
seeing_urls = [seeing_url_1,seeing_url_2,seeing_url_3]

weather_url = "http://weather.lco.cl/clima/weather/Magellan/PHP/grabWeather.php"
pos_url_1 = "http://weather.lco.cl/clima/weather/Magellan/PHP/grabMag1pos.php"
pos_url_2 = "http://weather.lco.cl/clima/weather/Magellan/PHP/grabMag2pos.php"

all_urls = seeing_urls + [weather_url,pos_url_1,pos_url_2]
save_fnames = ['seeing1','seeing2','dimm','weather','pos1','pos2']

if __name__=="__main__":
#    output = []
    folder = 'weather'
    prefix = 'ut151005'
    for fname,url in zip(save_fnames,all_urls):
        out_fname = folder+'/'+prefix+'_'+fname+'.txt'
        start = time.time()
        response = urllib2.urlopen(url)
        print("Took {:.1f} to read {}".format(time.time()-start,url))
        html = response.read()
        with open(out_fname,'w') as f:
            f.write(html)

#    for url in seeing_urls:
#        start = time.time()
#        response = urllib2.urlopen(url)
#        print "Took {:.1f} to read {}".format(time.time()-start,url)
#        html = response.read()
#        out = json.loads(html)
#        output.append(out)
    
