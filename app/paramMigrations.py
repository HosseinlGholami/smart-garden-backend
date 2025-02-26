# from util.param import HubParameterId
from nd.trf_com import TRFParameterId
import os
import django

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Configure Django settings
django.setup()

if __name__ == "__main__":
    # Import models inside the block to avoid Django settings error
    from nd.models import TRFParam

    def update_parameters(enum_class, model_class):
        # Delete all existing entries in the table
        model_class.objects.all().delete()

        # # Iterate over enum values to create new entries
        for enum_member in enum_class:
            param_data = enum_member.value
            param_id = param_data["param_id"]
            param_name = param_data["param_name"]
            param_detail = param_data.get("detail", "")
            print(param_name)
            model_class.objects.create(
                param_id=param_id,
                param_name=param_name,
                default_value=param_data.get("default_value", "1"),
                is_advance=param_data.get("is_advance", True),
                is_settable=param_data.get("is_settable", True),
                detail=param_detail,
            )

    # Call the update_parameters function
    update_parameters(TRFParameterId, TRFParam)