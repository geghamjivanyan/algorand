#
import base64
#
from typing import Optional

#
from pyteal import And, Cond, Expr, Assert, App, Txn, Mode
from pyteal import Bytes, Int, Approve, Return, Btoi
from pyteal import Arg, Sha256, Addr, Seq, Or, Global
from pyteal import compileTeal, InnerTxnBuilder, TxnField, TxnType

#
from algosdk.v2client.algod import AlgodClient


#
class TealManager:
    """
    TealManager object for creating teal contracts from pyteal code
    """

    #
    def __init__(self, path: str) -> None:
        """
        Constructor

        :param path: path where smart contracts should be saved

        :returns: None
        """
        self.__path = path

    #
    @property
    def path(self) -> str:
        """
        getter for path private field

        :returns: path field value
        """
        return self.__path

    #
    def compile_teal_file(self, teal_code) -> str:
        """
        Compile TEAL code to base64-encoded TEAL.

        :param teal_code: pyteal expression

        :returns: A TEAL assembly program compiled from the input expression.
        """
        return compileTeal(teal_code, mode=Mode.Application, version=5)

    #
    def save_teal_to_file(self, teal_code, filename: str) -> None:
        """
        Save the compiled TEAL code to a file.

        param teal_code: A TEAL assembly program compiled
                         from the input expression.
        param filename: file where compiled program should be saved

        :returns: None
        """
        with open("{}/{}".format(self.path, filename), 'w') as f:
            f.write(teal_code)

    #
    def compile_teal_code(
                self,
                client: Optional[AlgodClient],
                filename: str
            ) -> bytes:
        """
        Convert TEAL assembly program to base64

        param client: Client class for algod. Handles all algod requests.
        param filename: filename from  where compiled program should be read

        :returns: compiled bytes
        """

        with open("{}/{}".format(self.path, filename), "r") as f:
            teal_program = f.read()

        teal_result = client.compile(teal_program)
        teal = base64.b64decode(teal_result["result"])
        return teal

    @staticmethod
    def commit() -> Optional[Expr]:
        """
        PyTeal code for Alice committing funds for Bob.

        :returns: pyteal.Expr value
        """

        committed_amount_key = Bytes("committed_amount")
        lock_timestamp_key = Bytes("lock_timestamp")
        alice_key = Bytes("alice")
        bob_key = Bytes("bob")
        hashlock_key = Bytes("hashlock")

        # Step 1: Alice commits funds for Bob without the hashlock
        on_commit = Seq([
            Assert(App.globalGet(committed_amount_key) == Int(0)),  # Ensure no previous commitment
            App.globalPut(committed_amount_key, Btoi(Txn.application_args[1])),  # Store committed amount
            App.globalPut(lock_timestamp_key, Txn.last_valid()),  # Record commitment timestamp
            App.globalPut(alice_key, Txn.sender()),  # Store Alice's address
            App.globalPut(bob_key, Txn.accounts[1]),  # Store Bob's address
            Return(Int(1))
        ])

        # Step 2: Lock the commitment by providing the hashlock and transferring funds
        on_lock = Seq([
            Assert(App.globalGet(alice_key) == Txn.sender()),  # Ensure only Alice can lock the funds
            Assert(App.globalGet(committed_amount_key) > Int(0)),  # Ensure there's an amount committed
            InnerTxnBuilder.Begin(),  # Start inner transaction to transfer funds to the smart contract
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.amount: App.globalGet(committed_amount_key),
                TxnField.receiver: Global.current_application_address(),  # Transfer to the smart contract address
            }),
            InnerTxnBuilder.Submit(),
            App.globalPut(hashlock_key, Txn.application_args[1]),  # Store the hashlock (hash of the secret)
            Return(Int(1))
        ])
        # Step 3: Bob claims the committed funds by providing the correct preimage
        on_claim = Seq([
            Assert(App.globalGet(bob_key) == Txn.sender()),  # Ensure only Bob can claim the funds
            Assert(Sha256(Txn.application_args[1]) == App.globalGet(hashlock_key)),  # Verify the preimage matches the hashlock
            InnerTxnBuilder.Begin(),  # Start inner transaction to transfer funds to Bob
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.amount: App.globalGet(committed_amount_key),
                TxnField.receiver: Txn.sender(),  # Send funds to Bob
            }),
            InnerTxnBuilder.Submit(),
            App.globalPut(committed_amount_key, Int(0)),  # Reset committed amount after transfer
            Return(Int(1))
        ])

        program = Cond(
            [Txn.application_id() == Int(0), Approve()],  # NoOp on creation
            [Txn.application_args[0] == Bytes("commit"), on_commit],  # Commit funds
            [Txn.application_args[0] == Bytes("lock"), on_lock],  # Lock funds with hashlock
            [Txn.application_args[0] == Bytes("claim"), on_claim]  # Bob claims the funds
        )

        return program

    def deploy_contract(self, client):
        teal_code = self.compile_teal_file(self.commit())
        self.save_teal_to_file(teal_code, 'commit.teal')
        compiled_teal = self.compile_teal_code(client, "commit.teal")
        clear_teal = self.compile_teal_code(client, "clear.teal")

        return compiled_teal, clear_teal


    @staticmethod
    def lock_contract(
                receiver: str,
                lock_time: int,
                hash_of_secret: str
            ) -> Optional[And]:
        """
        PyTeal code for lock smart contract.

        :returns: pyteal.And value

        """
        is_payment_to_receiver = And(
            Txn.receiver() == Addr(receiver),
            Txn.amount() > Int(0),
        )

        after_lock_time = Txn.first_valid() > Int(lock_time)
        correct_secret_provided = Sha256(Txn.application_args[0]) == Bytes(hash_of_secret)

        return And(
            is_payment_to_receiver,
            Or(
                after_lock_time,
                correct_secret_provided
            )
        )

    #
    @staticmethod
    def redeem(self):
        pass

    #
    @staticmethod
    def clear_state_program() -> int:
        """
        Specific type of program in Algorand applications
        that is executed when a user removes their local state.

        :retruns: int
        """
        return Approve()


tm = TealManager("smart_contracts")
cc = tm.compile_teal_file(tm.commit())
tm.save_teal_to_file(cc, "commit.teal")
