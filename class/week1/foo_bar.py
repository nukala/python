""" Some "random" module without including the word module

Generates a random street number followed by some word and a "random" street type!
"""


# @WorthLooking("some random name need not be a module even")
import random
import string


def street_type():
    # Street types from: view-source:https://www.acgov.org/ptax_pub_app/RealSearchInit.do
    return random.choice(['Street', 'Avenue', 'Blvd', 'Road', 'Square',
                               'Alley',
                               'Avenue',
                               'Bay',
                               'Boulevard',
                               'Circle',
                               'Common',
                               'Court',
                               'Cove',
                               'Crescent',
                               'Crest',
                               'Drive',
                               'Freeway',
                               'Glen',
                               'Hill',
                               'Hills',
                               'Highway',
                               'Lane',
                               'Loop',
                               'Mall',
                               'Park',
                               'Parkway',
                               'Path',
                               'Place',
                               'Plaza',
                               'Point',
                               'Road',
                               'Square',
                               'Street',
                               'Terrace',
                               'Trail',
                               'Vista',
                               'Walk',
                               'Way',
                               ])


def my_detail(street = 'Artizan'):
    addr = f'{random.randint(101, 290)} {street} {street_type()}, '
    return addr + f'Unit {random.randint(1, 8)}{random.randint(1, 40):02}'


def random_string(length=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))
