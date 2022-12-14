from web3 import Web3


class Worker:
    def __init__(self, address, private_key):
        self.address = address
        self.private_key = private_key
        self.model_weights = None

    def register_to_learning(self, contract_address, contract_abi):

        web3 = Web3(Web3.WebsocketProvider("ws://192.168.203.3:9000"))
        print(
            "Registering the worker to the learning server",
        )

        # 4. Create contract instance
        contract = web3.eth.contract(
            address=contract_address, abi=contract_abi)

        # 5. Build increment tx
        register_tx = contract.functions.register_worker().buildTransaction(
            {
                "gasPrice": 0,
                "from": Web3.toChecksumAddress(self.address),
                "nonce": web3.eth.get_transaction_count(
                    Web3.toChecksumAddress(self.address)
                ),
            }
        )

        # 6. Sign tx with PK
        tx_create = web3.eth.account.sign_transaction(
            register_tx, self.private_key)

        # 7. Send tx and wait for receipt
        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        print(
            f"Tx successful with hash: { tx_receipt.transactionHash.hex() } for registering worker"
        )

    def unregister_from_learning(self, contract_address, contract_abi):

        web3 = Web3(Web3.WebsocketProvider("ws://192.168.203.3:9000"))
        value = 1

        print(
            f"Calling the decrement by { value } function in contract at address: { contract_address }"
        )

        # 4. Create contract instance
        contract = web3.eth.contract(
            address=contract_address, abi=contract_abi)

        register_tx = contract.functions.unregister_worker().buildTransaction(
            {
                "gasPrice": 0,
                "from": Web3.toChecksumAddress(self.address),
                "nonce": web3.eth.get_transaction_count(
                    Web3.toChecksumAddress(self.address)
                ),
            }
        )

        tx_create = web3.eth.account.sign_transaction(
            register_tx, self.private_key)
        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        print(
            f"Tx successful with hash: { tx_receipt.transactionHash.hex() } for unregistering the worker"
        )

    def get_new_model_weigths(self, model_weigths):
        """Update the model weigths with new ones obtained from the learning server

        We assumed that the model weigths are only send by learning server when the worker just registered for learning
        or already gave back the model weigths from the previous learning round

        Args:
            model_weigths (float[]): the new model weigths
        """
        self.model_weights = model_weigths
