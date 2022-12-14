import json
import matplotlib.pyplot as plt

waiting_times = []
percentages_committed = []
n_txs = []
scenario = "power_2_bis"
# workers = [10 * pow(10, i) for i in range(4)]
workers = [10 * pow(2, i) for i in range(16)]

i = 0
for n_workers in workers:
    i += 1
    print("n_workers:", n_workers)
    with open("res/{}/{}_workers.txt".format(scenario, n_workers)) as json_file:
        data = json.load(json_file)
        tx_submitted = 0
        tx_committed = 0
        tot_commit_time = 0
        for tx in data["Locations"][0]["Clients"][0]["Interactions"]:
            submit_time = tx["SubmitTime"]
            commit_time = tx["CommitTime"]
            tx_submitted += 1
            if commit_time != -1:
                tx_committed += 1
                tot_commit_time += commit_time - submit_time
        perc_committed = tx_committed / tx_submitted * 100
        avg_commit_time = tot_commit_time / tx_committed if tx_committed != 0 else 0
        print("tx_submitted:", tx_submitted)
        print("tx_committed:", tx_committed)
        print("avg_commit_time", avg_commit_time)
        print("perc_committed:", perc_committed)
        waiting_times.append(avg_commit_time)
        percentages_committed.append(perc_committed)
        # if tx_commited is bigger than 1000, replace thsousands with k
        if tx_committed > 1000:
            n_txs.append("{}k txs".format(tx_committed // 1000))
        else:
            n_txs.append("{} txs".format(tx_committed))

print("i:", i)
fig, axs = plt.subplots(2, 1, figsize=(15, 7.5))
# add vertical padding
fig.subplots_adjust(hspace=0.5)

axs[0].set_title("Average waiting time")
axs[1].set_title("Percentage committed")
fig.suptitle("Results")

axs[0].plot(workers, waiting_times, linestyle="dashed", marker="o")
axs[0].set_xlabel("Number of workers")
axs[0].set_ylabel("Average waiting time (s)")
axs[1].plot(
    workers,
    percentages_committed,
    linestyle="dashed",
    marker="o",
)
axs[1].set_xlabel("Number of workers")
axs[1].set_ylabel("Percentage committed")
for i, ax in enumerate(axs):
    ax.grid(True)
    ax.set_xscale("log")
    for x, y, label in zip(
        workers,
        waiting_times if i == 0 else percentages_committed,
        n_txs,
    ):
        ax.text(x, y, label, ha="center", va="bottom", fontsize=12, color="b")

plt.show()
