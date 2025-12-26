## levelup.gitconnected.com/working-with-data-in-python-596bbc6d6c2

####  dict demos
my_dict = dict(name='California', country='US', date='08')
print(f"as constructed dict=[{my_dict}]")
my_dict.update({"item4": 'four'})
print(f"after update1=[{my_dict}]")
my_dict.update({"gender": "female"})
print(f"after update2=[{my_dict}]")
## :.2f for two digit decimal formatting!
my_dict.update({"time": f"{2.0:.2f}"})
print(f"after update2=[{my_dict}]")

print(f"pop(\"gender\")={my_dict.pop('gender')}")
print(f"after pop('gender')=[{my_dict}]")


