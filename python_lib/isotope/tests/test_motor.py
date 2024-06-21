import unittest
from unittest.mock import MagicMock
from isotope.isotope_comms_lib import Isotope_comms_protocol
from isotope.port.motor import MotorPort, Motor

class TestMotorPort(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.motor_port = MotorPort(self.isotope_mock, 0)
        
    def test_constructor_with_invalid_port_id(self):
        with self.assertRaises(ValueError):
            MotorPort(self.isotope_mock, 4)
            
    def test_configure_with_valid_parameters(self):
        resolution = 1
        current = 100
        rpm = 200
        self.isotope_mock.send_cmd.return_value = True
        result = self.motor_port.configure(resolution, current, rpm)
        self.assertTrue(result)
        self.assertEqual(self.motor_port.resolution, resolution)
        self.assertEqual(self.motor_port.current, current)
        self.assertEqual(self.motor_port.rpm, rpm)
        
    def test_configure_with_negative_resolution(self):
        with self.assertRaises(ValueError):
            self.motor_port.configure(-1, 100, 200)
            
    def test_configure_with_negative_current(self):
        with self.assertRaises(ValueError):
            self.motor_port.configure(1, -100, 200)
            
    def test_configure_with_negative_rpm(self):
        with self.assertRaises(ValueError):
            self.motor_port.configure(1, 100, -200)
        
    def test_enable(self):
        self.motor_port._enabled = False
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertTrue(self.motor_port.enable())
        self.assertTrue(self.motor_port.is_enabled())
        
    def test_enable_fail(self):
        self.motor_port._enabled = False
        self.isotope_mock.is_resp_ok.return_value = False
        self.assertFalse(self.motor_port.enable())
        self.assertFalse(self.motor_port.is_enabled())
        
    def test_disable(self):
        self.motor_port._enabled = True
        self.isotope_mock.is_resp_ok.return_value = True
        self.motor_port.enable()
        self.assertTrue(self.motor_port.disable())
        self.assertFalse(self.motor_port.is_enabled())
        
    def test_disable(self):
        self.motor_port._enabled = True
        self.isotope_mock.is_resp_ok.return_value = False
        self.motor_port.enable()
        self.assertFalse(self.motor_port.disable())
        self.assertTrue(self.motor_port.is_enabled())
        
    def test_rotate_by_steps(self):
        steps = 100
        self.isotope_mock.is_resp_ok.return_value = True
        self.motor_port.configure(1, 100, 200)
        self.motor_port.enable()
        self.assertTrue(self.motor_port.rotate_by_steps(steps))
        
    def test_rotate_by_steps(self):
        steps = 100
        self.isotope_mock.is_resp_ok.return_value = False
        self.motor_port.configure(1, 100, 200)
        self.motor_port.enable()
        self.assertFalse(self.motor_port.rotate_by_steps(steps))
        
    def test_rotate_by_degrees(self):
        degrees = 90
        self.isotope_mock.is_resp_ok.return_value = True
        self.motor_port.configure(1, 100, 200)
        self.motor_port.enable()
        result = self.motor_port.rotate_by_degrees(degrees)
        self.assertTrue(result)
        
    def test_rotate_by_degrees_fail(self):
        degrees = 90
        self.isotope_mock.is_resp_ok.return_value = False
        self.motor_port.configure(1, 100, 200)
        self.motor_port.enable()
        self.assertFalse(self.motor_port.rotate_by_degrees(degrees))

    def test_rotate_by_degrees_without_enable_motor(self):
        degrees = 90
        self.motor_port.configure(1, 100, 200)
        self.assertFalse(self.motor_port.rotate_by_degrees(degrees))
        
    def test_set_rpm_success(self):
        rpm = 300
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertTrue(self.motor_port.set_rpm(rpm))
        self.assertEqual(self.motor_port.rpm, rpm)
        
    def test_set_rpm_fail(self):
        self.motor_port._rpm = 100
        self.isotope_mock.is_resp_ok.return_value = False
        self.assertFalse(self.motor_port.set_rpm(0))
        self.assertEqual(self.motor_port.rpm, 100)
        
    def test_set_current_success(self):
        current = 200
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertTrue(self.motor_port.set_current(current))
        self.assertEqual(self.motor_port.current, current)
        
    def test_set_current_fail(self):
        self.motor_port._current = 5
        self.isotope_mock.is_resp_ok.return_value = False
        self.assertFalse(self.motor_port.set_current(10))
        self.assertEqual(self.motor_port.current, 5)
        
        
class TestMotor(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.motor = Motor(self.isotope_mock)

    def test_get_motor_port(self):
        motor_port = self.motor[0]
        self.assertIsInstance(motor_port, MotorPort)
        self.assertEqual(motor_port._id, 0)

    def test_get_invalid_motor_port(self):
        with self.assertRaises(ValueError):
            motor_port = self.motor[4]

if __name__ == '__main__':
    unittest.main()