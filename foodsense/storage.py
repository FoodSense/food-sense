import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

class Storage:
    # Initialize object
    def __init__(self):
        print('Initializing Storage object')

        # Authenticate using Firebase AdminSDK service account
        self.cred = credentials.Certificate('/home/derrick/foodsense-firebase.json')
        firebase_admin.initialize_app(self.cred)
        
        self.db = firestore.client()
        self.bucket = storage.bucket('food-sense-199718.appspot.com')
    
    # Add new item to Firebase
    def addItem(self, item, weight, timestamp):
        print('Adding {} to list'.format(item))

        # Data fields for key
        data = { u'name': item, u'weight': weight }

        # Push 'key: {data}' to 'list' collection
        self.db.collection(u'list').document(timestamp).set(data)

    # Remove item from Firebase
    def removeItem(self, weight):
        print('Removing item with weight {} from list'.format(weight))

        try:
            docs = self.db.collection(u'list').where(u'weight', u'==', weight).get()
            for doc in docs:
                item = doc.id
            self.db.collection(u'list').document(item).delete()
        except google.cloud.exceptions.NotFound:
            print('Item with weight {} not found.'.format(weight))

    # Search Firebase for timestamp
    def findbyDTS(self, timestamp):
        print('Searching for {}'.format(timestamp))


    # Search Firebase for name
    def findByName(self, name):
        print('Searching for {}'.format(name))

        try:
            item = []
            docs = self.db.collection(u'list').where(u'name', u'==', name).get()
            for doc in docs:
                item.append(doc.id)
            print('{} instances of {} found'.format(len(item), name))
        except google.cloud.exceptions.NotFound:
            print('Item {} not found.'.format(name))

    # Search Firebae for weight
    def findByWeight(self, weight):
        print('Searching for {}'.format(weight))

        dict = None
        items = self.db.collection(u'list').get()
        print(items)

        #try:
        #    item = []
        #    name = []
        #    docs = self.db.collection(u'list').where(u'weight', u'==', weight).get()
        #    for doc in docs:
        #        item.append(doc.id)
        #        #name.append(
        #    print('{} items with weight {} found'.format(len(item), weight))
        #    print('')
        #except google.cloud.exceptions.NotFound:
        #    print('Item with weight {} not found.'.format(weight))

    # Print list
    def printlist(self):
        print('Printing list')

        dict = None
        items = self.db.collection(u'list').get()
        for doc in items:
            if doc.id != u'default':
                dict = doc.to_dict()
        print(u'{}'.format(dict['name']))

    # Upload image to Storage
    def uploadImage(self, timestamp, filename):
        print('Uploading image to Firebase Storage')

        blob = self.bucket.blob(timestamp)
        blob.upload_from_filename(filename=filename)
