from investment_accounts import investment_account
from users import User

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np



def main():
    print("Hello World!")
    jake = User("Jake", 26, "male", 65)
    test_account = investment_account("Roth IRA", 26658.70)
    test_account2 = investment_account("401K", 15063.55)
    test_account3 = investment_account("Roth IRA 2", 26658.70)

    #jake.calculate_death_age()
    jake.set_death_age(95)

    jake.set_salary(97000)
    jake.simulate_salary_growth([0.05, 0.01], [0.02, 0.005])

    # now try and simulate the growth of some investment accounts
    principal_update_by_year = np.vstack((6500*np.ones((jake.accumulate_wealth_duration,1)), np.zeros((jake.withdraw_wealth_duration, 1))))
    principal_update_by_year2 = np.vstack((0.07*jake.salary_by_year, np.zeros((jake.withdraw_wealth_duration,1))))
    account_value = test_account.simulate_growth(jake, principal_update_by_year, [0.08, 0.03], [0.02, 0.005], jake.sim_length)
    account_value2 = test_account2.simulate_growth(jake, principal_update_by_year2, [0.08, 0.03], [0.02, 0.005], jake.sim_length)
    account_value3 = test_account3.simulate_growth(jake, principal_update_by_year, [0.08, 0.03], [0.02, 0.005], jake.sim_length)

    jake.simulate_decay([test_account, test_account2, test_account3], 0.9)

    plt.figure()
    plt.plot(np.arange(jake.age, jake.death_age+1, 1), test_account.account_value+test_account2.account_value+test_account3.account_value)
    plt.title("Investment Account Value Over Time")
    plt.savefig("account_over_time.png")


if __name__ == "__main__":
    main()
