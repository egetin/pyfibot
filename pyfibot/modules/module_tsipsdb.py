#-*- coding:utf-8 -*-

# Tsips-laskuri v2.0
# Tsipsit tallentuvat tietokantaan

from peewee import *
from datetime import datetime
import time, logging

# Konsoliin logittamista varten
log = logging.getLogger("tsipslaskuri")

# Avataan SQLite tietokanta
db = SqliteDatabase('/home/erkka/pyfibot/tsips.db', check_same_thread=False)
db.connect()

global aikamuoto
aikamuoto = "%d-%m-%Y %H:%M:%S"


"""Tämä ajetaan aina kun botti käynnistetään tai rehashataan"""

# Määritellään myöhemmille modeleille yhteinen tietokanta
class Yhteys(Model):
	class Meta:
		database = db

# Tässä modelissa pidetään yllä lähinnä irkkajat ja niiden statit yleensä
class Irkkaaja(Yhteys):
	id = PrimaryKeyField() 		# Jokaisen irkkajan oma id
	name = CharField() 		# Irkkajan nick
	kok_maara = IntegerField()	# Kokonaismäärä tsipsauksista
	temp_maara = IntegerField()	# Viimeisimmän putken tsippailut

# Tähän modeliin kerätään kaikki yksittäiset tsipsaukset
class Tsipsit(Yhteys):
	id = PrimaryKeyField()					# Tsipsauksen id
	user = ForeignKeyField(Irkkaaja, related_name='tsips')	# Tällä yhdistetään tsipsaus käyttäjään
	pvm = DateTimeField(aikamuoto)				# Ajankohta

# Luodaan taulut jos sellaisia ei ole, muuten jatketaan eteenpäin
try:
	Irkkaaja.create_table()
	Tsipsit.create_table()
except OperationalError:
	pass


def erolaskuri(aika, nick):
	""" Tämä funktio palauttaa joko ykkösen tai nollan - nolla jos aikaero on yli 5h ja muuten 1 """
	# Aika on samassa muodossa kuin aikamuoto-muuttujan formaatti
	# Konvertoidaan aikaleima sekunneiksi
	aika_sek = time.mktime(datetime.strptime(aika, aikamuoto).timetuple())
	# Otetaan nykyhetken sekunnit
	nykyhetki = time.time()
	#debug
	log.info("Aikaerolaskuri:")
	log.info("aika_sek: %d" % aika_sek)
	log.info("nykyhetki: %d" % nykyhetki)
	# Tarkistetaan onko 5h aikaeroa (5h = 18 000 sekuntia)
	if (nykyhetki - aika_sek) <= 18000:
		return 1
	else:
		return 0

# Viestien parsinta alkaa
def handle_privmsg(bot, user, channel, msg):
	msg = msg.lower()
	eventit = ["*tsips*", "*tsipsh*", "*naks*", "*naksh*", "*tsipsnaks*", "*raks*", "*blob*", "*tsih*", "*plops*", "*plob*", "*plop*", "*tsipis*"]
	for kohta in eventit: # Käydään event-listaus läpi jokaisen viestin kohdalla
		if kohta in msg: # Tarkistetaan löytyykö eventti viestistä
			# Otetaan tsipsauksen ajankohta talteen
			uusipaivays = time.strftime(aikamuoto)
			# Luodaan muuttuja tarkistamaan onko jouduttu lisäämään uusi käyttäjä (tarvitseeko putken jatkumista miettiä)
			log.info("*tsips* happened!")
			uusi = 0
			putki = 0 # Tällä liputetaan huudellaanko kanavalle lopuksi putkesta vai ei
			# Oksennetaan logiin tietoa
			log.info("Käyttäjä %s avasi juoman!" % user)
			# Otetaan nick hostnamesta talteen
			nick = user.split("!")[0]
			
			# Haetaan kyseisen nickin statsit tietokannasta:
			try:
				juoja = Irkkaaja.get(Irkkaaja.name == nick)
				tsipsit = juoja.tsips
				juoja.kok_maara += 1
				juoja.save()
				log.info("juoja.kok_maara = %d" % juoja.kok_maara)
			# Jos jantteria ei löydy vielä tietokannasta, lisätään hänet sinne
			except DoesNotExist:
				juoja = Irkkaaja.create(name=nick, kok_maara=1, temp_maara=1)
				uusi = 1
			
			if uusi == 0: # Jos ei ollut uusi käyttäjä niin tarkistellaan putkea
				# Haetaan tietokannasta viimeisimmän tsipsauksen aika
				for rivi in tsipsit.order_by(Tsipsit.id.desc()).limit(1):
					ed_aika = rivi.pvm
				# Tehdään mitä tehdään riippuen jatkuuko putki vai ei
				if erolaskuri(ed_aika, nick):
					juoja.temp_maara += 1
					log.info("juoja.temp_maara = %d" % juoja.temp_maara)
					juoja.save()
					if juoja.temp_maara > 3:
						teksti = "%s avasi tölkin/pullon jo %d. kerran!" % (juoja.name.encode("utf-8"), juoja.temp_maara)
						putki = 1
				else:
					juoja.temp_maara = 1
					juoja.save()
			
			# Luodaan uusi tsipsaus tietokantaan
			tsips_rivi = Tsipsit.create(user=juoja, pvm=time.strftime(aikamuoto))

			# Tarkisteaan huutelun tarve
			if putki == 1:
				return bot.say(channel, teksti)
			else:
				return

