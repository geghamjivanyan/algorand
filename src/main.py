#
import hashlib

#
from algosdk import mnemonic

#
from teal import TealManager
from algorand_htlc import AlgorandHTLC

# Alice creds
alice_address = 'HRFZBG6EATH3AIRUBNSA7WBVWBQZLMPTBP3VW5X3UQISVKJSDCQ3WC6VFU'
alice_pk = ('5Zc9kbo3nNpoCfCiliXjPvhinzqD71L7B3i59vBfaUc'
            '8S5CbxATPsCI0C2QP2DWwYZWx8wv3W3b7pBEqqTIYoQ=='
        )
alice_mnemonic = ('witness wagon embrace knife debris'
                    ' cute ensure useless stairs north'
                    ' immense loop shine pond border'
                    ' usage heart cable rose high'
                    ' tiger fitness deputy able author'
                )
alice_pk = mnemonic.to_private_key(alice_mnemonic)

alice = {
    "address": alice_address,
    "pk": alice_pk
}

# Bob creds
bob_pk = ('2UD7l0AgVnkmWbueEXny5+BxY966baQnMYKX5D45R5BHs'
          'R7jdU3BHRpAoeaby1QFkGk06i8j/IbB9YOyBMuGtw=='
         )
bob_address = 'I6YR5Y3VJXAR2GSAUHTJXS2UAWIGSNHKF4R7ZBWB6WB3EBGLQ23YUIGSXM'

bob = {
    "address": bob_address,
    "pk": bob_pk
}


if __name__ == "__main__":

    teal_manager = TealManager("smart_contracts")
    htlc = AlgorandHTLC(
            algo_token='',
            algo_address='https://testnet-api.algonode.cloud:443'
        )

    contract = "commit.teal"
    amount = 100
    app_args = [b"commit", amount]

    app_id = htlc.commit(teal_manager, contract, alice, app_args)

    m = hashlib.sha256()
    m.update(b'layerswap')
    m.digest()
    hashlock = m.hexdigest()
    htlc.lock_commitment(alice, app_id, hashlock)
