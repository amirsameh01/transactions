from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId, errors as bson_errors
import jdatetime
from mongoengine.queryset.visitor import Q

from transactions_management.models import Transaction, TransactionSummary

class TransactionReportView(APIView):

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

    def get(self, request):
        report_type = request.query_params.get('type')
        mode = request.query_params.get('mode')
        merchant_id = request.query_params.get('merchantId', None)
        
        if report_type not in ['count', 'amount']:
            return Response({"error": "Invalid type. Must be 'count' or 'amount'"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if mode not in ['daily', 'weekly', 'monthly']:
            return Response({"error": "Invalid mode. Must be 'daily', 'weekly', or 'monthly'"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        pipeline = []
        
        if merchant_id:
            try:
                merchant_oid = ObjectId(merchant_id)
                pipeline.append({"$match": {"merchantId": merchant_oid}})
            except bson_errors.InvalidId:
                return Response({"error": "Invalid merchantId format"}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        pipeline = self._build_pipeline(pipeline, mode)

        result = Transaction.objects.aggregate(pipeline)
        
        #NOTE: Response formatting should be handled in a dedicated serializer - 
        # temporarily implemented here for rapid development        
        formatted_result = []
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
            
            value = item['count'] if report_type == 'count' else item['amount']
            formatted_result.append({"key": key, "value": value})
        
        return Response(formatted_result)

class TransactionSummaryReportView(APIView):
    """
    API endpoint that returns transaction reports from pre-calculated summaries.
    This should be much faster for large datasets.
    """
    def get(self, request):
        report_type = request.query_params.get('type', 'count')
        mode = request.query_params.get('mode', 'daily')
        merchant_id = request.query_params.get('merchantId', None)
        
        if report_type not in ['count', 'amount']:
            return Response({"error": "Invalid type. Must be 'count' or 'amount'"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if mode not in ['daily', 'weekly', 'monthly']:
            return Response({"error": "Invalid mode. Must be 'daily', 'weekly', or 'monthly'"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        query = Q(mode=mode) & Q(type=report_type)
        
        if merchant_id:
            try:
                merchant_oid = ObjectId(merchant_id)
                query &= Q(merchantId=merchant_oid)
            except bson_errors.InvalidId:
                return Response({"error": "Invalid merchantId format"}, 
                                status=status.HTTP_400_BAD_REQUEST)
        #else:
            #query &= Q(merchantId=None) #NOTE: when merhcnat id is not provided, i gotta query the whole collections not the null merchand ids.

        summaries = TransactionSummary.objects(query).order_by('key')
        
        formatted_result = [{"key": summary.key, "value": summary.value} for summary in summaries]
        
        return Response(formatted_result)