import numpy as np

class investment_account:

    def __init__(self, name, principal, type="generic"):
        self.name = name
        self.principal = principal
        print("Initialized investment account named " + self.name )

    def simulate(self, return_range, mean, std_dev, sim_length):
        # the goal here is to implement monte carlo simulations eventually, but to get this running I just want to plug in some pretty simple exponential growth

        # assume the return range is normally distributed about the mean with given std_dev
        return_by_year = np.random.normal(mean, std_dev, (sim_length, 1))
        # min_return_range = return_range[0]
        # max_return_range = return_range[1]

        # just working with the minimum return range now, and I'll assume it's compounded continuously (most optimal)
        account_value = np.zeros((sim_length,1))
        for index in range(0, sim_length):
            if index == 0:
                account_value[index] = self.principal
            else:
                account_value[index] = account_value[index-1] * (1 + return_by_year[index])

        return account_value
