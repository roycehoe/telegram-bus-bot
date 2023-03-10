from enum import Enum
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from app.bus_stop import get_bus_stop_description, is_valid_bus_stop
from constants import MAIN_MENU_MESSAGE
from database import TelegramBotDb
from models.NestedMenuProtocol import NestedMenu


class NewInputStates(Enum):
    INPUT = 0
    CONFIRM = 1


CONVERSATION_OPTIONS = """Type /finish to finish adding bus stops
Type /show to show current list of bus stops.
Type /exit to exit without saving."""
BUS_STOP_ALREADY_BOOKMARKED_MESSAGE = (
    "You have already bookmarked this bus stop. Please input another bus stop."
)
ASK_FOR_NEXT_BUS_STOP_MESSAGE = "Bus stop added. Please key in your next bus stop."
ASK_FOR_FIRST_BUS_STOP_MESSAGE = "Please key in your first bus stop"
INVALID_BUS_STOP_MESSAGE = "Please input a valid bus stop."
BUS_STOP_SAVED_MESSAGE = "Your bus stops has been saved."
EXIT_SUCCESSFUL_MESSAGE = "Exit successful"
SAVED_BUS_STOP_DISPLAY_PREPEND_MESSAGE = "Here are your saved bus stops:"


def _get_saved_bus_stop_display(bus_stops: list[str]) -> str:
    bus_stop_data: list[str] = [
        f"{bus_stop} - {get_bus_stop_description(bus_stop)}" for bus_stop in bus_stops
    ]
    bus_stop_display = "\n".join([data for data in bus_stop_data])

    return f"{SAVED_BUS_STOP_DISPLAY_PREPEND_MESSAGE} \n{bus_stop_display}\n\n{CONVERSATION_OPTIONS}"


class Add(NestedMenu):
    new_bus_stops: list[str] = []

    async def start(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        db_instance=TelegramBotDb(),
    ) -> NewInputStates:
        # user_id = str(update.message.chat.id)
        # instance = TelegramBotDb()
        # instance.create({user_id: ["hello world"]})
        # instance.get_distinct(user_id)

        if not db_instance.get_distinct(str(update.message.chat.id)):
            db_instance.create({str(update.message.chat.id): []})

        # print(context)
        # if not context.user_data.get("bus_stops"):
        #     context.user_data["bus_stops"] = []

        # if TelegramBotDb().get_distinct()

        await update.message.reply_text(
            f"{ASK_FOR_FIRST_BUS_STOP_MESSAGE}\n\n{CONVERSATION_OPTIONS}"
        )
        return NewInputStates.INPUT

    async def input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not is_valid_bus_stop(update.message.text):
            await update.message.reply_text(INVALID_BUS_STOP_MESSAGE)
            return

        if update.message.text in self.new_bus_stops:
            await update.message.reply_text(BUS_STOP_ALREADY_BOOKMARKED_MESSAGE)
            return

        self.new_bus_stops.append(update.message.text)
        await update.message.reply_text(
            f"{ASK_FOR_NEXT_BUS_STOP_MESSAGE}\n\n{CONVERSATION_OPTIONS}"
        )

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        saved_bus_stop_display = _get_saved_bus_stop_display(self.new_bus_stops)
        await update.message.reply_text(saved_bus_stop_display)

    async def finish(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["bus_stops"] = [
            *context.user_data["bus_stops"],
            *self.new_bus_stops,
        ]
        await update.message.reply_text(BUS_STOP_SAVED_MESSAGE)
        await update.message.reply_text(MAIN_MENU_MESSAGE)
        return ConversationHandler.END

    async def exit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.new_bus_stops = []
        await update.message.reply_text(EXIT_SUCCESSFUL_MESSAGE)
        await update.message.reply_text(MAIN_MENU_MESSAGE)
        return ConversationHandler.END

    def get_conversation_handler(self, command: str) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[CommandHandler(command, self.start)],
            states={
                NewInputStates.INPUT: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), self.input),
                    CommandHandler("show", self.show),
                    CommandHandler("finish", self.finish),
                ],
            },
            fallbacks=[CommandHandler("exit", self.exit)],
        )
