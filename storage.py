import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class Storage:
    def __init__(self):
        print('Initializing Storage object')
        
        # Authenticate using application default credentials
        self.__cred = credentials.Certificate('/home/pi/FoodSense-Firebase.json')
        firebase_admin.initialize_app(self.__cred)

    # Add item to Datastore
    def addItem(self, item, weight, filename):
        print('Adding item to list')

    # Remove item from Datastore
    def removeItem(self, weight):
        print('Removing item')


    # Search Datastore for item
    def searchList(self, item, weight):
        print('Searching for item')

