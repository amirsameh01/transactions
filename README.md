# Transactions & notification Backend Project

This project implements a transaction reporting system and notification service similar to Zibal payment gateway functionality.

## Features

- Transaction reporting with different aggregation modes
- Optimized report generation using pre-calculated summaries
- Asynchronous notification service supporting multiple communication channels

## Management Commands

### Calculate Transaction Summary
python manage.py calculate_transaction_summary

Pre-calculates transaction summaries and stores them in a separate collection for faster query performance. This command must be run before using the optimized Transaction Summary Report API.


## APIs

### Transaction Report API
GET /api/transactions/report/

**Query Parameters:**
- `type`: Should be either `amount` or `count`
- `mode`: Should be either `daily`, `weekly`, or `monthly`
- `merchantId`: (Optional) Filter by merchant ID

**Response:**
Returns aggregated transaction data as key-value pairs of dates and values.


### Transaction Summary Report API (Optimized)

GET /api/transactions/summary-report/

**Query Parameters:**
- Same as Transaction Report API

**Response:**
Returns the same data format as the Transaction Report API but with significantly faster response times by using pre-calculated summaries.

### Notification API

**Request Body:**
```json
{
    "merchantId": "63a69a2d18f93478889d5f11",
    "content": "Your order has been shipped",
    "mediums": ["email"],
    "recipient_info": {
        "email": "customer@example.com"
    }
}
```
## Description:
Queues notifications to be sent through specified channels (email, SMS, Telegram, etc.)
Full details and examples for each API endpoint are provided within the Postman collection included in this repository.

## Technologies Used

- Python and Django
- Django REST Framework
- MongoDB (via MongoEngine)
- Celery for asynchronous task processing
- Docker for containerization
