#!/bin/bash

# Read in a string from the user
read -p "Enter a scenario name: " scenario

echo "Scenario: $scenario"

num_workers=5

# Iterate 5 times
for i in {1..16}; do
# for i in {1..5}; do
# for i in {1..1}; do
    # Multiply the variable by 10
    # num_workers=$((num_workers * 10))
    num_workers=$((num_workers * 2))
    echo "Testing blockchain with $num_workers workers"
    # create file names as number_of_workers and scenario (to save results)
    file_name="$num_workers"_workers
    mkdir res/$scenario
    touch res/$scenario/$file_name.txt
    # create the workload.yaml file for the given number of workers and upload it
    echo "Creating workload for $num_workers workers"
    # call the script create_workload.sh with the number of workers as argument
    ./create_workload.sh $num_workers
    # upload the workload.yaml file to the dclbigmem machine
    scp workload.yaml user@dclbigmem.epfl.ch:~/ml_on_blockchain/workload/federated_learning_generated.yaml
    rm workload.yaml
    echo "Deploying blockchain..."
    # connect in ssh to launch the blockchain
    timeout 35 ssh user@dclbigmem.epfl.ch -p 2232 "cd ~/minion && ./bin/minion run -vvv --user=user --breakpoint=chain quorum ../workloads/counter.yaml 127.0.0.1,192.168.203.3,192.168.203.4,192.168.203.5,192.168.203.6@vm-dclbigmem-1"
    echo "deployed blockchain"
    # open 2 ssh connections to launch primary and secondary
    ssh user@dclbigmem.epfl.ch -p 2232 'export PATH=/home/user/.local/bin:/home/user/anaconda3/bin:/home/user/anaconda3/condabin:/home/user/solidity/build/solc:/home/user/diablo:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/user/solidity/build/solc/ ; /home/user/diablo/diablo primary -vvv --output=out.txt --stat --env=accounts=deploy/diablo/primary/accounts.yaml --env=contracts=ml_on_blockchain/smart-contracts/federatedLearning/ 1 deploy/diablo/primary/setup.yaml ml_on_blockchain/workload/federated_learning_generated.yaml; ' &
    # wait 5 seconds that primary is launched and then launch secondary
    sleep 5
    ssh user@dclbigmem.epfl.ch -p 2232 "/home/user/diablo/diablo secondary -vvv localhost" &
    wait
    # copy the results from the primary to the local machine
    scp user@dclbigmem.epfl.ch:out.txt res/
    mv res/out.txt res/$scenario/$file_name.txt
    echo -e "\n"

    # kill the blockchain: close all geth instances in parallel
    for ssh_port in {2233..2236}; do
        ssh user@dclbigmem.epfl.ch -p $ssh_port "pgrep geth | xargs kill -9" && echo "Closed geth instance on: $ssh_port" &
    done
    wait
    echo -e "\n"
done
