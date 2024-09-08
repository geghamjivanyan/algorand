#
from typing import Optional

#
from algorand import Algorand, AlgoUser

#
from teal import TealManager
from utils import fill_smart_contract_balance

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

        approval_teal, clear_teal = teal_manager.deploy_contract(self.client, 'commit')

        txn = self.create_application_transaction(
                    sender.address,
                    approval_teal,
                    clear_teal
                )

        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)

        self.wait_for_confirmation(tx_id)

        app_id = self.get_application_id(tx_id)
        app_address = self.get_application_address(app_id)

        app_args = [b"commit", (amount).to_bytes(8, 'big')]

        txn = self.call_application_transaction(
                    sender.address,
                    app_id,
                    app_args,
                    receiver.address
                )

        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)

        self.wait_for_confirmation(tx_id)

        return app_id, app_address

    #
    def lock_commitment(
                self,
                sender: Optional[AlgoUser],
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

        app_txn = self.call_application_transaction(
                    sender.address,
                    app_id,
                    app_args,
                    receiver
                )
        pmt_txn = self.build_payment_transaction(
                    sender.address,
                    self.get_application_address(app_id),
                    amount,
                    "Lock Commitment"
                )

        signed_app_txn = self.sign_transaction(sender.pk, app_txn)
        signed_pmt_txn = self.sign_transaction(sender.pk, pmt_txn)

        app_txn_id = self.send_transaction(signed_app_txn)
        pmt_txn_id = self.send_transaction(signed_pmt_txn)

        self.wait_for_confirmation(app_txn_id)
        self.wait_for_confirmation(pmt_txn_id)

        
    #
    def redeem(self, sender, app_id, secret):
        # 3d. Bob Claims the Funds
        app_args = [b"claim", secret]
        txn = self.call_application_transaction(
                    sender.address,
                    app_id,
                    app_args
                )
        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)
        print(f"Claim Transaction ID: {tx_id}")

    #
    def create_new_asset(self, teal_manager, sender):

        asset_id = self.create_asset(sender)
        self.opt_in_to_asset(sender, asset_id)
        
        approval_teal, clear_teal = teal_manager.deploy_contract(self.client, 'lock_redeem_dest')
        txn = self.create_application_transaction(sender.address, approval_teal, clear_teal)

        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)
        self.wait_for_confirmation(tx_id)
        resp = self.client.pending_transaction_info(tx_id)

        return resp['application-index'], asset_id

    #
    def lock_dest_chain(self, sender, app_id, asset_id, amount, hashlock, receiver):
    
        app_args=[b"lock", (amount).to_bytes(8, "big"), hashlock]
        txn = self.call_application_transaction(sender.address, app_id, app_args, receiver.address, asset_id)
    
        signed_txn = self.sign_transaction(sender.pk, txn)
        tx_id = self.send_transaction(signed_txn)
        self.wait_for_confirmation(tx_id)
        print(f"Locked {amount} tokens for Bob in application {app_id}")

    #
    def redeem_dest(self, receiver, app_id, secret):
        
        app_args=[b"redeem", secret]
    
        txn = self.call_application_transaction(receiver.address, app_id, app_args)
        signed_txn = self.sign_transaction(receiver.pk, txn)
        tx_id = self.send_transaction(signed_txn)
        self.wait_for_confirmation(tx_id)
        print(f"Redeemed tokens in application {app_id}")
