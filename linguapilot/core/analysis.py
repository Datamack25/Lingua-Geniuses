"""
Analyse d'expression écrite (agent Plume).

Grille inspirée des critères qualitatifs du CECRL (Volume complémentaire, Conseil de l'Europe) :
  • Étendue (richesse lexicale et syntaxique)
  • Correction (erreurs fréquentes, ponctuation, majuscules)
  • Cohérence (connecteurs, structuration)
  • Adéquation sociolinguistique (registre visé vs registre détecté)

C'est une analyse indicative et heuristique ; si un serveur Ollama est disponible
(variable OLLAMA_URL, ex. http://localhost:11434), un retour qualitatif est ajouté.
"""
from __future__ import annotations
import json, os, re, urllib.request
from collections import Counter

LEX = {
 "en": dict(
   basic=["and", "but", "so", "because", "then", "also", "or"],
   advanced=["however", "moreover", "therefore", "nevertheless", "furthermore", "whereas", "consequently",
             "although", "in addition", "on the other hand", "as a result", "despite", "notwithstanding"],
   familiar=["gonna", "wanna", "gotta", "yeah", "cool", "stuff", "guys", "kinda", "awesome", "lol", "mate",
             "ain't", "dude", "btw"],
   formal=["furthermore", "hence", "thus", "whereby", "notwithstanding", "albeit", "henceforth", "pursuant"],
   pro=["regards", "please find", "attached", "deadline", "stakeholder", "follow up", "meeting", "kindly",
        "dear", "sincerely", "as discussed", "deliverable"],
   errors=[(r"\bi\b", "Le pronom « I » s'écrit toujours en majuscule."),
           (r"\bcould of\b|\bwould of\b|\bshould of\b", "« could of » → « could have »."),
           (r"\bthere is \w+s\b", "Vérifiez l'accord : « there are » + pluriel."),
           (r"\bmore better\b", "« more better » → « better »."),
           (r"\bpeoples\b", "« people » est déjà pluriel."),
           (r"\bhe don't\b|\bshe don't\b|\bit don't\b", "3e personne : « doesn't »."),
           (r"\binformations\b|\badvices\b", "« information / advice » sont indénombrables.")]),
 "fr": dict(
   basic=["et", "mais", "donc", "parce que", "puis", "aussi", "ou"],
   advanced=["cependant", "néanmoins", "toutefois", "en outre", "par conséquent", "ainsi", "d'une part",
             "d'autre part", "bien que", "en revanche", "dès lors", "nonobstant", "en effet", "or"],
   familiar=["truc", "machin", "ouais", "bah", "genre", "trop", "kiffer", "boulot", "fric", "mec", "ça va",
             "t'es", "j'sais", "chui", "grave", "ouf"],
   formal=["nonobstant", "en outre", "dès lors", "il sied", "aussi convient-il", "eu égard", "afin de",
           "je vous prie", "veuillez"],
   pro=["madame", "monsieur", "cordialement", "ci-joint", "veuillez", "réunion", "échéance", "suite à",
        "je reste à votre disposition", "salutations"],
   errors=[(r"\bmalgré que\b", "« malgré que » est critiqué : préférez « bien que » + subjonctif."),
           (r"\bsi j'aurais\b|\bsi tu aurais\b|\bsi il aurait\b", "Après « si » : imparfait (« si j'avais »)."),
           (r"\bpallier à\b", "« pallier » est transitif direct : « pallier un problème »."),
           (r"\bau jour d'aujourd'hui\b", "Pléonasme : « aujourd'hui » suffit."),
           (r"\bse rappeler de\b", "« se rappeler quelque chose » (sans « de »)."),
           (r"\bje vais au coiffeur\b", "« chez le coiffeur »."),
           (r"\bsuite à\b", "Admis en langue commerciale ; en registre soutenu : « à la suite de »."),
           (r" [!?;:]", None)]),
 "es": dict(
   basic=["y", "pero", "porque", "entonces", "también", "o"],
   advanced=["sin embargo", "no obstante", "además", "por lo tanto", "por consiguiente", "aunque",
             "en cambio", "asimismo", "es decir", "a pesar de", "por un lado", "por otro lado"],
   familiar=["tío", "guay", "mola", "chévere", "vale", "pues nada", "curro", "pasta", "chamba", "bacán",
             "o sea", "flipar"],
   formal=["no obstante", "asimismo", "empero", "por consiguiente", "en virtud de", "le saluda atentamente"],
   pro=["estimado", "estimada", "atentamente", "adjunto", "reunión", "plazo", "quedo a su disposición",
        "un cordial saludo"],
   errors=[(r"\bhaber si\b", "« haber si » → « a ver si »."),
           (r"\bhubieron\b", "« haber » impersonal es invariable : « hubo »."),
           (r"\bpienso de que\b|\bcreo de que\b", "Dequeísmo : « pienso que »."),
           (r"\bmás mejor\b", "« más mejor » → « mejor »."),
           (r"\bdijistes\b|\bhicistes\b", "2.ª persona del pretérito sin -s final : « dijiste »."),
           (r"\bla agua\b", "« el agua » (sustantivo femenino con a tónica).")]),
 "ht": dict(
   basic=["epi", "men", "paske", "apre", "tou", "oswa", "ak"],
   advanced=["sepandan", "kidonk", "poutan", "konsènan", "anplis", "malgre", "se poutèt sa", "yon lòt bò",
             "kòm", "pou kòmanse", "an konklizyon"],
   familiar=["sak pase", "n ap boule", "bagay la", "zanmi m", "monchè", "ey", "chè", "anfòm"],
   formal=["konsènan", "anplis", "an konklizyon", "se poutèt sa", "mesye", "madam"],
   pro=["mesye", "madam", "reyinyon", "dosye", "mèsi davans", "respè", "salitasyon", "pwojè"],
   errors=[(r"\bmoi\b", "En kreyòl standard : « mwen » (ou « m »)."),
           (r"\boui\b", "Orthographe officielle : « wi »."),
           (r"\bmerci\b", "Orthographe officielle : « mèsi »."),
           (r"\bbonjour\b", "Orthographe officielle : « bonjou »."),
           (r"\bqui\b|\bque\b", "Graphie française : en kreyòl « ki » / « ke »."),
           (r"ou\b(?= ?[,.])", None)]),
}

