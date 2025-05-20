import pytest
#from numpy.matlib import empty

from basern.pdf_comp import PageNumberParser


@pytest.fixture
def parser():
    """Create a Parser instance for tests."""
    return PageNumberParser()


def test_parse_range_element(parser):
    """Test parsing of individual range elements."""
    assert parser.parse_range_element("5") == {5}
    assert parser.parse_range_element("3-7") == {3, 4, 5, 6, 7}
    assert parser.parse_range_element("10-10") == {10}


def test_parse_range_string(parser):
    """Test parsing of complete range strings.
       Range strings have -p separator
    """
    assert parser.parse_range_string("-p1,3-10,12,14-18") == {1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18}
    assert parser.parse_range_string("-p1,3-5") == {1, 3, 4, 5}
    assert parser.parse_range_string("-p42") == {42}
    assert parser.parse_range_string("-p1-3,5-7") == {1, 2, 3, 5, 6, 7}
    assert parser.parse_range_string("") == set()
    assert parser.parse_range_string("-p") == set()
    assert parser.parse_range_string("-p1,3,4,6") == {1, 3, 4, 6}
    assert parser.parse_range_string("-p1,3-4,6") == {1, 3, 4, 6}
    assert parser.parse_range_string(" 1_a29-hd-p1,3.pdf") == {1, 3}
    assert parser.parse_range_string(" a30-pma-p4,7,8.pdf ") == {4, 7, 8}
    

def test_format_range_set(parser):
    """Test formatting sets of numbers into readable strings with ranges."""
    assert parser.format_range_set({1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18}) == "1, 3 to 10, 12, 14 to 18"
    assert parser.format_range_set({5}) == "5"
    assert parser.format_range_set({1, 2, 3}) == "1 to 3"
    assert parser.format_range_set({1, 3, 5}) == "1, 3, 5"
    assert parser.format_range_set(set()) == ""


def test_complete_workflow(parser):
    """Test the full workflow from string to set and back to formatted string."""
    input_str = "-p1,3-10,12,14-18"
    number_set = parser.parse_range_string(input_str)
    formatted = parser.format_range_set(number_set)
    assert formatted == "1, 3 to 10, 12, 14 to 18"


def test_nopage_number(parser):
    """Input_String with no page (lacking -p) detail."""
    input_str = "May-2025_9453545_10066-Monthly-Notice.pdf"
    number_set = parser.parse_range_string(input_str)
    assert len(number_set) == 0
