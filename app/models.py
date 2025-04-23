from django.db import models

def default_client_settings():
    return {
        "simkl": {
            "access_token": "",
            "account_id": ""
        }
    }

class Client(models.Model):
    logging_service = models.CharField(max_length=16, null=False, default="")
    settings = models.JSONField(null=False, default=default_client_settings())

    class Meta:
        db_table = "client"
