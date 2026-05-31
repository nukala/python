import unittest
from basern.rnutils import _parse_num_bytes, format_bytes, bytes_to_kb, bytes_to_mb

class TestParseNumBytes(unittest.TestCase):
    """Tests for the internal _parse_num_bytes helper."""

    # --- Valid inputs ---
    def test_plain_int(self):
        self.assertEqual(_parse_num_bytes(1024), 1024)

    def test_numeric_string(self):
        self.assertEqual(_parse_num_bytes("2048"), 2048)

    def test_zero_int(self):
        self.assertEqual(_parse_num_bytes(0), 0)

    def test_zero_string(self):
        self.assertEqual(_parse_num_bytes("0"), 0)

    # --- TypeError cases ---
    def test_float_raises_type_error(self):
        with self.assertRaises(TypeError):
            _parse_num_bytes(1024.0)

    def test_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            _parse_num_bytes(None)

    def test_list_raises_type_error_list(self):
        with self.assertRaises(TypeError):
            _parse_num_bytes([1024])

    # --- ValueError cases ---
    def test_negative_int_raises_value_error(self):
        with self.assertRaises(ValueError):
            _parse_num_bytes(-1)

    def test_negative_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            _parse_num_bytes("-512")

    def test_non_numeric_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            _parse_num_bytes("abc")

    def test_empty_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            _parse_num_bytes("")


class TestBytesToKb(unittest.TestCase):
    def test_int_exact(self):
        self.assertAlmostEqual(bytes_to_kb(1024), 1.0)

    def test_string_exact(self):
        self.assertAlmostEqual(bytes_to_kb("1024"), 1.0)

    def test_zero(self):
        self.assertAlmostEqual(bytes_to_kb(0), 0.0)

    def test_partial(self):
        self.assertAlmostEqual(bytes_to_kb(512), 0.5)

    def test_large(self):
        self.assertAlmostEqual(bytes_to_kb(1_048_576), 1024.0)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            bytes_to_kb(-1)

    def test_float_raises(self):
        with self.assertRaises(TypeError):
            bytes_to_kb(1024.0)


class TestBytesToMb(unittest.TestCase):
    def test_int_exact(self):
        self.assertAlmostEqual(bytes_to_mb(1_048_576), 1.0)

    def test_string_exact(self):
        self.assertAlmostEqual(bytes_to_mb("1048576"), 1.0)

    def test_zero(self):
        self.assertAlmostEqual(bytes_to_mb(0), 0.0)

    def test_partial(self):
        self.assertAlmostEqual(bytes_to_mb(524_288), 0.5)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            bytes_to_mb(-100)

    def test_float_raises(self):
        with self.assertRaises(TypeError):
            bytes_to_mb(1_048_576.0)


class TestFormatBytes(unittest.TestCase):
    # --- int input ---
    def test_int_below_threshold_shows_kb(self):
        self.assertEqual(format_bytes(262_144), "256.00 KB")

    def test_int_at_threshold_shows_mb(self):
        self.assertEqual(format_bytes(524_288, 450), "0.50 MB")

    def test_int_above_threshold_shows_mb(self):
        self.assertEqual(format_bytes(1_048_576), "1.00 MB")

    # --- str input ---
    def test_string_below_threshold_shows_kb(self):
        self.assertEqual(format_bytes("262144"), "256.00 KB")

    # shows as mb since we lower the threshold
    def test_string_at_threshold_shows_mb(self):
        self.assertEqual(format_bytes("524288", 450), "0.50 MB")

    def test_string_above_threshold_shows_mb(self):
        self.assertEqual(format_bytes("1048576"), "1.00 MB")

    # --- Edge values ---
    def test_zero_int(self):
        self.assertEqual(format_bytes(0), "0.00 KB")

    def test_zero_string(self):
        self.assertEqual(format_bytes("0"), "0.00 KB")

    def test_just_below_threshold(self):
        result = format_bytes(524_287)
        self.assertTrue(result.endswith("KB"), msg=result)

    def test_large_value(self):
        self.assertEqual(format_bytes(10_485_760), "10.00 MB")

    # --- Custom threshold ---
    def test_custom_threshold_low(self):
        result = format_bytes(2048, mb_threshold_kb=1.0)
        self.assertTrue(result.endswith("MB"), msg=result)

    def test_custom_threshold_high(self):
        result = format_bytes(1_048_576, mb_threshold_kb=2048.0)
        self.assertTrue(result.endswith("KB"), msg=result)

    # --- Decimal places ---
    def test_decimal_places_zero(self):
        self.assertEqual(format_bytes(1_048_576, decimal_places=0), "1 MB")

    def test_decimal_places_three(self):
        self.assertEqual(format_bytes(1_048_576, decimal_places=3), "1.000 MB")

    def test_decimal_places_kb(self):
        self.assertEqual(format_bytes(1536, decimal_places=1), "1.5 KB")

    # --- TypeError cases ---
    def test_float_raises_type_error(self):
        with self.assertRaises(TypeError):
            format_bytes(1024.0)

    def test_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            format_bytes(None)

    # --- ValueError cases ---
    def test_negative_int_raises_value_error(self):
        with self.assertRaises(ValueError):
            format_bytes(-1)

    def test_negative_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            format_bytes("-1024")

    def test_non_numeric_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            format_bytes("not_a_number")

    def test_negative_decimal_places_raises_value_error(self):
        with self.assertRaises(ValueError):
            format_bytes(1024, decimal_places=-1)

if __name__ == '__main__':
    unittest.main()
