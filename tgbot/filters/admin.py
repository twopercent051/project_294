from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.models.redis_connector import RedisConnector as rds


class RootFilter(BaseFilter):
    is_root: bool = True

    async def __call__(self, obj: Union[Message, CallbackQuery], config: Config) -> bool:
        if isinstance(obj, Message):
            var = obj.chat.id
        else:
            var = obj.message.chat.id
        return (var in config.tg_bot.root_ids) == self.is_root

#
# class RootCallbackQueryFilter(BaseFilter):
#     is_root: bool = True
#
#     async def __call__(self, obj: CallbackQuery, config: Config) -> bool:
#         return (obj.message.chat.id in config.tg_bot.root_ids) == self.is_root


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Union[Message, CallbackQuery], config: Config) -> bool:
        if isinstance(obj, Message):
            var = obj.chat.id
        else:
            var = obj.message.chat.id
        if var in config.tg_bot.root_ids:
            return True
        admins = await rds.get_role_redis("admin")
        return (str(var) in admins) == self.is_admin


class ModeratorFilter(BaseFilter):
    is_moderator: bool = True

    async def __call__(self, obj: Union[Message, CallbackQuery], config: Config) -> bool:
        if isinstance(obj, Message):
            var = obj.chat.id
        else:
            var = obj.message.chat.id
        if var in config.tg_bot.root_ids:
            return True
        admins = await rds.get_role_redis("admin")
        moderators = await rds.get_role_redis("moderator")
        admins.extend(moderators)
        return (str(var) in admins) == self.is_moderator
