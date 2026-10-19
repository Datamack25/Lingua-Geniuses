# LinguaPilot — application Android

Application Android native qui embarque la plateforme **LinguaPilot** (5 agents, anglais / français / créole haïtien / espagnol). L'APK est compilé automatiquement par GitHub Actions : aucun Android Studio n'est nécessaire.

## Ce que fait l'application

- Icône LinguaPilot sur l'écran d'accueil, écran de démarrage, plein écran sans barre de navigateur
- **Micro** pour les exercices de prononciation (autorisation demandée la première fois)
- **Import de fichiers** (CSV de progression, documents) depuis le téléphone
- **Téléchargement des certificats PDF et exports CSV** → dossier `Téléchargements/LinguaPilot`
- Connexion conservée (cookies), y compris la connexion Streamlit / GitHub / Google
- Liens externes (ressources, chansons, vidéos) ouverts dans le navigateur ou l'appli concernée
- Écran « Pas de connexion » avec bouton Réessayer
- Bouton retour : revient en arrière, double appui pour quitter

## Mise en place (5 minutes)

1. **Copie ces dossiers à la racine de ton dépôt LinguaPilot sur GitHub** :
   - `android/`
   - `.github/workflows/android-apk.yml`

   (Si ton dépôt a déjà un dossier `.github/workflows`, ajoute simplement le fichier dedans.)

2. **Indique l'adresse de ta plateforme**, au choix :
   - dans GitHub : *Settings → Secrets and variables → Actions → onglet Variables → New repository variable*
     Nom : `LINGUAPILOT_URL` — Valeur : l'adresse de ton app (ex. `https://linguapilot-xxxx.streamlit.app`)
   - ou directement dans `android/gradle.properties` (ligne `LINGUAPILOT_URL=`).

3. **Lance la compilation** : onglet *Actions* → *LinguaPilot Android (APK)* → *Run workflow*.
   Elle se relance aussi automatiquement à chaque modification du dossier `android/`.

4. **Récupère l'APK** : à la fin du run (≈ 4 min), section *Artifacts* → `LinguaPilot-APK` (fichier zip contenant `LinguaPilot-debug.apk`).

## Installer sur le téléphone

1. Envoie le fichier `LinguaPilot-debug.apk` sur ton téléphone (Drive, mail, câble…).
2. Ouvre-le ; Android demande d'autoriser l'installation depuis cette source → accepte.
3. LinguaPilot apparaît dans tes applications.

Pour une mise à jour, installe simplement le nouvel APK par-dessus (tes données et ta connexion sont conservées).

## Version signée (Play Store / diffusion publique) — optionnel

L'APK *debug* suffit pour toi et tes testeurs. Pour une version signée :

1. Crée une clé une seule fois (sur un ordinateur avec Java) :
   ```bash
   keytool -genkeypair -v -keystore linguapilot.jks -alias linguapilot -keyalg RSA -keysize 2048 -validity 10000
   base64 -w0 linguapilot.jks > keystore.txt
   ```
2. Ajoute 4 **secrets** GitHub (*Settings → Secrets and variables → Actions → Secrets*) :
   `ANDROID_KEYSTORE_BASE64` (contenu de keystore.txt), `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS` (`linguapilot`), `ANDROID_KEY_PASSWORD`.
3. Le workflow produit alors aussi `LinguaPilot.apk` (signé). Pousse un tag `v1.0.0` pour qu'il soit publié automatiquement dans les *Releases* du dépôt.

Garde précieusement le fichier `.jks` et ses mots de passe : sans eux, impossible de publier une mise à jour de la même application.

## Bon à savoir

- **Streamlit Community Cloud met l'app en veille** après quelques jours sans visite : au réveil, l'appli affiche le bouton « Yes, get this app back up » — c'est normal, un appui suffit.
- L'application a besoin d'Internet (les agents tournent sur le serveur).
- Personnaliser : couleurs dans `android/app/src/main/res/values/colors.xml`, textes dans `strings.xml`, icône dans `drawable/ic_launcher_foreground.xml`, identifiant d'application (`com.linguapilot.app`) dans `android/app/build.gradle`.
- Android 8.0 ou plus récent.

## Structure

```
android/
├── settings.gradle, build.gradle, gradle.properties
└── app/
    ├── build.gradle
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/linguapilot/app/MainActivity.java
        └── res/ (layout, couleurs, textes, thème, icône)
.github/workflows/android-apk.yml
```
