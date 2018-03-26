from google.cloud import datastore

class Storage:
    def __init__(self):
        print('Initializing storage object')
        
        self.client = datastore.Client()
        
    # Add item to Datastore
    def addItem(self, item, weight, filename):
        print('Adding item to list')
        
        kind = 'Contents'
        name = item
        task_key = self.client.key(kind, name)

        # Prepares the new entity
        task = datastore.Entity(key=task_key)
        task['weight'] = weight
        task['date/time'] = filename

        # Saves the entity
        self.client.put(task)
        print('Saved {}: {}, {}'.format(task.key.name, task['weight'], task['date/time']))

    # Remove item from Datastore
    def removeItem(self, weight):
        print('Removing item')

    # Search Datastore for item
    def searchList(self, item, weight):
        print('Searching for item')
