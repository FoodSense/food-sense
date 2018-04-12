import sys

try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    from firebase_admin import storage
    import google.cloud.exceptions
    from pyfcm import FCMNotification
except ImportError:
    print('Failed to import all necessary packages for Storage class')
    sys.exit()

class Storage:
    def __init__(self):
        print('Initializing Storage object')

        # Authenticate using Firebase AdminSDK service account
        self.cred = credentials.Certificate('/home/pi/Food Sense/Service Accounts/foodsense-firebase.json')
        firebase_admin.initialize_app(self.cred)


        self.db = firestore.client()
        self.bucket = storage.bucket('food-sense-199718.appspot.com')

        self.api_key = 'AAAAYDyGdIE:APA91bHW_WpPWEjG-GgxwszERAfIADupdxKiyzZjoI_O84j4Xv6XQnjXugRAC07b0wtWWC3A9S_7miYEHYs4T_R8SI0x6EK3McxmR7AJ-4UEARp9wgiCsv5K0Z57-yJqiELIj8ACflyY'
        self.pushService = FCMNotification(api_key=self.api_key)

    # Add new item to Firebase
    def addItem(self, item, weight, timestamp):
        print('Adding {} to list'.format(item))

        dts = str(timestamp)

        # Data fields for key
        data = { u'name': item, u'weight': weight, u'dts': dts }

        # Push 'key: {data}' to 'list' collection
        self.db.collection(u'list').document(dts).set(data)

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


    # Upload image to Storage
    def uploadImage(self, timestamp, filename):
        print('Uploading image to Firebase Storage')

        dts = str(timestamp)

        blob = self.bucket.blob(dts)
        blob.upload_from_filename(filename=filename)

    # Send door warning notification to app
    def doorWarning(self):
        print('Door push notification')               

        message = 'The door has been open for more than 2 minutes!'

        result = self.pushService.notify_topic_subscribers(
                topic_name = 'door',
                message_title = 'Door Warning',
                message_body = message
                )

    # Send temp warning notificaiotn to app
    def tempWarning(self):
        print('Temp push notification')

        message = 'Temperature has exceeded safe limits!'

        result = self.pushService.notify_topic_subscribers(
                topic_name = 'temp',
                message_title = 'Temperature Warning',
                message_body = message
                )

    # Send power warning notificaiton to app
    def powerWarning(self):
        print('Power push notification')

        message = 'Power has failed! Food Sense is now operating on battery power'

        result = self.pushService.notify_topic_subscribers(
                topic_name = 'power',
                message_title = 'Power Warning',
                message_body = message
                )
