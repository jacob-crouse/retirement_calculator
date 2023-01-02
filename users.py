import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

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

    def calculate_death_age(self, ):
        with open('actuarial_tables_2019_2022.csv', newline='') as csvfile:
            self.actuarial_table = list(csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC))
            running_sum = 0
            for row in range(len(self.actuarial_table)):
                running_sum += self.actuarial_table[row][1]
                print("The cumulative probability of dying at age " + str(row) + " is: " + str(running_sum))
            if self.gender == "male":
                self.death_age = self.age + self.actuarial_table[self.age][3]
            else:
                self.death_age = self.age + self.actuarial_table[self.age][6]

            print("User " + self.name + " is projected to die at age " + str(self.death_age))

    def set_death_age(self, death_age):
        self.death_age = death_age

    def simulate_salary_growth(self, means, std_devs):
        # define durations for both the object and to be used in this simulation
        self.sim_length = self.death_age - self.age + 1
        self.accumulate_wealth_duration = self.retirement_age - self.age + 1
        self.withdraw_wealth_duration = self.death_age - self.retirement_age + 1

        means_by_year, std_devs_by_year = self.model_progressive_conservatism(means, std_devs, self.accumulate_wealth_duration)

        self.increase_by_year = np.zeros((self.accumulate_wealth_duration,1))
        for index in range(0, self.accumulate_wealth_duration):
            self.increase_by_year[index] = np.random.normal(means_by_year[index], std_devs_by_year[index], 1)

        # calculate salary per year
        self.salary_by_year = np.zeros((self.accumulate_wealth_duration,1))
        for index in range(0, self.accumulate_wealth_duration):
            if index == 0:
                self.salary_by_year[index] = self.salary
            else:
                self.salary_by_year[index] = self.salary_by_year[index-1] * (1 + self.increase_by_year[index])

        # plot the salary (for fun)
        plt.figure()
        plt.plot(np.arange(self.age, self.retirement_age+1, 1), self.salary_by_year)
        plt.title("Salary Per Year Until Retirement")
        plt.savefig("salary_over_time.png")

   
    def model_progressive_conservatism(self, means, std_devs, sim_length):
        # I want something that will show that early in life we'll be more aggressive with our investments, so we get higher average return, but with larger standard deviations. As we get older, our investment straegy becomes more conservative, so our means and standard deviations become smaller
        a = (means[0] - means[1])/(np.log(1/sim_length))
        b = np.exp( (means[1]*np.log(1) - means[0]*np.log(sim_length)) / (means[0]-means[1]) )
        out_means = a * np.log(b * np.arange(1,sim_length+1)) 

        a = (std_devs[0] - std_devs[1])/(np.log(1/sim_length))
        b = np.exp( (std_devs[1]*np.log(1) - std_devs[0]*np.log(sim_length)) / (std_devs[0]-std_devs[1]) )
        out_std_devs = a * np.log(b * np.arange(1,sim_length+1)) 

        return out_means, out_std_devs