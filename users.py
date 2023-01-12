import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from investment_accounts import investment_account

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

    def simulate_decay(self, accounts, percentage_of_final_salary):
        # the previous method simulates the growth of an investment account while the principal contribution is being continuously updated. This method will show what happens once the account decays

        # for now, I'll assume it's most optimal to draw from the smallest accounts first, since they will make less returns by year than the larger accounts
        num_accounts = len(accounts)
        account_values_at_retirement = np.zeros((num_accounts, 1))
        counter = 0
        for account in accounts:
            account_values_at_retirement[counter] = account.account_value[self.accumulate_wealth_duration]
            if account.type == "Ball Pension": # Pensions don't accumulate after retirement, so withdraw from them first
                account_values_at_retirement[counter] = 0 # make sure this is withdrawn from first

            print("Account " + account.name + " value at retirement: " + str(account_values_at_retirement[counter]))
            counter += 1

        # with the account values at retirement known, I'll sort them into the order from which I'll withdraw them (ascending order)
        temp = sorted(zip(account_values_at_retirement, accounts))
        account_withdrawl_order = [x for y, x in temp]

        # with the accounts sorted, I'm going to start withdrawing from one account until it hits zero. I will take note of this age, and continue withdrawing from the next account. Repeat for all accounts until all accounts are exhausted
        withdrawl_age = self.accumulate_wealth_duration
        counter = 0
        for account in account_withdrawl_order:
            # need to handle the scenario where we die before we run out of money
            if counter < self.withdraw_wealth_duration:
                principal_update = (-percentage_of_final_salary * self.salary_by_year[-1]) * np.ones((self.withdraw_wealth_duration-counter, 1))
            else: # we died before we ran out of money, so stop withdrawing from accounts
                principal_update = 0 * np.ones((self.withdraw_wealth_duration-counter, 1))

            if account.type == "generic":
                new_account = investment_account(account.name, account.account_value[self.accumulate_wealth_duration+counter])
            elif account.type == "Ball Pension":
                new_account = investment_account(account.name, account.account_value[self.accumulate_wealth_duration+counter], "Ball Pension")


            # I'll need to re-simulate the account after the point where we start to withdraw from it
            new_account.simulate_growth(self, principal_update, [0,0], [0,0], self.withdraw_wealth_duration-counter, account.return_by_year)

            # update the account I've remodeled to reflect this withdrawl behavior
            account.account_value = np.delete(account.account_value, range(-self.withdraw_wealth_duration+counter, 0))
            account.account_value = account.account_value.reshape((len(account.account_value),1))
            account.account_value = np.vstack((account.account_value, new_account.account_value))
            empty_index = np.where(new_account.account_value == 0)
            if len(empty_index[0]) != 0:
                counter += int(empty_index[0][0])
            else:
                counter += 0

            # print the results to make sure it's working
            plt.figure()
            plt.grid(True)
            plt.plot(np.arange(self.age, self.death_age+1, 1), account.account_value)
            plt.title("Updated " + account.name + " with Withdrawls Added")
            plt.savefig("withdrawn_" + account.name + "_over_time.png")