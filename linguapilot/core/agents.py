"""Les 5 agents pédagogiques de LinguaPilot : rôles, compétences, conseils personnalisés."""
from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
from . import storage as S


@dataclass
class Agent:
    code: str
    name: str
    emoji: str
    title: str
    mission: str
    skills: list[str] = field(default_factory=list)
    color: str = "#0E7490"


AGENTS = {
    "atlas": Agent("atlas", "Atlas", "🧭", "Diagnostic & Certification",
                   "Mesure votre niveau réel (test adaptatif CECRL + ML), organise les évaluations "
                   "certifiantes et délivre vos certificats PDF.", [], "#1E3A8A"),
    "nova": Agent("nova", "Nova", "🧱", "Grammaire & Vocabulaire",
                  "Construit vos fondations : exercices ciblés dans votre zone de progression, "
                  "répétition espacée, flashcards et arcade.", ["grammaire", "vocabulaire"], "#7C3AED"),
    "griot": Agent("griot", "Griot", "🎧", "Compréhension & Culture",
                   "Vous fait voyager : grands discours, histoires, chansons populaires, proverbes et "
                   "culture des pays de la langue.", ["comprehension", "culture"], "#B45309"),
    "plume": Agent("plume", "Plume", "✍️", "Expression & Registres",
                   "Analyse vos textes (grille CECRL) et vous entraîne aux registres soutenu, courant, "
                   "familier et professionnel.", ["registre"], "#BE185D"),
    "lumi": Agent("lumi", "Lumi", "🌱", "Coach, Progrès & Motivation",
                  "Suit votre apprentissage par machine learning, envoie vos notifications, vos quêtes "
                  "et célèbre chaque progrès.", [], "#047857"),
}

BAND = lambda lvl: "deb" if lvl in ("A1", "A2") else ("int" if lvl in ("B1", "B2") else "adv")

ADVICE = {
 "grammaire": {
   "deb": ["Maîtrisez d'abord le présent des verbes les plus fréquents (être, avoir, aller, faire).",
           "Apprenez les structures par phrases complètes plutôt que par règles isolées.",
           "10 minutes par jour valent mieux qu'une heure par semaine."],
   "int": ["Travaillez les temps du passé et leur contraste (action ponctuelle vs habitude).",
           "Repérez les déclencheurs du subjonctif / conditionnel et créez vos propres exemples.",
           "Réécrivez une phrase de 3 façons différentes pour assouplir la syntaxe."],
   "adv": ["Travaillez les structures emphatiques et l'inversion pour un style plus soutenu.",
           "Analysez la grammaire de textes juridiques ou journalistiques de qualité.",
           "Traquez vos erreurs fossilisées : tenez un carnet de vos 10 erreurs récurrentes."]},
 "vocabulaire": {
   "deb": ["Apprenez par thèmes (maison, travail, transports) avec 5 à 10 mots par jour.",
           "Associez chaque mot à une image ou à une phrase personnelle.",
           "Révisez à J+1, J+3, J+7 (répétition espacée : Nova s'en charge)."],
   "int": ["Apprenez les collocations (« prendre une décision ») plutôt que des mots seuls.",
           "Lisez un article par jour et notez 3 expressions nouvelles.",
           "Travaillez les faux amis entre le français et la langue cible."],
   "adv": ["Constituez un lexique spécialisé de votre domaine (finance, conformité, droit…).",
           "Explorez les nuances entre quasi-synonymes et les expressions idiomatiques.",
           "Lisez la presse de référence et la littérature contemporaine."]},
 "comprehension": {
   "deb": ["Écoutez des contenus très courts (1-2 min) adaptés aux apprenants, plusieurs fois.",
           "Lisez d'abord la question, puis cherchez l'information dans le texte.",
           "Utilisez les sous-titres dans la langue cible, pas en français."],
   "int": ["Alternez écoute globale (idée générale) et écoute détaillée (chiffres, noms).",
           "Podcasts et journaux à débit ralenti, puis à débit normal.",
           "Pratiquez le « shadowing » : répétez à voix haute juste après l'orateur."],
   "adv": ["Écoutez des débats, discours politiques et conférences sans sous-titres.",
           "Analysez la rhétorique : anaphores, implicites, ironie.",
           "Variez les accents régionaux et les registres."]},
 "registre": {
   "deb": ["Apprenez les formules de politesse de base (s'il vous plaît, merci, excusez-moi).",
           "Distinguez le tutoiement et le vouvoiement (ou leurs équivalents).",
           "Mémorisez 3 salutations : formelle, neutre, familière."],
   "int": ["Comparez une même idée dans les 4 registres (table des registres de Plume).",
           "Entraînez-vous à rédiger des e-mails professionnels courts.",
           "Repérez les marques d'oralité dans les chansons et les séries."],
   "adv": ["Maîtrisez les formules épistolaires soutenues et administratives.",
           "Adaptez votre discours à l'interlocuteur : négociation, réunion, présentation.",
           "Lisez des textes officiels et des éditoriaux pour le registre soutenu."]},
 "culture": {
   "deb": ["Découvrez les fêtes, plats et traditions des pays de la langue.",
           "Écoutez des chansons populaires en lisant les paroles sur une plateforme licenciée.",
           "Apprenez 1 proverbe par semaine."],
   "int": ["Regardez un film ou une série par semaine en version originale.",
           "Lisez l'histoire des grands événements nationaux.",
           "Étudiez un grand discours historique (bibliothèque de Griot)."],
   "adv": ["Lisez la littérature classique et contemporaine.",
           "Suivez l'actualité politique et culturelle dans la langue.",
           "Analysez les références implicites (humour, allusions historiques)."]},
}

LANG_TIPS = {
 "en": "Astuce anglais : travaillez le rythme et l'accent tonique ; les discours d'American Rhetoric sont idéaux.",
 "fr": "Astuce français : soignez les accords du participe passé et le registre soutenu de l'écrit administratif.",
 "es": "Astuce espagnol : maîtrisez ser/estar et le subjonctif, pierres angulaires de la langue.",
 "ht": "Astuce kreyòl : les marqueurs te / ap / pral / ta portent tout le système verbal — maîtrisez-les en premier.",
}


def advice_for(skill: str, level: str, lang: str) -> list[str]:
    tips = list(ADVICE.get(skill, {}).get(BAND(level), []))
    return tips + [LANG_TIPS[lang]] if skill in ("grammaire", "registre") else tips


def resources_for(lang: str, skill: str | None = None, level: str = "B1", n: int = 6) -> pd.DataFrame:
    r = S.content("ressources")
    r = r[r.lang == lang]
    if skill:
        r = pd.concat([r[r.skill == skill], r[r.skill != skill]])
    r = r[r.level_min.map(lambda l: S.LEVELS.index(l) <= S.LEVELS.index(level) + 1)]
    return r.head(n)


def agent_for_skill(skill: str) -> Agent:
    for a in AGENTS.values():
        if skill in a.skills:
            return a
    return AGENTS["lumi"]
