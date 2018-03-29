import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class Storage:
    def __init__(self):
        print('Initializing Storage object')
        
        # Authenticate using Firebase AdminSDK service account
        self.__cred = credentials.Certificate('/home/pi/FoodSense-Firebase.json')
        firebase_admin.initialize_app(self.__cred, {
            'databaseURL': 'https://foodsense-194320.firebaseio.com/'
        })

    # Add new item to Firebase
    def addItem(self, item, weight, timestamp):
        print('Adding item to list')

        ref = db.reference('Contents')
        ref.set({
            item: {
                'weight': weight,
                'timestamp': timestamp
            }
        })

    # Remove item from Firebase
    def removeItem(self, weight):
        print('Removing item')
        
    # Search Firebase for item
    def searchList(self, item):
        print('Searching for item')

        ref = db.reference('Contents')
        snapshot = ref.get()
        if item in snapshot:
            print(item)

    # Print list
    def printList(self):
        print('Printing list')

        ref = db.reference('Contents')
        print(ref.get())
