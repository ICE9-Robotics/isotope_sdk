import unittest
from unittest.mock import MagicMock
from isotope.isotope_comms_lib import IsotopeCommsProtocol
from isotope.port.temp_input import TempInputPort, TempInput

class TestTempInputPort(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=IsotopeCommsProtocol)
        self.temp_input_port = TempInputPort(self.isotope_mock, 0)

    def test_get_value_success(self):
        self.isotope_mock.send_cmd.return_value = (25, "ACK")
        self.isotope_mock.is_resp_ok.return_value = True
        temperature = self.temp_input_port.get_value()
        self.assertEqual(temperature, 25)

    def test_get_value_err_resp(self):
        self.isotope_mock.send_cmd.return_value = (1, "ERR")
        self.isotope_mock.is_resp_ok.return_value = False
        temperature = self.temp_input_port.get_value()
        self.assertIsNone(temperature)

    def test_invalid_port_id(self):
        with self.assertRaises(ValueError):
            TempInputPort(self.isotope_mock, -1)


class TestTempInput(unittest.TestCase):

    def setUp(self):
        self.isotope_mock = MagicMock(spec=IsotopeCommsProtocol)
        self.temp_input = TempInput(self.isotope_mock)

    def test_getitem_valid_index(self):
        port = self.temp_input[0]
        self.assertIsInstance(port, TempInputPort)
        self.assertEqual(port._id, 0)

    def test_getitem_invalid_index(self):
        with self.assertRaises(ValueError):
            self.temp_input[4]

if __name__ == '__main__':
    unittest.main()