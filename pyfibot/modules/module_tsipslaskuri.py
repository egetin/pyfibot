#-*- coding: utf-8 -*-

import logging

log = logging.getLogger("tsipslaskuri")

def init(bot):
	"""Tämä ajetaan aina kun botti käynnistetään tai rehashataan"""
	# Tähän pistetään filen käsittely - avaa siis tekstifilun ja lataa sen sisällön sanakirjaan
	pass

def handle_privmsg(bot, user, channel, msg):
	eventit = ["*tsips*", "*naks*", "*tsipsnaks*", "*raks*", "*blob*", "*tsih*"]
	for kohta in eventit:
		if kohta in msg:
			log.info("Käyttäjä %s avasi juoman" % user)
