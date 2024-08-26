#
import hashlib

#
from teal import TealManager
from algorand_htlc import AlgorandHTLC
from accounts import get_user


teal_manager = TealManager("smart_contracts")
htlc = AlgorandHTLC(
            algo_token='',
            algo_address='https://testnet-api.algonode.cloud:443'
        )


alice = get_user("alice")
bob = get_user("bob")
john = get_user("john")

amount = 10**6  # 1 ALGO
secret = b'layerswap'

if __name__ == "__main__":

    # app_id, app_address = htlc.commit(teal_manager, alice, amount, bob)
    # print("APP   ID:", app_id)
    # print("APP ADDR:", app_address)

    app_id = 717537989
    app_address = 'SY3G4Q3NIIY7MRHTUJENLLL4ICZQ5YOLOZNPPGZTO62MX65ZYRKK3P3FL4'
    hashlock = hashlib.sha256(secret).digest()
    # htlc.lock_commitment(alice, app_id, amount, hashlock, app_address)

    htlc.redeem(bob, app_id, secret, bob)
