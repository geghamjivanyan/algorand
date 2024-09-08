#
import hashlib
import logging

#
from teal import TealManager
from algorand_htlc import AlgorandHTLC
from utils import get_user, show_logs, fill_smart_contract_balance


logger = logging.getLogger("PreHTLC")
logging.basicConfig(filename='prehtlc.log', level=logging.INFO)

teal_manager = TealManager("smart_contracts")
htlc = AlgorandHTLC(
            algo_token='',
            algo_address='https://testnet-api.algonode.cloud:443'
        )

alice = get_user("alice")
bob = get_user("bob")
alice_dest = get_user("alice_dest")
bob_dest = get_user("bob_dest")

amount = 10**5  # 1 ALGO
secret = b'layerswap'
transaction_fee = 1000

if __name__ == "__main__":
    logger.info("   Started")
  
    #logger.info("   Transaction fee: {}".format(transaction_fee))
    #alice_initial_balance = htlc.get_balance(alice.address)
    #bob_initial_balance = htlc.get_balance(bob.address)

    #logger.info("   Alice initial balance: {}".format(alice_initial_balance))
    #logger.info("   Bob  initial  balance: {}".format(bob_initial_balance))




    #app_id, app_address = htlc.commit(teal_manager, alice, amount, bob)
    #
    #logger.info("   App created successfully: ID - {}, Address - {}".format(
    #            app_id, app_address
    #        )
    #    )

    #print("APP   ID:", app_id)
    #print("APP ADDR:", app_address)

    #alice_balance = htlc.get_balance(alice.address)
    #bob_balance = htlc.get_balance(bob.address)
    #app_balance = htlc.get_balance(app_address)

    #logger.info("   Alice balance after commit: {}".format(alice_balance))
    #logger.info("   Bob  balance  after commit: {}".format(bob_balance))
    #logger.info("   Smart contract balance after creating: {}".format(app_balance))

    #fill_smart_contract_balance(htlc, alice, app_address, amount)

    #alice_balance = htlc.get_balance(alice.address)
    #app_balance = htlc.get_balance(app_address)
    #app_state = htlc.get_application_global_state(app_id)
    #
    #logger.info("   Alice balance after transaction: {}".format(alice_balance))
    #logger.info("   Smart contract balance after filling: {}".format(app_balance))
    #logger.info("   Smart contract global state: {}".format(app_state))

    # create new asset and simulate nnew coin as destination chain
    # This is not a part of protocol

    app_index, asset_id = htlc.create_new_asset(teal_manager, bob_dest)
    print("APP Index", app_index, asset_id)


    # bob_dest lock for alice_dest
    hashlock = hashlib.sha256(b"layerswap").digest()
    htlc.lock_dest_chain(bob_dest, app_index, asset_id, amount, hashlock, alice_dest)
    htlc.redeem_dest(bob_dest, app_index, secret)


    # alice lock commitment
    #hashlock = hashlib.sha256(secret).digest()
    #htlc.lock_commitment(alice, app_id, amount, hashlock, app_address)

    # bob redeem commitment
    #htlc.redeem(bob, app_id, secret)


    # bob dest reedem  alice_dest
    #show_logs()
