import unittest
from unittest.mock import MagicMock
from isotope.isotope_comms_lib import Isotope_comms_protocol
from isotope.port.motor import Motor

class TestMotor(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.motor = Motor(self.isotope_mock, 0, 1, 100, 100)

    def test_constructor_with_invalid_port_id(self):
        with self.assertRaises(ValueError):
            Motor(self.isotope_mock, 4, 1, 100, 100)

    def test_constructor_with_invalid_resolution(self):
        with self.assertRaises(ValueError):
            Motor(self.isotope_mock, 0, -1, 100, 100)

    def test_constructor_with_invalid_rpm(self):
        with self.assertRaises(ValueError):
            Motor(self.isotope_mock, 0, 1, 100, -100)

    def test_constructor_with_invalid_current(self):
        with self.assertRaises(ValueError):
            Motor(self.isotope_mock, 0, 1, -100, 100)

    def test_enable(self):
        self.isotope_mock.set_motor_enable.return_value = True
        result = self.motor.enable()
        self.assertTrue(result)
        self.assertTrue(self.motor.is_enabled())

    def test_disable(self):
        self.isotope_mock.set_motor_enable.return_value = True
        self.motor.enable()
        result = self.motor.disable()
        self.assertTrue(result)
        self.assertFalse(self.motor.is_enabled())

    def test_get_rpm(self):
        result = self.motor.get_rpm()
        self.assertEqual(result, 100)

    def test_get_current(self):
        result = self.motor.get_current()
        self.assertEqual(result, 100)

    def test_get_resolution(self):
        result = self.motor.get_resolution()
        self.assertEqual(result, 1)

    def test_rotate_by_steps(self):
        self.isotope_mock.set_motor_step.return_value = True
        result = self.motor.rotate_by_steps(100)
        self.assertTrue(result)

    def test_rotate_by_degrees(self):
        self.isotope_mock.set_motor_step.return_value = True
        result = self.motor.rotate_by_degrees(90)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()