import sqlite3
import urllib2, urllib
import time
import xml.etree.ElementTree as ET

import numpy as np
import random
from matplotlib import pyplot as plt

'''
https://www.flickr.com/services/api/flickr.photos.search.html

An example request: https://www.flickr.com/services/rest/?api_key=9b35acbf22d3e28bc60bfc68417ed11a&text=art&method=flickr.photos.search

An example response:
<photos page="1" pages="2952" perpage="100" total="295103">
<photo id="32912498723" owner="53130103@N05" secret="749e11bb35" server="2818" farm="3" title="Broto Roy Quartet" ispublic="1" isfriend="0" isfamily="0"/>
<photo id="33569677142" owner="149213314@N04" secret="9461812afa" server="3790" farm="4" title="Digital art" ispublic="1" isfriend="0" isfamily="0"/>

Photo source: https://www.flickr.com/services/api/misc.urls.html

flickr.photos.getFavorites: https://www.flickr.com/services/api/flickr.photos.getFavorites.html
'''

search_key = "art"

API_KEY = "9b35acbf22d3e28bc60bfc68417ed11a"
SEARCH_METHOD = "flickr.photos.search"
INFO_METHOD = "flickr.photos.getInfo"
#FAV_METHOD = "flickr.photos.getFavorites"

search_url = "https://www.flickr.com/services/rest/?api_key={}&per_page=500&text={}&method={}".format(API_KEY, search_key, SEARCH_METHOD)
photo_info_url = "https://www.flickr.com/services/rest/?api_key={}&method={}".format(API_KEY, INFO_METHOD)

sqlite_file = "data/" + search_key + ".sqlite"
sql_create_photo_table = "CREATE TABLE IF NOT EXISTS FlickrRecords (Id TEXT, owner TEXT, secret TEXT, server TEXT, farm TEXT, title TEXT, ispublic INT, isfriend INT, isfamily INT, fetched INT, UNIQUE(Id)) "
sql_create_photo_info_table = "CREATE TABLE IF NOT EXISTS PhotoInfos (Id TEXT, view INT, comment INT, dateuploaded TEXT, UNIQUE(Id))"


'''
Store all flickr search results into DB
'''
def flickr_search_load():

    conn = sqlite3.connect(sqlite_file)
    with conn:
        conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
        c = conn.cursor()
        c.execute(sql_create_photo_table)
        conn.commit()

        print("Table created")

        response = urllib2.urlopen(search_url).read()
        
        root = ET.fromstring(response)
        #print(root)

        pages = 0
        for photos in root.findall('photos'):
            #print photos.attrib
            pages = int(photos.get('pages'))

        #pages = 3

        for i in range(1, pages + 1):

            if i % 20 == 0:
                time.sleep(20)
                print i

            response = urllib2.urlopen(search_url + "&page=" + str(i)).read()
            root = ET.fromstring(response)

            for photo in root.iter('photo'):
                id = photo.get('id')
                owner = photo.get('owner')
                secret = photo.get('secret')
                server = photo.get('server')
                farm = photo.get('farm')
                title = photo.get('title')
                ispublic = int(photo.get('ispublic'))
                isfriend = int(photo.get('isfriend'))
                isfamily = int(photo.get('isfamily'))

                title = title.replace("'", "")
                title = title.replace('"', "")

                # Duplicated records are allowed
                insert_str = u'INSERT OR IGNORE INTO FlickrRecords (id, owner, secret, server, farm, title, ispublic, isfriend, isfamily, fetched) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", {}, {}, {}, 0)'.format(id, owner, secret, server, farm, title, ispublic, isfriend, isfamily)

                c.execute(insert_str)
                #print id
                conn.commit()

        #conn.commit()
        #sqconn.close()


def get_photo_popularity(photo_id):
    response = urllib2.urlopen(photo_info_url + "&photo_id=" + photo_id).read()
    root = ET.fromstring(response)
    
    views = -1
    comments = -1
    dateuploaded = ""

    for photo in root.iter('photo'):
        views = int(photo.get('views'))
        dateuploaded = photo.get('dateuploaded')

        for comment in photo.iter('comments'):
            comments = int(comment.text)

    return dateuploaded, views, comments


