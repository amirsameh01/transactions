from mongoengine import Document, IntField, DateTimeField, ObjectIdField, StringField, DictField

class Transaction(Document):
    merchantId = ObjectIdField(required=True)
    amount = IntField(required=True)
    createdAt = DateTimeField(required=True)
    
    meta = {'collection': 'transaction'}

#TODO: rewrite comments 
class TransactionSummary(Document):
    mode = StringField(required=True, choices=['daily', 'weekly', 'monthly'])  
    type = StringField(required=True, choices=['count', 'amount'])
    merchantId = ObjectIdField(required=False)
    key = StringField(required=True) # amount / count
    value = IntField(required=True) # 
    
    meta = {
        'collection': 'transaction_summary',
        'indexes': [
            {'fields': ['mode', 'type', 'merchantId', 'key']}
        ]
    }