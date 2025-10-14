class VacuumCleaner:
    def __init__(self) -> None:
         self.dust_collected = 0  # Собранная пыль

    def vacuum(self):
         """Метод для всасывания пыли"""
         self.dust_collected += 1
         print(f"Впитывание пыли... Собрано {self.dust_collected} единиц пыли.")

 # Базовый класс для машины на радиоуправлении
class RemoteControlCar:
    def __init__(self) -> None:
         self.position = [0, 0]  # Начальная позиция
         self.direction = "N"  # Направление: N, E, S, W

    def move_forward(self, distance: int) -> None:
         """Метод для движения вперед"""
         if self.direction == "N":
             self.position[1] += distance
         elif self.direction == "E":
             self.position[0] += distance
         elif self.direction == "S":
             self.position[1] -= distance
         elif self.direction == "W":
             self.position[0] -= distance
         print(f"Двигаемся вперед на {distance} единиц. Позиция: {self.position}")

    def move_backward(self, distance: int) -> None:
         """Метод для движения назад"""
         if self.direction == "N":
             self.position[1] -= distance
         elif self.direction == "E":
             self.position[0] -= distance
         elif self.direction == "S":
             self.position[1] += distance
         elif self.direction == "W":
             self.position[0] += distance
         print(f"Двигаемся назад на {distance} единиц. Позиция: {self.position}")

    def turn_left(self) -> None:
         """Поворот налево"""
         directions = ["N", "W", "S", "E"]
         self.direction = directions[(directions.index(self.direction) + 1) % 4]
         print(f"Поворот налево. Теперь направление: {self.direction}")

    def turn_right(self) -> None:
         """Поворот направо"""
         directions = ["N", "E", "S", "W"]
         self.direction = directions[(directions.index(self.direction) + 1) % 4]
         print(f"Поворот направо. Теперь направление: {self.direction}")

 # Класс для автономного движения
class AutonomousMovement:
    def __init__(self) -> None:
        self.sensors = {"front": False, "left": False, "right": False}  # Ложь означает, что препятствий нет

    def detect_obstacle(self, direction) -> dict:
        """Метод для распознавания препятствия"""
        return self.sensors[direction]

    def auto_move(self) -> None:
        """Метод для автономного движения"""
        if not self.detect_obstacle("front"):
            print("Препятствий впереди нет, едем вперед.")
            self.move_forward(1)
        else:
            print("Обнаружено препятствие! Пытаемся объехать...")
            if not self.detect_obstacle("left"):
                self.turn_left()
                self.move_forward(1)
            elif not self.detect_obstacle("right"):
                self.turn_right()
                self.move_forward(1)
            else:
                print("Заблокирован со всех сторон. Остановка.")

 # Итоговый класс автономного робота для уборки
class AutonomousCleaningRobot(VacuumCleaner, RemoteControlCar, AutonomousMovement):
    def __init__(self) -> None:
        VacuumCleaner.__init__(self)
        RemoteControlCar.__init__(self)
        AutonomousMovement.__init__(self)

    def clean_and_move(self) -> None:
        """Метод для автономной уборки и движения"""
        print("Начинаем уборку...")
        self.vacuum()  # Включаем всасывание
        self.auto_move()  # Автономное движение