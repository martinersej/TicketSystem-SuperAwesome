from datetime import datetime
import getpass
import sys
import re
import os
import json
import colorama
import time
import requests
from urllib.request import Request, urlopen
from colorama import Fore
from optparse import OptionParser

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
colorama.init()

os.system('cls')
os.system('title Script lavet af MartinErSej - Brug for hjælp, kontakt mart1n#0482 på Discord.')

try:
	with open('config.json', 'r', encoding='UTF-8') as f:
		indhold = json.load(f)
		username = indhold['Mail']
		password = indhold['Kodeord']
		WEBHOOK_URL = indhold['Webhook-URL']
		Blacklist_Add = indhold['Blacklist-Add']
		blacklisted_spillere = indhold['Blacklist']
except:
	with open('config.json', 'w', encoding='UTF-8') as f:
		data = {"Mail": "indsæt her", "Kodeord": "indsæt her", "Webhook-URL": "indsæt her", "Blacklist-Add": False, "Blacklist": []}
		json.dump(data, f, indent=4, sort_keys=False, ensure_ascii=False)
	print('Du skal nok lige kigge i configgen først.')
	time.sleep(10)
	sys.exit()

server = 'superawesome.dk'

def get_options():
	global username, password, server
	parser = OptionParser()
	
	parser.add_option("-d", "--dump-packets", dest="dump_packets",
					  action="store_true",
					  help="print sent and received packets to standard error")

	parser.add_option("-v", "--dump-unknown-packets", dest="dump_unknown",
					  action="store_true",
					  help="include unknown packets in --dump-packets output")

	(options, args) = parser.parse_args()

	match = re.match(r"((?P<host>[^\[\]:]+)|\[(?P<addr>[^\[\]]+)\])"
					 r"(:(?P<port>\d+))?$", server)
	if match is None:
		raise ValueError("Invalid server address: '%s'." % server)
	options.address = match.group("host") or match.group("addr")
	options.port = int(match.group("port") or 25565)

	return options

rek = 0
kitsa = 0
vipsedler = 0
blacklisted = 0
quit = False
larme = False
ticket = False
reklame = ['\n\n**REKLAME**']
kit_superawesome = ['\n\n**KIT SUPERAWESOME**']
vip_sedler = ['\n\n**VIP SEDLER**']

def blacklist():
	global Blacklist_Add, blacklisted_spillere
	blacklist = str(input("Hvis du vil springe over denne blacklist check, så sæt Blacklist-Add til false i config.json.\nSe et eksmempel på hvordan det skal skrives her, så se næste linje:\neksempel: MartinErSej King_Aps Eksempel1 Eksempel2 Eksempel3\nSkriv her, hvem der skal blacklistes: ")).split(" ")
	if blacklist != ['']:
		with open('config.json', 'w', encoding='UTF-8') as f:
			for x in blacklist:
				blacklisted_spillere.append(x)
			json.dump(indhold, f, indent=4, sort_keys=False, ensure_ascii=False)


