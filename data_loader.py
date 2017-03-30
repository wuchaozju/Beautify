import sqlite3

API_KEY = "9b35acbf22d3e28bc60bfc68417ed11a"

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

sqlite_file = search_key + ".sqlite"
sql_create_table = "CREATE TABLE FlickrRecords (Id TEXT, owner TEXT, secret TEXT, server TEXT, farm TEXT, title TEXT, ispublic INT, isfriend INT, isfamily INT)"

def flickr_search_load():
	conn = sqlite3.connect(sqlite_file)
	with conn:
		c = conn.cursor()
		c.execute(sql_create_table)

		conn.commit()
		conn.close()
		print("Table created")

if __name__ == "__main__":
	flickr_search_load()