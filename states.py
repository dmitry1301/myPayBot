from aiogram.dispatcher.filters.state import StatesGroup, State


class Purchase(StatesGroup):
    EnterQuantity = State()
    Approval = State()
    Payment = State()

class EditItem(StatesGroup):
    Name = State()
    Desc = State()
    #Photo = State()
    #Price = State()
    Contact = State()
    Pay = State()

class NewItem(StatesGroup):
    Name = State()
    Desc = State()
    #Photo = State()
    #Price = State()
    Contact = State()
    Pay = State()

class EditVacancy(StatesGroup):
    Name = State()
    Desc = State()
    #Photo = State()
    #Price = State()
    Contact = State()
    Pay = State()

class NewVacancy(StatesGroup):
    Name = State()
    Desc = State()
    #Photo = State()
    #Price = State()
    Contact = State()
    Pay = State()

class NewReview(StatesGroup):
    Review = State()

class Mailing(StatesGroup):
    Text = State()
    Confirm = State()

class Find(StatesGroup):
    Find = State()

class Support(StatesGroup):
    SupportMessage = State()