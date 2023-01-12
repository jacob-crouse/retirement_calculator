import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime

class investment_account:

    def __init__(self, name, principal, type="generic"):
        self.name = name
        self.principal = principal
        self.type = type
        print("Initialized investment account named " + self.name )

    def declare_ball_pension(self, starting_age):
        self.starting_age = starting_age

    def simulate_growth(self, user, principal_update, means, std_devs, num_sim_years, return_by_year=0):
        # the goal here is to implement monte carlo simulations eventually, but to get this running I just want to plug in some pretty simple exponential growth
        
        # assume the return range is normally distributed about the mean with given std_dev
        if type(return_by_year) == int:
            means_by_year, std_devs_by_year = self.model_progressive_conservatism(means, std_devs, num_sim_years)
            self.return_by_year = np.zeros((num_sim_years,1))
            for index in range(0, num_sim_years):
                self.return_by_year[index] = np.random.normal(means_by_year[index], std_devs_by_year[index],1)
        else: # the user has passed in some returns by year, and I'll default to using those
            self.return_by_year = return_by_year


        # just working with the minimum return range now, and I'll assume it's compounded yearly
        self.account_value = np.zeros((num_sim_years,1))
        if self.type == "generic":
            for index in range(0, num_sim_years):
                if index == 0:
                    self.account_value[index] = self.principal
                else: # account is simulated until death, but the values will be updated depending on withdrawls 
                    self.account_value[index] = principal_update[index-1] + self.account_value[index-1] * (1 + self.return_by_year[index])
                    if(self.account_value[index] <= 0): # we don't have any more money, so need to stop the simulation
                        self.account_value[index] = 0
        elif self.type == "Ball Pension":
            # Ball pensions don't accumulate interest -- you just earn a specific amount of money per year
            if num_sim_years == user.sim_length: # this is the first simulation of this account, so treat it as normal
                years_already_there = user.age - self.starting_age
                self.account_value[0] = self.principal
                for index in range(1,num_sim_years):
                    if index < user.accumulate_wealth_duration:
                        if (index + years_already_there) < 10:
                            self.account_value[index] = self.account_value[index-1] + (user.salary_by_year[index] * 0.115) + 0.05*(user.salary_by_year[index] - 0.5*self.extrapolate_ss_base_wage(user, user.age+index))
                        elif (index + years_already_there) < 20:
                            self.account_value[index] = self.account_value[index-1] + (user.salary_by_year[index] * 0.13) + 0.05*(user.salary_by_year[index] - 0.5*self.extrapolate_ss_base_wage(user, user.age+index))
                        elif (index + years_already_there) >= 20:
                            self.account_value[index] = self.account_value[index-1] + (user.salary_by_year[index] * 0.15) + 0.05*(user.salary_by_year[index] - 0.5*self.extrapolate_ss_base_wage(user, user.age+index))

                    else: # doesn't accumulate value after retirement
                        if index == user.accumulate_wealth_duration: # if the user is <65 years old at retirement, we need to reduce the value of the pension account
                            retirement_age = user.age + index
                            if retirement_age < 65: # this is considered an early retirement -- you will get a reduced lump sum value
                                with open('Ball_Early_Retirement_Scale_Factors.csv', newline='') as csvfile:
                                    ball_early_retirement_scale_factors = list(csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC))
                                    self.account_value[index] = self.account_value[index-1] * float(ball_early_retirement_scale_factors[0][retirement_age-55])
                        else:
                            self.account_value[index] = self.account_value[index-1]

            else: # this is us withdrawing from the account
                # when withdrawing from the account, we don't need to simulate any growth because we're retired, so just update the principal
                self.account_value[0] = self.principal
                for index in range(1,num_sim_years):
                    self.account_value[index] = self.account_value[index-1] + principal_update[0]
                    if self.account_value[index] <= 0: # we don't have any more money, so need to stop the simulation
                        self.account_value[index] = 0
            
            # plot things to make sure they're working properly
            #plt.figure()
            #plt.grid(True)
            #plt.plot(np.arange(user.age,user.death_age+1,1), self.account_value)
            #plt.title("Ball Pension Yearly Account Value")
            #plt.savefig("ball_pension_value_over_time.png")
            

        # plot results for fun
        plt.figure()
        plt.plot(np.arange(user.age,user.death_age+1,1), self.return_by_year)
        plt.title("Investment Account Yearly Return Over Time")
        plt.savefig(self.name + "_account_return_over_time.png")

        return self.account_value

    def model_progressive_conservatism(self, means, std_devs, sim_length):
        # I want something that will show that early in life we'll be more aggressive with our investments, so we get higher average return, but with larger standard deviations. As we get older, our investment straegy becomes more conservative, so our means and standard deviations become smaller
        a = (means[0] - means[1])/(np.log(1/sim_length))
        b = np.exp( (means[1]*np.log(1) - means[0]*np.log(sim_length)) / (means[0]-means[1]) )
        out_means = a * np.log(b * np.arange(1,sim_length+1)) 

        a = (std_devs[0] - std_devs[1])/(np.log(1/sim_length))
        b = np.exp( (std_devs[1]*np.log(1) - std_devs[0]*np.log(sim_length)) / (std_devs[0]-std_devs[1]) )
        out_std_devs = a * np.log(b * np.arange(1,sim_length+1)) 

        return out_means, out_std_devs

    def extrapolate_ss_base_wage(self, user, age):
        # read through the social security base wage spreadsheet to figure out what 
        # I fit a line to historical social security base wage values by year to determine what the base wage will be per year into the future
        # I fit the data to the form Y=m*X + b, where X is the Year and Y is the Social Security Base Wage.

        # coefficients from my fit
        m = 2.74039102E3
        b = -5.40118875E6

        # find the current year
        today = datetime.date.today()
        this_year = int(today.strftime("%Y"))

        # calculate the year during at which I will be the inputted age
        sample_year = this_year + (age - user.age)

        return m * sample_year + b

