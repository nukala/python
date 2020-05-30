vv = "1.0"

class Dog: 
  def __init__(self, name, breed, age, pronoun="He"): 
    self.name = name
    self.age = age
    self.breed = breed
    self.pronoun = pronoun

  def bark(self):
    print(self.name + "." + str(self.age) + ": says bark BARK!")


  def show(self):
    print(self.name + " is a [" + self.breed + "]. "  + self.pronoun + " is " + str(self.age) + " yrs old")
#    if self.buddy is not None:
#      print(self.name + "   has a friend=[" + self.buddy.name + "]")


  def birthday(self): 
    self.age += 1

  def setFriend(self, other):
    self.buddy = other
    other.buddy = self


print(__name__)

if __name__ == '__main__':
  # ideally belongs in dog_test
  teddy = Dog("teddy", "maltipoo", 9)
  #print(teddy)
  teddy.bark()
  teddy.birthday()
  teddy.setFriend(Dog("snoopy", "terrier", 9))
  teddy.show()

