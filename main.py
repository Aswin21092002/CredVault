import os
import django
import firebase_admin
from firebase_admin import credentials, firestore, auth
from django.forms.models import model_to_dict
from datetime import date, datetime
from google.api_core import exceptions
from django.db.models.fields.files import FieldFile

# Setup project settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sendesta.settings')

# Setup django and then import all the models from everywhere
django.setup()
from django.apps import apps

# setup firebase / firestore
cred = credentials.Certificate("./ServiceAccountKey.json")
app = firebase_admin.initialize_app(cred)
store = firestore.client()

def convert_value(value):
    """Convert unsupported types to Firestore-compatible types."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day)
    
    if value is None:
        return ""
    
    if isinstance(value, FieldFile):
        return value.url
    # Add more type conversions if necessary
    return value

def instance_to_dict(instance):
    """Convert a Django model instance to a dictionary with Firestore-compatible values."""
    instance_dict = model_to_dict(instance)
    for key, value in instance_dict.items():
        instance_dict[key] = convert_value(value)
    return instance_dict

def delete_collection(collection_name, batch_size=500):
    """Delete all documents in a collection."""
    collection_ref = store.collection(collection_name)
    docs = collection_ref.limit(batch_size).stream()

    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(collection_name, batch_size)

# run 'py main.py' in project terminal then refresh database to see
batch = store.batch()
# loop through all models
for model in apps.get_models():
    print(f"Model: {model.__name__}")
    # user and companies and UserIDs Firestore fields need to stay clean because published apps rely on them
    # Empty categories are also not added
    # Business causes an error - fix
    if model.__name__ not in ['user', 'companies', 'UserIDs', 'LogEntry', 'Permission', 'ContentType', 
                              'Session', 'StripeCustomer', 'CanDownloadReport', 'Plan', 'Business',
                              'option', 'question']:
        # Delete all existing documents in the collection so we don't have duplicates      
        delete_collection(model.__name__)

        # if no data, skips inner loop
        for instance in model.objects.all():
            doc_ref = store.collection(model.__name__).document(str(instance.id))
            instance_dict = instance_to_dict(instance)
            # will add a new collection if doesn't exist unless
            batch.set(doc_ref, instance_dict)
        
        # Batch can only do 500 at a time - need to handle that
        batch.commit()