def command_tsips(bot, user, channel, args):
	# .tsips kertoo käyttäjälle omat statsit
	# .tsips[nick] kertoo toisen käyttäjän statsit
	""".tsips palauttaa kysyjän statsit. .tsips [nick] palauttaa annetun nickin statsit."""
	nick = getNick(user)
	if len(args) == 0:
		target = nick
	else:
		target = args
		target = target.strip()

	try:
		juomastatsit = Irkkaaja.get(Irkkaaja.name == target)
	except DoesNotExist:
		log.info("Käyttäjästä %s ei löytynyt tietoja" % target)
		teksti = "%s ei ole juopotellut vielä kertaakaan!" % target
		return bot.say(channel, teksti)

	nykyaika = time.strftime(aikamuoto)
	tsipsit = juomastatsit.tsips
	# Haetaan viimeisimmän tsipsin aika
	for rivi in tsipsit.order_by(Tsipsit.id.desc()).limit(1):
		tsips_aika = rivi.pvm
	
	putki = erolaskuri(tsips_aika, target)	
	if putki:
		teksti = "%s on avannut pullon tai tölkin %d kertaa! Tähän putkeen hän on napsutellut %d kertaa. Viimeisin aukaisu tapahtui %s." % (target.encode("utf-8"), juomastatsit.kok_maara, juomastatsit.temp_maara, tsips_aika.encode("utf-8"))
	else:	
		teksti = "%s on avannut pullon tai tölkin %d kertaa! Viimeisin putki kesti %d juomaa ja viimeisin aukaisu tapahtui %s." % (target.encode("utf-8"), juomastatsit.kok_maara, juomastatsit.temp_maara, tsips_aika.encode("utf-8"))
	
	log.info("Tiedot tongittu onnistuneesti")
	return bot.say(channel, teksti)

def command_addtsips(bot, user, channel, args):
	# .addtsips lisää käyttäjälle annetun määrän tsipsejä
	# .addtsips [nick] [lkm]
	""".addtsips [nick] [lkm] lisää annetulle käyttäjälle syötetyn määrän verran tsipsejä."""
	nick = getNick(user)
	try:
		target, lkm = args.split()
	except:
		args = args.split()
		target = args[0]
		lkm = args[1]
	log.info(args)
	log.info("Nick: %s" % target)
	log.info("Lkm: %s" % lkm)
	if nick == "eGetin":
		try:
			juoja = Irkkaaja.get(Irkkaaja.name == target)
		except DoesNotExist:
			juoja = Irkkaaja.create(name=target, kok_maara=0, temp_maara=1)
			Tsipsit.create(user=juoja, pvm=time.strftime(aikamuoto))
		
		juoja.kok_maara += int(lkm)
		juoja.save()
		
		return bot.say(channel, "%d juomaa lisätty käyttäjälle %s" % (int(lkm), target))
	else:
		return bot.say(channel, "Et ole oikeutettu aiheuttamaan ihmisille maksakirroosia!")
