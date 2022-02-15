import threading
from web3 import Web3
from web3.auto import w3
from ctypes import windll
from loguru import logger
from sys import stderr
from threading import Thread
from os import system

system("cls")
def clear(): return system('cls')
print('Telegram Channel - https://t.me/n4z4v0d\n')
windll.kernel32.SetConsoleTitleW('RANKERDAO Auto Claim | by NAZAVOD')
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")


selected_option = int(input('Enter your choice (1 - claim nft; 2 - send nft to main wallet): '))
if selected_option == 2:
	main_wallet = str(input('Main address: '))
wallets_folder = str(input('Drop TXT here (format: wallet:privatekey): '))
wait_tx_result = str(input('Wait TX result? (y/N): '))
threads = int(input('Threads: '))


with open(wallets_folder, 'r') as file:
	wallet_datas = [row.strip() for row in file]


def claim_nft(wallet_data, contract):
	try:
		private_key = wallet_data.split(':')[1]
		address = wallet_data.split(':')[0]

		transaction = contract.functions.mint().buildTransaction({
			'gas': 148981,
			'gasPrice': web3.toWei('5', 'gwei'),
			'from': address,
			'nonce': web3.eth.getTransactionCount(address)
			})

		signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)

		tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
		logger.info('TX id: '+web3.toHex(tx_hash))
		txstatus = web3.eth.waitForTransactionReceipt(tx_hash).status
		if txstatus == 1:
			logger.success(f'TX status: {txstatus}')
		else:
			logger.error(f'TX status: {txstatus}')

	except Exception as error:
		logger.error(f'{address} - {str(error)}')


def transfer_nft(wallet_data, main_wallet, contract):
	try:
		private_key = wallet_data.split(':')[1]
		address = wallet_data.split(':')[0]

		balanceOf = contract.functions.balanceOf(address).call()
		if balanceOf >= 1:
			for i in range(balanceOf):
				current_token_id = int(contract.functions.tokenOfOwnerByIndex(address, i).call())

				transaction = contract.functions.transferFrom(address, main_wallet, current_token_id).buildTransaction({
					'gas': 200000,
					'gasPrice': web3.toWei('5', 'gwei'),
					'from': address,
					'nonce': web3.eth.getTransactionCount(address)
					})

				signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)

				tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
				logger.info('TX id: '+web3.toHex(tx_hash))
				txstatus = web3.eth.waitForTransactionReceipt(tx_hash).status
				if txstatus == 1:
					logger.success(f'TX status: {txstatus}')
				else:
					logger.error(f'TX status: {txstatus}')
	except Exception as error:
		logger.error(f'{address} - {str(error)}')



if __name__ == '__main__':
	clear()
	web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
	while wallet_datas:
		if threading.active_count() <= threads:
			for _ in range(threads):
				wallet_data = wallet_datas.pop(0)
				abi = open('ABI','r').read().replace('\n','')
				contract = web3.eth.contract(address=web3.toChecksumAddress('0x5790a8c33733d82C2648f3d36E1E215D4e81EDf0'), abi=abi)
				if selected_option == 1:
					Thread(target=claim_nft, args=(wallet_data, contract)).start()
				else:
					Thread(target=transfer_nft, args=(wallet_data, main_wallet, contract,)).start()
