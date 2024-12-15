import sqlite3
from typing import Any

from config import DATA_BASE
from physics_error import SearchError, ValueNotUniqueError


class PhysicsFormul:

    '''Класс для поиска формул по физике'''

    def __init__(self, name: str) -> None:

        self.name = name
        self.physics_name = self.__get_physics_name()
        self.unit = self.__get_unit()
        self.physics_formuls = self.__get_physics_formul()
        self.physics_formuls_decoding = self.__get_decoding_formuls()

    def __get_physics_name(self) -> str:  # Возвращает физическое обозначение от его названия

        with sqlite3.connect(DATA_BASE) as connect:

            cursor = connect.cursor()
            result = cursor.execute(f'''SELECT Value FROM physics_value
                                        WHERE Description = '{self.name}' OR Value = '{self.name}' ''').fetchall()

        if not result:

            raise SearchError(f'😢Извините, но результат поиска имени {self.name} в базе данных не найден😢')

        return self.remove_tuple(result[0])

    def __get_unit(self) -> str:

        with sqlite3.connect(DATA_BASE) as connect:

            curosr = connect.cursor()
            result = curosr.execute(f'''SELECT Unit FROM physics_value
                                        WHERE Value = '{self.physics_name}' ''').fetchall()

        if result[0][0] is None:

            result = 'просто числах'

        else:

            result = result[0][0]

        return result

    def __get_physics_formul(self) -> list:  # Возвращает список найденных физических обозначений

        with sqlite3.connect(DATA_BASE) as connect:

            cursor = connect.cursor()
            print(self.physics_name)
            result = cursor.execute(f'''SELECT Formuls FROM physics_formuls
                                        WHERE Value = '{self.physics_name}' ''').fetchall()

        if not result:

            raise SearchError(f'😢Извините, но результат поиска формулы по имени {self.name} в базе данных не найден😢')

        return [self.remove_tuple(formul) for formul in result]

    def __get_decoding_formuls(self) -> list:  # Возвращает список расшифрованных физических обозначений

        with sqlite3.connect(DATA_BASE) as connect:

            decoding_formuls_list = []

            for formul in self.physics_formuls:

                decoding_formul = ''
                values = formul.split()

                for value in values:

                    cursor = connect.cursor()
                    result = cursor.execute(f'''SELECT Description FROM physics_value
                                                WHERE Value = '{value}' ''').fetchall()

                    if not result:

                        decoding_formul += value + ' '

                    else:

                        decoding_formul += result[0][0] + ' '

                decoding_formuls_list.append(decoding_formul)

        return decoding_formuls_list

    @staticmethod
    def remove_tuple(formul: tuple) -> str:  # Убирает скобки у кортежа

        string = str(formul)
        string = string[2:-3]

        return string


class PhysicsName:

    '''Класс для нахождения физических обозначений'''

    STEP_NAME = 50

    @classmethod
    def get_all_physics_name(cls) -> list[list]:

        with sqlite3.connect(DATA_BASE) as connect:

            cursor = connect.cursor()
            result = cursor.execute('''SELECT Description, Value FROM physics_value''').fetchall()

        index = 0
        start_index = 0
        end_index = 50
        physics_name_lists = []

        for index in range(len(result) // cls.STEP_NAME + 1):

            physics_name_lists.append([])

            for name, physics_name in result[start_index:end_index]:

                value = f'{name} - {physics_name}'
                physics_name_lists[index].append(value)

            index += 1
            start_index = end_index
            end_index += 50

        return physics_name_lists


class AppendPhysicsFormuls:

    '''Класс для добавление формулы в базу данных'''

    def __init__(self, value: str, description: str, formul: str, unit: str) -> None:

        self.value = value
        self.description = description
        self.formul = formul
        self.unit = unit

        self.is_append_value = True
        self.is_append_formul = True

    def __setattr__(self, name: str, value: Any) -> None:

        if (name == 'value' or name == 'description') and not self.check_value_unique(value):

            self.is_append_value = False

        elif name == 'formul' and not self.check_formul_unique(value):

            self.is_append_formul = False

        super().__setattr__(name, value)

    def append_formul(self) -> None:

        if not self.is_append_formul and not self.is_append_value:

            raise ValueNotUniqueError('Такая формула уже есть для этого обозначения')

        with sqlite3.connect(DATA_BASE) as connect:

            cursor = connect.cursor()

            if self.is_append_formul:

                cursor.execute(f'''INSERT INTO physics_formuls(Value, Formuls) VALUES('{self.value}', '{self.formul}')''')

            if self.is_append_value:

                cursor.execute(f'''INSERT INTO physics_value(Value, Description, Unit) VALUES('{self.value}', '{self.description}', '{self.unit}')''')

    def check_value_unique(self, value: str) -> None:

        with sqlite3.connect(DATA_BASE) as connect:

            cursor = connect.cursor()
            result = cursor.execute(f'''SELECT COUNT(ID) FROM physics_value
                                        WHERE Value = '{value}' AND Description = '{value}' ''').fetchall()

        return True if result[0][0] else False

    def check_formul_unique(self, formul: str) -> None:

        with sqlite3.connect(DATA_BASE) as connect:

            cursor = connect.cursor()
            result = cursor.execute(f'''SELECT COUNT(ID) FROM physics_formuls
                                        WHERE Formuls = '{formul}' ''').fetchall()

        return True if result[0][0] else False
