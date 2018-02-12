from environment_mbc import Env
import matplotlib.pyplot as plt

def main():
    record1 = []
    record2 = []

    state_space = {"depths":["V-1"],
            "flows":["C-7"]}
    control_points = ["R-4"]
    reward_space = {"depths":[],
            "flows":[]}
    reward_fun = 0.0

    env = Env("./1tanksTSS_flooding.inp",
            state_space,
            control_points)

    done = False
    while not done:
        state, _, done = env.step([0.05])
        record1.append(state[0])

    print("Done")
    env.reset()
    done = False
    while not done:
        state, _, done = env.step([1.0])
        record2.append(state[0])

    plt.subplot(1,3,1)
    plt.plot(record1)
    plt.subplot(1,3,2)
    plt.plot(record2)
    plt.subplot(1,3,3)
    plt.plot([i-j for i,j in zip(record1, record2)])
    plt.show()
