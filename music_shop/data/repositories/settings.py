from sqlalchemy import select

from music_shop.data.database import db
from music_shop.data.models import AppSetting


def get_setting(key, default=None):
    setting = db.session.scalar(
        select(AppSetting).where(AppSetting.key == key)
    )
    return setting.value if setting else default


def set_setting(key, value):
    setting = (
        db.session.scalar(
            select(AppSetting).where(AppSetting.key == key)
        )
        or AppSetting(key=key)
    )

    setting.value = str(value)
    db.session.add(setting)
    db.session.commit()
    return setting