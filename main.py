from investment_accounts import investment_account
from users import User

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np



def main():
    print("Hello World!")
    test_account = investment_account("401K", 1000)
    jake = User("Jake", 26, 55)

    jake.set_salary(84000)

    # calculate out the growth of my salary until I retire
    salary_over_time = np.zeros((jake.retirement_age-jake.age+1, 1))
    salary_over_time[0] = jake.salary

    age_range = np.arange(jake.age, jake.retirement_age + 1, 1)

    for year in range(1, salary_over_time.size):
        salary_over_time[year] = salary_over_time[year-1] + (salary_over_time[year-1]*0.03)


    #fig, ax = plt.subplots()
    #ax.plot(age_range, salary_over_time)
    plt.figure()
    plt.plot(age_range, salary_over_time)
    plt.title("Jake's Salary Over Time")
    plt.savefig("salary_over_time.png")

    # now try and simulate the growth of an investment account
    account_value = test_account.simulate([0.03, 0.05], 1, 1, jake.retirement_age-jake.age+1)
    plt.figure()
    plt.plot(age_range, account_value)
    plt.title("Investment Account Value Over Time")
    plt.savefig("account_over_time.png")


if __name__ == "__main__":
    main()
