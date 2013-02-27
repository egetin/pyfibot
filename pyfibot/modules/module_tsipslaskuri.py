#-*- coding: utf-8 -*-

import logging

log = logging.getLogger("tsipslaskuri")

def init(bot):
	"""Tämä ajetaan aina kun botti käynnistetään tai rehashataan"""
	# Tähän pistetään filen käsittely - avaa siis tekstifilun ja lataa sen sisällön sanakirjaan
	pass

def handle_privmsg(bot, user, channel, msg):
	if ("*tsips*" or "*naks*" or "*tsipsnaks*" or "*raks*" or "*blob*" or "*tsih*") in msg:
		log.info("Käyttäjä %s avasi juoman" % user)
