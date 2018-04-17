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

class Firebase:
	def __init__(self):
		print('Initializing Storage object')

		# Authenticate with Firebase using AdminSDK service account
		self.cred = credentials.Certificate(
                '/home/pi/food-sense/service-accounts/foodsense-firebase.json'
                )

		firebase_admin.initialize_app(self.cred)
		self.db = firestore.client()

		# Connect to Firebase Storage bucket
		self.bucket = storage.bucket('food-sense-199718.appspot.com')

		# Authenticate with FCM through PyFCM
		self.apiKey = 'AAAAYDyGdIE:APA91bHW_WpPWEjG-GgxwszERAfIADupdxKiyzZjoI_O84j4Xv6XQnjXugRAC07b0wtWWC3A9S_7miYEHYs4T_R8SI0x6EK3McxmR7AJ-4UEARp9wgiCsv5K0Z57-yJqiELIj8ACflyY'
		self.pushService = FCMNotification(api_key=self.apiKey)

	# Add new item to Firebase
	def addItem(self, name, weight, dts):
		print('Adding {} to list'.format(item))

		# Data fields for key
		data = { u'name': name, u'weight': weight, u'dts': dts }

		# Push 'key: {data}' to 'list' collection
		self.db.collection(u'list').document(dts).set(data)

	# Remove item by name
	def removeItem(self, name):
		print('Removing {} from list'.format(name))

		try:
			item = None
			match = self.db.collection(u'list').where(u'name', u'==', name).get()
			for doc in match:
				item = doc.id
			self.db.collection(u'list').document(item).delete()
		except google.cloud.exceptions.NotFound:
			print('No match found for name {}'.format(name))
    
    # Add item to shopping list
    def addShopping(self, name):
        print('Adding {} to shopping list'.format(name))

        data = { u'name': name }
        self.db.collection(u'shopping_list').document(name).set(data)

    # Remove item from shopping list
    def removeShopping(self, name):
        print('Removing {} from shopping list'.format(name))

        try:
            item = []
            match = self.db.collection(u'shopping_list').where(u'name', u'==', name).get()
            for doc in match:
                item = doc.id
            self.db.collection(u'shopping_list').document(item).delete()
        except google.cloud.exceptions.NotFound:
            print('No match found for {}'.format(name))

	# Search Firebase for name
	def searchName(self, name):
		print('Searching for name {}'.format(name))

		dict = None
		matches = self.db.collection(u'list').where(u'name', u'==', name).get()
		for doc in matches:
			dict = doc.to_dict()
		print('Match(es) found:')
		print(dict)

	# Search Firebase for weight
	def searchWeight(self, weight):
		print('Searching for weight {}'.format(weight))

		dict = None
		matches = self.db.collection(u'list').where(u'weight', u'==', weight).get()
		for doc in matches:
			dict = doc.to_dict()
		print('Match(es) found:')
		print(dict)

	# Search Firebase for timestamp
	def searchTimestamp(self, timestamp):
		print('Searching for timestamp {}'.format(timestamp))

		match = self.db.collection(u'list').document(timestamp)
		try:
			item = match.get()
			print('Match found: {}'.format(item.to_dict()))
		except google.cloud.exceptions.NotFound:
			print('No Match found')

	# Return list
	def getList(self):
		dic = {}
		items = []
		
		docs = self.db.collection(u'list').get()
		for doc in docs:
			if doc.id != u'default':
				dic = doc.to_dict()
				items.append(dic['name'])
		return items

	# Return shopping list
	def getShopping(self):
		dic = {}
		items = []
		
		docs = self.db.collection(u'shopping_list').get()
		for doc in docs:
			if doc.id != u'default':
				dic = doc.to_dict()
				items.append(dic['name'])
		return items

	# Print list
	def printList(self):
		print('Printing list')

		dict = None
		docs = self.db.collection(u'list').get()
		for doc in docs:
			if doc.id != u'default':
				dict = doc.to_dict()
				print(u'{}'.format(dict['name']))


    # Print shopping list
    def printShopping(self):
        print('Printin shopping list')
        
     	dict = None
		docs = self.db.collection(u'shopping_list').get()
		for doc in docs:
			if doc.id != u'default':
				dict = doc.to_dict()
				print(u'{}'.format(dict['name']))

	# Upload image to Storage
	def uploadImage(self, filename):
		print('Uploading image to Firebase Storage')

		blob = self.bucket.blob('contents')
		blob.upload_from_filename(filename=filename)

	# Send list updated notification to app
	def listUpdated(self):
		print('List updated push notification')

		message = 'The list has been updated'

		result = self.pushService.notify_topic_subscribers(
				topic_name = 'list',
				message_title = 'List Updated',
				message_body = message
				)

	# Send door warning notification to app
	def doorWarning(self):
		print('Door push notification')               

		message = 'The door has been open for more than 2 minutes!'

		result = self.pushService.notify_topic_subscribers(
				topic_name = 'door',
				message_title = 'Door Warning',
				message_body = message
				)

	# Send temp warning notification to app
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

		message = 'Power failure: Food Sense is now operating on battery power'

		result = self.pushService.notify_topic_subscribers(
				topic_name = 'power',
				message_title = 'Power Warning',
				message_body = message
				)
