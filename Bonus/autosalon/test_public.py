import unittest

from salon import StringValue, PriceValue, AutoSalon, Car


class TestStringValue(unittest.TestCase):
    def test_valid_string(self) -> None:
        class TestClass:
            name: str = StringValue(2, 50)

            def __init__(self, name: str) -> None:
                self.name = name

        obj = TestClass("ValidName")
        self.assertEqual(obj.name, "ValidName")

    def test_invalid_string_length(self) -> None:
        class TestClass:
            name: str = StringValue(2, 50)

            def __init__(self, name: str) -> None:
                self.name = name

        obj = TestClass("OK")
        obj.name = "A"  # слишком короткая строка
        self.assertEqual(obj.name, "OK")  # значение не должно измениться

    def test_non_string_value(self) -> None:
        class TestClass:
            name: str = StringValue(2, 50)

            def __init__(self, name: str) -> None:
                self.name = name

        obj = TestClass("ValidName")
        obj.name = 12345  # не строка
        self.assertEqual(obj.name, "ValidName")  # значение не должно измениться


class TestPriceValue(unittest.TestCase):
    def test_valid_price(self) -> None:
        class TestClass:
            price: float = PriceValue(10000)

            def __init__(self, price: float) -> None:
                self.price = price

        obj = TestClass(9999.99)
        self.assertEqual(obj.price, 9999.99)

    def test_invalid_price_negative(self) -> None:
        class TestClass:
            price: float = PriceValue(10000)

            def __init__(self, price: float) -> None:
                self.price = price

        obj = TestClass(5000)
        obj.price = -100  # отрицательное значение
        self.assertEqual(obj.price, 5000)  # значение не должно измениться

    def test_invalid_price_over_max(self) -> None:
        class TestClass:
            price: float = PriceValue(10000)

            def __init__(self, price: float) -> None:
                self.price = price

        obj = TestClass(5000)
        obj.price = 15000  # больше максимального значения
        self.assertEqual(obj.price, 5000)  # значение не должно измениться

    def test_non_numeric_price(self) -> None:
        class TestClass:
            price: float = PriceValue(10000)

            def __init__(self, price: float) -> None:
                self.price = price

        obj = TestClass(5000)
        obj.price = "expensive"  # не числовое значение
        self.assertEqual(obj.price, 5000)  # значение не должно измениться


class TestCar(unittest.TestCase):
    def test_car_creation(self) -> None:
        car: Car = Car("Lada", 3000)
        self.assertEqual(car.name, "Lada")
        self.assertEqual(car.price, 3000)

    def test_invalid_car_name(self) -> None:
        car: Car = Car("Lada", 3000)
        car.name = "A"  # слишком короткое имя
        self.assertEqual(car.name, "Lada")  # значение не должно измениться

    def test_invalid_car_price(self) -> None:
        car: Car = Car("Lada", 3000)
        car.price = -500  # отрицательная цена
        self.assertEqual(car.price, 3000)  # значение не должно измениться


class TestAutoSalon(unittest.TestCase):
    def test_autosalon_creation(self) -> None:
        salon: AutoSalon = AutoSalon("AutoWorld")
        self.assertEqual(salon.name, "AutoWorld")
        self.assertEqual(salon.cars, [])

    def test_add_car(self) -> None:
        salon: AutoSalon = AutoSalon("AutoWorld")
        car: Car = Car("Nissan", 8000)
        salon.add_car(car)
        self.assertIn(car, salon.cars)

    def test_remove_car(self) -> None:
        salon: AutoSalon = AutoSalon("AutoWorld")
        car: Car = Car("Nissan", 8000)
        salon.add_car(car)
        salon.remove_car(car)
        self.assertNotIn(car, salon.cars)

    def test_remove_nonexistent_car(self) -> None:
        salon: AutoSalon = AutoSalon("AutoWorld")
        car1: Car = Car("Nissan", 8000)
        car2: Car = Car("Toyota", 9000)
        salon.add_car(car1)
        salon.remove_car(car2)  # пытаемся удалить машину, которой нет в списке
        self.assertIn(car1, salon.cars)
        self.assertNotIn(car2, salon.cars)


if __name__ == "__main__":
    unittest.main()
