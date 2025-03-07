from sqlite3 import connect
from typing import Any

from config import DATA_BASE
from physics_error import SearchError, WriteNotStr


class FindPhysicsFormul:

    '''Класс для поиска формул по физике'''

    def __init__(self, name: str) -> None:

        self.name = name
        self.physics_name = self.__get_physics_name()
        self.unit = self.__get_unit()
        self.physics_formuls = self.__get_physics_formul()
        self.physics_formuls_decoding = self.__get_decoding_formuls()

    def __setattr__(self, name: str, value: str) -> None:

        if name == 'name' and type(value) is not str:

            raise WriteNotStr('😢Извините, но вы ввели недопустимое значение !😢')

        else:

            super().__setattr__(name, value)

    def __get_physics_name(self) -> str:  # Возвращает физическое обозначение от его названия

        with connect(DATA_BASE) as con:

            curcor = con.cursor()

            result = curcor.execute(f'''SELECT Value FROM physics_value
                                        WHERE Value LIKE '%{self.name.lower()}%' OR Description LIKE '%{self.name.lower()}%' ''').fetchall()
            print(result)

            if not result:

                raise SearchError(f'Не найденно физического значения по имени: {self.name}')

        return self.remove_tuple(result[0])

    def __get_unit(self) -> str:

        with connect(DATA_BASE) as con:

            cursor = con.cursor()
            result = cursor.execute(f'''SELECT Unit FROM physics_value
                                        WHERE Value = '{self.physics_name}' ''').fetchall()

        if result[0][0] is None:

            result = 'просто числах'

        else:

            result = result[0][0]

        return result

    def __get_physics_formul(self) -> list:  # Возвращает список найденных физических обозначений

        with connect(DATA_BASE) as con:

            cursor = con.cursor()
            result = cursor.execute(f'''SELECT Formuls FROM physics_formuls
                                        WHERE Value = '{self.physics_name}' ''').fetchall()

        if not result:

            raise SearchError(f'😢Извините, но результат поиска формулы по имени {self.name} в базе данных не найден😢')

        return [self.remove_tuple(formul) for formul in result]

    def __get_decoding_formuls(self) -> list:  # Возвращает список расшифрованных физических обозначений

        with connect(DATA_BASE) as con:

            cursor = con.cursor()
            result = cursor.execute(f'''SELECT Description_Formuls FROM physics_formuls
                                        WHERE Value = '{self.physics_name}' ''').fetchall()

            all_description = []

            for value_formuls in result:

                if not value_formuls:

                    raise SearchError('Неизвестная ошибка. Просим обратиться в поддержку')

                value_formuls = self.remove_tuple(value_formuls)
                values = value_formuls.split(';')
                description_values = []

                for value in values:

                    result_description = cursor.execute(f'''SELECT Description, Unit FROM physics_value
                                                            WHERE Value = '{value}' ''').fetchall()
                    description_values.append(f'{value[:value.find('(')]} - {result_description[0][0]} [{result_description[0][1]}]')

                all_description.append(description_values)

        return all_description

    @staticmethod
    def remove_tuple(formul: tuple) -> str:  # Убирает скобки у кортежа

        string = str(formul)
        string = string[2:-3]

        return string


class FindPhysicsName:

    '''Класс для нахождения физических обозначений'''

    @classmethod
    def get_all_physics_name(cls) -> list[list[str]]:  # Делит физические обозначения по категориям

        with connect(DATA_BASE) as con:

            cursor = con.cursor()
            result = cursor.execute('''SELECT Description, Value, Chapter FROM physics_value''').fetchall()

        result.sort(key=lambda data: data[2])
        chapters = cls.get_chapters()
        last_chapter = chapters[0]
        physics_name_lists = []
        physics_name_list = []

        for data in result:

            description, value, chapter = data

            if last_chapter != chapter:

                last_chapter = chapter
                physics_name_lists.append(physics_name_list)
                physics_name_list = []

            physics_name_list.append(f'{value} - {description}')

        return physics_name_lists

    @classmethod
    def get_chapters(cls) -> list[str]:

        with connect(DATA_BASE) as con:

            cursor = con.cursor()
            result = list(map(FindPhysicsFormul.remove_tuple, cursor.execute('''SELECT DISTINCT Chapter FROM physics_value''').fetchall()))

        return sorted(result)


class AppendPhysicsFormuls:

    '''Класс для добавление формулы в базу данных'''

    def __init__(self, value: str, description: str, formul: str, description_formul: str, unit: str, chapter: str) -> None:

        self.value = value
        self.description = description
        self.formul = formul
        self.unit = unit
        self.description_formul = description_formul
        self.chapter = chapter

    def __setattr__(self, name: str, value: Any) -> None:

        if name in ('value', 'description', 'formul', 'unit', 'description_formul', 'chapter') and type(value) is str:

            raise WriteNotStr('Неизвестеная ошибка. Извините, отправлены неизвестные объекты')

        super().__setattr__(name, value)

    def append_formul(self) -> None:

        with connect(DATA_BASE) as con:

            cursor = con.cursor()

            cursor.execute(f'''INSERT INTO physics_formuls (Value, Formuls, Description_Formuls)
                               VALUES ({self.value}, {self.formul}, {self.description_formul})''')
            cursor.execute(f'''INSERT INTO physics_value (Descriptions, Value, Unit, Chapter)
                               VALUES ({self.description}, {self.value}, {self.unit}, {self.chapter})''')
