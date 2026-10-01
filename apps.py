from django.apps import AppConfig
from django.conf import settings


class AifConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aif"
    if settings.DEBUG:
        site_address = (
            "https://canoneuropenv.sharepoint.com/teams/businessintelligencecig/"
        )
        library = "AIF"
    else:
        site_address = "https://canoneuropenv.sharepoint.com/teams/EMEA-BDO/"
        library = "AIFSetupTool"