REG_LABEL = {"familier": "Familier", "courant": "Courant", "soutenu": "Soutenu", "professionnel": "Professionnel"}


def _count(text: str, words: list[str]) -> int:
    t = " " + text.lower() + " "
    return sum(len(re.findall(r"(?<![\wà-ÿ])" + re.escape(w) + r"(?![\wà-ÿ])", t)) for w in words)


def analyze(text: str, lang: str, target_register: str = "courant") -> dict:
    L = LEX[lang]
    words = re.findall(r"[\wÀ-ÿ'’-]+", text.lower())
    n = len(words)
    sents = [s for s in re.split(r"[.!?]+\s*", text.strip()) if s.strip()]
    ns = max(1, len(sents))
    uniq = len(set(words))
    ttr = uniq / n if n else 0
    # MSTTR (moyenne des TTR par segments de 25 mots) — moins sensible à la longueur
    segs = [words[i:i + 25] for i in range(0, n, 25) if len(words[i:i + 25]) >= 15]
    msttr = sum(len(set(s)) / len(s) for s in segs) / len(segs) if segs else ttr
    avg_len = n / ns
    long_words = sum(len(w) >= 8 for w in words) / n if n else 0

    adv = _count(text, L["advanced"]); bas = _count(text, L["basic"])
    fam = _count(text, L["familiar"]); frm = _count(text, L["formal"]); pro = _count(text, L["pro"])

    issues = []
    for pat, msg in L["errors"]:
        if msg and "suite à" in pat and target_register != "soutenu":
            continue
        if msg and re.search(pat, text, flags=re.I if pat != r"\bi\b" else 0):
            issues.append(msg)
    if lang == "ht":
        # alphabet officiel (32 graphèmes) : pas de c (hors ch), q, x, é, ê, â, î, ô, û, ç, ë
        bad = sorted({w for w in words if re.search(r"c(?!h)|[qxéêâîôûçëœ]", w)})
        if bad:
            issues.append("Lettres hors de l'alphabet officiel (orthographe 1980 / AKA) dans : « "
                          + " », « ".join(bad[:6]) + " » — ex. « lécol » → « lekòl », « qui » → « ki ».")
        fused = re.findall(r"\b(?:m|w|l|n|y)'(?:ap|te|pral|ta)\b", text.lower())
        if fused:
            issues.append("Formes courtes : écrivez le pronom séparé du marqueur (« m ap », « l te »), sans apostrophe.")
    if sents and any(s.strip()[0].islower() for s in sents if s.strip()[0].isalpha()):
        issues.append("Certaines phrases ne commencent pas par une majuscule.")
    if "  " in text:
        issues.append("Doubles espaces détectées.")
    rep = [w for w, c in Counter(w for w in words if len(w) > 4).most_common(3) if c >= 3]
    if rep:
        issues.append("Répétitions : « " + " », « ".join(rep) + " » — variez avec des synonymes.")
    if avg_len > 35:
        issues.append("Phrases très longues : découpez pour gagner en clarté.")

    # ---- scores (0-100)
    etendue = min(100, round(40 * msttr / .75 + 30 * min(1, long_words / .25) + 30 * min(1, n / 150)))
    correction = max(0, 100 - 12 * len(issues))
    coherence = min(100, round(35 * min(1, (adv + bas) / max(1, ns)) + 45 * min(1, adv / max(1, ns * .5))
                               + 20 * min(1, ns / 5)))
    detected = ("familier" if fam > max(frm, pro) and fam > 0 else
                "professionnel" if pro >= max(frm, 1) else
                "soutenu" if frm >= 2 or (adv >= 3 and fam == 0) else "courant")
    adequation = 100 if detected == target_register else (70 if {detected, target_register} <= {"courant", "professionnel", "soutenu"} else 40)
    if target_register in ("soutenu", "professionnel") and fam:
        adequation = max(20, adequation - 15 * fam)
    glob = round(.3 * etendue + .25 * correction + .25 * coherence + .2 * adequation)
    if n < 30:
        glob = min(glob, 45)
    level = ("A1" if glob < 30 else "A2" if glob < 45 else "B1" if glob < 60 else
             "B2" if glob < 75 else "C1" if glob < 88 else "C2")

    advice = []
    if etendue < 60:
        advice.append("Enrichissez votre lexique : remplacez les mots très fréquents par des termes plus précis.")
    if coherence < 60:
        advice.append("Structurez avec des connecteurs logiques : " + ", ".join(L["advanced"][:5]) + "…")
    if adequation < 80:
        advice.append(f"Registre détecté : {REG_LABEL[detected]} — visé : {REG_LABEL[target_register]}. "
                      "Consultez la table des registres pour ajuster le ton.")
    if n < 80:
        advice.append("Visez au moins 80 à 150 mots pour une évaluation fiable.")
    if not advice:
        advice.append("Très bon texte ! Essayez maintenant un registre différent pour gagner en souplesse.")

    return dict(words=n, sentences=ns, ttr=round(msttr, 2), avg_sentence=round(avg_len, 1),
                connectors_adv=adv, familiar=fam, formal=frm, pro=pro,
                etendue=etendue, correction=correction, coherence=coherence, adequation=adequation,
                global_score=glob, level=level, register_detected=detected, issues=issues, advice=advice)


def ollama_feedback(text: str, lang_name: str, register: str) -> str | None:
    url = os.environ.get("OLLAMA_URL")
    if not url:
        return None
    prompt = (f"Tu es un examinateur de langue bienveillant (grille CECRL). Texte en {lang_name}, "
              f"registre visé : {register}. Donne en français : 1) niveau estimé, 2) trois points forts, "
              f"3) trois corrections précises avec la forme correcte, 4) un conseil. Texte :\n{text}")
    body = json.dumps({"model": os.environ.get("OLLAMA_MODEL", "mistral"), "prompt": prompt,
                       "stream": False}).encode()
    try:
        req = urllib.request.Request(url.rstrip("/") + "/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["response"]
    except Exception:
        return None
