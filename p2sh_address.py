from bitcoinutils.setup import setup
from bitcoinutils.keys import P2shAddress
from bitcoinutils.script import Script


def main():

    setup('regtest')

    public_key1 = input("Enter the first public key: ").strip()
    public_key2 = input("Enter the second public key: ").strip()
    public_key3 = input("Enter the third public key: ").strip()

    redeem_script = Script(["OP_2", public_key1, public_key2, public_key3, "OP_3", 'OP_CHECKMULTISIG'])
    
    p2sh_address = P2shAddress.from_script(redeem_script)

    print(f"\nP2SH Address: {p2sh_address.to_string()}")

if __name__ == "__main__":
    main()