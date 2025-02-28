from django.db.models import IntegerChoices


class AccessLevels(IntegerChoices):
    VIEWER = 0, "Viewer"
    OPERATOR = 1, "Operator"
    DEVELOPER = 2, "Developer"
    MAINTAINER = 3, "Maintainer"
