from algorand import AlgoUser

alice = {
    "pk": "d/TdnjyUOs1dT8Aha3F7Hk+o0B/lQI+UNKtJxyCk3KZ5WmCGxUY7qyjv9an2vlng/B5UoibVSlL2CQ4gt7q/sA==",
    "address": "PFNGBBWFIY52WKHP6WU7NPSZ4D6B4VFCE3KUUUXWBEHCBN52X6YJG5FWAI",
    "mnemonic": "moment jelly exhaust duck inside infant kit scare goddess shield diet vehicle explain vintage cigar domain music spoil stereo innocent dose cinnamon dad absent reveal" 
}

bob = {
    "pk": "WTBsLqfDC75q8T7LaexoVwkx7uuSK6aM/XhHDhZZNGTOnTDkiqgszFQ4YT4CQPHnwQ4wjmq40ZmH0ecZqA30Pw==",
    "address": "Z2OTBZEKVAWMYVBYME7AEQHR47AQ4MEONK4NDGMH2HTRTKAN6Q7UFD2FFA",
    "mnemonic": "arctic radio now denial bleak question mercy discover defense random refuse nice ginger wine nuclear clog network wage round tongue clown bind canvas about fiction"
}

john = {
    "pk": "XD4ECg7pQxVPTyv2KAWYZUse2sQjSxyWcOvThZ1oDwb/QqBsoMRAIdCXMyQQvpAajkyJ1l0CqROSTuNkyMeLTg==",
    "address": "75BKA3FAYRACDUEXGMSBBPUQDKHEZCOWLUBKSE4SJ3RWJSGHRNHARBI5BQ",
    "mnemonic": "slide axis agree movie march shed kidney clip burst believe slot rent develop custom bullet enroll seminar seat volcano frog deposit surface corn abandon sad"
}

users = {
    "alice": alice,
    "bob": bob,
    "john": john
}

def get_user(name):
    user = users[name]
    return AlgoUser(user["pk"], user["address"], user["mnemonic"])
