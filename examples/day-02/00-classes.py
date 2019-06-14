"""
Основы ООП - конструктор, наследование, перегрузка
"""


class User:
    name: str

    def hello(self):
        print(f"Hello, {self.name}!")


john = User()
john.name = "John"

john.hello()