def main():
	global quit, larme, ticket, reklame, kit_superawesome, rek, kitsa, vipsedler, vip_sedler, blacklisted
	options = get_options()

	auth_token = authentication.AuthenticationToken()
	try:
		auth_token.authenticate(username, password)
	except YggdrasilError:
		print('Din mail eller adgangskode er forkert.')
		time.sleep(10)
		sys.exit()
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	data = json.dumps({"agent":{"name":"Minecraft","version":1},"username":username,"password":password,"clientToken":""})
	responsAuth = requests.post('https://authserver.mojang.com/authenticate', data=data, headers=headers)
	real_username = responsAuth.json()['selectedProfile']['name']
	print("\nLogger ind med: %s\n" % real_username)
	connection = Connection(
		options.address, options.port, auth_token=auth_token)

	if options.dump_packets:
		def print_incoming(packet):
			if type(packet) is Packet:
				if options.dump_unknown:
					print('--> [unknown packet] %s' % packet, file=sys.stderr)
			else:
				print('--> %s' % packet, file=sys.stderr)

		def print_outgoing(packet):
			print('<-- %s' % packet, file=sys.stderr)

		connection.register_packet_listener(
			print_incoming, Packet, early=True)
		connection.register_packet_listener(
			print_outgoing, Packet, outgoing=True)

	def handle_join_game(join_game_packet):
		global larme
		if larme == False:
			time.sleep(0.5)
			packet = serverbound.play.ChatPacket()
			packet.message = "/server larmelobby"
			connection.write_packet(packet)
			larme = True


	connection.register_packet_listener(
		handle_join_game, clientbound.play.JoinGamePacket)

	def colorFix(color):
		try:
			if color == 'dark_gray':
				return '\33[90m'
			if color == 'gray':
				return '\033[37m'
			if color == 'gold':
				return '\033[33m'
			if color == 'dark_aqua':
				return "\033[36m"
			if color == 'aqua':
				return '\033[96m'
			if color == 'dark_red':
				return "\033[31m"
			if color == 'red':
				return "\033[91m"
			if color == 'white':
				return '\033[97m'
			if color == 'black':
				return "\033[30m"
			if color == 'yellow':
				return "\033[93m"
			if color == 'green':
				return "\033[92m"
			if color == 'dark_green':
				return "\033[32m"
			if color == 'blue':
				return "\033[94m"
			if color == 'dark_blue':
				return "\033[34m"
			if color == 'dark_green':
				return "\033[32m"
			if color == 'light_purple':
				return "\033[95m"
			if color == 'dark_purple':
				return "\033[35m"
			print(color)
			return '\033[97m'
		except:
			return '\033[97m'

	def print_chat(chat_packet):
		message = ''
		for x in chat_packet.json_data.split('},{'):
			text = x.split('},{')
			for l in text:
				if l.endswith('"'):
					l += '}'
				if l.startswith('"'):
					l = '{' + l
				l = l.replace('],"text":""}', '').replace('{"extra":[', '')
				try:
					myjson = json.loads(l)
					message += colorFix(myjson['color']) + myjson['text']
				except: return

	connection.connect()
	
	def besked(chat_packet):
		global reklame, kit_superawesome, rek, kitsa, vipsedler, vip_sedler, blacklisted_spillere, blacklisted
		message = ''
		try:
			for x in json.loads(chat_packet.json_data)['extra']:
				if str(x) == "{'text': ''}":
					continue
				try:
					message += colorFix(x['color']) + x['text']
				except Exception as e:
					if colorFix('white') + str(x) == "{'bold': False, 'italic': False, 'underlined': False, 'strikethrough': False, 'obfuscated': False, 'text': ' '}":
						continue
					if 'string indices' in str(e):
						message += colorFix('white') + str(x)
						continue
			if not message == "'color":
				message = message + colorFix('white')
				if message.__contains__('Spiller: ' and ' Ticket nummer: '):
					message = message.replace('\x1b[33m', '')
					message = message.replace('\x1b[97m', '')
					message = message.split(' ')
					if str(message[1]) not in blacklisted_spillere:
						try:
							resp = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{message[1]}")
							uuid = resp.json()["id"]
							uuid = uuid[:8]+'-'+uuid[8:]
							uuid = uuid[:13]+'-'+uuid[13:]
							uuid = uuid[:18]+'-'+uuid[18:]
							uuid = uuid[:23]+'-'+uuid[23:]
							uuidurl = uuid
							uuid = '\n'+'`'+uuid+'`'
							navn = '`'+message[1]+'`'
						except:
							navn = '`'+message[1]+'`' + f' ([NameMC](https://da.namemc.com/{message[1]}))'
							uuid = ''
						if str(uuid) != "''":
							url = "https://api.superawesome.ml/api/verify/uuid/"
							headers = {"root": "GM&dm.wb,3kmpGm4"}
							try:
								r = requests.get(url+uuidurl, headers=headers)
								discord = '\n`'+str(r.json()["discord"])+'`'
							except:
								discord = ''
						if str(message[5]) == 'kit':
							try:
								if str(message[6]) == 'superawesome':
									kitsa += 1
									if len(kit_superawesome) == 1:
										kit_superawesome.append('\n'+ navn +' har købt ' + '**'+ message[5]+' '+message[6] +'**' + ' - ' + f'`/st t s {message[1]} {message[4]}`' +uuid+discord)
									else:
										kit_superawesome.append('\n\n'+ navn +' har købt ' + '**'+ message[5]+' '+message[6] +'**' + ' - ' + f'`/st t s {message[1]} {message[4]}`' +uuid+discord)
							except:
								pass
						elif str(message[5]) == 'VIP':
							try:
								if str(message[6]) == 'sedler':
									vipsedler += 1
									if len(vip_sedler) == 1:
										vip_sedler.append('\n'+ navn +' har købt ' + '**'+ message[5]+' '+message[6] +'**' + ' - ' + f'`/st t s {message[1]} {message[4]}`' +uuid+discord)
									else:
										vip_sedler.append('\n\n'+ navn +' har købt ' + '**'+ message[5]+' '+message[6] +'**' + ' - ' + f'`/st t s {message[1]} {message[4]}`' +uuid+discord)
							except:
								pass
						elif str(message[5]) == 'Reklame':
							rek += 1
							if len(reklame) == 1:
								reklame.append('\n'+ navn +' har købt ' + '**'+ message[5] +'**' + ' - ' + f'`/st t s {message[1]} {message[4]}`' +uuid+discord)
							else:
								reklame.append('\n\n'+ navn +' har købt ' + '**'+ message[5] +'**' + ' - ' + f'`/st t s {message[1]} {message[4]}`' +uuid+discord)
					else:
						blacklisted += 1
		except Exception as e:
			pass
	connection.register_packet_listener(besked, clientbound.play.ChatMessagePacket)

	while True:
		try:
			if larme is True and ticket is not True:
				time.sleep(1)
				packet = serverbound.play.ChatPacket()
				packet.message = "/st t n vip"
				ticket = True
				connection.write_packet(packet)
				time.sleep(8)
				quit = True
			if quit is True:
				headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
				embedstr = 0
				embed1 = ''
				embed2 = ''
				for x in reklame:
					if x == '\n\n**REKLAME**':
						if len(reklame) == 1:
							continue
					else:
						embedstr += 1
					if embedstr > 10:
						embed2 = embed2+x
					else:
						embed1 = embed1+x
				for x in kit_superawesome:
					if x == '\n\n**KIT SUPERAWESOME**':
						if len(kit_superawesome) == 1:
							continue
					else:
						embedstr += 1
					if embedstr > 10:
						embed2 = embed2+x
					else:
						embed1 = embed1+x	
				for x in vip_sedler:
					if x == '\n\n**VIP SEDLER**':
						if len(vip_sedler) == 1:
							continue
					else:
						embedstr += 1
					if embedstr > 10:
						embed2 = embed2+x
					else:
						embed1 = embed1+x
				if embedstr > 10:
					embed2 = embed2+f'\n\nTickets med Reklame: {rek}\nTickets med Kit SuperAwesome: {kitsa}\nTickets med VIP sedler: {vipsedler}\nBlacklisted, men har en ticket: {blacklisted}\n '
					send_embed1 = {"description": f"{embed1}", "title": "**ÅBNE TICKETS**", "color": 65527}
					send_embed2 = {"description": f"{embed2}", "color": 65527, "timestamp": f"{datetime.utcnow()}", "footer": {"text": "Dette script er lavet af MartinErSej", "icon_url": "https://imgur.com/Yr2zlXn.gif"}}
					data = {"username": "Tickets", "embeds": [send_embed1,send_embed2],}
				else:
					embed1 = embed1+f'\n\nTickets med Reklame: {rek}\nTickets med Kit SuperAwesome: {kitsa}\nTickets med VIP sedler: {vipsedler}\nBlacklisted, men har en ticket: {blacklisted}\n '
					send_embed1 = {"description": f"{embed1}", "title": "**ÅBNE TICKETS**", "timestamp": f"{datetime.utcnow()}", "footer": {"text": "Dette script er lavet af MartinErSej", "icon_url": "https://imgur.com/Yr2zlXn.gif"}}
					data = {"username": "Tickets", "embeds": [send_embed1],}
				payload = json.dumps(data)
				try:
					req = Request(WEBHOOK_URL, data=payload.encode(), headers=headers)
					urlopen(req)
					print('Sådan, så er de tickets blevet lagt op.')
				except:
					pass
					print('Ja, det fejlede med at ligge dem op.\nFejlen kan ligge ved Webhook-URL eller Discord.')
				time.sleep(5)
				sys.exit()
		except KeyboardInterrupt:
			sys.exit()

if __name__ == "__main__":
	if Blacklist_Add == True:
		blacklist()
	main()