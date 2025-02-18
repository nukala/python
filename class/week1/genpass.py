# https://python.plainenglish.io/19-insanely-useful-python-automation-scripts-i-use-every-day-99d390718630

import random 
import string  


def generate_password(length=12):     
    characters = string.ascii_letters + string.digits + string.punctuation     
    return ''.join(random.choice(characters) for _ in range(length))  
    
    
# sub-optimal -- as all "characters" have equal weight
print(f"Generated Password: {generate_password(16)}")
