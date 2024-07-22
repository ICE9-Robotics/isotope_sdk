import unittest
from unittest.mock import MagicMock
from isotope.isotope_comms_lib import IsotopeCommsProtocol
from isotope.port.pwm_output import PWMOutputPort, PWMOutput

class TestPWMOutputPort(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=IsotopeCommsProtocol)
        self.pwm_output_port = PWMOutputPort(self.isotope_mock, 0)

    def test_set_pwm_success(self):
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertTrue(self.pwm_output_port.set_pwm(512))
        
    def test_set_pwm_with_valid_value_err_resp(self):
        self.isotope_mock.is_resp_ok.return_value = False
        self.assertFalse(self.pwm_output_port.set_pwm(512))

    def test_set_pwm_with_invalid_value(self):
        with self.assertRaises(ValueError):
            self.pwm_output_port.set_pwm(2048)
        
    def test_get_pwm_success(self):        
        self.isotope_mock.send_cmd.return_value = (512, "ACK")
        self.isotope_mock.is_resp_ok.return_value = True
        self.assertEqual(self.pwm_output_port.get_pwm(), 512)

    def test_get_pwm_err_resp(self):
        self.isotope_mock.send_cmd.return_value = (512, "ERR")
        self.isotope_mock.is_resp_ok.return_value = False
        self.assertEqual(self.pwm_output_port.get_pwm(), None)


class TestPWMOutput(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=IsotopeCommsProtocol)
        self.pwm_output = PWMOutput(self.isotope_mock)

    def test_getitem_with_valid_index(self):
        port = self.pwm_output[0]
        self.assertIsInstance(port, PWMOutputPort)
        self.assertEqual(port._id, 0)

    def test_getitem_with_invalid_index(self):
        with self.assertRaises(ValueError):
            self.pwm_output[4]

if __name__ == '__main__':
    unittest.main()