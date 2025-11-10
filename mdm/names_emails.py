######################################################
# Generate fake names and email from:
#   python.plainenglish.io/7-python-libraries-that-made-my-friends-think-i-was-a-hacker-7da1a22550a9
######################################################
from faker import Faker

fake = Faker()
for i in range(4):
    print(f"{i}: {fake.name()} | {fake.email()}")