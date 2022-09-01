

class Validator():
    """Проверка и очистка данных."""
    def __init__(self, value):
        self.value = value
        self.stripped = ''


    def is_integer(self):
        """Проверка содержания суммы на целое число."""
        try:
            int(self.value)
            return True
        except ValueError:
            return False


    def strip(self):
        """Удаление лишних символов.
        Фильтрует до первого символа, не являющегося целым числом."""
        string = [*self.value]
        for i in string:
            try:
                int(i)
                self.stripped += i
            except ValueError:
                break
        return str(self.stripped)


    def clean(self):
        """Метод очистки строки. Проверяет и изменяет строку.
        Если строка начинается не с целых чисел, возвращает False."""
        if self.is_integer():
            return self.value
        stripped = self.strip()
        if stripped:
            return stripped
        else:
            return False