def get_all_photo_popularity():
    conn = sqlite3.connect(sqlite_file)
    with conn:
        conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')

        c = conn.cursor()
        c.execute(sql_create_photo_info_table)
        conn.commit()
        print("Table created")

        c.execute('SELECT id FROM FlickrRecords WHERE  id NOT IN (SELECT id FROM PhotoInfos)')
        all_rows = c.fetchall()

        for row in all_rows:
            id = row[0]
            #print id
            dateuploaded, views, comments = get_photo_popularity(id)

            insert_str = u'INSERT OR IGNORE INTO PhotoInfos (id, view, comment, dateuploaded) VALUES ("{}", "{}", "{}", "{}")'.format(id, views, comments, dateuploaded)
            c.execute(insert_str)
            conn.commit()


def download_photos(id=None, folder="photo/"):
    conn = sqlite3.connect(sqlite_file)
    with conn:
        c = conn.cursor()
        if id == None:
            c.execute('SELECT id, farm, server, secret FROM FlickrRecords WHERE fetched = 0')
        else:
            c.execute('SELECT id, farm, server, secret FROM FlickrRecords WHERE id = {}'.format(id))
        
        all_rows = c.fetchall()
        count = 0

        for row in all_rows:
            count += 1
            id = row[0]
            farm = row[1]
            server = row[2]
            secret = row[3]

            download_photo(farm, server, id, secret, folder)

            update_str = u'UPDATE FlickrRecords SET fetched = 1 WHERE id = {}'.format(id)
            c.execute(update_str)
            conn.commit()

            if count % 100 == 0:
                print count
                print url
            if count % 1000 == 0:
                time.sleep(200)


def download_photo(farm, server, id, secret, folder):
    url = u'https://farm{}.staticflickr.com/{}/{}_{}_b.jpg'.format(farm, server, id, secret)
    print url
    urllib.urlretrieve(url, folder + id + ".jpg")

def download_bad_good_photo():
    good_arts_folder = "good_arts/"
    bad_arts_folder = "bad_arts/"

    conn = sqlite3.connect(sqlite_file)
    with conn:
        c = conn.cursor()
        c.execute('SELECT view, comment, dateuploaded, id FROM PhotoInfos')
        all_rows = c.fetchall()

        for row in all_rows:
            if row[2] == '':
                continue
            dateuploaded = int(row[2])
            one_year_time = 365.0 * 24 * 60 * 60
            time_norm = 47.8 - dateuploaded / one_year_time
            
            view = row[0]
            view = view / time_norm

            if view > 320:
                photo_id = row[3]
                download_photos(photo_id, good_arts_folder)

            if view < 25:
                photo_id = row[3]
                download_photos(photo_id, bad_arts_folder)


def hist_of_photo_info():
    conn = sqlite3.connect(sqlite_file)
    with conn:
        c = conn.cursor()
        c.execute('SELECT view, comment, dateuploaded, id FROM PhotoInfos')
        all_rows = c.fetchall()

        views = []
        #comments = []
        #times = []

        #count_small = 0
        #count_big = 0

        for row in all_rows:            
            view = row[0]
    
            '''
            if view > 320:
                count_big += 1

            if view < 25:
                count_small += 1
            '''        
            
            if view > -1 and view < 700:
                views.append(view)

            '''
            comment = row[1]
            if comment > 1:
                comments.append(comment) 
            '''

        #print min(views)
        #print max(views)
        #print min(times) #42.90
        #print max(times) #47.47
        #print count_big
        #print count_small
 
        #print np.median(views) #29
        #print np.median(comments) # Most are 0, so use views for measuring popularity
        
        bins = np.arange(0, 700, 20) # fixed bin size

        plt.xlim([min(views)-5, max(views)+5])
        plt.hist(views, bins=bins, alpha=0.5)
        plt.show()
        


if __name__ == "__main__":

    #for iter in range(1, 20):
    #    print "round " + str(iter)
    #    flickr_search_load()
    #    time.sleep(6000)

    #download_photos()
    #test()

    #get_photo_popularity("34061715374")

    #get_all_photo_popularity()

    #hist_of_photo_info()

    download_bad_good_photo()

    



