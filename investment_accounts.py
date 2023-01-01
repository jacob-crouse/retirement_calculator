import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

class investment_account:

    def __init__(self, name, principal, type="generic"):
        self.name = name
        self.principal = principal
        print("Initialized investment account named " + self.name )

    def simulate(self, principal_update, return_range, means, std_devs, sim_length):
        # the goal here is to implement monte carlo simulations eventually, but to get this running I just want to plug in some pretty simple exponential growth

        # assume the return range is normally distributed about the mean with given std_dev
        means_by_year, std_devs_by_year = self.model_progressive_conservatism(means, std_devs, sim_length)
        return_by_year = np.zeros((sim_length,1))
        for index in range(0, sim_length):
            return_by_year[index] = np.random.normal(means_by_year[index], std_devs_by_year[index],1)
        plt.figure()
        plt.plot(np.arange(26,56,1), return_by_year)
        plt.title("Investment Account Yearly Return Over Time")
        plt.savefig("account_return_over_time.png")

        # just working with the minimum return range now, and I'll assume it's compounded continuously (most optimal)
        account_value = np.zeros((sim_length,1))
        for index in range(0, sim_length):
            if index == 0:
                account_value[index] = self.principal
            else:
                account_value[index] = principal_update[index-1] + account_value[index-1] * (1 + return_by_year[index])

        return account_value

    def model_progressive_conservatism(self, means, std_devs, sim_length):
        # I want something that will show that early in life we'll be more aggressive with our investments, so we get higher average return, but with larger standard deviations. As we get older, our investment straegy becomes more conservative, so our means and standard deviations become smaller
        a = (means[0] - means[1])/(np.log(1/sim_length))
        b = np.exp( (means[1]*np.log(1) - means[0]*np.log(sim_length)) / (means[0]-means[1]) )
        out_means = a * np.log(b * np.arange(1,sim_length+1)) 

        a = (std_devs[0] - std_devs[1])/(np.log(1/sim_length))
        b = np.exp( (std_devs[1]*np.log(1) - std_devs[0]*np.log(sim_length)) / (std_devs[0]-std_devs[1]) )
        out_std_devs = a * np.log(b * np.arange(1,sim_length+1)) 

        return out_means, out_std_devs
