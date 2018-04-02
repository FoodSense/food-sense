import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Storage:
    # Initialize object
    def __init__(self):
        print('Initializing Firestore object')
        
        # Authenticate using Firebase AdminSDK service account
        self.cred = credentials.Certificate('foodSense-firebase.json')
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

        # Get current number of items in list
        self.count = 0
        self.docs = self.db.collection(u'List').get()
        for doc in self.docs:
            self.count += 1

    # Add new item to Firebase
    def addItem(self, item, weight, timestamp):
        print('Adding {} to list'.format(item))

        # Create unique key for item
        key = 'Item ' + str(self.count)
        
        # Data fields for key
        data = { u'name': item, u'weight': weight, u'timestamp': timestamp }
        self.count += 1
        
        # Push 'key: {data}' to 'List' collection
        self.db.collection(u'List').document(key).set(data)

    # Remove item from Firebase
    def removeItem(self, weight):
        print('Removing item with weight {} from list'.format(weight))
        
        try:
            docs = self.db.collection(u'List').where(u'weight', u'==', weight).get()
            for doc in docs:
                item = doc.id
            self.db.collection(u'List').document(item).delete()
            self.count -= 1
        except google.cloud.exceptions.NotFound:
            print('Item with weight {} not found.'.format(weight))

    # Search Firebase for item
    def findByName(self, name):
        print('Searching for {}'.format(name))

        try:
            item = []
            docs = self.db.collection(u'List').where(u'name', u'==', name).get()
            for doc in docs:
                item.append(doc.id)
            print('{} instances of {} found'.format(len(item), name))
        except google.cloud.exceptions.NotFound:
            print('Item {} not found.'.format(name))

    # Print list
    def printList(self):
        print('Printing list')

        items = self.db.collection(u'List').get()
        for doc in items:
            if doc.id != 'default':
                dict = doc.to_dict()
                print(u'{}'.format(dict['name']))

    # Upload image to Storage
    def uploadImage(self):
        print('Uploading image to Storage')
