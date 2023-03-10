from enum import Enum
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from app.bus_stop import get_bus_stop_description
from constants import InputStates
from models.NestedMenuProtocol import NestedMenu
from utils import show_main_menu


CONVERSATION_OPTIONS = """Type /finish to finish deleting bus stops
Type /show to show current list of bus stops."""


def _get_saved_bus_stop_display(bus_stops: list[str]) -> str:
    bus_stop_data: list[str] = [
        f"{bus_stop} - {get_bus_stop_description(bus_stop)}" for bus_stop in bus_stops
    ]
    bus_stop_display = "\n".join([data for data in bus_stop_data])

    return (
        f"Here are your saved bus stops: \n{bus_stop_display}\n\n{CONVERSATION_OPTIONS}"
    )


class Remove(NestedMenu):
    async def start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> InputStates:
        if not context.user_data.get("bus_stops"):
            await update.message.reply_text(f"You have no saved bus stops")
            return ConversationHandler.END

        await update.message.reply_text(
            f"Please input your bus stops.\n\n{CONVERSATION_OPTIONS}"
        )
        return InputStates.INPUT

    async def input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message.text not in context.user_data["bus_stops"]:
            await update.message.reply_text(
                "No bus stop found. Please input a previously saved bus stop."
            )
        else:
            context.user_data["bus_stops"].remove(update.message.text)
            await update.message.reply_text(
                f"Bus stop removed. Please key in your next bus stop.\n\n{CONVERSATION_OPTIONS}"
            )

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        saved_bus_stop_display = _get_saved_bus_stop_display(
            context.user_data["bus_stops"]
        )
        await update.message.reply_text(saved_bus_stop_display)

    @show_main_menu
    async def exit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return ConversationHandler.END

    def get_conversation_handler(self, command: str) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[CommandHandler(command, self.start)],
            states={
                InputStates.INPUT: [
                    MessageHandler(filters.TEXT & (~filters.COMMAND), self.input),
                    CommandHandler("show", self.show),
                    CommandHandler("finish", self.exit),
                ],
            },
            fallbacks=[CommandHandler("finish", self.exit)],
        )
