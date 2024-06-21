import unittest
from unittest.mock import MagicMock
from isotope.isotope_comms_lib import Isotope_comms_protocol
from isotope.port.power_output import PowerOutput, PowerOutputPort

class TestPowerOutputPort(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.power_output_port = PowerOutputPort(self.isotope_mock, 0)

    def test_default_pwm(self):
        self.assertEqual(self.power_output_port.default_pwm, 1024)

    def test_set_default_pwm(self):
        self.power_output_port.default_pwm = 512
        self.assertEqual(self.power_output_port.default_pwm, 512)

    def test_set_default_pwm_invalid_value(self):
        with self.assertRaises(ValueError):
            self.power_output_port.default_pwm = 2048

    def test_enable_with_default_pwm(self):
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertTrue(self.power_output_port.enable())
        self.assertEqual(self.power_output_port.get_pwm(), 1024)

    def test_enable_with_custom_pwm(self):
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertTrue(self.power_output_port.enable(512))
        self.assertEqual(self.power_output_port.get_pwm(), 512)

    def test_enable_err_resp(self):
        pwm = self.power_output_port.get_pwm()
        self.isotope_mock.is_resp_ok.return_value = False
        self.assertFalse(self.power_output_port.enable(250))
        self.assertEqual(self.power_output_port.get_pwm(), pwm)

    def test_enable_with_zero_pwm(self):
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertTrue(self.power_output_port.enable(0))
        self.assertEqual(self.power_output_port.get_pwm(), 0)
        self.assertFalse(self.power_output_port.is_enabled())

    def test_enable_with_custom_pwm_invalid_value(self):
        with self.assertRaises(ValueError):
            self.power_output_port.enable(2048)

    def test_disable(self):
        self.assertTrue(self.power_output_port.disable())
        self.assertEqual(self.power_output_port.get_pwm(), 0)

    def test_is_enabled(self):
        self.assertFalse(self.power_output_port.is_enabled())
        self.power_output_port.enable()
        self.assertTrue(self.power_output_port.is_enabled())

    def test_get_pwm(self):
        self.assertEqual(self.power_output_port.get_pwm(), 0)
        self.power_output_port.enable(512)
        self.assertEqual(self.power_output_port.get_pwm(), 512)
        
class TestPowerOutput(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.power_output = PowerOutput(self.isotope_mock)

    def test_getitem_with_valid_index(self):
        port_id = 0
        port = self.power_output[port_id]
        self.assertIsInstance(port, PowerOutputPort)
        self.assertEqual(port._id, port_id)

    def test_getitem_with_invalid_index(self):
        with self.assertRaises(ValueError):
            self.power_output[3]

    def test_getitem_with_negative_index(self):
        with self.assertRaises(ValueError):
            self.power_output[-1]

if __name__ == '__main__':
    unittest.main()
