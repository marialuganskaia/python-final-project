class StringValue:
    def __init__(self, min_length, max_length):
        pass

    def __set_name__(self, owner, name):
        pass # Обратите внимание, имя должно быть protected

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass


class PriceValue:
    def __init__(self, max_value):
        pass

    def __set_name__(self, owner, name):
        pass # Обратите внимание, имя должно быть protected

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass


class AutoSalon:
    def __init__(self, name):
        pass

    def add_car(self, car):
        pass

    def remove_car(self, car):
        pass


class Car:
    # YOUR CODE: Descriptors for name and price

    def __init__(self, name, price):
        pass