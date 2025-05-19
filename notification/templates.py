#TODO: this one could use a strategy pattern (or mapping dic), (to be more flexiable for new mediums)

class MessageTemplate:
    @staticmethod
    def format_for_medium(message, medium):
        if medium == "sms":
            return f'Sample sms {message}'
        elif medium == "email":
            return f"Subject: Sample email\nBody:\n{message}"
        elif medium == "telegram":
            return f"Sample telegram message {message}"