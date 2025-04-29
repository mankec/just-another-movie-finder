from django.db import models

def default_client_settings():
    return {
        "simkl": {
            "access_token": "",
            "account_id": ""
        }
    }

class Client(models.Model):
    # TODO: movies.Client.settings: (fields.E010) JSONField default should be a callable instead of an instance so that it's not shared between all field instances.
	# HINT: Use a callable instead, e.g., use `dict` instead of `{}`.
    logging_service = models.CharField(max_length=16, null=False, default="")
    settings = models.JSONField(null=False, default=default_client_settings())

    class Meta:
        db_table = "client"

    def find_or_create(logging_service):
        ...
