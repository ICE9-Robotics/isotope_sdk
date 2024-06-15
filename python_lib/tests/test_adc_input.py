import unittest
from unittest.mock import MagicMock
from isotope.isotope_comms_lib import Isotope_comms_protocol
from isotope.port.adc_input import ADCInputPort, ADCInput

class TestADCInputPort(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.adc_input_item = ADCInputPort(self.isotope_mock, 0)
        
    def test_constructor_with_valid_port_id(self):
        self.assertEqual(self.adc_input_item._id, 0)
        
    def test_constructor_with_invalid_port_id(self):
        with self.assertRaises(ValueError):
            ADCInputPort(self.isotope_mock, 3)
            
    def test_get_value_success(self):
        expected_value = 512
        self.isotope_mock.send_cmd.return_value = (expected_value, "ACK")
        self.isotope_mock.is_resp_ok.return_value = True
        result = self.adc_input_item.get_value()
        self.assertEqual(result, expected_value)
        
    def test_get_value_failure(self):
        self.isotope_mock.send_cmd.return_value = (1, "ERR")
        self.isotope_mock.is_resp_ok.return_value = False
        result = self.adc_input_item.get_value()
        self.assertIsNone(result)

class TestADCInput(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=Isotope_comms_protocol)
        self.adc_input = ADCInput(self.isotope_mock)

    def test_get_adc_input_port_with_valid_index(self):
        result = self.adc_input[0]
        self.assertIsInstance(result, ADCInputPort)
        self.assertEqual(result._id, 0)

    def test_get_adc_input_port_with_invalid_index(self):
        with self.assertRaises(ValueError):
            self.adc_input[3]

    def test_get_value_success(self):
        expected_value = 512
        self.isotope_mock.send_cmd.return_value = (expected_value, "ACK")
        self.isotope_mock.is_resp_ok.return_value = True
        result = self.adc_input[0].get_value()
        self.assertEqual(result, expected_value)

    def test_get_value_failure(self):
        self.isotope_mock.send_cmd.return_value = (1, "ERR")
        self.isotope_mock.is_resp_ok.return_value = False
        result = self.adc_input[0].get_value()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
    