from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from utils.bot_logconfig import logger


class ModeratorMiddleware(BaseMiddleware):
    def __init__(self, bot, filter_group_id, db):
        self.bot = bot
        self.filter_group_id = filter_group_id
        self.db = db
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        if not event.text:
            return await handler(event, data)


        state = data.get('state')
        current_state = await state.get_state() if state else None


        if current_state == 'AllStates:full_name_and_grade':
            logger.info(f"MODERATOR SKIPPED: state={current_state} (entering name/grade)")
            return await handler(event, data)

        logger.info(f"MODERATOR CHECK: user={event.from_user.username}, state={current_state}, text={event.text[:50]}")


        from utils.service import analyze_message

        await event.bot.send_chat_action(event.chat.id, "typing")
        analysis = await analyze_message(message_text=event.text)
        logger.info(f"ANALYSIS RESULT: {analysis}")

        if analysis == "not_okay":

            user_id = event.from_user.id

            warnings = await self.db.get_warnings(user_id)
            warnings += 1
            await self.db.update_warnings(user_id, warnings)

            await self.bot.send_message(
                self.filter_group_id,
                f"{event.from_user.username}: {event.text}"
            )

            if warnings == 1:
                await event.answer('Без токсичности! Это твое первое предупреждение.')
                logger.info(f'FIRST WARNING {event.from_user.username}: {event.text}')
            elif warnings == 2:
                await event.answer('Пиши по делу! Это твое второе предупреждение')
                logger.info(f'SECOND WARNING {event.from_user.username}: {event.text}')
            elif warnings >= 3:
                await event.answer('Данные о твоем аккаунте улетели в чат модерации. Я предупреждал')
                logger.info(f'THIRD WARNING {event.from_user.username}: {event.text}')

            return

        elif analysis == "model_failed":
            logger.info(f"MODEL FAILED for {event.from_user.username}")
            return await handler(event, data)



        logger.info(f"MESSAGE PASSED FILTER")
        return await handler(event, data)

