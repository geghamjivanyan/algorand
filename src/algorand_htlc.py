#
from typing import Optional

#
from algorand import Algorand

#
from teal import TealManager


#
class AlgorandHTLC(Algorand):
    """
    AlgoriandHTLC object for running preHtlc protocol steps
    """

    #
    def commit(
                self,
                teal_manager: Optional[TealManager],
                sender: dict,
                amount: int,
                receiver: dict
            ) -> int:
        """
        Commit funds for choosen LP

        :param teal_manager: object for interacting with teal contracts
        :param sender: commit account info
        :param amount: commited amount
        :param receiver: receiver account

        :returns: application id
        """

        approval_teal, clear_teal = teal_manager.deploy_contract(self.client)

        txn = self.create_application_transaction(sender.address, approval_teal, clear_teal)
        
        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)
        
        self.wait_for_confirmation(tx_id)

        app_id = self.get_application_id(tx_id)
        app_address = self.get_application_address(app_id)


        app_args = [b"commit", (amount).to_bytes(8, 'big')]
        
        txn = self.call_application_transaction(sender.address, app_id, app_args, receiver.address)

        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)
        
        self.wait_for_confirmation(tx_id)

        return app_id, app_address


    #
    def lock_commitment(
                self,
                sender: dict,
                app_id: int,
                amount: int,
                hashlock: str,
                receiver: dict
            ) -> dict:
        """
        lock commited fund and write hashlock in smart contract

        :param sender: locker account information
        :param app_id: application id
        :param hashlock: hashlock from LP for writing in smart contract
        :param receiver: receiver address

        :returns: state of application
        """

        app_args = [b"lock", hashlock]

        app_txn = self.call_application_transaction(sender.address, app_id, app_args, receiver)
        pmt_txn = self.build_payment_transaction(sender.address, self.get_application_address(app_id), amount, "Lock Commitment")
        
        signed_app_txn = self.sign_transaction(sender.pk, app_txn)
        signed_pmt_txn = self.sign_transaction(sender.pk, pmt_txn)

        app_txn_id = self.send_transaction(signed_app_txn)
        pmt_txn_id = self.send_transaction(signed_pmt_txn)

        self.wait_for_confirmation(app_txn_id)
        self.wait_for_confirmation(pmt_txn_id)



    #
    def lock(
                self,
                sender: dict,
                hash_of_secret: str,
                app_id: int
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

        app_args = [b"claim", hash_of_secret]
        app_call_txn = self.call_application_transaction(
            sender["address"],
            app_id,
            app_args=app_args
        )

        signed_txn = self.sign_transaction(sender["pk"], app_call_txn)
        tx_id = self.send_transaction(signed_txn)
        self.wait_for_transaction(tx_id)
        print(f"I Lock Transaction ID: {tx_id}")
        state = self.get_application_global_state(app_id)
        print("I Global State after locking:", state)
        return state
    
    #
    def redeem(self, sender, app_id, secret, receiver):
        # 3d. Bob Claims the Funds
        app_args = [b"claim", secret]
        txn = self.call_application_transaction(sender.address, app_id, app_args, receiver.address)
        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)
        print(f"Claim Transaction ID: {tx_id}")
