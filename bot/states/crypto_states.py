from aiogram.fsm.state import State, StatesGroup

class CryptoStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_key = State()