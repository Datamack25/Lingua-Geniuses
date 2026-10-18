"""
Génère tous les CSV de contenu pédagogique de LinguaPilot.
Usage : python scripts/build_content.py
Les CSV sont écrits dans data/content/. Vous pouvez ensuite les enrichir à la main
(Excel, Google Sheets) : l'application relit les CSV à chaque démarrage.

Note droits d'auteur : les chansons sont référencées (titre, artiste, thèmes,
activités originales) avec des liens vers des plateformes licenciées ; aucune
parole n'est reproduite dans ce dépôt.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "content"
OUT.mkdir(parents=True, exist_ok=True)

LANGS = {"en": "Anglais", "fr": "Français", "ht": "Créole haïtien", "es": "Espagnol"}

# --------------------------------------------------------------------------
# 1. BANQUE DE QUESTIONS  (niveau, compétence, question, options, réponse, explication)
#    compétences : grammaire | vocabulaire | comprehension | registre | culture
#    la bonne réponse est toujours la 1re option (mélangée à l'affichage)
# --------------------------------------------------------------------------
Q = {
"en": [
 ("A1","grammaire","She ___ a teacher.",["is","are","am","be"],"Le verbe 'to be' à la 3e personne du singulier est 'is'."),
 ("A1","vocabulaire","What is the opposite of 'cold'?",["hot","wet","old","slow"],"'Hot' (chaud) est le contraire de 'cold' (froid)."),
 ("A1","grammaire","I ___ coffee every morning.",["drink","drinks","drinking","drunk"],"Présent simple, 1re personne : pas de -s."),
 ("A1","comprehension","Tom has a dog. The dog is brown. — What colour is the dog?",["Brown","Black","White","Grey"],"Le texte dit : 'The dog is brown'."),
 ("A2","grammaire","Yesterday we ___ to the cinema.",["went","go","gone","going"],"'Yesterday' → prétérit ; 'go' est irrégulier : went."),
 ("A2","grammaire","There isn't ___ milk left.",["any","some","many","a"],"Dans une phrase négative, on utilise 'any'."),
 ("A2","registre","Which request is the most polite?",["Could I have some water, please?","Give me water.","Water now.","I want water."],"'Could I…, please?' est la formule de politesse standard."),
 ("A2","vocabulaire","A place where you borrow books is a…",["library","bookshop","bakery","museum"],"Faux ami : 'library' = bibliothèque, 'bookshop' = librairie."),
 ("B1","grammaire","If it rains tomorrow, we ___ at home.",["will stay","would stay","stayed","stay"],"Premier conditionnel : if + présent → will + base verbale."),
 ("B1","grammaire","I've lived here ___ 2019.",["since","for","from","during"],"'Since' + point de départ ; 'for' + durée."),
 ("B1","registre","Which is the most informal way to say 'I am very tired'? (UK)",["I'm knackered.","I am exhausted.","I feel fatigued.","I am experiencing fatigue."],"'Knackered' est un mot familier britannique."),
 ("B1","culture","In the United States, Thanksgiving is celebrated in…",["November","July","December","March"],"Le 4e jeudi de novembre."),
 ("B2","grammaire","By the time we arrived, the film ___.",["had started","has started","started","was starting"],"Antériorité dans le passé → past perfect."),
 ("B2","grammaire","She suggested ___ earlier.",["leaving","to leave","leave","we leaving"],"'Suggest' + verbe en -ing (ou 'that we leave')."),
 ("B2","registre","Best closing for a formal business email:",["Kind regards,","Cheers mate,","Later!","Love,"],"'Kind regards' est neutre et professionnel."),
 ("B2","vocabulaire","'To postpone' means…",["to delay to a later time","to cancel","to bring forward","to announce"],"Postpone = reporter."),
 ("C1","grammaire","Not only ___ late, but he also forgot the documents.",["did he arrive","he arrived","he did arrive","arrived he"],"Après 'Not only' en tête de phrase : inversion sujet-auxiliaire."),
 ("C1","grammaire","Hardly had she sat down ___ the phone rang.",["when","than","then","that"],"Structure figée : Hardly… when (No sooner… than)."),
 ("C1","vocabulaire","The report ___ the need for urgent reform.",["underscores","undermines","understates","undergoes"],"'Underscore' = souligner, mettre en évidence."),
 ("C1","culture","The 'I Have a Dream' speech (1963) was delivered by…",["Martin Luther King Jr.","John F. Kennedy","Abraham Lincoln","Barack Obama"],"Discours prononcé lors de la Marche sur Washington, 28 août 1963."),
 ("C2","grammaire","His argument, ___ compelling, failed to persuade the committee.",["albeit","despite","however","although of"],"'Albeit' (quoique) introduit une concession sans verbe conjugué."),
 ("C2","vocabulaire","'To pay lip service to something' means…",["to express support without acting on it","to speak loudly","to pay a fee","to sing in public"],"Soutenir en paroles seulement."),
 ("C2","grammaire","Choose the correct formal subjunctive:",["It is essential that he be informed.","It is essential that he will be informed.","It is essential that he being informed.","It is essential that he to be informed."],"Subjonctif 'mandatif' : base verbale après 'essential that'."),
 ("C2","culture","'Ask not what your country can do for you…' — which president?",["John F. Kennedy","Franklin D. Roosevelt","Ronald Reagan","Bill Clinton"],"Discours d'investiture de JFK, 20 janvier 1961."),
 ("B1","comprehension","'I'm running late, start without me.' — What does the speaker mean?",["They will arrive late","They are jogging","They are not coming","They are early"],"'Running late' = être en retard."),
 ("B2","comprehension","'The meeting has been pushed back to Friday.' — The meeting is now…",["later, on Friday","earlier, on Friday","cancelled","on Monday"],"'Push back' = repousser à plus tard."),
],
"fr": [
 ("A1","grammaire","Je ___ étudiante.",["suis","es","est","sommes"],"Être, 1re personne du singulier : je suis."),
 ("A1","vocabulaire","Le contraire de « grand » est…",["petit","gros","long","haut"],"Grand ≠ petit."),
 ("A1","grammaire","Nous ___ du pain.",["mangeons","mangez","mange","mangent"],"Verbes en -ger : nous mangeons (le e garde le son [ʒ])."),
 ("A1","comprehension","« Marie habite à Lyon avec son chat. » — Où habite Marie ?",["À Lyon","À Paris","À Marseille","À Lille"],"Le texte dit : à Lyon."),
 ("A2","grammaire","Hier, je ___ au marché.",["suis allé(e)","vais","irai","allais"],"Action ponctuelle passée → passé composé avec être."),
 ("A2","grammaire","Je parle à Paul. → Je ___ parle.",["lui","le","leur","y"],"Parler À quelqu'un → COI singulier : lui."),
 ("A2","registre","Quelle est la façon la plus polie de demander l'heure ?",["Excusez-moi, auriez-vous l'heure ?","T'as l'heure ?","L'heure !","Il est quelle heure ?"],"Vouvoiement + conditionnel de politesse."),
 ("A2","vocabulaire","Où achète-t-on du pain ?",["À la boulangerie","À la pharmacie","À la librairie","À la poste"],"Boulangerie = pain ; librairie = livres."),
 ("B1","grammaire","Si j'avais le temps, je ___ plus.",["lirais","lirai","lis","lisais"],"Si + imparfait → conditionnel présent."),
 ("B1","grammaire","Il faut que tu ___ tes devoirs.",["fasses","fais","feras","faisais"],"« Il faut que » + subjonctif."),
 ("B1","registre","Quelle phrase relève du registre familier ?",["J'ai la flemme.","Je manque d'entrain.","Je suis peu motivé.","Je ne le souhaite guère."],"« Avoir la flemme » est familier."),
 ("B1","culture","Le 14 juillet commémore notamment…",["la prise de la Bastille (1789)","la fin de la Seconde Guerre mondiale","la naissance de Napoléon","l'abolition de l'esclavage"],"Fête nationale : prise de la Bastille et Fête de la Fédération (1790)."),
 ("B2","grammaire","Bien qu'il ___ fatigué, il a continué.",["soit","est","était","sera"],"« Bien que » + subjonctif."),
 ("B2","grammaire","Les lettres que j'ai ___ sont parties.",["écrites","écrit","écrits","écrite"],"COD placé avant avoir (que = les lettres) → accord féminin pluriel."),
 ("B2","registre","Formule de clôture d'une lettre administrative :",["Je vous prie d'agréer, Madame, l'expression de mes salutations distinguées.","Bisous !","À plus.","Ciao, bonne journée."],"Formule de politesse soutenue standard."),
 ("B2","vocabulaire","« Entériner une décision » signifie…",["la valider officiellement","l'annuler","la reporter","la critiquer"],"Entériner = ratifier, rendre valable."),
 ("C1","grammaire","Quoi qu'il ___, nous partirons.",["advienne","advient","adviendra","advenait"],"« Quoi que » + subjonctif."),
 ("C1","grammaire","Elle s'est ___ compte de son erreur.",["rendu","rendue","rendus","rendre"],"Dans « se rendre compte », compte est le COD placé après : pas d'accord."),
 ("C1","registre","Quel mot appartient au registre soutenu ?",["nonobstant","bouquin","boulot","genre"],"« Nonobstant » = malgré, langue juridique/soutenue."),
 ("C1","culture","Qui a défendu le projet de loi sur l'IVG à l'Assemblée nationale en 1974 ?",["Simone Veil","Gisèle Halimi","Simone de Beauvoir","Françoise Giroud"],"Discours de Simone Veil, 26 novembre 1974."),
 ("C2","vocabulaire","« Faire long feu » signifie…",["échouer, rater son effet","durer longtemps","se mettre en colère","réussir brillamment"],"Piège classique : à l'origine, une charge qui part mal ; donc échouer."),
 ("C2","grammaire","Les heures que j'ai ___ dormir…",["pu","pues","pus","pue"],"Participe passé suivi d'un infinitif sous-entendu : invariable."),
 ("C2","grammaire","Passé simple de « naître », 3e personne du singulier :",["naquit","naissa","naît","nacquit"],"Il naquit."),
 ("C2","culture","« J'accuse…! » (1898), lettre au président de la République, est signée…",["Émile Zola","Victor Hugo","Jean Jaurès","Anatole France"],"Publiée dans L'Aurore pendant l'affaire Dreyfus."),
 ("B1","comprehension","« Je suis à la bourre, commencez sans moi. » — La personne…",["est en retard","est fatiguée","est malade","est déjà arrivée"],"« Être à la bourre » (familier) = être en retard."),
 ("B2","comprehension","« La réunion est reportée à vendredi. » — La réunion aura lieu…",["plus tard, vendredi","plus tôt","jamais","lundi"],"Reporter = remettre à plus tard."),
],
"es": [
 ("A1","grammaire","Yo ___ estudiante.",["soy","estoy","es","eres"],"Identidad/profesión → ser : yo soy."),
 ("A1","vocabulaire","El contrario de « alto » es…",["bajo","gordo","largo","viejo"],"Alto ≠ bajo."),
 ("A1","grammaire","Nosotros ___ en Madrid.",["vivimos","viven","vivís","vivo"],"Vivir, 1.ª persona del plural : vivimos."),
 ("A1","comprehension","« Ana tiene dos hermanos. » — ¿Cuántos hermanos tiene Ana?",["Dos","Uno","Tres","Ninguno"],"El texto dice : dos."),
 ("A2","grammaire","Ayer ___ al cine.",["fui","voy","iré","iba"],"Acción puntual pasada → pretérito indefinido : fui."),
 ("A2","grammaire","¿Dónde ___ el museo?",["está","es","hay","son"],"Localización de algo concreto → estar."),
 ("A2","registre","¿Cuál es la petición más cortés?",["¿Podría traerme la cuenta, por favor?","¡La cuenta!","Dame la cuenta.","Quiero la cuenta."],"Condicional de cortesía + usted."),
 ("A2","vocabulaire","Lugar donde se compran medicinas :",["la farmacia","la panadería","la librería","el mercado"],"Farmacia = pharmacie."),
 ("B1","grammaire","Si tengo tiempo, te ___.",["llamaré","llamaría","llamara","llamé"],"Si + presente → futuro."),
 ("B1","grammaire","Espero que ___ bien.",["estés","estás","estarás","estabas"],"Esperar que + subjuntivo."),
 ("B1","registre","¿Qué expresión es coloquial (España)?",["¡Qué guay!","¡Excelente!","¡Magnífico!","¡Extraordinario!"],"« Guay » = génial, registro coloquial."),
 ("B1","culture","El Día de Muertos se celebra sobre todo en…",["México","Argentina","España","Chile"],"Patrimonio cultural inmaterial (UNESCO, 2008)."),
 ("B2","grammaire","Si hubiera estudiado, ___ aprobado.",["habría","había","hubo","haya"],"Irreal del pasado : pluscuamperfecto de subjuntivo → condicional compuesto."),
 ("B2","grammaire","Busco un piso que ___ terraza.",["tenga","tiene","tendrá","tenía"],"Antecedente desconocido → subjuntivo."),
 ("B2","registre","Cierre adecuado de un correo formal :",["Atentamente,","¡Chao!","Besos,","Nos vemos,"],"« Atentamente » es la fórmula estándar."),
 ("B2","vocabulaire","« Aplazar » significa…",["posponer","cancelar","adelantar","anunciar"],"Aplazar = reporter."),
 ("C1","grammaire","Por mucho que ___, no lo convencerás.",["insistas","insistes","insistirás","insistías"],"« Por mucho que » + subjuntivo (valor concesivo)."),
 ("C1","grammaire","No es que no ___, es que no puedo.",["quiera","quiero","querré","quise"],"« No es que » + subjuntivo."),
 ("C1","registre","¿Qué palabra pertenece al registro culto?",["empero","curro","tío","guay"],"« Empero » = sin embargo (culto, literario)."),
 ("C1","culture","¿Quién escribió « Cien años de soledad »?",["Gabriel García Márquez","Mario Vargas Llosa","Julio Cortázar","Pablo Neruda"],"Novela publicada en 1967."),
 ("C2","vocabulaire","« Dar gato por liebre » significa…",["engañar","regalar un animal","correr deprisa","cocinar mal"],"Faire passer une chose de moindre valeur pour une meilleure."),
 ("C2","vocabulaire","« Sea como fuere » expresa…",["en cualquier caso","sin duda","por casualidad","al final"],"Locución concesiva culta."),
 ("C2","grammaire","¿Qué forma es futuro de subjuntivo (textos jurídicos)?",["infringiere","infrinja","infringía","infringirá"],"El futuro de subjuntivo sobrevive en leyes y refranes."),
 ("C2","culture","¿Quién es el autor de « Don Quijote de la Mancha »?",["Miguel de Cervantes","Lope de Vega","Francisco de Quevedo","Calderón de la Barca"],"Publicado en 1605 y 1615."),
 ("B1","comprehension","« Voy con retraso, empezad sin mí. » — La persona…",["llegará tarde","está enferma","no vendrá","ya llegó"],"Ir con retraso = llegar tarde."),
 ("B2","comprehension","« La reunión se ha aplazado al viernes. » — La reunión será…",["más tarde, el viernes","antes","nunca","el lunes"],"Aplazar = posponer."),
],
"ht": [
 ("A1","grammaire","Mwen ___ Ayiti. (Je viens d'Haïti.)",["soti","manje","dòmi","bwè"],"Soti = venir de."),
 ("A1","vocabulaire","« Kijan ou rele ? » veut dire…",["Comment t'appelles-tu ?","Où habites-tu ?","Quel âge as-tu ?","Comment vas-tu ?"],"Rele = s'appeler."),
 ("A1","vocabulaire","« Kòman ou ye ? » veut dire…",["Comment vas-tu ?","Comment t'appelles-tu ?","Où vas-tu ?","Que fais-tu ?"],"Réponse possible : M byen, mèsi."),
 ("A1","comprehension","« Jan gen yon chen nwa. » — Ki koulè chen an ?",["Nwa","Blan","Wouj","Ble"],"Nwa = noir."),
 ("A2","grammaire","Yè mwen ___ ale lekòl. (Hier je suis allé à l'école.)",["te","ap","pral","fin"],"« Te » marque le passé."),
 ("A2","grammaire","Demen mwen ___ travay. (Demain je vais travailler.)",["pral","te","fin","t ap"],"« Pral » (pra, prale) = futur proche."),
 ("A2","registre","Quelle demande est la plus polie ?",["Souple, ban m yon ti dlo.","Ban m dlo !","Dlo !","M vle dlo."],"« Souple » = s'il vous plaît ; « yon ti » adoucit."),
 ("A2","vocabulaire","« Liv yo » signifie…",["les livres","le livre","un livre","mon livre"],"« Yo » après le nom marque le pluriel défini."),
 ("B1","grammaire","Kounye a m ___ manje. (En ce moment je mange.)",["ap","te","pral","ta"],"« Ap » marque le progressif."),
 ("B1","grammaire","Choisissez le déterminant correct : « chat ___ » (le chat)",["la","a","an","nan"],"Après une consonne orale : « la »."),
 ("B1","registre","Réponse naturelle et familière à « Sak pase ? »",["N ap boule !","Mèsi madanm.","Bonswa msye.","Wi, souple."],"« Sak pase ? — N ap boule » : salutation familière très courante."),
 ("B1","culture","Haïti a proclamé son indépendance le…",["1er janvier 1804","14 juillet 1789","4 juillet 1776","18 mai 1803"],"Première république noire indépendante."),
 ("B2","grammaire","Quel marqueur exprime le conditionnel ? « Si m te gen lajan, m ___ achte yon machin. »",["ta","te","ap","pral"],"« Ta » = conditionnel."),
 ("B2","vocabulaire","« Piti piti zwazo fè nich li » signifie…",["La patience mène au but","Les oiseaux sont petits","Il faut partir tôt","Chacun chez soi"],"Proverbe : petit à petit l'oiseau fait son nid."),
 ("B2","registre","Pour s'adresser poliment à un supérieur :",["Eskize m, mesye, èske m ka pale avè w ?","Ey, vin la !","Gade m non !","Sa w genyen ?"],"« Eskize m » + « mesye/madam » + question en « èske »."),
 ("B2","grammaire","Choisissez le déterminant correct : « papa ___ » (le père)",["a","la","an","nan"],"Après une voyelle orale : « a »."),
 ("C1","culture","Le créole haïtien est langue officielle d'Haïti (avec le français) depuis la Constitution de…",["1987","1804","1946","2010"],"Article 5 de la Constitution de 1987."),
 ("C1","vocabulaire","« Dèyè mòn gen mòn » signifie…",["Après une difficulté, une autre se présente","Il y a des montagnes partout","Il faut grimper","La vue est belle"],"Proverbe : derrière les montagnes, il y a des montagnes."),
 ("C1","culture","Dans les contes haïtiens, le personnage rusé face à Bouki est…",["Ti Malis","Konpè Lapen","Tonton Nwèl","Zanmi Lou"],"Bouki (naïf) et Ti Malis (rusé) sont des figures centrales de l'oralité."),
 ("C1","grammaire","Choisissez le déterminant correct : « machin ___ » (la voiture)",["nan","la","a","an"],"Après une voyelle nasale finale : « nan »."),
 ("C2","vocabulaire","« Pale franse pa di lespri pou sa » signifie…",["Parler français ne prouve pas qu'on est intelligent","Il faut parler français","Le français est difficile","L'esprit parle français"],"Proverbe sur le prestige linguistique."),
 ("C2","culture","Un « konbit » est…",["un travail collectif solidaire","un plat traditionnel","une danse","un marché"],"Tradition d'entraide agricole, valeur centrale de la culture haïtienne."),
 ("C2","culture","Où l'indépendance d'Haïti a-t-elle été proclamée ?",["Aux Gonaïves","À Port-au-Prince","Au Cap-Haïtien","À Jacmel"],"Par Jean-Jacques Dessalines, le 1er janvier 1804."),
 ("C2","registre","Quel mot relève d'un créole plus soutenu / écrit ?",["Konsènan (concernant)","Ey","Sak pase","Bagay la"],"Dans les textes officiels et la presse, on trouve des connecteurs comme « konsènan »."),
 ("B1","comprehension","« M an reta, kòmanse san mwen. » — La personne…",["est en retard","est malade","est déjà là","ne viendra pas"],"An reta = en retard."),
 ("B2","comprehension","« Reyinyon an ranvwaye pou vandredi. » — La réunion…",["est repoussée à vendredi","est annulée","a lieu aujourd'hui","est avancée"],"Ranvwaye = repousser, reporter."),
],
}

# --------------------------------------------------------------------------
# 1 bis. ENRICHISSEMENT — priorité au créole haïtien et aux niveaux C1-C2
#   6e champ = source / référentiel. Pour le kreyòl, la référence est
#   l'Akademi Kreyòl Ayisyen (AKA, loi du 7 avril 2014) et l'orthographe officielle
#   de 1980 (32 graphèmes, 1 son = 1 graphie, aucune lettre muette), confirmée par
#   la « Premye rezolisyon sou òtograf kreyòl ayisyen an » (AKA, juin 2017).
# --------------------------------------------------------------------------
OTO = "Òtograf ofisyèl 1980 / AKA"
AKA = "Akademi Kreyòl Ayisyen"
Q_EXTRA = {
"ht": [
 ("A1","vocabulaire","« Mèsi » veut dire…",["merci","bonjour","au revoir","pardon"],"Mèsi = merci ; « mèsi anpil » = merci beaucoup.",""),
 ("A1","vocabulaire","Comment dit-on « personne, gens » en kreyòl ?",["moun","zanmi","kay","liv"],"« moun » s'écrit avec le trigramme « oun », l'un des 32 graphèmes officiels.",OTO),
 ("A1","grammaire","Comment dit-on « Il est malade » ?",["Li malad.","Li se malad.","Li ye malad.","Li te se malad."],"Devant un adjectif, pas de copule : « Li malad ». « Se » s'emploie devant un nom (« Li se doktè »).",""),
 ("A1","comprehension","« Kote w rete ? » veut dire…",["Où habites-tu ?","Quand pars-tu ?","Comment vas-tu ?","Qui es-tu ?"],"Rete = habiter, rester ; « w » est la forme courte de « ou ».",""),
 ("A2","grammaire","Comment dit-on « Je ne sais pas » ?",["M pa konnen.","M konnen pa.","Pa m konnen.","M pa t konnen."],"« pa » se place avant le verbe. « M pa t konnen » = je ne savais pas.",""),
 ("A2","grammaire","Pluriel de « liv la » (le livre) :",["liv yo","liv las","yo liv","liv lan yo"],"Le déterminant pluriel « yo » remplace « la » après le nom.",""),
 ("A2","vocabulaire","Le nombre 8 s'écrit…",["uit","wit","huit","ouit"],"Le graphème « ui » fait partie des 8 voyelles orales officielles (a, e, è, i, o, ò, ou, ui).",OTO),
 ("A2","registre","Salutation polie de l'après-midi ou du soir :",["Bonswa, madam.","Sak pase, chè ?","Ey !","N ap boule."],"« Bonswa » s'utilise dès le début de l'après-midi ; « madam / mesye » marquent le respect.",""),
 ("A2","culture","Quel plat est servi le 1er janvier pour célébrer l'indépendance ?",["Soup joumou","Diri ak pwa","Griyo","Akra"],"La soup joumou, symbole de liberté, est inscrite au patrimoine immatériel de l'UNESCO (2021).",""),
 ("B1","grammaire","« Mwen konn manje mango » exprime…",["une habitude","un futur","une action en cours","une obligation"],"« konn » (konnen) devant un verbe = aspect habituel : j'ai l'habitude de manger des mangues.",""),
 ("B1","grammaire","« M sot manje » signifie…",["Je viens de manger","Je vais manger","Je suis en train de manger","Je mangerais"],"« sot » (soti) = passé récent.",""),
 ("B1","grammaire","Déterminant correct : « chen ___ » (le chien)",["an","la","a","nan"],"Après une voyelle nasale finale (« en ») : « an ».",""),
 ("B1","grammaire","Déterminant correct : « fanm ___ » (la femme)",["nan","la","a","an"],"Après une consonne nasale (m, n) : « nan ».",""),
 ("B1","vocabulaire","Combien de graphèmes compte l'alphabet officiel du kreyòl ayisyen ?",["32","26","24","40"],"12 voyelles, 18 consonnes et 2 semi-voyelles (w, y) : 32 graphèmes.",OTO),
 ("B1","comprehension","« Pa gen pwoblèm, m ap vini demen. » — La personne…",["viendra demain","est venue hier","ne viendra pas","a un problème"],"« ap » + demen = futur ; « pa gen pwoblèm » = pas de problème.",""),
 ("B1","registre","Pour demander poliment son chemin à un inconnu :",["Eskize m, èske w ka di m kote lopital la ye ?","Ey, kote lopital la ?","Lopital la, kote ?","Di m kote lopital la !"],"« Eskize m » + question en « èske » = formule polie.",""),
 ("B2","grammaire","« Si m te konnen, m t ap vini. » exprime…",["un irréel du passé (je serais venu)","un futur certain","une habitude","un ordre"],"« te » dans la subordonnée + « t ap » dans la principale = conditionnel passé.",""),
 ("B2","grammaire","Négation correcte de « M te ale » (j'étais allé) :",["M pa t ale.","M te pa ale.","Pa m te ale.","M ale pa."],"« pa » précède toujours les marqueurs (te → t).",""),
 ("B2","grammaire","Quelle graphie est conforme à l'orthographe officielle ?",["lekòl","lécol","lekol","lecòl"],"Pas de « é » ni de « c » dans l'alphabet ; « ò » note le o ouvert.",OTO),
 ("B2","grammaire","Pourquoi écrit-on « pèn » (peine) avec un accent grave ?",["Pour le distinguer de « pen » (pain), où « en » est une voyelle nasale","Par tradition française","Pour marquer l'accent tonique","C'est facultatif"],"Sans accent, « en » est une nasale ; « èn » se lit è + n. Un graphème = un son.",OTO),
 ("B2","vocabulaire","« Tèt ansanm » signifie…",["solidarité, union","mal de tête","réunion de famille","fête nationale"],"Littéralement « têtes ensemble » : l'union qui fait la force.",""),
 ("B2","culture","Quel article de la Constitution de 1987 prévoit la création d'une Académie du créole ?",["Article 213","Article 5","Article 1","Article 24"],"L'article 213 annonce l'Académie ; l'article 5 fait du kreyòl la langue commune et officielle.","Konstitisyon 1987"),
 ("B2","comprehension","« Malgre lapli a, yo kontinye travay. » — Que s'est-il passé ?",["Ils ont continué à travailler malgré la pluie","Ils ont arrêté à cause de la pluie","Il n'a pas plu","Ils ont travaillé au soleil"],"Malgre = malgré ; kontinye = continuer.",""),
 ("B2","registre","Formule de clôture adaptée à un courriel professionnel en kreyòl :",["Mèsi davans, ak tout respè m.","N a wè, monchè !","Ciao !","Bon, m ale."],"« Mèsi davans » (merci d'avance) et « respè » relèvent du registre professionnel.",""),
 ("C1","culture","La loi portant création de l'Akademi Kreyòl Ayisyen date de…",["2014","1987","1979","2017"],"Loi du 7 avril 2014 ; l'Académie est installée en décembre 2014.",AKA),
 ("C1","culture","Selon la loi, l'AKA compte…",["entre 33 et 55 akademisyen","exactement 12 membres","entre 100 et 200 membres","un membre par département"],"Article 21 de la loi : 33 à 55 membres, titre honorifique et non rémunéré.",AKA),
 ("C1","culture","Laquelle est une mission de l'AKA fixée par la loi ?",["Garantir les droits linguistiques des Haïtiens et établir des normes pour le kreyòl","Remplacer le français dans la Caraïbe","Gérer les écoles privées","Organiser les élections"],"Elle est la référence du kreyòl oral et écrit et émet des recommandations orthographiques.",AKA),
 ("C1","culture","En juin 2017, l'AKA a publié…",["sa première résolution sur l'orthographe du kreyòl","la première Constitution en kreyòl","un dictionnaire anglais-kreyòl","une loi sur l'éducation"],"« Premye rezolisyon sou òtograf kreyòl ayisyen an » ; une deuxième résolution a suivi en 2023.",AKA),
 ("C1","grammaire","« Se manje li manje. » (clivage du prédicat) met l'accent sur…",["l'action elle-même : il a bel et bien mangé / il n'a fait que manger","le sujet","le lieu","le futur"],"La reprise du verbe après « se » focalise le procès — trait typique de la syntaxe du kreyòl.",""),
 ("C1","grammaire","« Se Mari ki te rele w. » signifie…",["C'est Marie qui t'a appelé.","Marie t'appellera.","Marie s'appelle comme toi.","Appelle Marie."],"Mise en relief « se … ki » + passé « te ».",""),
 ("C1","grammaire","Graphie standard de « je suis en train de manger » :",["M ap manje.","M'ap manjé.","Map manger.","Mwen apé manjé."],"Le « é » n'existe pas dans l'alphabet officiel ; le pronom court « m » s'écrit séparé du marqueur « ap ».",OTO),
 ("C1","vocabulaire","« Pàn » (avec accent grave) signifie…",["panne","paon","pain","peine"],"« àn » se lit a + n (pàn = panne), tandis que « an » est nasal (pan = paon).",OTO),
 ("C1","comprehension","« Lang kreyòl la se yon zouti tout Ayisyen pataje ; se poutèt sa, administrasyon piblik la dwe kominike ak pèp la nan lang li konprann nan. » — Idée principale :",["L'administration doit communiquer avec la population en kreyòl, langue commune","Le kreyòl est une langue étrangère","L'administration doit utiliser l'anglais","La population ne comprend pas le kreyòl"],"Se poutèt sa = c'est pourquoi ; dwe = devoir. Idée conforme à la mission de l'AKA.",""),
 ("C2","culture","Premier roman écrit entièrement en kreyòl ayisyen (1975) :",["Dezafi, de Frankétienne","Gouverneurs de la rosée, de Jacques Roumain","Compère Général Soleil, de J. S. Alexis","Choucoune, d'Oswald Durand"],"Dezafi (1975) ; les autres œuvres citées sont en français (Choucoune est un poème).",""),
 ("C2","culture","Félix Morisseau-Leroy est célèbre pour son adaptation en kreyòl de…",["Antigòn (Antigone de Sophocle)","Hamlet","Le Cid","Don Quichotte"],"Antigòn (1953), jalon du théâtre en kreyòl.",""),
 ("C2","grammaire","Selon les principes de l'orthographe officielle, quelle affirmation est vraie ?",["Chaque graphème se prononce toujours de la même façon et aucune lettre n'est muette","Certaines lettres finales sont muettes comme en français","On écrit selon l'étymologie française","Le « h » est toujours muet"],"Trois principes : un son = une graphie, une graphie = un son, pas de lettre muette.",OTO),
 ("C2","vocabulaire","Quel mot contient le trigramme « oun » ?",["moun","mouton","mont","boul"],"« oun » (moun, youn) est l'un des deux graphèmes à plusieurs lettres avec « ng ».",OTO),
 ("C2","grammaire","« Li bèl bèl » (redoublement de l'adjectif) signifie…",["Elle est vraiment très belle","Elle est deux fois belle","Elle était belle","Elle sera belle"],"Le redoublement exprime l'intensité.",""),
 ("C2","registre","Quel connecteur appartient au kreyòl écrit argumentatif ?",["Sepandan","Ey","Monchè","Anfòm"],"Sepandan = cependant ; s'emploie dans la presse, les essais et les textes officiels.",""),
 ("C2","comprehension","Proverbe « Bourik travay, chwal galonnen » : sens ?",["Les uns travaillent, d'autres en récoltent les honneurs","Le cheval travaille plus que l'âne","Il faut soigner ses animaux","Le travail paie toujours"],"Littéralement : l'âne travaille, le cheval porte les galons.",""),
],
"en": [
 ("C1","grammaire","Seldom ___ such dedication.",["have I seen","I have seen","I saw","did I saw"],"Adverbe négatif en tête (seldom, rarely) → inversion.",""),
 ("C1","grammaire","Were I in your position, I ___ the offer.",["would accept","will accept","accepted","accept"],"Inversion conditionnelle formelle (= If I were…).",""),
 ("C1","vocabulaire","'To be on the fence' means…",["to be undecided","to be in danger","to be outside","to be bored"],"Ne pas avoir pris parti.",""),
 ("C1","registre","Most appropriate wording for a formal report: 'The results ___ that…'",["indicate","kinda show","show off","tell us, like,"],"Verbe neutre et précis, sans marques d'oralité.",""),
 ("C1","comprehension","'The proposal was shelved.' — The proposal was…",["postponed indefinitely","approved","put on display","rewritten"],"To shelve = mettre de côté, reporter sine die.",""),
 ("C2","vocabulaire","A 'Pyrrhic victory' is…",["a victory won at too great a cost","an easy victory","a shared victory","a legal victory"],"Du roi Pyrrhus d'Épire.",""),
 ("C2","vocabulaire","'Notwithstanding' is closest in meaning to…",["despite","because of","in addition to","instead of"],"Registre juridique / soutenu.",""),
 ("C2","culture","'We shall fight on the beaches' (1940) was delivered by…",["Winston Churchill","Neville Chamberlain","Franklin D. Roosevelt","Clement Attlee"],"Discours à la Chambre des communes, 4 juin 1940.",""),
 ("C2","registre","Which sentence suits a legal contract?",["The Supplier shall deliver the goods within thirty (30) days.","The Supplier's gonna deliver in a month.","Supplier will try to deliver soon.","Goods coming in 30 days, hopefully."],"« shall » d'obligation, termes définis, chiffres en lettres.",""),
 ("C2","comprehension","'Her remarks were nothing if not candid.' — Her remarks were…",["extremely frank","not frank at all","rude","unclear"],"« nothing if not » = extrêmement.",""),
],
"fr": [
 ("C1","grammaire","Je doute qu'il ___ raison.",["ait","a","aura","avait"],"Douter que + subjonctif.",""),
 ("C1","vocabulaire","« Être aux abois » signifie…",["être dans une situation désespérée","aboyer","être très heureux","être en avance"],"Image du cerf encerclé par la meute.",""),
 ("C1","registre","Formule adaptée pour solliciter un entretien :",["Je me permets de solliciter un entretien afin de vous présenter ma candidature.","J'veux vous voir vite fait.","Faut qu'on cause.","Donnez-moi un rendez-vous."],"Registre professionnel : formule de politesse + objet clair.",""),
 ("C1","comprehension","« La mesure a été entérinée sans coup férir. » — Elle a été…",["validée sans difficulté","rejetée violemment","reportée","contestée"],"Sans coup férir = sans rencontrer de résistance.",""),
 ("C2","grammaire","« Il eût fallu qu'il vînt. » — « vînt » est au…",["subjonctif imparfait","passé simple","conditionnel passé","plus-que-parfait de l'indicatif"],"Concordance des temps littéraire.",""),
 ("C2","grammaire","« Elles se sont ___ des cadeaux. »",["offert","offertes","offerts","offerte"],"Le COD (des cadeaux) est placé après : pas d'accord ; « se » est COI.",""),
 ("C2","vocabulaire","« Sabler le champagne » signifie…",["boire du champagne pour fêter un événement","le refroidir dans le sable","le jeter","le servir mal"],"Expression figée et festive.",""),
 ("C2","culture","Qui a écrit « Cahier d'un retour au pays natal » ?",["Aimé Césaire","Léopold Sédar Senghor","Frantz Fanon","Édouard Glissant"],"Œuvre fondatrice de la Négritude (1939).",""),
 ("C2","registre","« Nonobstant les dispositions qui précèdent » relève du registre…",["juridique / soutenu","familier","argotique","oral courant"],"Lexique des contrats et textes officiels.",""),
 ("C2","comprehension","« Son discours, pour brillant qu'il fût, ne convainquit personne. » — Le discours était…",["brillant mais peu convaincant","terne et convaincant","brillant et convaincant","inexistant"],"« pour + adj. + que » = concession (bien que).",""),
],
"es": [
 ("C1","grammaire","Ojalá ___ venido ayer.",["hubieras","habías","has","habrías"],"Deseo irrealizable en el pasado → pluscuamperfecto de subjuntivo.",""),
 ("C1","vocabulaire","« Estar en la luna de Valencia » significa…",["estar distraído","estar enamorado","viajar mucho","estar triste"],"Équivalent de « être dans la lune ».",""),
 ("C1","registre","Fórmula adecuada para una petición formal :",["Le agradecería que me enviara la documentación.","Mándame los papeles, porfa.","Pásame eso.","Quiero los papeles ya."],"Condicional de cortesía + usted + subjuntivo.",""),
 ("C1","comprehension","« El proyecto quedó en agua de borrajas. » — El proyecto…",["no llegó a nada","fue un éxito","se aprobó","se mojó"],"Quedar en agua de borrajas = tourner court.",""),
 ("C2","vocabulaire","« Erre que erre » significa…",["con obstinación","por error","rápidamente","en voz baja"],"S'obstiner, ne pas en démordre.",""),
 ("C2","grammaire","« De haberlo sabido, no habría venido » equivale a…",["Si lo hubiera sabido, no habría venido.","Como lo sabía, no vine.","Aunque lo sabía, vine.","Cuando lo supe, vine."],"« De + infinitivo compuesto » = condición irreal del pasado.",""),
 ("C2","culture","¿Quién escribió « Pedro Páramo »?",["Juan Rulfo","Carlos Fuentes","Octavio Paz","Jorge Luis Borges"],"Novela mexicana de 1955.",""),
 ("C2","registre","« Por la presente se hace constar que… » pertenece al registro…",["administrativo / jurídico","coloquial","juvenil","poético"],"Fórmula de certificados y documentos oficiales.",""),
 ("C2","comprehension","« No es oro todo lo que reluce. » — Significa…",["las apariencias engañan","el oro es caro","todo brilla","hay que buscar oro"],"Proverbe : tout ce qui brille n'est pas or.",""),
],
}

SKILL_AGENT = {"grammaire":"nova","vocabulaire":"nova","comprehension":"griot","culture":"griot","registre":"plume"}

rows = []
for lang, items in Q.items():
    items = [t + ("",) for t in items] + Q_EXTRA.get(lang, [])
    for i, (lvl, skill, q, opts, expl, src) in enumerate(items, 1):
        assert len(set(opts)) == len(opts), q
        rows.append({
            "id": f"{lang}-{i:03d}", "lang": lang, "level": lvl, "skill": skill,
            "agent": SKILL_AGENT[skill], "question": q, "options": "|".join(opts),
            "answer": opts[0], "explanation": expl, "source": src,
        })

def write(name, data):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        w.writeheader(); w.writerows(data)
    print(f"{name:28s} {len(data):4d} lignes")

write("questions.csv", rows)

# --------------------------------------------------------------------------
# 2. REGISTRES DE LANGUE (sens, soutenu, courant, familier, professionnel)
# --------------------------------------------------------------------------
REG = [
 ("en","Je suis fatigué","I am rather weary.","I'm tired.","I'm knackered / I'm beat.","I'm at reduced capacity today; may we reschedule?"),
 ("en","Je ne comprends pas","I fail to grasp your meaning.","I don't understand.","I don't get it.","Could you clarify that point, please?"),
 ("en","C'est super","That is truly remarkable.","That's great.","That's awesome / sick!","That's an excellent outcome."),
 ("en","On se voit plus tard","I shall see you in due course.","See you later.","Catch you later!","Let's reconnect later today."),
 ("en","Donne-moi ça","Would you be so kind as to pass me that?","Can you give me that?","Gimme that.","Could you send that over when you have a moment?"),
 ("en","J'ai un problème","I find myself in a predicament.","I have a problem.","I'm in a bit of a pickle.","I'd like to flag an issue."),
 ("fr","Je suis fatigué","Je suis las.","Je suis fatigué.","Je suis crevé / naze.","Je dispose de peu de disponibilité aujourd'hui."),
 ("fr","Je ne comprends pas","Je ne saisis pas votre propos.","Je ne comprends pas.","J'pige rien.","Pourriez-vous préciser ce point ?"),
 ("fr","C'est super","C'est remarquable.","C'est très bien.","C'est trop génial / ouf !","Le résultat est très satisfaisant."),
 ("fr","L'argent","Les deniers / les fonds","L'argent","Le fric / la thune / le blé","Le budget / les ressources financières"),
 ("fr","Le travail","L'ouvrage / la besogne","Le travail","Le boulot / le taf","Le poste / la mission"),
 ("fr","Partir","Se retirer / prendre congé","Partir","Se casser / se barrer","Quitter la réunion / clore l'échange"),
 ("es","Estoy cansado","Me hallo fatigado.","Estoy cansado.","Estoy reventado / hecho polvo.","Hoy tengo disponibilidad limitada."),
 ("es","No entiendo","No alcanzo a comprender.","No entiendo.","No me entero / ni idea.","¿Podría aclarar ese punto?"),
 ("es","Es genial","Es extraordinario.","Es muy bueno.","¡Es guay / chévere / bacán!","Es un resultado excelente."),
 ("es","El dinero","Los caudales / los fondos","El dinero","La pasta / la plata / la lana","El presupuesto / los recursos"),
 ("es","El trabajo","La labor / la ocupación","El trabajo","El curro / la chamba","El puesto / el proyecto"),
 ("es","Irse","Retirarse / despedirse","Irse","Pirarse / largarse","Concluir la reunión"),
 ("ht","Je suis fatigué","Mwen santi m bouke anpil.","Mwen bouke.","M about !","Jodi a m pa twò disponib."),
 ("ht","Je ne comprends pas","Mwen pa fin konprann sa w di a.","M pa konprann.","M pa pran l.","Èske w ka eksplike pwen sa a ankò, souple ?"),
 ("ht","Comment ça va ?","Kòman ou ye, mesye/madam ?","Kòman ou ye ?","Sak pase ? / Sa k ap fèt ?","Bonjou, mwen espere tout bagay anfòm."),
 ("ht","L'argent","Resous finansye","Lajan","Kòb / grinn","Bidjè a / finansman an"),
 ("ht","Le travail","Okipasyon","Travay","Djòb","Pòs la / misyon an"),
 ("ht","Au revoir","Mwen pran konje.","Orevwa.","N a wè ! / Pita !","Mèsi pou tan nou, n ap rete an kontak."),
]
write("registres.csv", [dict(lang=a, sens=b, soutenu=c, courant=d, familier=e, professionnel=f) for a,b,c,d,e,f in REG])

# --------------------------------------------------------------------------
# 3. CULTURE : proverbes, expressions, faits
# --------------------------------------------------------------------------
CUL = [
 ("en","expression","Break the ice","Briser la glace, détendre l'atmosphère","B1"),
 ("en","expression","Bite the bullet","Serrer les dents et affronter une épreuve","B2"),
 ("en","proverbe","The early bird catches the worm","Le monde appartient à ceux qui se lèvent tôt","B1"),
 ("en","expression","The ball is in your court","C'est à toi de jouer / de décider","B2"),
 ("en","fait","Juneteenth (19 juin) commémore la fin de l'esclavage aux États-Unis","Jour férié fédéral depuis 2021","B2"),
 ("en","fait","Le 'Gettysburg Address' (1863) de Lincoln compte environ 270 mots","Modèle de concision rhétorique","C1"),
 ("fr","expression","Poser un lapin","Ne pas venir à un rendez-vous","B1"),
 ("fr","expression","Avoir le cafard","Être déprimé, avoir des idées noires","B1"),
 ("fr","proverbe","Qui ne risque rien n'a rien","Il faut oser pour obtenir","B1"),
 ("fr","expression","Ménager la chèvre et le chou","Ne pas prendre parti, satisfaire les deux camps","C1"),
 ("fr","fait","L'Académie française a été fondée en 1635 par Richelieu","Gardienne de la norme","B2"),
 ("fr","fait","La francophonie compte plus de 300 millions de locuteurs","Organisation internationale de la Francophonie","B1"),
 ("es","expression","Estar en las nubes","Être dans la lune","B1"),
 ("es","expression","Tomar el pelo","Se moquer de quelqu'un, le faire marcher","B1"),
 ("es","proverbe","Más vale tarde que nunca","Mieux vaut tard que jamais","A2"),
 ("es","expression","Ser pan comido","Être du gâteau, très facile","B1"),
 ("es","fait","L'espagnol est langue officielle dans 20 pays","Deuxième langue maternelle au monde","A2"),
 ("es","fait","La RAE (Real Academia Española) a été fondée en 1713","Publie le dictionnaire de référence","B2"),
 ("ht","proverbe","Piti piti zwazo fè nich li","Petit à petit l'oiseau fait son nid","B1"),
 ("ht","proverbe","Dèyè mòn gen mòn","Après une difficulté, une autre","B1"),
 ("ht","proverbe","Men anpil, chay pa lou","L'union fait la force (beaucoup de mains, la charge n'est pas lourde)","B1"),
 ("ht","proverbe","Bèl dan pa di zanmi","Un beau sourire ne veut pas dire amitié","B2"),
 ("ht","proverbe","Sak vid pa kanpe","Un sac vide ne tient pas debout (on ne peut rien faire le ventre vide)","B1"),
 ("ht","fait","La soupe joumou est servie le 1er janvier pour célébrer l'indépendance","Inscrite au patrimoine immatériel de l'UNESCO en 2021","B1"),
 ("ht","fait","Le konbit est une tradition de travail collectif","Valeur de solidarité","B2"),
 ("ht","fait","L'Akademi Kreyòl Ayisyen a été créée par la loi du 7 avril 2014 et installée en décembre 2014","Référence officielle pour la norme du kreyòl","C1"),
 ("ht","fait","L'alphabet officiel compte 32 graphèmes : 1 son = 1 graphie, aucune lettre muette","Orthographe de 1980, confirmée par l'AKA (résolution de 2017)","B1"),
 ("ht","fait","Dezafi (1975) de Frankétienne est le premier roman entièrement en kreyòl","Jalon de la littérature haïtienne","C1"),
 ("ht","fait","Le 28 octobre est la Journée internationale du créole","Célébrée dans tout l'espace créolophone","B1"),
 ("ht","expression","Tèt ansanm","Union, solidarité","B1"),
 ("ht","proverbe","Bourik travay, chwal galonnen","Les uns travaillent, les autres récoltent les honneurs","C1"),
]
write("culture.csv", [dict(lang=a, type=b, item=c, signification=d, level=e) for a,b,c,d,e in CUL])

# --------------------------------------------------------------------------
# 4. HISTOIRES ORIGINALES (texte + question)
# --------------------------------------------------------------------------
STO = [
 ("en","A2","The Lost Umbrella","Every Monday, Lily takes the bus to work. Last Monday it was raining, so she took her red umbrella. When she arrived at the office, she realised she had left it on the bus. At lunch, she called the bus company. A kind man answered: 'Yes, we found a red umbrella!' Lily smiled. She picked it up after work and bought the man a coffee.","Where did Lily leave her umbrella?","On the bus|At the office|At home|In a café"),
 ("en","B2","The Interview","Daniel had prepared for weeks. He had researched the company, rehearsed his answers and even practised his handshake. Yet when the first question came — 'Tell me about a time you failed' — his mind went blank. After a pause, he decided to be honest: he described a project that had collapsed and what he had learned. The interviewer leaned forward. 'That,' she said, 'is exactly what we wanted to hear.'","Why did the interviewer appreciate Daniel's answer?","Because he was honest and reflective|Because he never failed|Because he had a good handshake|Because he answered quickly"),
 ("fr","A2","Le marché du samedi","Chaque samedi, Paul va au marché avec sa grand-mère. Elle achète des tomates, du fromage et des fleurs. Paul porte le panier. Aujourd'hui, le marchand de fruits lui offre une pomme. « Tu es un bon assistant ! » dit-il. Paul est fier. Il mange sa pomme sur le chemin du retour.","Qu'est-ce que le marchand offre à Paul ?","Une pomme|Une fleur|Du fromage|Une tomate"),
 ("fr","C1","La lettre","Il avait longtemps hésité avant d'ouvrir l'enveloppe. Le cachet de la mairie, la formule « Monsieur, nous avons le regret… » qu'il redoutait déjà : tout semblait annoncer un refus. Pourtant, à mesure qu'il lisait, son appréhension se dissipait. Le regret ne portait que sur le retard du courrier ; son projet de jardin partagé était bel et bien retenu.","Quelle était la véritable nouvelle ?","Son projet était accepté|Son projet était refusé|La mairie fermait|Il devait déménager"),
 ("es","A2","La paella de la abuela","Los domingos, toda la familia come en casa de la abuela Carmen. Ella prepara una paella enorme con arroz, pollo y verduras. Los nietos ponen la mesa y el abuelo cuenta historias de su juventud. Después de comer, todos duermen la siesta. Es el mejor día de la semana.","¿Qué hacen los nietos?","Ponen la mesa|Cocinan la paella|Cuentan historias|Lavan el coche"),
 ("es","B2","El viaje inesperado","Lucía había planeado unas vacaciones tranquilas en la playa, pero su vuelo fue cancelado. En lugar de enfadarse, aceptó la propuesta de la aerolínea: un billete a Cartagena de Indias. Allí descubrió calles de colores, música en cada esquina y a una amiga de la infancia que no veía desde hacía diez años. A veces, pensó, los imprevistos son los mejores guías.","¿Qué aprendió Lucía?","Que los imprevistos pueden ser positivos|Que no debe viajar|Que la playa es aburrida|Que las aerolíneas son malas"),
 ("ht","A2","Mache a","Chak samdi, Mari ale nan mache ak manman l. Yo achte diri, pwa ak bannann. Mari renmen gade machann fwi yo. Jodi a, yon machann ba li yon mango. Mari kontan anpil. Li di : « Mèsi anpil, madanm ! »","Kisa machann nan bay Mari ?","Yon mango|Diri|Pwa|Bannann"),
 ("ht","B1","Bouki ak Ti Malis (rezime)","Yon jou, Bouki ak Ti Malis jwenn yon bokit myèl. Ti Malis di Bouki : « Ann sere l, n a manje l ansanm pita. » Men chak swa, Ti Malis al manje ti myèl an kachèt. Lè Bouki vin chèche bokit la, li vid ! Ti Malis fè tankou li pa konn anyen. Kont sa a montre kijan Malis toujou chèche twonpe Bouki.","Kiyès ki te manje myèl la ?","Ti Malis|Bouki|Yon chen|Pèsonn"),
]
write("histoires.csv", [dict(lang=a, level=b, title=c, text=d, question=e, options=f, answer=f.split("|")[0]) for a,b,c,d,e,f in STO])

# --------------------------------------------------------------------------
# 5. DISCOURS CÉLÈBRES (référence + lien vers la source)
# --------------------------------------------------------------------------
SPE = [
 ("en","Martin Luther King Jr.","I Have a Dream",1963,"soutenu / oratoire","C1","droits civiques, anaphore","https://www.americanrhetoric.com/top100speechesall.html"),
 ("en","John F. Kennedy","Inaugural Address",1961,"soutenu / oratoire","C1","chiasme, engagement civique","https://www.americanrhetoric.com/top100speechesall.html"),
 ("en","Abraham Lincoln","Gettysburg Address",1863,"soutenu","C2","concision, démocratie","https://millercenter.org/the-presidency/presidential-speeches"),
 ("en","Barack Obama","A More Perfect Union",2008,"soutenu / argumentatif","C1","identité, nuance","https://millercenter.org/the-presidency/presidential-speeches"),
 ("en","Franklin D. Roosevelt","First Inaugural Address",1933,"soutenu","C1","crise, confiance","https://www.americanrhetoric.com/top100speechesall.html"),
 ("en","Top 100 American Speeches","Corpus complet (texte + audio)",0,"varié","B2","corpus de référence","https://www.americanrhetoric.com/top100speechesall.html"),
 ("en","Miller Center","Presidential Speeches Archive",0,"varié","B2","archives présidentielles","https://millercenter.org/the-presidency/presidential-speeches"),
 ("fr","Simone Veil","Discours sur l'IVG à l'Assemblée",1974,"soutenu / argumentatif","C1","droits des femmes, rhétorique parlementaire","https://www.vie-publique.fr/discours"),
 ("fr","Charles de Gaulle","Appel du 18 juin",1940,"soutenu / oratoire","B2","résistance","https://www.ina.fr"),
 ("fr","Robert Badinter","Abolition de la peine de mort",1981,"soutenu","C1","justice, argumentation","https://www.vie-publique.fr/discours"),
 ("fr","Vie publique","Recueil des discours publics",0,"varié","B2","corpus officiel français","https://www.vie-publique.fr/discours"),
 ("es","Gabriel García Márquez","La soledad de América Latina (Nobel)",1982,"soutenu / littéraire","C1","identité latino-américaine","https://www.nobelprize.org/prizes/literature/"),
 ("es","Pablo Neruda","Discurso Nobel",1971,"littéraire","C2","poésie, engagement","https://www.nobelprize.org/prizes/literature/"),
 ("es","Mario Vargas Llosa","Elogio de la lectura y la ficción (Nobel)",2010,"soutenu","C1","lecture, liberté","https://www.nobelprize.org/prizes/literature/"),
 ("ht","MIT-Ayiti","Leçons et vidéos en kreyòl (sciences)",0,"courant / académique","B2","kreyòl académique","https://haiti.mit.edu"),
 ("ht","MIT OpenCourseWare","Inisyativ MIT-Ayiti (cours en kreyòl)",2023,"académique","B2","pédagogie en kreyòl","https://ocw.mit.edu/courses/res-24-002-mit-haiti-initiative-inisyativ-mit-ayiti-spring-2023"),
 ("ht","Wikipedya","Encyclopédie en kreyòl ayisyen",0,"écrit standard","B1","lecture authentique","https://ht.wikipedia.org"),
 ("ht","Akademi Kreyòl Ayisyen","Premye rezolisyon sou òtograf kreyòl ayisyen an",2017,"officiel / normatif","C1","norme orthographique","https://www.communication.gouv.ht/2017/06/premye-rezolisyon-sou-otograf-kreyol-ayisyen-an/"),
 ("ht","Akademi Kreyòl Ayisyen","Résolutions et publications (site officiel)",0,"officiel","C1","norme, droits linguistiques","https://akademikreyol.net"),
]
def yt(q): return "https://www.youtube.com/results?search_query=" + q.replace(" ", "+")
write("discours.csv", [dict(lang=a, orateur=b, titre=c, annee=d, registre=e, level=f, themes=g, url=h,
        ecouter=(yt(f"{b} {c}") if d else "")) for a,b,c,d,e,f,g,h in SPE])

# --------------------------------------------------------------------------
# 6. CHANSONS POPULAIRES (référence uniquement – activités originales)
# --------------------------------------------------------------------------
def yt(q): return "https://www.youtube.com/results?search_query=" + q.replace(" ", "+")
def gen(q): return "https://genius.com/search?q=" + q.replace(" ", "%20")
SON = [
 ("en","John Lennon","Imagine",1971,"A2","paix, utopie","courant","Repérez les verbes à l'impératif et au présent ; écrivez votre propre strophe 'Imagine…'."),
 ("en","Bill Withers","Lean on Me",1972,"A2","amitié, entraide","courant","Listez les expressions d'aide ; réutilisez-les dans un message à un ami."),
 ("en","Adele","Someone Like You",2011,"B1","rupture, nostalgie","courant","Repérez le prétérit et le present perfect ; racontez un souvenir."),
 ("en","Queen","Bohemian Rhapsody",1975,"B2","narration, drame","littéraire","Résumez l'histoire en 5 phrases ; identifiez les changements de ton."),
 ("en","Eminem","Lose Yourself",2002,"C1","opportunité, persévérance","familier / argot","Travail du débit rapide et des contractions orales."),
 ("fr","Édith Piaf","La Vie en rose",1947,"A2","amour","courant","Repérez le présent et les sensations ; décrivez un moment heureux."),
 ("fr","Jacques Brel","Ne me quitte pas",1959,"C1","supplication, images poétiques","soutenu / poétique","Analysez les métaphores et l'impératif négatif."),
 ("fr","Stromae","Formidable",2013,"B2","ironie, ivresse, société","familier","Repérez les marques d'oralité et l'ironie."),
 ("fr","Zaz","Je veux",2010,"B1","liberté, anti-matérialisme","familier","Repérez 'je veux / je ne veux pas' + complément ; exprimez vos souhaits."),
 ("fr","Indila","Dernière danse",2013,"B1","solitude, Paris","courant","Repérez le vocabulaire des émotions."),
 ("es","Luis Fonsi ft. Daddy Yankee","Despacito",2017,"B1","séduction, danse","coloquial","Repérez les diminutifs et adverbes en -ito."),
 ("es","Violeta Parra","Gracias a la vida",1966,"B2","gratitude, sens","poético","Listez les dons remerciés ; écrivez vos propres 'gracias a…'."),
 ("es","Marc Anthony","Vivir mi vida",2013,"A2","optimisme","courant","Repérez le futur et le présent ; exprimez des résolutions."),
 ("es","Juanes","La camisa negra",2004,"B1","peine de cœur, ironie","coloquial","Repérez les expressions de sentiments."),
 ("ht","Boukman Eksperyans","Kalfou Danjere",1992,"B2","justice, mizik rasin","courant / engagé","Repérez les mots liés à la justice et au danger."),
 ("ht","Emeline Michel","Plezi Mizik",0,"B1","joie, musique","courant","Repérez le vocabulaire de la fête et des émotions."),
 ("ht","Tabou Combo","New York City",1975,"A2","diaspora, ville","courant","Repérez les mots kreyòl / anglais mélangés."),
 ("ht","Mikaben","Ou se pa m",0,"B1","amour","courant","Repérez les possessifs (pa m, pa w…)."),
]
write("chansons.csv", [dict(lang=a, artiste=b, titre=c, annee=d, level=e, themes=f, registre=g, activite=h,
        ecouter=yt(f"{b} {c}"), paroles_licenciees=gen(f"{b} {c}")) for a,b,c,d,e,f,g,h in SON])

# --------------------------------------------------------------------------
# 7. RESSOURCES PAR COMPÉTENCE (liens vers sites reconnus)
# --------------------------------------------------------------------------
RES = [
 # anglais
 ("en","grammaire","site","British Council – LearnEnglish Grammar","https://learnenglish.britishcouncil.org/grammar","A1","Explications et exercices gradués"),
 ("en","vocabulaire","site","Cambridge Dictionary","https://dictionary.cambridge.org","A1","Définitions, prononciation UK/US"),
 ("en","comprehension","vidéo","BBC Learning English","https://www.bbc.co.uk/learningenglish","A2","Vidéos courtes et cours"),
 ("en","comprehension","audio","VOA Learning English","https://learningenglish.voanews.com","A2","Actualités en anglais ralenti"),
 ("en","comprehension","vidéo","TED Talks","https://www.ted.com/talks","B2","Conférences avec transcriptions"),
 ("en","registre","guide","Purdue OWL – Professional Writing","https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/index.html","B2","Rédaction professionnelle"),
 ("en","culture","discours","American Rhetoric – Top 100 Speeches","https://www.americanrhetoric.com/top100speechesall.html","B2","Discours américains (texte + audio)"),
 ("en","culture","discours","Miller Center – Presidential Speeches","https://millercenter.org/the-presidency/presidential-speeches","B2","Archives des discours présidentiels"),
 ("en","expression","outil","Hemingway Editor","https://hemingwayapp.com","B1","Clarté et lisibilité de vos écrits"),
 # français
 ("fr","grammaire","site","Le Point du FLE","https://www.lepointdufle.net","A1","Annuaire d'exercices de grammaire"),
 ("fr","vocabulaire","site","CNRTL – Dictionnaire","https://www.cnrtl.fr/definition/","B1","Définitions, synonymes, étymologie"),
 ("fr","comprehension","vidéo","TV5MONDE – Apprendre le français","https://apprendre.tv5monde.com","A1","Vidéos et exercices par niveau"),
 ("fr","comprehension","audio","RFI – Français facile","https://francaisfacile.rfi.fr","A2","Journal en français facile"),
 ("fr","registre","guide","Académie française – Dire, ne pas dire","https://www.academie-francaise.fr/dire-ne-pas-dire","B2","Bon usage et registres"),
 ("fr","culture","discours","Vie publique – Discours","https://www.vie-publique.fr/discours","B2","Discours officiels"),
 ("fr","culture","archives","INA – Archives audiovisuelles","https://www.ina.fr","B1","Archives historiques"),
 ("fr","expression","site","Projet Voltaire (orthographe)","https://www.projet-voltaire.fr","B1","Orthographe et expression écrite"),
 # espagnol
 ("es","grammaire","site","Centro Virtual Cervantes","https://cvc.cervantes.es","A1","Ressources de l'Instituto Cervantes"),
 ("es","vocabulaire","site","Diccionario de la RAE","https://dle.rae.es","A2","Dictionnaire de référence"),
 ("es","registre","guide","FundéuRAE","https://www.fundeu.es","B2","Bon usage de l'espagnol"),
 ("es","comprehension","vidéo","RTVE Play","https://www.rtve.es/play/","B1","Télévision publique espagnole"),
 ("es","comprehension","site","ProfeDeELE","https://www.profedeele.es","A1","Vidéos et fiches ELE"),
 ("es","culture","discours","Nobel Prize – Lectures en espagnol","https://www.nobelprize.org/prizes/literature/","C1","Discours Nobel (García Márquez, Neruda…)"),
 ("es","expression","site","Ver-taal – exercices","https://www.ver-taal.com","B1","Exercices de compréhension et grammaire"),
 # créole
 ("ht","grammaire","guide","Cambridge – A learner's dictionary of Haitian Creole","https://www.langcen.cam.ac.uk/resources/langh/data/hc_102.html","A1","Référence d'apprentissage"),
 ("ht","vocabulaire","site","HaitiHub – Learn Haitian Creole","https://haitihub.com/learn-haitian-creole-free/","A1","Cours gratuits"),
 ("ht","comprehension","vidéo","MIT-Ayiti","https://haiti.mit.edu","B1","Contenus pédagogiques en kreyòl"),
 ("ht","comprehension","cours","MIT OCW – Inisyativ MIT-Ayiti","https://ocw.mit.edu/courses/res-24-002-mit-haiti-initiative-inisyativ-mit-ayiti-spring-2023","B2","Cours en kreyòl"),
 ("ht","culture","lecture","Wikipedya kreyòl","https://ht.wikipedia.org","B1","Lecture authentique"),
 ("ht","vocabulaire","dictionnaire","Potomitan – Diksyonè kreyòl (PDF)","https://www.potomitan.info/ayiti/berrouet-oriol/diksyone_kreyol.pdf","B1","Lexique kreyòl"),
 ("ht","culture","annuaire","HaitiHub – Haiti & Kreyòl on the web","https://haitihub.com/resources","A2","Annuaire de ressources"),
 ("ht","registre","officiel","Akademi Kreyòl Ayisyen (site officiel)","https://akademikreyol.net","B1","Résolutions, normes et publications de l'AKA"),
 ("ht","grammaire","officiel","AKA – Premye rezolisyon sou òtograf kreyòl ayisyen an (2017)","https://www.communication.gouv.ht/2017/06/premye-rezolisyon-sou-otograf-kreyol-ayisyen-an/","B1","Texte de la 1re résolution orthographique"),
 ("ht","grammaire","guide","Espas Kreyòl – Ekri kreyòl fasil","https://espaskreyol.org/ekri-kreyol-fasil/","A1","Les 32 graphèmes et les 3 principes de l'orthographe officielle"),
 ("ht","culture","officiel","Loi portant création de l'Académie du créole haïtien (2014)","https://axl.cefan.ulaval.ca/amsudant/haiti-loi-2014.htm","C1","Missions, composition et pouvoirs de l'AKA"),
]
write("ressources.csv", [dict(lang=a, skill=b, type=c, titre=d, url=e, level_min=f, description=g) for a,b,c,d,e,f,g in RES])

# --------------------------------------------------------------------------
# 8. VOCABULAIRE (flashcards + arcade HTML/JS)
# --------------------------------------------------------------------------
VOC = {
"en": [("house","maison"),("work","travail"),("friend","ami"),("water","eau"),("book","livre"),("city","ville"),("meeting","réunion"),("deadline","échéance"),("to improve","améliorer"),("skill","compétence"),("to borrow","emprunter"),("weather","météo"),("journey","voyage"),("receipt","reçu"),("to achieve","accomplir"),("thoughtful","attentionné")],
"fr": [("la maison","house"),("le travail","work"),("l'ami","friend"),("l'eau","water"),("le livre","book"),("la ville","city"),("la réunion","meeting"),("l'échéance","deadline"),("améliorer","to improve"),("la compétence","skill"),("emprunter","to borrow"),("la météo","weather"),("le voyage","journey"),("le reçu","receipt"),("accomplir","to achieve"),("attentionné","thoughtful")],
"es": [("la casa","maison"),("el trabajo","travail"),("el amigo","ami"),("el agua","eau"),("el libro","livre"),("la ciudad","ville"),("la reunión","réunion"),("el plazo","échéance"),("mejorar","améliorer"),("la habilidad","compétence"),("pedir prestado","emprunter"),("el tiempo","météo"),("el viaje","voyage"),("el recibo","reçu"),("lograr","accomplir"),("atento","attentionné")],
"ht": [("kay","maison"),("travay","travail"),("zanmi","ami"),("dlo","eau"),("liv","livre"),("vil","ville"),("reyinyon","réunion"),("lekòl","école"),("amelyore","améliorer"),("lajan","argent"),("manje","manger / nourriture"),("tan","temps / météo"),("vwayaj","voyage"),("fanmi","famille"),("mèsi","merci"),("souple","s'il vous plaît")],
}
write("vocabulaire.csv", [dict(lang=l, word=w, traduction=t, level="A1" if i < 8 else "B1") for l, pairs in VOC.items() for i,(w,t) in enumerate(pairs)])

# --------------------------------------------------------------------------
# 8 bis. ORTHOGRAPHE OFFICIELLE DU KREYÒL (32 graphèmes – référence AKA)
# --------------------------------------------------------------------------
OTO_ROWS = [
 ("a","voyelle orale","papa","papa"),("e","voyelle orale","fe","faire"),("è","voyelle orale (e ouvert)","fè","fer / faire"),
 ("i","voyelle orale","di","dire"),("o","voyelle orale","dodo","dormir (enfantin)"),("ò","voyelle orale (o ouvert)","lekòl","école"),
 ("ou","voyelle orale","fou","fou"),("ui","voyelle orale","uit","huit"),
 ("an","voyelle nasale","manman","maman"),("en","voyelle nasale","pen","pain"),("on","voyelle nasale","bon","bon"),("oun","voyelle nasale (trigramme)","moun","personne"),
 ("b","consonne","bato","bateau"),("ch","consonne","chat","chat"),("d","consonne","dlo","eau"),("f","consonne","fanmi","famille"),
 ("g","consonne (toujours dur)","gade","regarder"),("h","consonne (prononcée)","hont","honte"),("j","consonne","jaden","jardin"),
 ("k","consonne","kay","maison"),("l","consonne","lavi","la vie"),("m","consonne","mache","marcher / marché"),("n","consonne","nou","nous"),
 ("ng","consonne (digramme)","bilding","bâtiment"),("p","consonne","pitit","enfant"),("r","consonne","radyo","radio"),
 ("s","consonne (toujours [s])","sèl","sel / seul"),("t","consonne","tab","table"),("v","consonne","vil","ville"),("z","consonne","zanmi","ami"),
 ("w","semi-voyelle","wi","oui"),("y","semi-voyelle","yo","ils / les"),
]
write("orthographe_ht.csv", [dict(grapheme=a, type=b, exemple=c, sens=d) for a,b,c,d in OTO_ROWS])

# --------------------------------------------------------------------------
# 9. BADGES (gamification)
# --------------------------------------------------------------------------
BAD = [
 ("first_step","🌱","Premier pas","Terminer le diagnostic"),
 ("streak_3","🔥","Flamme","3 jours d'affilée"),
 ("streak_7","☄️","Comète","7 jours d'affilée"),
 ("xp_500","⭐","Étoile montante","500 XP cumulés"),
 ("xp_2000","🌟","Constellation","2 000 XP cumulés"),
 ("polyglot","🌍","Polyglotte","Diagnostic dans 3 langues"),
 ("writer","✍️","Plume d'or","5 textes analysés"),
 ("certified","🎓","Certifié·e","Obtenir un certificat"),
 ("culture","🎭","Ambassadeur culturel","10 activités culture réussies"),
 ("perfect","💎","Sans faute","Série de 10 bonnes réponses"),
]
write("badges.csv", [dict(code=a, icon=b, nom=c, condition=d) for a,b,c,d in BAD])

# --------------------------------------------------------------------------
# 10. DESCRIPTEURS CECRL (évaluation — Conseil de l'Europe, Volume complémentaire 2018/2020)
# --------------------------------------------------------------------------
CEF = [
 ("A1","Débutant","Usage personnel élémentaire","Comprend et utilise des expressions familières et quotidiennes ; peut se présenter.","Novice High"),
 ("A2","Élémentaire","Usage personnel","Communique lors de tâches simples et habituelles ; décrit son environnement.","Intermediate Low/Mid"),
 ("B1","Intermédiaire (seuil)","Usage social et voyage","Comprend l'essentiel d'un discours clair ; se débrouille en voyage ; raconte un événement.","Intermediate High"),
 ("B2","Avancé indépendant","Usage professionnel opérationnel","Comprend des textes complexes ; communique avec aisance et spontanéité ; argumente.","Advanced Mid/High"),
 ("C1","Autonome / Professionnel","Usage professionnel avancé","S'exprime couramment et de façon structurée ; usage souple en contexte professionnel et académique.","Superior"),
 ("C2","Maîtrise","Usage expert / quasi natif","Comprend sans effort pratiquement tout ; nuances fines de sens.","Distinguished"),
]
write("cecrl.csv", [dict(level=a, label=b, usage=c, descripteur=d, actfl=e) for a,b,c,d,e in CEF])
print("Contenus générés dans", OUT)
