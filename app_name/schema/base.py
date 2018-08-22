from  app_name import ma
import time


def safe_execute(default, exception, *args):
    try:
        return int(time.mktime(time.strptime(str(*args)[:19], "%Y-%m-%d %H:%M:%S"))) - time.timezone
    except exception:
        return default


class BaseSchema(ma.ModelSchema):
    created_at = ma.Method('created_at_epoch')
    updated_at = ma.Method('updated_at_epoch')

    def created_at_epoch(self, obj):
        return safe_execute(None, ValueError, obj.created_at)

    def updated_at_epoch(self, obj):
        return safe_execute(None, ValueError, obj.updated_at)