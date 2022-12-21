class User:

    #self.retirement_age = 67 # normally need to be 67 to collect full social security, so lets go with that

    def __init__(self, name, age, retirement_age=67):
        self.name = name
        self.age = age
        self.retirement_age = retirement_age
        print("Initialized a user named " + self.name + ", aged " + str(self.age))

    def set_age(self, age):
        self.age = age

    def set_retirement_age(self, retirement_age):
        self.retirement_age = retirement_age

    def set_salary(self, salary, rate_of_increase=0.03):
        self.salary = salary
        self.rate_of_increase = rate_of_increase
