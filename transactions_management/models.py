from mongoengine import Document, IntField, DateTimeField, ObjectIdField, StringField, DictField

class Transaction(Document):
    merchantId = ObjectIdField(required=True)
    amount = IntField(required=True)
    createdAt = DateTimeField(required=True)
    
    meta = {'collection': 'transaction'}

class TransactionSummary(Document):
    mode = StringField(required=True, choices=['daily', 'weekly', 'monthly'])  # 'daily', 'weekly', 'monthly'
    type = StringField(required=True, choices=['count', 'amount'])  # 'count', 'amount'
    merchantId = ObjectIdField(required=False)  # Optional, for per-merchant summaries
    key = StringField(required=True)  # Date formatting as per specs
    value = IntField(required=True)  # Count or amount value
    
    meta = {
        'collection': 'transaction_summary',
        'indexes': [
            {'fields': ['mode', 'type', 'merchantId', 'key']}
        ]
    }