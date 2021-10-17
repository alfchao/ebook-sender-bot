import datetime

from peewee import *

database = SqliteDatabase('database.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0
})


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    telegram_id = CharField(unique=True)
    username = CharField()
    nickname = CharField(default=None)
    join_time = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def find_or_create(from_user):
        telegram_id = str(from_user.id)
        username = from_user.username
        nickname = " ".join((from_user.first_name, from_user.last_name))
        user, _ = User.get_or_create(telegram_id=telegram_id,
                                     defaults={'username': username,
                                               'nickname': nickname})
        if username != user.username or nickname != user.nickname:
            user.username = username
            user.nickname = nickname
            user.save()
        return user

    def set_email(self, email: str):
        if len(self.emails) == 0:
            return UserEmail.create(user=self, email=email)
        else:
            # todo: one2many update bug
            return UserEmail.update(email=email).where(UserEmail.user == self).execute()

    def today_send_times(self):
        return (User
                .select()
                .join(UserSendLog)
                .where((UserSendLog.send_time >= datetime.date.today()) & (User.id == self.id))
                .count()
                )

    def log_send_email(self):
        # todo: kindle_email, file_unique_id
        return (
            UserSendLog.create(user=self)
        )


class UserEmail(BaseModel):
    user = ForeignKeyField(User, backref='emails')
    email = CharField()


class UserSendLog(BaseModel):
    # todo: add columns: email file_unique_id
    user = ForeignKeyField(User, backref='user_send_logs')
    send_time = DateTimeField(default=datetime.datetime.now)
