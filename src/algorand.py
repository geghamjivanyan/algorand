#
import base64

#
from typing import Optional

#
from algosdk import account, mnemonic, transaction, logic
from algosdk.v2client.algod import AlgodClient
from algosdk.transaction import PaymentTxn, SignedTransaction
from algosdk.transaction import ApplicationCreateTxn, ApplicationCallTxn


#
class Algorand:
    """
    Algorand object for interacting with algosdk
    """

    # global and local schema parameters
    GLOBAL_SCHEMA = transaction.StateSchema(num_uints=2, num_byte_slices=2)
    LOCAL_SCHEMA = transaction.StateSchema(num_uints=2, num_byte_slices=2)

    #
    def __init__(self, algo_token: str, algo_address: str) -> None:
        """
        Constructor

        :param algo_token: token for connecting algorand testnet
        :param algo_address: algorand testnet address

        :returns: None
        """
        self.__token = algo_token
        self.__address = algo_address
        self.__headers = {"X-API-Key": self.token}
        self.__client = self.__get_client()
        self.__params = self.client.suggested_params()

    #
    def __get_client(self) -> Optional[AlgodClient]:
        """
        create AlgodClient object from given token and address

        :returns: AlgodClient object
        """
        return AlgodClient(self.token, self.address, self.headers)

    #
    @property
    def headers(self) -> dict:
        """
        Getter for header private field

        :returns: headers field value
        """
        return self.__headers

    #
    @property
    def token(self) -> str:
        """
        Getter for token private field

        :returns: token field value
        """
        return self.__token

    #
    @property
    def address(self) -> str:
        """
        Getter for address private field

        :returns: address field value
        """
        return self.__address

    #
    @property
    def params(self) -> str:
        """
        Getter for params private field

        :returns: params field value
        """
        return self.__params

    #
    @property
    def client(self) -> Optional[AlgodClient]:
        """
        Getter for client private field

        :returns: client field value
        """
        return self.__client

    #
    def get_balance(self, address: str) -> int:
        """
        Get balance of given account

        :params address: address of account

        :returns: amount balance
        """
        return self.client.account_info(address).get("amount")

    #
    def get_transaction_info(self, tx_id: str):
        """
        Get transaction information

        :param tx_id: transaction id

        :returns: transaction information
        """
        return self.client.pending_transaction_info(tx_id)

    #
    def generate_new_account(self) -> dict:
        """
        Generate new account for algorand testnet

        :returns: new generated account key, address and mnemonic
        """
        private_key, address = account.generate_account()
        mnem = mnemonic.from_private_key(private_key)

        return {"pk": private_key, "address": address, "mnemonic": mnem}

    #
    def get_application_id(self, tx_id: str) -> int:
        """
        Get application id from transaction id

        :param tx_id: transaction id

        :returns: application id
        """
        transaction_info = self.get_transaction_info(tx_id)
        app_id = transaction_info.get("application-index")
        return app_id

    #
    def get_application_address(self, app_id: int) -> str:
        """
        Get application address from id

        :param app_id: id of application

        :returns: address of application
        """
        app_address = logic.get_application_address(app_id)
        return app_address

    #
    def build_payment_transaction(
                self,
                sender: str,
                receiver: str,
                amount: int,
                note: str
            ) -> Optional[PaymentTxn]:
        """
        Build payment transaction from sender to receiver

        :param sender: sender address
        :param receiver: receiver address
        ;param amount: amount which should be transferred
        :param note: note for transaction

        :returns: payment transaction
        """
        txn = transaction.PaymentTxn(
            sender=sender,
            sp=self.params,
            receiver=receiver,
            amt=amount,
            note=note,
        )
        return txn

    #
    def create_application_transaction(
                self,
                sender: str,
                approval_teal: bytes,
                clear_teal: bytes
            ) -> Optional[ApplicationCreateTxn]:
        """
        Create transaction that interacts with the application system

        :param sender: address
        :param approval_teal: transaction smart contract in bytes
        :param clear_teal: clear smart contract in bytes

        :returns: application transaction
        """
        app_create_txn = transaction.ApplicationCreateTxn(
            sender=sender,
            sp=self.params,
            on_complete=transaction.OnComplete.NoOpOC.real,
            approval_program=approval_teal,
            clear_program=clear_teal,
            global_schema=self.GLOBAL_SCHEMA,
            local_schema=self.LOCAL_SCHEMA
        )
        return app_create_txn

    #
    def sign_transaction(
                self,
                sender: str,
                txn: Optional[ApplicationCreateTxn]
            ) -> Optional[SignedTransaction]:
        """
        Sign created transaction

        :param sender: sender private key
        :param txn: transaction which should be signed

        :returns: signed transaction
        """
        signed_txn = txn.sign(sender)
        return signed_txn

    #
    def send_transaction(self, signed_txn: Optional[SignedTransaction]) -> str:
        """
        Send already signed transaction

        :param signed_txn: signed transaction which should be sent

        :returns: transaction id
        """
        tx_id = self.client.send_transaction(signed_txn)
        return tx_id

    #
    def wait_for_transaction(self, tx_id: str) -> None:
        """
        Block until a pending transaction is confirmed by the network

        :param tx_id: transaction id

        :returns None
        """
        transaction.wait_for_confirmation(self.client, tx_id, 4)

    #
    def call_application_transaction(
                self,
                sender: str,
                app_id: int,
                app_args: list
            ) -> Optional[ApplicationCallTxn]:
        """
        Create Application call transaction object

        :param sender: sender address
        :param app_id: application id for which transaction is made
        :param app_args: arguments for application smart contract

        :returns: ApplicationCallTxn objects
        """
        app_call_txn = transaction.ApplicationCallTxn(
            sender=sender,
            sp=self.params,
            index=app_id,
            on_complete=transaction.OnComplete.NoOpOC.real,
            app_args=app_args
        )
        return app_call_txn

    #
    def get_application_global_state(self, app_id: int) -> dict:
        """
        Get application global state info

        :param app_id: application id

        :returns: info about applicatioj global state
        """
        app_info = self.client.application_info(app_id)
        global_state = app_info['params']['global-state']
        state = {}
        for item in global_state:
            key = base64.b64decode(item['key']).decode('utf-8')
            value = item['value']
            if key == "committed_amount":
                state[key] = value["uint"]
        return state
