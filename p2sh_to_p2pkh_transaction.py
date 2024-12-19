# Output.png screenshot is provided in case the code doesn't run on your computer

from bitcoinutils.setup import setup
from bitcoinutils.proxy import NodeProxy
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from bitcoinutils.script import Script
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
import requests

class SecondProgram:

    def calculate_transaction_fee(self, total_utxo, p2pkh_address, utxos):
        try:
            # Fetch the fee rate estimates from Blockstream's API
            response = requests.get("https://blockstream.info/api/fee-estimates")
            fees = response.json()

            # Choose the desired fee rate (Fee rate in satoshis per byte for ~6 blocks)
            fee_rate_sat_per_byte = fees["6"]

            # Calculate transaction size
            tx = self.create_transaction(utxos, total_utxo, 0, p2pkh_address)
            transaction_size = len(str(tx))

            # Calculate total fee based on transaction size
            total_fee = fee_rate_sat_per_byte * transaction_size

            return total_fee * 0.00000001 # in BTC
        
        except Exception:
            return 0.0000150274 # default value
        
        
    def create_transaction(self, utxos, total_utxo, fees, p2pkh_address):

        # Create transaction inputs from UTXOs
        tx_inputs = [TxInput(utxo['txid'], utxo['vout']) for utxo in utxos]

        # Calculate total amount to send (accounting fees)
        amount_to_send = float(total_utxo) - fees

        if amount_to_send <= 0:
            print("Insufficient funds after fee deduction.")
            return

        amount_to_send_sat = int(to_satoshis(amount_to_send))

        # Create transaction output using P2PKH scriptPubKey (locking script)
        tx_outputs = [TxOutput(amount_to_send_sat, Script(
            ["OP_DUP", "OP_HASH160", P2pkhAddress(p2pkh_address).to_hash160(), "OP_EQUALVERIFY", "OP_CHECKSIG"]),
        )]
        
        # Create the transaction
        return Transaction(tx_inputs, tx_outputs)


    def sign_transaction(self, redeem_script, private_key1, private_key2, raw_tx):
        
        # Set the unlocking script for each input
        for i, tx_in in enumerate(raw_tx.inputs):
            # Sign the transaction with the provided private keys
            sk1 = private_key1.sign_input(raw_tx, i, redeem_script)
            sk2 = private_key2.sign_input(raw_tx, i, redeem_script)

            # Create the unlocking script
            unlocking_script = Script(["OP_0", sk1, sk2, redeem_script.to_hex()])
            tx_in.script_sig = unlocking_script

        return raw_tx.serialize(), raw_tx.get_txid()
    
    
    def broadcast_transaction(self, signed_tx, proxy):
        result = proxy.testmempoolaccept([signed_tx])
        # Verify that the transaction is valid
        if result[0]['allowed']:
        # Send it to the blockchain
            proxy.sendrawtransaction(signed_tx)
            print("\nTransaction broadcasted successfully.")
        else:
            print("\nTransaction is invalid:", result[0]['reject-reason'])


    def main(self):
        setup('regtest')
        
        proxy = NodeProxy("user", "password").get_proxy()

        private_key1 = PrivateKey(input("Enter the first private key: ").strip())
        private_key2 = PrivateKey(input("Enter the second private key: ").strip())
        public_key3 = PublicKey(input("Enter the first public key: ").strip()).to_hex() 

        public_key1 = private_key1.get_public_key().to_hex()
        public_key2 = private_key2.get_public_key().to_hex()

        redeem_script = Script(["OP_2", public_key1, public_key2, public_key3, "OP_3", 'OP_CHECKMULTISIG'])
        
        p2sh_address = input("Enter the P2SH address: ").strip()
        p2pkh_address = input("Enter the P2PKH address: ").strip()

        
        # Fetch UTXOs for the P2SH address
        utxos = proxy.listunspent(0, 9999999, [p2sh_address])
        
        if not utxos: 
            print("No UTXO")
            return

        total_utxo = sum([utxo['amount'] for utxo in utxos])
        print("\nTotal utxo:\n", total_utxo, "btc")

        fees = self.calculate_transaction_fee(total_utxo, p2pkh_address, utxos)
        print("\nEstimated fees:\n", fees, "sat")

        raw_tx = self.create_transaction(utxos, total_utxo, fees, p2pkh_address)
        print("\nRaw unsigned transaction:\n", raw_tx.serialize())

        signed_transaction, tx_id = self.sign_transaction(redeem_script, private_key1, private_key2, raw_tx)
        print("\nSigned Transaction:\n", signed_transaction)
        print("\nTransaction ID:\n", tx_id)

        self.broadcast_transaction(signed_transaction, proxy)



if __name__ == "__main__":
    program = SecondProgram()
    program.main()

