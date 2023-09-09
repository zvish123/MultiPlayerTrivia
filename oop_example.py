
class Person:
    def __init__(self, name, phone, mail ):
        self.name = name
        self.phone = phone
        self.mail = mail

    def __str__(self):
        return f"name: {self.name}, phone: {self.phone}, mail: {self.mail}"


class JsonPerson(Person):
    def __init__(self, json_dict):
        super().__init__(json_dict["name"], json_dict["phone"], json_dict["mail"])


p1 = Person("zvi", "03-5353531", "zvi.shiran@google.com")
json_person = {"name": "avi", "phone": "052-5252521", "mail": "avi@gmail.com"}
p2 = JsonPerson(json_person)

all_persons = [p1, p2]
for p in all_persons:
    print(p)

class Item:
    def __init__(self, name, amount, price ):
        self.name = name
        self.amount = amount
        self.price = price

    def value(self):
        return self.amount * self.price

    def __str__(self):
        return f"name: {self.name}, amount: {self.amount}, price: {self.price}"


class SaleItem(Item):
    def __init__(self, json_dict):
        super().__init__(json_dict["name"], json_dict["amount"], json_dict["price"])
        self.discount = json_dict["discount"]

    def value(self):
        return super().value() * (100 - self.discount) / 100


i1 = Item("pencil", 5, 6.5)
json_item1 = {"name": "eraser", "amount": 12, "price": 1.5, "discount": 10}
i2 = SaleItem(json_item1)

all_items = [i1, i2]

for itm in all_items:
    print(itm, "value:", itm.value())

class Parent:
  def f1(self):
    print("Function of parent class.")

class Child(Parent):
  def f2(self):
    print("Function of child class.")

object1 = Child()
object1.f1()
object1.f2()

object2 = Parent()
object2.f1()
object2.f2()
