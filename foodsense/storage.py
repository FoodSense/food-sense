import sys

try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    from firebase_admin import storage
    import google.cloud.exceptions
except ImportError:
    print('Failed to import all necessary packages for Storage class')
    sys.exit()

class Storage:
    # Initialize object
    def __init__(self):
        print('Initializing Storage object')

        # Authenticate using Firebase AdminSDK service account
        #self.cred = credentials.Certificate('/home/derrick/service-accounts/foodsense-firebase.json')
        #self.cred = credentials.Certificate('/home/derrick/service-accounts/test-firebase.json')
        #firebase_admin.initialize_app(self.cred)
        firebase_admin.initialize_app()

        self.db = firestore.client()
        #self.bucket = storage.bucket('food-sense-199718.appspot.com')
        self.bucket = storage.bucket('avian-silicon-200216.appspot.com')
    
    ### FIREBASE FIRESTORE ###

    # Add new item to Firebase
    def addItem(self, item, weight, timestamp):
        print('Adding {} to list'.format(item))

        # Data fields for key
        data = { u'name': item, u'weight': weight, u'dts': timestamp }

        # Push 'key: {data}' to 'list' collection
        self.db.collection(u'list').document(timestamp).set(data)

    # Remove item from Firebase
    def removeItem(self, weight):
        print('Removing item with weight {} from list'.format(weight))
        
        try:
            item = None
            match = self.db.collection(u'list').where(u'weight', u'==', weight).get()
            for doc in match:
                item = doc.id
            self.db.collection(u'list').document(item).delete()
            #if len(item) == 1:
            #
            #elif len(item) > 1:
            #    error = 0.01
            #    lowerBound = round(((weight - error*weight) * 2 ) / 2)
            #    upperBound = round(((weight + error*weight) * 2 ) / 2)
            #
            #    for i in np.arange(lowerBound, upperBound, 0.5):
            #        match = self.db.collection(u'list').where(u'weight', u'==', i).get()
            #        for doc in match:
            #            item.append(doc.id)
            #        self.db.collection(u'list').document(item).delete()
        except google.cloud.exceptions.NotFound:
            print('No match found for weight {}'.format(weight))

    # Search Firebase for name
    def findName(self, name):
        print('Searching for name {}'.format(name))

        dict = None
        matches = self.db.collection(u'list').where(u'name', u'==', name).get()
        for doc in matches:
            dict = doc.to_dict()
        print('Match(es) found:')
        print(dict)

    # Search Firebase for weight
    def findWeight(self, weight):
        print('Searching for weight {}'.format(weight))

        dict = None
        matches = self.db.collection(u'list').where(u'weight', u'==', weight).get()
        for doc in matches:
            dict = doc.to_dict()
        print('Match(es) found:')
        print(dict)

    # Search Firebase for timestamp
    def findDTS(self, timestamp):
        print('Searching for timestamp {}'.format(timestamp))

        match = self.db.collection(u'list').document(timestamp)
        try:
            item = match.get()
            print('Match found: {}'.format(item.to_dict()))
        except google.cloud.exceptions.NotFound:
            print('No Match found')
            
    # Print list
    def printList(self):
        print('Printing list')

        dict = None
        docs = self.db.collection(u'list').get()
        for doc in docs:
            if doc.id != u'default':
                dict = doc.to_dict()
                print(u'{}'.format(dict['name']))

    ### FIREBASE STORAGE ###

    # Upload image to Storage
    def uploadImage(self, timestamp, filename):
        print('Uploading image to Firebase Storage')

        blob = self.bucket.blob(timestamp)
        blob.upload_from_filename(filename=filename
    
    ## CLOUD MESSAGING ##

    # Send door warning notification to app
    def doorWarning():
        print('Door push notification')               
    
    # Send temp warning notificaiotn to app
    def tempWarning():
        print('Temp push notification')

    # Send power warning notificaiton to app
    def powerWarning():
        print('Power push notification')


