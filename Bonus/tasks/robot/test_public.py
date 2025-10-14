import unittest
from robot import (
    AutonomousCleaningRobot,
    Direction,
    Movement,
    TurnDirection,
    SensorDirection,
)


class TestAutonomousCleaningRobotMovement(unittest.TestCase):

    def setUp(self) -> None:
        self.robot: AutonomousCleaningRobot = AutonomousCleaningRobot()

    def test_initial_position(self) -> None:
        self.assertEqual(self.robot.position, [0, 0])
        self.assertEqual(self.robot.direction, Direction.NORTH)

    def test_move_forward(self) -> None:
        self.robot.move(3, Movement.FORWARD)
        self.assertEqual(self.robot.position, [0, 3])

    def test_move_backward(self) -> None:
        self.robot.move(2, Movement.BACKWARD)
        self.assertEqual(self.robot.position, [0, -2])

    def test_turn_left_and_move_forward(self) -> None:
        self.robot.turn(TurnDirection.LEFT)
        self.robot.move(4, Movement.FORWARD)
        self.assertEqual(self.robot.direction, Direction.WEST)
        self.assertEqual(self.robot.position, [-4, 0])

    def test_turn_right_and_move_forward(self) -> None:
        self.robot.turn(TurnDirection.RIGHT)
        self.robot.move(5, Movement.FORWARD)
        self.assertEqual(self.robot.direction, Direction.EAST)
        self.assertEqual(self.robot.position, [5, 0])

    def test_move_in_square(self) -> None:
        for _ in range(4):
            self.robot.move(2, Movement.FORWARD)
            self.robot.turn(TurnDirection.RIGHT)
        self.assertEqual(self.robot.position, [0, 0])
        self.assertEqual(self.robot.direction, Direction.NORTH)

    def test_multiple_turns(self) -> None:
        for _ in range(4):
            self.robot.turn(TurnDirection.RIGHT)
        self.assertEqual(self.robot.direction, Direction.NORTH)

    def test_autonomous_movement_with_obstacle(self) -> None:
        self.robot.sensors[SensorDirection.FRONT] = True
        self.robot.auto_move()
        self.assertNotEqual(self.robot.direction, Direction.NORTH)
        self.assertNotEqual(self.robot.position, [0, 0])


class TestAutonomousCleaningRobotMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.robot: AutonomousCleaningRobot = AutonomousCleaningRobot()

    def test_vacuum_once(self) -> None:
        self.robot.vacuum()
        self.assertEqual(self.robot.dust_collected, 1)

    def test_vacuum_multiple_times(self) -> None:
        for _ in range(5):
            self.robot.vacuum()
        self.assertEqual(self.robot.dust_collected, 5)

    def test_detect_obstacle_front(self) -> None:
        self.robot.sensors[SensorDirection.FRONT] = True
        self.assertTrue(self.robot.detect_obstacle(SensorDirection.FRONT))

    def test_detect_no_obstacle(self) -> None:
        self.assertFalse(self.robot.detect_obstacle(SensorDirection.LEFT))
        self.assertFalse(self.robot.detect_obstacle(SensorDirection.RIGHT))

    def test_clean_and_move_no_obstacles(self) -> None:
        self.robot.clean_and_move()
        self.assertEqual(self.robot.dust_collected, 1)
        self.assertEqual(self.robot.position, [0, 1])

    def test_clean_and_move_with_obstacle(self) -> None:
        self.robot.sensors[SensorDirection.FRONT] = True
        self.robot.clean_and_move()
        self.assertEqual(self.robot.dust_collected, 1)
        self.assertNotEqual(self.robot.direction, Direction.NORTH)
        self.assertNotEqual(self.robot.position, [0, 1])

    def test_move_invalid_movement(self) -> None:
        with self.assertRaises(AttributeError):
            self.robot.move(3, "FORWARD")  # type: ignore[arg-type]

    def test_turn_invalid_direction(self) -> None:
        with self.assertRaises(AttributeError):
            self.robot.turn("LEFT")  # type: ignore[arg-type]


class TestEnums(unittest.TestCase):

    def test_direction_values(self) -> None:
        self.assertEqual(Direction.NORTH.value, "N")
        self.assertEqual(Direction.EAST.value, "E")
        self.assertEqual(Direction.SOUTH.value, "S")
        self.assertEqual(Direction.WEST.value, "W")

    def test_sensor_direction_values(self) -> None:
        self.assertEqual(SensorDirection.FRONT.value, "front")
        self.assertEqual(SensorDirection.LEFT.value, "left")
        self.assertEqual(SensorDirection.RIGHT.value, "right")

    def test_movement_values(self) -> None:
        self.assertEqual(Movement.FORWARD.value, 1)
        self.assertEqual(Movement.BACKWARD.value, -1)

    def test_turn_direction_values(self) -> None:
        self.assertEqual(TurnDirection.LEFT.value, -1)
        self.assertEqual(TurnDirection.RIGHT.value, 1)

    def test_direction_enum_membership(self) -> None:
        self.assertIn(Direction.NORTH, Direction)
        self.assertIn(Direction.SOUTH, Direction)

    def test_sensor_direction_enum_membership(self) -> None:
        self.assertIn(SensorDirection.FRONT, SensorDirection)
        self.assertIn(SensorDirection.LEFT, SensorDirection)

    def test_invalid_enum_access(self) -> None:
        with self.assertRaises(AttributeError):
            _ = Direction.UP  # type: ignore[attr-defined]

    def test_enum_type(self) -> None:
        self.assertIsInstance(Direction.NORTH, Direction)
        self.assertIsInstance(Movement.FORWARD, Movement)


if __name__ == "__main__":
    unittest.main()
