#-*- coding: utf-8 -*-

# Laskuri laskemaan IRC-kanavan tölkinnaksautukset ja pullonavaamiset!
# Sanakirjat ovat seuraavassa muodossa:
# {nick : [kokonaismäärä, iltakohtainen, viimeisimmän tsipsauksen kellonaika]}
# esim: {eGetin : [1337, 2, 11-07-1993 00:12:33]}
# Filuun sanakirja tallennetaan seuraavasti:
# nick|kokmäärä|iltakoht|DD-MM-YY hh:mm:ss
# esim: eGetin|1337|2|11-07-1993 00:12:33
#
# Jos tsipsauksia on kolme tai enemmän 5h sisään niin botti alkaa vittuilemaan käyttäjälle

import logging
import time
from datetime import datetime

log = logging.getLogger("tsipslaskuri")

global kayttajalista
kayttajalista = {}

def init(bot):
	"""Tämä ajetaan aina kun botti käynnistetään tai rehashataan"""
	global kayttajalista
	# Tähän pistetään filen käsittely - avaa siis tekstifilun ja lataa sen sisällön sanakirjaan
	try:
		for rivi in open("tsips.txt"):
			rivi = rivi.strip()
			rivi = rivi.split("|")
			nick = rivi[0]
			kokmaara = int(rivi[1])
			iltakoht = int(rivi[2])
			kello = rivi[3]
			kayttajalista[nick] = [kokmaara, iltakoht, kello]
	except IOError:
		log.info("Luodaan uusi tiedosto tsips.txt")
		filu = open("tsips.txt", "w")
		filu.close()

def handle_privmsg(bot, user, channel, msg):
	global kayttajalista
	aikamuoto = "%d-%m-%Y %H:%M:%S"
	uusipaivays = time.strftime(aikamuoto)
	eventit = ["*tsips*", "*naks*", "*tsipsnaks*", "*raks*", "*blob*", "*tsih*"]
	for kohta in eventit:
		if kohta in msg:
			log.info("Käyttäjä %s avasi juoman" % user)
			nick = user.split("!")[0] # Otetaan nick talteen
			try:
				kayttajalista[nick][0] += 1 # Nostetaan kokonaisjuomamäärää
			except KeyError:
				kayttajalista[nick] = [1, 0, uusipaivays]
			paivays = kayttajalista[nick][2] # Tongitaan entinen päiväys
			# Käsitellään päiväyksiä
			paivays = datetime.strptime(paivays, aikamuoto)
			paivays = time.mktime(paivays.timetuple())
			uusipaivays = datetime.strptime(uusipaivays, aikamuoto)
			uusipaivays= time.mktime(uusipaivays.timetuple())
			# Lasketaan päiväysten aikaero
			aikaero = int(uusipaivays - paivays) / 60
			# Jos aikaero on alle 5h niin nostetaan väliaikaislaskuria, muuten nollataan
			if aikaero < 300:
				kayttajalista[nick][1] += 1
				maara = kayttajalista[nick][1]
				if maara > 3:
					# Vittuilua
					teksti = "%s avasi tölkin/pullon jo %d. kerran!" % (nick, maara)
					return bot.say(channel, teksti)
			else:
				kayttajalista[nick][1] = 0
			kayttajalista[nick][2] = time.strftime(aikamuoto)
			filu = open("tsips.txt", "w")
			teksti = ""
			for kayttaja in kayttajalista:
				teksti = teksti + "%s|%d|%d|%s\n" % (kayttaja, kayttajalista[kayttaja][0], kayttajalista[kayttaja][1], kayttajalista[kayttaja][2])
			filu.write(teksti)
			filu.close()
			return

def command_tsips(bot, user, channel, args):
	# .tsips kertoo käyttäjälle paljonko tämä on juopotellut
	# .tsips [nick] kertoo toisen nickin statsit
	""".tsips palauttaa kysyjän statsit. .tsips [nick] palauttaa annetun nickin statsit."""
	nick = getNick(user)
	if len(args) == 0:
		target = nick
	else:
		target = args
	
	try:
		kokmaara = kayttajalista[target][0]
	except KeyError:
		log.info("Käyttäjästä %s ei löytynyt tietoja" % target)
		teksti = "%s ei ole juopotellut vielä kertaakaan!" % target
		return bot.say(channel, teksti)
	valiaik = kayttajalista[target][1]
	kello = kayttajalista[target][2]
	teksti = "%s on avannut pullon tai tölkin %d kertaa kokonaisuudessaan! Viiden tunnin sisään hän on napsutellut %d kertaa. Viimeisin aukaisu tapahtui %s." % (target, kokmaara, valiaik, kello)
	log.info("Tiedot tongittu onnistuneesti")
	return bot.say(channel, teksti)
