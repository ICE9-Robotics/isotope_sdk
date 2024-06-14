import unittest
from unittest.mock import MagicMock
from isotope.isotope_comms_lib import Isotope_comms_protocol
from isotope.port.power_output import PowerOutput

class TestPowerOutput(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.power_output = PowerOutput(self.isotope_mock, 0)
        
    def test_constructor_with_invalid_port_id(self):
        with self.assertRaises(ValueError):
            PowerOutput(self.isotope_mock, 3)

    def test_constructor_with_valid_pwm(self):
        pwm_val = 512
        power_output = PowerOutput(self.isotope_mock, 1, pwm_val)
        self.assertEqual(power_output.get_default_pwm(), pwm_val)

    def test_constructor_with_invalid_pwm(self):
        with self.assertRaises(ValueError):
            PowerOutput(self.isotope_mock, 2, 2048)

    def test_get_pwm(self):
        pwm_val = 512
        self.power_output._current_pwm = pwm_val
        result = self.power_output.get_pwm()
        self.assertEqual(result, pwm_val)

    def test_get_default_pwm(self):
        pwm_val = 1024
        self.power_output._defaut_pwm = pwm_val
        result = self.power_output.get_default_pwm()
        self.assertEqual(result, pwm_val)

    def test_enable_with_valid_pwm(self):
        self.isotope_mock.set_power_output.return_value = True
        result = self.power_output.enable(pwm=512)
        self.assertTrue(result)
        self.assertTrue(self.power_output.is_enabled())
        self.assertEqual(self.power_output.get_pwm(), 512)

    def test_enable_with_invalid_pwm(self):
        with self.assertRaises(ValueError):
            self.power_output.enable(pwm=2048)

    def test_enable_with_zero_pwm(self):
        self.isotope_mock.set_power_output.return_value = True
        result = self.power_output.enable(pwm=0)
        self.assertTrue(result)
        self.assertFalse(self.power_output.is_enabled())
        self.assertEqual(self.power_output.get_pwm(), 0)

    def test_enable_with_default_pwm(self):
        self.isotope_mock.set_power_output.return_value = True
        result = self.power_output.enable()
        self.assertTrue(result)
        self.assertTrue(self.power_output.is_enabled())
        self.assertEqual(self.power_output.get_pwm(), self.power_output.get_default_pwm())

    def test_disable(self):
        self.isotope_mock.set_power_output.return_value = True
        self.power_output.enable()
        result = self.power_output.disable()
        self.assertTrue(result)
        self.assertFalse(self.power_output.is_enabled())
        self.assertEqual(self.power_output.get_pwm(), 0)

if __name__ == '__main__':
    unittest.main()