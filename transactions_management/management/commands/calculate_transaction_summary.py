from django.core.management.base import BaseCommand
from bson import ObjectId
import jdatetime
from datetime import datetime, timedelta
from transactions_management.models import Transaction, TransactionSummary

class Command(BaseCommand):
    help = 'calculate and store transaction summaries for faster reporting'

    def handle(self, *args, **options):
        
        print('starting transaction summary calculation.')    
        end_date = datetime.now()
        oldest = Transaction.objects.order_by('createdAt').first()

        start_date = oldest.createdAt

        print(f'Processing transactions from {start_date} to {end_date}')
        
        merchant_ids = Transaction.objects.distinct('merchantId')
        
        self._process_summary(None, start_date, end_date)
        
        for merchant_id in merchant_ids:
            self._process_summary(merchant_id, start_date, end_date)
        
        print("completed transaction summary calculation.")

    def _build_pipeline(self, pipeline, mode):

        group_stage = {
            "daily": {
                "$group": {
                    "_id": {
                        "year": {"$year": "$createdAt"},
                        "month": {"$month": "$createdAt"},
                        "day": {"$dayOfMonth": "$createdAt"}
                    },
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }
            },
            "weekly": {
                "$group": {
                    "_id": {
                        "year": {"$year": "$createdAt"},
                        "week": {"$week": "$createdAt"}
                    },
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }
            },
            "monthly": {
                "$group": {
                    "_id": {
                        "year": {"$year": "$createdAt"},
                        "month": {"$month": "$createdAt"}
                    },
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }
            }
        }[mode]

        pipeline.extend([
            group_stage,
            {"$sort": {"_id": 1}}
        ])
        
        return pipeline
    
    def _process_summary(self, merchant_id, start_date, end_date):
        """Process and store summaries for a specific merchant or all merchants combined"""
        merchant_str = str(merchant_id) if merchant_id else 'all merchants'
        self.stdout.write(f'Processing summaries for {merchant_str}')
        
        modes = ['daily', 'weekly', 'monthly']
        types = ['count', 'amount']
        
        for mode in modes:
            for summary_type in types:
                TransactionSummary.objects(
                    mode=mode,
                    type=summary_type,
                    merchantId=merchant_id
                ).delete()
                
                
                match_query = {
                    "createdAt": {
                        "$gte": start_date,
                        "$lte": end_date} }
                pipeline = []

                if merchant_id:
                    match_query["merchantId"] = merchant_id
                
                pipeline = self._build_pipeline(pipeline, mode)                
                
                result = Transaction.objects.aggregate(pipeline)

                summaries = []
                for item in result:
                    if mode == 'daily':
                        year, month, day = item['_id']['year'], item['_id']['month'], item['_id']['day']
                        persian_date = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                        key = persian_date.strftime('%Y/%m/%d')
                    elif mode == 'weekly':
                        year, week = item['_id']['year'], item['_id']['week']
                        persian_date = jdatetime.date.fromgregorian(year=year, month=1, day=1)
                        key = f"هفته {week} سال {persian_date.year}"
                    elif mode == 'monthly':
                        year, month = item['_id']['year'], item['_id']['month']
                        persian_date = jdatetime.date.fromgregorian(year=year, month=month, day=1)
                        months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", 
                                "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
                        key = f"{months[persian_date.month-1]} {persian_date.year}"
                    
                    value = item['count'] if summary_type == 'count' else item['amount']
                    
                    
                    summary = TransactionSummary(
                        mode=mode,
                        type=summary_type,
                        merchantId=merchant_id,
                        key=key,
                        value=value
                    )
                    summaries.append(summary)
                
                if summaries:
                    TransactionSummary.objects.insert(summaries)
                    print(f'-created {len(summaries)} {mode} {summary_type} summaries')
                else:
                    print(f'- No data for {mode} {summary_type}')