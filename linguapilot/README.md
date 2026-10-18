# 🧭 LinguaPilot Academy

Plateforme d'apprentissage multilingue **anglais · français · espagnol · créole haïtien**, animée par **5 agents pédagogiques**, avec diagnostic adaptatif CECRL, machine learning, gamification bienveillante, notifications et **certificats PDF vérifiables**.

Stack : **Python · Streamlit · scikit-learn · Plotly · fpdf2 · HTML/CSS/JavaScript** (jeu arcade + page vitrine GitHub Pages).

---

## ✨ Fonctionnalités

| Agent | Rôle | Ce qu'il fait |
|---|---|---|
| 🧭 **Atlas** | Diagnostic & Certification | Test de positionnement adaptatif (15 questions, méthode de l'escalier), niveau A1→C2 + usage (personnel, social, **professionnel**, **avancé**, expert), évaluation certifiante, certificat PDF avec n° de vérification |
| 🧱 **Nova** | Grammaire & Vocabulaire | Exercices choisis par ML (~70 % de réussite visée), répétition espacée, flashcards, **arcade HTML/JS** chronométrée avec combos |
| 🎧 **Griot** | Compréhension & Culture | Grands discours (American Rhetoric, Miller Center, Vie publique, Nobel…), histoires originales, **chansons populaires** (références + activités), proverbes, expressions, faits culturels |
| ✍️ **Plume** | Expression & Registres | Analyse d'écrit selon 4 critères CECRL (étendue, correction, cohérence, adéquation), registres **soutenu / courant / familier / professionnel**, défis de registre |
| 🌱 **Lumi** | Coach & Progrès | Radar de compétences, courbes, prévision, profil ML, badges, quêtes du jour, classement, notifications, export RGPD |

Également : création de compte (mots de passe PBKDF2-SHA256 salés), notifications in-app (+ e-mail SMTP optionnel), bibliothèque de ressources filtrable, mode démo.

## 🧠 Machine learning

| Modèle | Usage | Données |
|---|---|---|
| RandomForest (200 arbres) | Affiner le niveau du diagnostic | `data/ml/synthetic_learners.csv` + `diagnostics.csv` |
| Régression logistique (traçage des connaissances) | p(réussite) d'un item → sélection dans la zone proximale | `data/ml/synthetic_attempts.csv` + `attempts.csv` |
| KMeans | Profils de forces/faiblesses | profils de compétences |
| Régression linéaire | Prévision de progression | historique des diagnostics |
| Lissage bayésien + oubli exponentiel | Maîtrise par compétence | `attempts.csv` |

Les modèles démarrent sur des données synthétiques puis intègrent les données réelles (bouton « Réentraîner » dans Lumi).

## 📁 Structure

```
linguapilot/
├── app.py                     # application Streamlit (routeur + pages)
├── core/
│   ├── agents.py              # 5 agents, conseils, ressources
│   ├── analysis.py            # analyse d'écrit (+ Ollama optionnel)
│   ├── auth.py                # comptes
│   ├── certificates.py        # PDF + vérification
│   ├── diagnostic.py          # test adaptatif + évaluation certifiante
│   ├── gamification.py        # XP, séries, badges, quêtes
│   ├── ml_engine.py           # modèles ML
│   ├── notifications.py       # notifications + e-mail
│   ├── storage.py             # couche CSV
│   └── ui.py                  # thème et composants
├── components/arcade.html     # jeu HTML/JavaScript
├── data/
│   ├── content/*.csv          # 10 CSV de contenu (questions, registres, culture, discours…)
│   ├── ml/*.csv               # données synthétiques + métriques
│   └── user_data/             # comptes et activité (créés à l'usage, ignorés par git)
├── docs/index.html            # page vitrine (GitHub Pages)
├── scripts/build_content.py   # régénère les CSV de contenu
└── scripts/generate_ml_data.py
```

## 🚀 Installation locale

```bash
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Déploiement GitHub + Streamlit Cloud

1. Créez un dépôt GitHub et poussez le dossier :
   ```bash
   git init && git add . && git commit -m "LinguaPilot Academy"
   git branch -M main && git remote add origin https://github.com/<vous>/linguapilot.git && git push -u origin main
   ```
2. Sur [share.streamlit.io](https://share.streamlit.io) : *New app* → dépôt → `app.py`.
3. (Optionnel) *Settings → Secrets* : collez le contenu de `.streamlit/secrets.toml.example` pour les e-mails.
4. Page vitrine : *Settings → Pages* → branche `main`, dossier `/docs`. Remplacez `APP_URL` dans `docs/index.html` par l'URL de votre app.

> ⚠️ Sur Streamlit Community Cloud, le disque est éphémère : les CSV de `data/user_data/` sont réinitialisés au redémarrage. Pour la production, branchez `core/storage.py` sur une base persistante (Supabase/PostgreSQL, Google Sheets…) — seules les fonctions `read / append / write` sont à adapter.

## 🤖 Retour génératif local (optionnel)

Avec [Ollama](https://ollama.com) :
```bash
ollama pull mistral
export OLLAMA_URL=http://localhost:11434   # OLLAMA_MODEL=mistral par défaut
streamlit run app.py
```
Plume ajoute alors un retour rédigé (niveau, points forts, corrections) à l'analyse automatique.

## ✏️ Enrichir les contenus

Modifiez les listes dans `scripts/build_content.py` puis `python scripts/build_content.py`, ou éditez directement les CSV de `data/content/` (la bonne réponse d'une question est stockée dans la colonne `answer` et doit figurer dans `options`, séparées par `|`).

## 🇭🇹 Kreyòl : référentiel Akademi Kreyòl Ayisyen

La banque créole (66 questions, A1 → C2) s'appuie sur l'**orthographe officielle de 1980** (32 graphèmes ; 1 son = 1 graphie ; aucune lettre muette), confirmée par la *Premye rezolisyon sou òtograf kreyòl ayisyen an* de l'**AKA** (juin 2017), et sur la loi du 7 avril 2014 qui crée l'Académie. Les questions concernées portent une étiquette 📜 source. Plume propose un onglet **Òtograf ofisyèl (AKA)** (tableau des graphèmes + entraînement) et signale les lettres hors alphabet et les formes courtes mal écrites.

## ⚖️ Notes

- **Chansons** : les paroles sont protégées ; la plateforme référence les titres et renvoie vers des plateformes licenciées (écoute + paroles), avec des activités pédagogiques originales.
- **Certificats** : évaluations internes référencées sur le CECRL (Conseil de l'Europe) ; ils ne remplacent pas DELF/DALF, TOEIC/IELTS/Cambridge, DELE/SIELE.
- **Analyse d'écrit** : heuristique et indicative ; elle aide à progresser, elle ne vaut pas correction humaine.
