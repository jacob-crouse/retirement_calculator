import csv

class User:

    #self.retirement_age = 67 # normally need to be 67 to collect full social security, so lets go with that

    def __init__(self, name, age, gender, retirement_age=67):
        self.name = name
        self.age = age
        self.retirement_age = retirement_age
        self.gender = gender
        print("Initialized a user named " + self.name + ", aged " + str(self.age))

    def set_age(self, age):
        self.age = age

    def set_retirement_age(self, retirement_age):
        self.retirement_age = retirement_age

    def set_salary(self, salary, rate_of_increase=0.03):
        self.salary = salary
        self.rate_of_increase = rate_of_increase

    def set_gender(self, gender):
        self.gender = gender

    def calculate_death_age(self):
        with open('actuarial_tables_2019_2022.csv', newline='', ) as csvfile:
            self.actuarial_table = list(csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC))
            if self.gender == "male":
                self.death_age = self.age + self.actuarial_table[self.age][3]
            else:
                self.death_age = self.age + self.actuarial_table[self.age][6]

            print("User " + self.name + " is projected to die at age " + str(self.death_age))
