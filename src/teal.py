#
import base64
#
from typing import Optional

#
from pyteal import And, Cond, Expr, Assert, App, Txn, Mode
from pyteal import Bytes, Int, Approve, Return, Btoi, Log
from pyteal import Sha256, Addr, Seq, Or, Global, OnComplete
from pyteal import compileTeal, InnerTxnBuilder, TxnField, TxnType, InnerTxn

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
        hashlock = Bytes("hashlock")

        # Step 1: Alice commits funds for Bob without the hashlock
        on_commit = Seq([
            Assert(App.globalGet(committed_amount_key) == Int(0)),
            App.globalPut(committed_amount_key, Btoi(Txn.application_args[1])),
            App.globalPut(lock_timestamp_key, Txn.last_valid()),
            App.globalPut(alice_key, Txn.sender()),
            App.globalPut(bob_key, Txn.accounts[1]),
            Return(Int(1))
        ])

        # Step 2: Lock commitment by providing hashlock and transferring funds
        on_lock = Seq([
            Assert(App.globalGet(alice_key) == Txn.sender()),
            Assert(App.globalGet(committed_amount_key) > Int(0)),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.amount: App.globalGet(committed_amount_key),
                TxnField.receiver: Global.current_application_address(),
            }),
            InnerTxnBuilder.Submit(),
            App.globalPut(hashlock, Txn.application_args[1]),
            Return(Int(1))
        ])
        # Step 3: Bob claims committed funds by providing the correct preimage
        on_claim = Seq([
            Assert(App.globalGet(bob_key) == Txn.sender()),
            Assert(Sha256(Txn.application_args[1]) == App.globalGet(hashlock)),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.amount: App.globalGet(committed_amount_key),
                TxnField.receiver: Txn.sender(),
            }),
            InnerTxnBuilder.Submit(),
            App.globalPut(committed_amount_key, Int(0)),
            Return(Int(1))
        ])

        program = Cond(
            [Txn.application_id() == Int(0), Approve()],
            [Txn.application_args[0] == Bytes("commit"), on_commit],
            [Txn.application_args[0] == Bytes("lock"), on_lock],
            [Txn.application_args[0] == Bytes("claim"), on_claim]
        )

        return program

    #
    @staticmethod
    def lock() -> Optional[Cond]:
        """
        PyTeal code for locking funds with a hashlock to a specified receiver and redeeming them to a different specified address.

        :returns: pyteal.Expr value
        """

        committed_amount_key = Bytes("committed_amount")
        hashlock_key = Bytes("hashlock")
        alice_key = Bytes("alice")
        receiver_key = Bytes("receiver")

        # Step 1: Lock funds by providing the hashlock and specifying the receiver
        on_lock = Seq([
            Assert(App.globalGet(committed_amount_key) == Int(0)),  # Ensure no funds are currently locked
            Assert(App.globalGet(receiver_key) == Txn.accounts[0]),  # Ensure the specified receiver is valid
            App.globalPut(committed_amount_key, Btoi(Txn.application_args[1])),
            App.globalPut(hashlock_key, Txn.application_args[2]),  # Store the hashlock
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.amount: App.globalGet(committed_amount_key),
                TxnField.receiver: App.globalGet(receiver_key),  # Transfer to the specified receiver
            }),
            InnerTxnBuilder.Submit(),
            Return(Int(1))
        ])

        # Step 2: Redeem funds by providing the correct preimage
        on_redeem = Seq([
            Assert(App.globalGet(committed_amount_key) > Int(0)),  # Ensure funds are locked
            Assert(Sha256(Txn.application_args[1]) == App.globalGet(hashlock_key)),  # Verify the preimage
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.amount: App.globalGet(committed_amount_key),
                TxnField.receiver: Txn.sender(),  # Send funds to the redeemer
            }),
            InnerTxnBuilder.Submit(),
            App.globalPut(committed_amount_key, Int(0)),  # Reset the committed amount
            Return(Int(1))
        ])

        program = Cond(
            [Txn.application_id() == Int(0), Approve()],
            [Txn.application_args[0] == Bytes("lock"), on_lock],
            [Txn.application_args[0] == Bytes("redeem"), on_redeem]
        )

        return program 
    

    # redeem on simulated destination chain. This is not part of protocol
    # redeem on simulated destination chain. This is not part of protocol
    @staticmethod
    def lock_redeem_dest():
        asset_id_key = Bytes("asset_id")
        committed_amount_key = Bytes("committed_amount")
        hashlock_key = Bytes("hashlock")
        receiver_key = Bytes("receiver")

        # Lock funds logic
        on_lock = Seq([
            Assert(App.globalGet(committed_amount_key) == Int(0)),
            App.globalPut(receiver_key, Txn.accounts[1]),
            App.globalPut(committed_amount_key, Btoi(Txn.application_args[1])),
            App.globalPut(hashlock_key, Txn.application_args[2]),
            Return(Int(1))
        ])

        # Redeem funds logic
        on_redeem = Seq([
            Assert(App.globalGet(committed_amount_key) > Int(0)),
            Assert(Sha256(Txn.application_args[1]) == App.globalGet(hashlock_key)),
            App.globalPut(committed_amount_key, Int(0)),
            Return(Int(1))
        ])

        program = Cond(
            [Txn.application_id() == Int(0), Approve()],
            [Txn.application_args[0] == Bytes("lock"), on_lock],
            [Txn.application_args[0] == Bytes("redeem"), on_redeem]
        )

        return program

    #
    def deploy_contract(self, client, contract):
        teal_code = self.compile_teal_file(TealManager.__dict__[contract]())
        self.save_teal_to_file(teal_code, '{}.teal'.format(contract))
        compiled_teal = self.compile_teal_code(client, "{}.teal".format(contract))
        clear_teal = self.compile_teal_code(client, "clear.teal")

        return compiled_teal, clear_teal

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
