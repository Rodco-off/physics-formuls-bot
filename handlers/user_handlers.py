import logging

from config import ID_ADMIN
from physics_error import SearchError, ValueNotUniqueError, WriteNotStr
from physics_scripts import PhysicsFormul, PhysicsName, AppendPhysicsFormuls
from utils.state_physics_formuls import StepGetPhysicsFormul, StepAppendPhysicsFormuls

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, URLInputFile


router = Router()

logger = logging.getLogger(__name__)


@router.message(Command(commands=['start']))
async def process_start_command(message: Message) -> None:

    await message.answer('''Привет👋, Я Бот Роберт, который поможет тебе найти формулы по ✨физике✨.
У тебя наверняка возник вопрос, как пользоваться данным ботом 🤔?
Чтобы найти нужную формулу тебя надо написать комманду
/physics_formuls и ввести физическое обозначение, и бот тебе найдет все возможные формулы для нахождения этого обозначения, чтобы выйти из него напишите "cancel"
\nВот команды которые тебе могут пригодиться:\n
/tutorial_names - Все физические обозначения, которые я знаю🎓,
/physics_formuls - ищу формулу для этого физического обозначения🔍, \n/help - список всех комманд📋
/support - Поможем разобраться. Контакты админов.🔥

🔥(Для администрации)🔥

/append_formul - Добавление новых формул🖊️''')


@router.message(Command(commands=['tutorial_names']))
async def process_tutorial_names_command(message: Message) -> None:

    physics_name_list = PhysicsName.get_all_physics_name()
    chapters = PhysicsName.get_chapters()

    await message.answer('Вот все обозначения, которые может считывать наш бот:')

    for index, name_list in enumerate(physics_name_list):

        await message.answer(f'Формулы по теме <<{chapters[index]}>>: ')
        await message.answer(f'\n{'·' + ',\n· '.join(name_list)}')


@router.message(Command(commands=['help']))
async def process_help_command(message: Message) -> None:

    await message.answer('''Комманды которые я умею распозновать:
                         \n/tutorial_names - Все физические обозначения, которые я знаю🎓,
/physics_formuls - Ищу формулы для указонного физического обозначения🔍,
/help - команды которые знает📋
/support - Данные админов, чтобы связаться и решить ваши проблемы.🔥

🔥(Для администрации)🔥

/append_formul - Добавление новых формул🖊️''')


@router.message(Command(commands=['physics_formuls']))
async def process_phisics_formuls(message: Message, state: FSMContext) -> None:  # Отлавливает комманду и выводит формулы которые нашёл

    await state.set_state(StepGetPhysicsFormul.GET_FORMULS)
    await message.answer('🔎Введите, пожалуйста, физическую величену, на которую хотите получить формулы🔍')
    await message.answer('Чтобы выйти из поиска нужно написать "cancel"✅')


@router.message(StepGetPhysicsFormul.GET_FORMULS)
async def get_physics_formuls(message: Message, state: FSMContext) -> None:

    if message.text == 'cancel':

        await state.clear()
        await message.answer('Вы вышли из режима поиска формул✅')

        return None

    value = message.text.strip()

    if value:

        try:

            physicsFormul = PhysicsFormul(value)

        except SearchError as error:

            await message.answer(str(error))
            logging.error(f'Ошибка поиска у пользователя с ошибкой: {str(error)}')

        except WriteNotStr as error:

            await message.answer(str(error))
            logging.error(f'Ввод неправильного формата пользователем с ошибкой: {str(error)}')

        else:

            await message.answer('Таккк. Я нашёл информацию по вашему запросу.')
            await message.answer(f'Измеряется {physicsFormul.name} в {physicsFormul.unit}')
            await message.answer('Вот все найденные мной формулы: ')

            for index, url_image in enumerate(physicsFormul.physics_formuls):

                await message.bot.send_photo(message.chat.id, URLInputFile(url_image))
                await message.answer(f'''Вот расшифровка значений: \n
{'·' + '\n·'.join(physicsFormul.physics_formuls_decoding[index])}''')

    else:

        await message.answer('❌Вы не ввели физическое обозначение❌')


@router.message(Command(commands=['append_formul']))
async def process_append_formul(message: Message, state: FSMContext) -> None:

    if message.from_user.id not in ID_ADMIN:

        await message.answer('❌Извините, но у вас недостаточно прав для пользованием этой коммандой❌')

        return None

    await message.answer('Введите, пожалуйста, что ищёт ваша формула')
    await state.set_state(StepAppendPhysicsFormuls.VALUE)


@router.message(StepAppendPhysicsFormuls.VALUE)
async def append_value_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(value=message.text)
    await message.answer('Отлично, теперь введите расшифровку физического обозначения (через ";")')
    await state.set_state(StepAppendPhysicsFormuls.DESCRIPTION)


@router.message(StepAppendPhysicsFormuls.DESCRIPTION)
async def appned_description_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(description=message.text)
    await message.answer('Хорошо, теперь введите ссылку на формулу')
    await state.set_state(StepAppendPhysicsFormuls.FORMUL)


@router.message(StepAppendPhysicsFormuls.FORMUL)
async def appned_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(formul=message.text)
    await message.answer('Превосходно, осталось совсем немного, введите в чём измеряется')
    await state.set_state(StepAppendPhysicsFormuls.UNIT)


@router.message(StepAppendPhysicsFormuls.UNIT)
async def appned_unit_formul(message: Message, state: FSMContext) -> None:

    await state.update_data(unit=message.text)

    data = await state.get_data()
    await message.answer(f'''Вы молодец. Вот что у нас с вами получилось:
\n·физическое обозначение: {data['value']},
·расшифровка: {data['description']}''')
    await message.bot.send_photo(message.chat.id, URLInputFile(data['formul']))
    await message.answer(f'·в чём измеряется: {data['unit']}')
    await message.answer('''Всё верно ? \n(Напишите yes, если верно.\nНапишите no, если хотите попробовать ещё раз написать.
Напишите cancel, если хотите выйти из режима добавления формулы)''')
    await state.set_state(StepAppendPhysicsFormuls.ACCEPT)


@router.message(StepAppendPhysicsFormuls.ACCEPT)
async def accept_formul(message: Message, state: FSMContext) -> None:

    if message.text == 'no':

        await state.clear()
        await message.answer('Введите, пожалуйста, что ищёт ваша формула')
        await state.set_state(StepAppendPhysicsFormuls.VALUE)

    elif message.text == 'cancel':

        await state.clear()
        await message.answer('Вы вышли из режима добавления формул')

    else:

        data = await state.get_data()

        try:

            append_physics_formul = AppendPhysicsFormuls(data['value'], data['description'], data['formul'], data['unit'])
            append_physics_formul.append_formul()

        except ValueNotUniqueError as error:

            await message.answer(str(error))
            logging.error(f'Ввод неподходящей формулы с ошибкой: {str(error)}')

        await message.answer('Формула успешно добавлена')
        logging.info(f'Добавление новой формулы с параметрами: {data}')


@router.message(Command(commands=['support']))
async def process_get_support(message: Message) -> None:

    await message.answer('''🔥Вот наши контакты:🔥
@Rodcooo,
@Id103628800.
Ответим в течение недели''')
