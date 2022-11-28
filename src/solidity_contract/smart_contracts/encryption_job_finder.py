from web3 import Web3
from src.solidity_contract.contract import Contract


class EncryptionJobFinder(Contract):
    def __init__(self, contract_name, contract_address, abi, bytecode):
        super().__init__(contract_name, contract_address, abi, bytecode)
        self.web3 = Web3(Web3.WebsocketProvider("ws://192.168.203.3:9000"))

    def get_job_container(self):
        return self.contract.functions.jobContainer().call()

    def get_job(self):
        """Should be call by a worker willing to participate to the learning

        Returns:
            (int, int): models weights, data indices to perform SGD
        """
        return self.contract.functions.getJob().call()

    def get_all_previous_jobs_best_model(self):
        return self.contract.functions.getAllPreviousJobsBestModel().call()

    def send_encrypted_model(
        self, model_keccak, model_secret_keccak, worker_address, worker_private_key
    ):
        """Send the encrypted model to the blockchain
        Args:
            model_secret_keccak (bytes[]): bytes array of hash of the model xored with the worker secret
            model_keccak (bytes[]): bytes array of model's hash
            worker_address (_type_): address of the worker
            worker_private_key (_type_): private key of the worker
        """
        # Sanize the worker address
        worker_address = Web3.toChecksumAddress(worker_address)
        # convert encrypted model to a byte array of size 140
        # split each byte of the encrypted model into a list of bytes
        model_keccak = [model_keccak[i:i + 1]
                        for i in range(0, len(model_keccak), 1)]
        model_secret_keccak = [model_secret_keccak[i:i + 1]
                               for i in range(0, len(model_secret_keccak), 1)]
        # ßßprint(len(encrypted_model))
        try:
            register_tx = self.contract.functions.addEncryptedModel(
                worker_address, model_keccak, model_secret_keccak
            ).build_transaction(
                {
                    "gasPrice": 0,
                    "from": worker_address,
                    "nonce": self.web3.eth.get_transaction_count(worker_address),
                }
            )
            tx_receipt = super().sign_txs_and_send_it(worker_private_key, register_tx)
            return self.get_send_encrypted_model_return_value(self.web3, tx_receipt)
        except Exception as e:
            print("Error sending encrypted model:", e)
            return [False]

    def check_can_send_verification_parameters(self):
        """Check weather the worker can send the verification parameters

        Returns:
            boolean: true if the worker can send the verification parameters false otherwise
        """
        # TODO check
        return self.contract.functions.canSendVerificationParameters().call()

    def send_verifications_parameters(
        # self, worker_nounce, worker_secret, worker_address, worker_private_key
        self, clear_worker_secret, clear_model, worker_address, worker_private_key
    ) -> bool:
        """Send the verification parameters to the blockchain (worker nounce, worker secret)

        Args:
            clear_worker_secret (bytes[]): bytes array of the worker secret
            clear_model (bytes[]): bytes array of the model
            worker_address (_type_): address of the worker
            worker_private_key (_type_): private key of the worker
        return: true if the transaction is successful false otherwise
        """
        worker_address = Web3.toChecksumAddress(worker_address)
        clear_worker_secret = [clear_worker_secret[i:i + 1]
                               for i in range(0, len(clear_worker_secret), 1)]
        clear_model = [clear_model[i:i + 1]
                       for i in range(0, len(clear_model), 1)]
        print("inside send verification parameters")
        print(len(clear_worker_secret))
        print(len(clear_model))
        try:
            # register_tx = self.contract.functions.addVerificationParameters(
            #     worker_address,
            #     worker_nounce,
            #     worker_secret
            # ).build_transaction(
            register_tx = self.contract.functions.addVerificationParameters(
                worker_address,
                clear_worker_secret,
                clear_model
            ).build_transaction(
                {
                    "gasPrice": 0,
                    "from": worker_address,
                    "nonce": self.web3.eth.get_transaction_count(
                        worker_address
                    ),
                }
            )
            tx_receipt = super().sign_txs_and_send_it(worker_private_key, register_tx)
        except Exception as e:
            print("Error sending verification parameters:", e)
            return False
        return True

    def parse_send_encrypted_model(self, result):
        return self.contract.web3.codec.decode_single(
            "bool", result
        )

    def get_send_encrypted_model_return_value(self, w3, txhash):
        try:
            tx = w3.eth.get_transaction(txhash)
        except Exception as e:
            print("Error getting transaction:", e)
            return None
        replay_tx = {
            'to': tx['to'],
            'from': tx['from'],
            'value': tx['value'],
            'data': tx['input'],
            'gas': tx['gas'],
        }
        # replay the transaction locally:
        try:
            ret = w3.eth.call(replay_tx, tx.blockNumber - 1)
            return (True, self.parse_send_encrypted_model(ret))
        except Exception as e:
            return (False, str(e))

    def get_final_model(self):
        return self.contract.functions.getFinalModel().call()

    # -----------------Debug functions-----------------
    def get_received_models(self):
        return self.contract.functions.getReceivedModels().call()

    def get_model_is_ready(self):
        return self.contract.functions.getModelIsready().call()
