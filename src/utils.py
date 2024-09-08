from algorand import AlgoUser

# alice account on main chain
alice = {
    "pk": (
            "d/TdnjyUOs1dT8Aha3F7Hk+o0B/lQI+UNKtJxyCk3KZ5"
            "WmCGxUY7qyjv9an2vlng/B5UoibVSlL2CQ4gt7q/sA=="
        ),
    "address": "PFNGBBWFIY52WKHP6WU7NPSZ4D6B4VFCE3KUUUXWBEHCBN52X6YJG5FWAI",
    "mnemonic": (
            "moment jelly exhaust duck inside"
            " infant kit scare goddess shield"
            " diet vehicle explain vintage cigar"
            " domain music spoil stereo innocent"
            " dose cinnamon dad absent reveal"
        )
}

# bob account on main chain
bob = {
    "pk": (
            "WTBsLqfDC75q8T7LaexoVwkx7uuSK6aM/XhHDhZZNGTO"
            "nTDkiqgszFQ4YT4CQPHnwQ4wjmq40ZmH0ecZqA30Pw=="
        ),
    "address": "Z2OTBZEKVAWMYVBYME7AEQHR47AQ4MEONK4NDGMH2HTRTKAN6Q7UFD2FFA",
    "mnemonic": (
            "arctic radio now denial bleak"
            " question mercy discover defense random"
            " refuse nice ginger wine nuclear"
            " clog network wage round tongue"
            " clown bind canvas about fiction"
        )
}

# bob account on destination chain
bob_dest = {
    "pk": (
            "474UeIayx/e52aSyrw2zqOai+MzPMn5cKBMXuXKohYLN"
            "s3izvxqAu4gofYiDLu+0RIQkxnrv/kh+VaeJErYkew=="
        ),
    "address": "ZWZXRM57DKALXCBIPWEIGLXPWRCIIJGGPLX74SD6KWTYSEVWER5SGYT2OM",
    "mnemonic": (
            "symbol fancy despair chronic month"
            " law soccer pill wagon cute"
            " flower hedgehog easy dilemma lazy"
            " crazy more pause maze multiply"
            " tornado head before above reopen"
        )
}

# alice account on destination chain
alice_dest = {
    "pk": (
            "XD4ECg7pQxVPTyv2KAWYZUse2sQjSxyWcOvThZ1oDwb/"
            "QqBsoMRAIdCXMyQQvpAajkyJ1l0CqROSTuNkyMeLTg=="
        ),
    "address": "75BKA3FAYRACDUEXGMSBBPUQDKHEZCOWLUBKSE4SJ3RWJSGHRNHARBI5BQ",
    "mnemonic": (
            "slide axis agree movie march"
            " shed kidney clip burst believe"
            " slot rent develop custom bullet"
            " enroll seminar seat volcano frog"
            " deposit surface corn abandon sad"
        )
}

users = {
    "alice": alice,
    "bob": bob,
    "alice_dest": alice_dest,
    "bob_dest": bob_dest
}


#
def get_user(name):
    user = users[name]
    return AlgoUser(user["pk"], user["address"], user["mnemonic"])

#
def show_logs():

    with open('prehtlc.log', 'r') as f:
        info = f.readlines()
    for r in info:
        print(r)


#
def fill_smart_contract_balance(htlc, sender, receiver, amount):
    txn = htlc.build_payment_transaction(sender.address, receiver, amount, "Fill Balance")
    signed_txn = htlc.sign_transaction(sender.pk, txn)
    tx_id = htlc.send_transaction(signed_txn)
    htlc.wait_for_confirmation(tx_id)


