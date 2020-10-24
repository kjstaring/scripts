from mongoengine import *  


disconnect()
# You can connect to a real mongo server instance by your own.
db = connect('CityJSON', host = 'localhost:27017')

