#
from typing import Optional

#
from algorand import Algorand

#
from teal import TealManager


#
class AlgorandHTLC(Algorand):
    """
    AlgorandHTLC object for running preHtlc protocol steps
    """

    #
    def commit(
                self,
                teal_manager: Optional[TealManager],
                filename: str,
                sender: dict,
                app_args: list
            ) -> int:
        """
        Commit funds for choosen LP

        :param teal_manager: object for interacting with teal contracts
        :param filename: teal smart contract file name
        :param sender: commit account info
        :param app_args: arguments for smart contract

        :returns: application id
        """

        approval_teal = teal_manager.compile_teal_code(self.client, filename)
        clear_teal = teal_manager.compile_teal_code(self.client, "clear.teal")

        app_create_txn = self.create_application_transaction(
                sender["address"],
                approval_teal, clear_teal
            )
        signed_txn = self.sign_transaction(sender["pk"], app_create_txn)

        tx_id = self.send_transaction(signed_txn)
        self.wait_for_transaction(tx_id)
        app_id = self.get_application_id(tx_id)
        app_address = self.get_application_address(app_id)
        print(f"Application ID: {app_id} {app_address}")

        app_call_txn = self.call_application_transaction(
                sender["address"],
                app_id,
                app_args
            )
        signed_txn = self.sign_transaction(sender["pk"], app_call_txn)

        tx_id = self.send_transaction(signed_txn)
        self.wait_for_transaction(tx_id)
        print(f"Commit Transaction ID: {tx_id}")

        state = self.get_application_global_state(app_id)
        print("Global State after locking:", state)

        return app_id

    #
    def lock_commitment(
                self,
                sender: dict,
                app_id: int,
                hashlock: bytes
            ) -> dict:
        """
        lock commited fund and write hashlock in smart contract

        :param sender: locker account information
        :param app_id: application id
        :param hashlock: hashlock from LP for writing in smart contract

        :returns: state of application
        """

        app_args = [b"lock", hashlock]

        app_call_txn = self.call_application_transaction(
                sender["address"],
                app_id,
                app_args
            )

        signed_txn = self.sign_transaction(sender["pk"], app_call_txn)
        tx_id = self.send_transaction(signed_txn)
        self.wait_for_transaction(tx_id)
        print(f"Lock Transaction ID: {tx_id}")
        state = self.get_application_global_state(app_id)
        print("Global State after locking:", state)
        return state

    #
    def lock(
                self,
                teal_manager: Optional[TealManager],
                receiver: dict,
                timelock: int,
                hash_of_secret: str,
                sender: dict,
                amount: int
            ) -> str:
        """
        Lock fund

        :param teal_manager: object for interacting with teal contracts
        :param receiver: receiver account info
        :param timelock: timelock for accepting lock
        :param hash_of_secret: hash of secret
        :param sender: sender account info
        :param amount: amount which should be locked

        :returns: transaction id
        """

        res = teal_manager.compile_teal_file(
                TealManager.lock_contract(
                    receiver["address"],
                    timelock,
                    hash_of_secret
                )
            )
        teal_manager.save_teal_to_file(res, 'lock.teal')

        approval_teal = teal_manager.compile_teal_code(
                self.client,
                'lock.teal'
            )
        clear_teal = teal_manager.compile_teal_code(self.client, "clear.teal")

        txn = self.build_payment_transaction(
                sender["address"],
                receiver["address"],
                amount,
                ''
            )
        signed_txn = self.sign_transaction(sender["pk"], txn)
        tx_id = self.send_transaction(signed_txn)

        print(f"Transaction ID: {tx_id}")

        # Wait for confirmation
        self.wait_for_transaction(tx_id)
        print(f"Funds committed to lock contract. Transaction ID: {tx_id}")
        return tx_id

    #
    def redeem(self):
        pass
