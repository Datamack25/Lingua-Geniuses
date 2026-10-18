"""
LinguaPilot Academy — plateforme d'apprentissage multilingue à 5 agents
Anglais · Français · Espagnol · Créole haïtien

Lancer :  streamlit run app.py
"""
from __future__ import annotations
import random, time, uuid
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from core import storage as S, auth, agents as AG, diagnostic as D, analysis as AN
from core import gamification as G, notifications as N, certificates as CERT, ml_engine as ML, ui

st.set_page_config(page_title="LinguaPilot Academy", page_icon="🧭", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject()


# =============================================================== cache
@st.cache_resource(show_spinner="Entraînement des modèles de machine learning…")
def models():
    return ML.train_models()


@st.cache_data
def C(name: str) -> pd.DataFrame:
    return S.content(name)


BANK = C("questions")
CEFR = C("cecrl").set_index("level")
BADGES = C("badges")
ss = st.session_state
ss.setdefault("user", None)
ss.setdefault("lang", "en")
ss.setdefault("page", "🏠 Tableau de bord")


def lang_name(code=None):
    return S.LANGS[code or ss.lang].split(" ", 1)[1]


def current_level(lang=None) -> str | None:
    d = S.user_rows("diagnostics", ss.user["user_id"], lang or ss.lang)
    return None if d.empty else d.iloc[-1].level


def prep(df: pd.DataFrame) -> list[dict]:
    items = []
    for _, r in df.iterrows():
        q = r.to_dict()
        opts = q["options"].split("|")
        random.shuffle(opts)
        q["shuffled"] = opts
        items.append(q)
    return items


def record(q: dict, ok: bool, seconds: float, context: str):
    uid = ss.user["user_id"]
    S.append("attempts", dict(ts=S.now(), user_id=uid, lang=q["lang"], question_id=q["id"], level=q["level"],
                              skill=q["skill"], correct="1" if ok else "0", seconds=str(round(seconds, 1)),
                              context=context))
    G.add_xp(uid, G.XP["correct"] if ok else G.XP["wrong"], "correct" if ok else "wrong", q["lang"])


# =============================================================== quiz générique
def quiz_runner(key: str, items: list[dict], context: str, title: str = ""):
    stt = ss.get(f"quiz_{key}")
    if stt is None:
        stt = ss[f"quiz_{key}"] = dict(items=items, i=0, answered=False,
                                       ok=None, good=0, t0=time.time())
    items = stt["items"]
    if not items:
        st.info("Aucun exercice disponible pour ce filtre — essayez une autre compétence ou langue.")
        return
    if stt["i"] >= len(items):
        pct = round(100 * stt["good"] / len(items))
        st.balloons() if pct >= 70 else None
        st.markdown(f'<div class="qcard" style="text-align:center"><div style="font-size:2.6rem">'
                    f'{"🏆" if pct >= 80 else "🌟" if pct >= 50 else "🌱"}</div>'
                    f'<div class="q">{stt["good"]} / {len(items)} bonnes réponses ({pct} %)</div>'
                    f'<p class="small">{"Remarquable ! Vous pouvez viser le niveau supérieur." if pct >= 80 else "Beau travail, la progression est là." if pct >= 50 else "Chaque session compte : les items ratés reviendront en révision espacée."}</p></div>',
                    unsafe_allow_html=True)
        if st.button("🔄 Nouvelle session", key=f"{key}_new", type="primary"):
            del ss[f"quiz_{key}"]
            ss.pop(f"{key}_seed", None)
            st.rerun()
        return
    q = items[stt["i"]]
    st.progress(stt["i"] / len(items), text=f"{title} Question {stt['i'] + 1} / {len(items)}")
    tags = (f'<span class="tag teal">{q["level"]}</span><span class="tag">{S.SKILLS[q["skill"]]}</span>'
            + (f'<span class="tag gold">p(réussite) ML : {int(q["p_success"] * 100)} %</span>' if "p_success" in q else ""))
    st.markdown(f'<div class="qcard">{tags}<div class="q" style="margin-top:8px">{ui.esc(q["question"])}</div></div>',
                unsafe_allow_html=True)
    choice = st.radio("Votre réponse", q["shuffled"], index=None, key=f"{key}_r_{stt['i']}_{q['id']}",
                      disabled=stt["answered"], label_visibility="collapsed")
    if not stt["answered"]:
        if st.button("Valider ✔", key=f"{key}_v", type="primary", disabled=choice is None):
            ok = choice == q["answer"]
            record(q, ok, time.time() - stt["t0"], context)
            stt.update(answered=True, ok=ok, good=stt["good"] + ok, cheer=G.cheer(ok))
            st.rerun()
    else:
        cls = "feedback-ok" if stt["ok"] else "feedback-ko"
        extra = "" if stt["ok"] else f"<br>Bonne réponse : <b>{ui.esc(q['answer'])}</b>"
        st.markdown(f'<div class="{cls}"><b>{stt["cheer"]}</b>{extra}<br><span>💡 {ui.esc(q["explanation"])}</span></div>',
                    unsafe_allow_html=True)
        if st.button("Suivant →", key=f"{key}_n", type="primary"):
            stt.update(i=stt["i"] + 1, answered=False, ok=None, t0=time.time())
            st.rerun()


# =============================================================== authentification
def seed_demo(uid: str):
    """Données de démonstration réalistes sur 10 jours (pour explorer les tableaux de bord)."""
    rows, xp = [], []
    for d in range(10, -1, -1):
        day = datetime.now() - timedelta(days=d)
        for _ in range(random.randint(4, 9)):
            q = BANK[BANK.lang.isin(["en", "fr"])].sample(1).iloc[0]
            p = .45 + (10 - d) * .03 + (.15 if q.skill in ("vocabulaire", "culture") else 0)
            ok = random.random() < p
            ts = (day - timedelta(minutes=random.randint(0, 600))).isoformat(timespec="seconds")
            rows.append(dict(ts=ts, user_id=uid, lang=q.lang, question_id=q.id, level=q.level, skill=q.skill,
                             correct="1" if ok else "0", seconds=str(random.randint(6, 40)), context="demo"))
            xp.append(dict(ts=ts, user_id=uid, xp=str(10 if ok else 3), reason="correct" if ok else "wrong", lang=q.lang))
    S.append_many("attempts", rows)
    S.append_many("xp_log", xp)
    for lang, lvl, sc, dd in (("en", "B1", 54, 9), ("en", "B2", 66, 2), ("fr", "C1", 81, 5)):
        S.append("diagnostics", dict(ts=(datetime.now() - timedelta(days=dd)).isoformat(timespec="seconds"),
                 user_id=uid, lang=lang, level=lvl, score=str(sc), ml_level=lvl, ml_confidence="0.7",
                 grammaire=str(sc + 5), vocabulaire=str(sc + 8), comprehension=str(sc), registre=str(sc - 12),
                 culture=str(sc - 3), usage=D.USAGE[lvl]))


def auth_screen():
    ui.hero("LinguaPilot Academy", "Anglais · Français · Espagnol · Créole haïtien — 5 agents IA pour diagnostiquer, "
            "entraîner, certifier et vous faire aimer apprendre.")
    c1, c2 = st.columns([1.15, 1])
    with c1:
        cols = st.columns(2)
        for i, a in enumerate(AG.AGENTS.values()):
            with cols[i % 2]:
                ui.agent_card(a)
                st.write("")
        st.markdown('<div class="card"><h4>🎯 Comment ça marche</h4><p>1. Diagnostic adaptatif CECRL (A1 → C2) affiné par '
                    'machine learning · 2. Parcours personnalisé par agent · 3. Contenus authentiques : discours, '
                    'histoires, chansons, culture · 4. Évaluation certifiante et certificat PDF vérifiable.</p></div>',
                    unsafe_allow_html=True)
    with c2:
        t1, t2 = st.tabs(["🔐 Connexion", "✨ Créer un compte"])
        with t1:
            with st.form("login"):
                u = st.text_input("Identifiant")
                p = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("Se connecter", type="primary", width="stretch"):
                    user = auth.login(u, p)
                    if user:
                        ss.user = user
                        st.rerun()
                    st.error("Identifiant ou mot de passe incorrect.")
        with t2:
            with st.form("register"):
                dn = st.text_input("Prénom et nom (affiché sur vos certificats)")
                u = st.text_input("Identifiant")
                e = st.text_input("E-mail (pour les notifications, facultatif)")
                p = st.text_input("Mot de passe (8 caractères min.)", type="password")
                goal = st.selectbox("Objectif principal", ["Carrière professionnelle", "Études", "Voyage",
                                                           "Racines & culture", "Plaisir"])
                if st.form_submit_button("Créer mon compte", type="primary", width="stretch"):
                    ok, msg = auth.register(u, e, dn, p, goal=goal)
                    if ok:
                        ss.user = auth.get_user(msg)
                        st.success("Compte créé ! Bienvenue 🎉")
                        st.rerun()
                    st.error(msg)
        st.divider()
        if st.button("🚀 Explorer en mode démo (données fictives)", width="stretch"):
            name = "demo_" + uuid.uuid4().hex[:5]
            ok, uid = auth.register(name, "", "Apprenant Démo", uuid.uuid4().hex)
            seed_demo(uid)
            ss.user = auth.get_user(uid)
            st.rerun()
        st.caption("Mots de passe hachés (PBKDF2-SHA256 salé). Données stockées en CSV dans data/user_data/.")


# =============================================================== barre latérale
PAGES = ["🏠 Tableau de bord", "🧭 Atlas · Diagnostic", "🧱 Nova · Grammaire & Vocabulaire",
         "🎧 Griot · Culture & Compréhension", "✍️ Plume · Expression & Registres", "🌱 Lumi · Coach & Progrès",
         "🎓 Certificats", "🔔 Notifications", "📚 Bibliothèque", "👤 Profil"]


def sidebar():
    u = ss.user
    with st.sidebar:
        st.markdown("## 🧭 LinguaPilot")
        xp = G.total_xp(u["user_id"])
        lvl, cur, need = G.player_level(xp)
        st.markdown(f"**{ui.esc(u['display_name'])}** · Joueur niv. {lvl}")
        st.markdown(f'<div class="xpbar"><i style="width:{int(100 * cur / need)}%"></i></div>'
                    f'<div class="small" style="color:#C7D2FE !important">{xp} XP · 🔥 série {G.streak(u["user_id"])} j</div>',
                    unsafe_allow_html=True)
        st.write("")
        ss.lang = st.selectbox("Langue étudiée", list(S.LANGS), format_func=S.LANGS.get,
                               index=list(S.LANGS).index(ss.lang))
        N.generate(u["user_id"], ss.lang, lang_name())
        nb = len(N.unread(u["user_id"]))
        labels = [p if p != "🔔 Notifications" or not nb else f"🔔 Notifications ({nb})" for p in PAGES]
        idx = PAGES.index(ss.page) if ss.page in PAGES else 0
        choice = st.radio("Navigation", labels, index=idx, label_visibility="collapsed")
        ss.page = PAGES[labels.index(choice)]
        st.divider()
        if st.button("Se déconnecter", width="stretch"):
            for k in list(ss.keys()):
                del ss[k]
            st.rerun()


# =============================================================== pages
def page_dashboard():
    u = ss.user
    uid = u["user_id"]
    first = u["display_name"].split()[0]
    lvl = current_level()
    ui.hero(f"Bonjour {first} 👋", f"Langue active : {S.LANGS[ss.lang]} — "
            + (f"niveau actuel {lvl} · {D.USAGE[lvl]}" if lvl else "commencez par le diagnostic d'Atlas pour un parcours sur mesure."))
    att = S.user_rows("attempts", uid, ss.lang)
    mast = ML.skill_mastery(att)
    k = st.columns(4)
    k[0].metric("Niveau CECRL", lvl or "—")
    k[1].metric("XP total", G.total_xp(uid), f"+{G.xp_today(uid)} aujourd'hui")
    k[2].metric("Série", f"{G.streak(uid)} jour(s) 🔥")
    k[3].metric("Précision", f"{round(pd.to_numeric(att.correct).mean() * 100) if not att.empty else 0} %",
                f"{len(att)} réponses")

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("### Votre carte de compétences")
        if mast:
            radar(mast)
        else:
            st.info("Votre radar de compétences apparaîtra après vos premières réponses.")
    with c2:
        st.markdown("### 🎯 Quêtes du jour")
        for q in G.daily_quests(uid):
            st.markdown(f'<div class="quest {"done" if q["done"] else ""}"><span>{q["icon"]} {q["label"]}</span>'
                        f'<b>{"✅" if q["done"] else str(q["progress"]) + "/" + str(q["goal"])}</b></div>', unsafe_allow_html=True)
        prof, strong, weak = ML.learner_profile(mast)
        st.markdown("### 🤖 Recommandation de Lumi")
        if not lvl:
            msg = "Lancez le diagnostic adaptatif (12 questions) : Atlas situera votre niveau sur l'échelle CECRL."
            target = "🧭 Atlas · Diagnostic"
        elif weak != "-":
            ag = AG.agent_for_skill(weak)
            msg = (f"Profil : {prof}. Votre point d'appui est « {S.SKILLS[strong]} ». "
                   f"Prochaine étape : une session « {S.SKILLS[weak]} » avec {ag.emoji} {ag.name}.")
            target = next(p for p in PAGES if ag.name in p)
        else:
            msg, target = "Faites une session d'entraînement pour activer les recommandations.", PAGES[2]
        st.markdown(f'<div class="card"><p>{ui.esc(msg)}</p></div>', unsafe_allow_html=True)
        if st.button("Y aller →", type="primary"):
            ss.page = target
            st.rerun()

    st.markdown("### Vos 5 agents")
    cols = st.columns(5)
    for col, a in zip(cols, AG.AGENTS.values()):
        with col:
            ui.agent_card(a)
    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("### 🌍 Niveaux par langue")
        rows = []
        for l in S.LANGS:
            lv = current_level(l)
            rows.append({"Langue": S.LANGS[l], "Niveau": lv or "à diagnostiquer", "Usage": D.USAGE.get(lv, "—")})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    with c4:
        st.markdown("### 🏆 Classement de la semaine")
        lb = G.leaderboard()
        st.dataframe(lb, hide_index=True, width="stretch") if not lb.empty else st.caption("Pas encore de joueurs.")


def radar(mast: dict, height=330):
    cats = [S.SKILLS[s] for s in S.SKILLS]
    vals = [round(mast.get(s, 0) * 100) for s in S.SKILLS]
    fig = go.Figure(go.Scatterpolar(r=vals + vals[:1], theta=cats + cats[:1], fill="toself",
                                    line_color="#0E7490", fillcolor="rgba(14,116,144,.25)", name="Maîtrise"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], ticksuffix="%")), showlegend=False, height=height,
                      margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch")


# --------------------------------------------------------------- Atlas
def page_atlas():
    a = AG.AGENTS["atlas"]
    ui.agent_banner(a, "Test de positionnement adaptatif : la difficulté s'ajuste à chaque réponse (méthode de "
                       "l'escalier). Le niveau final combine une règle de seuil CECRL et un classifieur RandomForest.")
    key = f"diag_{ss.lang}"
    stt = ss.get(key)
    if stt is None:
        c1, c2 = st.columns([1.4, 1])
        with c1:
            st.markdown(f"### Diagnostic {S.LANGS[ss.lang]}")
            st.markdown(f"- **{D.N_DIAG} questions** · environ 8 minutes\n- 5 compétences : grammaire, vocabulaire, "
                        "compréhension, registres, culture\n- Résultat : niveau **A1 → C2**, usage (personnel, social, "
                        "professionnel, expert), conseils et ressources\n- Pas de stress : il n'y a pas de piège, "
                        "répondez spontanément 🌱")
            if st.button("Commencer le diagnostic", type="primary"):
                ss[key] = D.new_state(ss.lang)
                ss[key]["t0"] = time.time()
                st.rerun()
        with c2:
            st.dataframe(C("cecrl")[["level", "label", "usage"]].rename(
                columns={"level": "Niveau", "label": "Libellé", "usage": "Usage"}), hide_index=True, width="stretch")
        hist = S.user_rows("diagnostics", ss.user["user_id"], ss.lang)
        if not hist.empty:
            st.markdown("#### Historique")
            st.dataframe(hist[["ts", "level", "score", "ml_level", "ml_confidence", "usage"]], hide_index=True,
                         width="stretch")
        return

    if stt.get("final"):
        show_diag_result(stt["final"])
        if st.button("Refaire un diagnostic"):
            del ss[key]
            st.rerun()
        return

    if stt.get("feedback"):
        fb = stt["feedback"]
        st.progress(len(stt["asked"]) / D.N_DIAG, text=f"Question {len(stt['asked'])} / {D.N_DIAG}")
        cls = "feedback-ok" if fb["ok"] else "feedback-ko"
        st.markdown(f'<div class="{cls}"><b>{fb["cheer"]}</b><br>💡 {ui.esc(fb["expl"])}</div>', unsafe_allow_html=True)
        if st.button("Continuer →", type="primary"):
            stt["feedback"] = None
            if stt["done"]:
                fin = D.finalize(stt, models())
                save_diag(fin)
                stt["final"] = fin
            st.rerun()
        return

    q = stt["current"] or D.next_question(stt, BANK)
    if q is None:
        fin = D.finalize(stt, models()); save_diag(fin); stt["final"] = fin; st.rerun()
    st.progress(len(stt["asked"]) / D.N_DIAG, text=f"Question {len(stt['asked']) + 1} / {D.N_DIAG}")
    st.markdown(f'<div class="qcard"><span class="tag">{S.SKILLS[q["skill"]]}</span>'
                f'<div class="q" style="margin-top:8px">{ui.esc(q["question"])}</div></div>', unsafe_allow_html=True)
    choice = st.radio("Réponse", q["shuffled"], index=None, key=f"dq_{q['id']}", label_visibility="collapsed")
    if st.button("Valider ✔", type="primary", disabled=choice is None):
        ok = D.answer(stt, choice, time.time() - stt.get("t0", time.time()))
        record(q, ok, time.time() - stt.get("t0", time.time()), "diagnostic")
        stt["t0"] = time.time()
        stt["feedback"] = dict(ok=ok, cheer=G.cheer(ok), expl=q["explanation"])
        st.rerun()


def save_diag(fin: dict):
    uid = ss.user["user_id"]
    ps = fin["per_skill"]
    S.append("diagnostics", dict(ts=S.now(), user_id=uid, lang=ss.lang, level=fin["level"], score=str(fin["score"]),
             ml_level=fin["ml_level"], ml_confidence=str(fin["ml_confidence"]),
             **{s: ("" if ps[s] is None else str(ps[s])) for s in S.SKILLS}, usage=fin["usage"]))
    G.add_xp(uid, G.XP["diagnostic"], "diagnostic", ss.lang)
    N.push(uid, "diag_result", f"🧭 Diagnostic {lang_name()} : niveau {fin['level']}",
           f"{fin['usage']}. Vos agents ont préparé un parcours personnalisé.")


def show_diag_result(fin: dict):
    lvl = fin["level"]
    if not fin.get("celebrated"):
        st.balloons(); fin["celebrated"] = True
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown(f"### Résultat — {S.LANGS[ss.lang]}")
        ui.level_badge(lvl, CEFR.loc[lvl, "label"], fin["usage"])
        st.write("")
        st.markdown(f'<div class="card"><p>{ui.esc(CEFR.loc[lvl, "descripteur"])}</p>'
                    f'<p class="small" style="margin-top:6px">Équivalence indicative ACTFL : {CEFR.loc[lvl, "actfl"]}</p></div>',
                    unsafe_allow_html=True)
        st.write("")
        st.caption(f"Règle CECRL : {fin['rule_level']} · Modèle ML : {fin['ml_level']} "
                   f"(confiance {int(fin['ml_confidence'] * 100)} %) · Score : {fin['score']} %")
    with c2:
        p = pd.DataFrame({"Niveau": list(fin["proba"]), "Probabilité": list(fin["proba"].values())})
        p["Niveau"] = pd.Categorical(p["Niveau"], S.LEVELS, ordered=True)
        fig = px.bar(p.sort_values("Niveau"), x="Niveau", y="Probabilité", color_discrete_sequence=["#0E7490"],
                     title="Distribution de probabilité du modèle")
        fig.update_layout(height=280, margin=dict(t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", yaxis_tickformat=".0%")
        st.plotly_chart(fig, width="stretch")
    st.markdown("### Compétences et plan d'amélioration")
    ps = {k: v for k, v in fin["per_skill"].items() if v is not None}
    for sk, v in sorted(ps.items(), key=lambda x: x[1]):
        ag = AG.agent_for_skill(sk)
        with st.expander(f"{ag.emoji} {S.SKILLS[sk]} — {v} %  ·  pris en charge par {ag.name}", expanded=v < 60):
            st.progress(v / 100)
            for t in AG.advice_for(sk, lvl, ss.lang):
                st.markdown(f"- {t}")
            ui.resource_list(AG.resources_for(ss.lang, sk, lvl, 3))
    with st.expander("🔍 Détail des réponses"):
        st.dataframe(pd.DataFrame(fin["results"])[["level", "skill", "question", "choice", "answer", "correct"]],
                     hide_index=True, width="stretch")


# --------------------------------------------------------------- Nova
def page_nova():
    a = AG.AGENTS["nova"]
    lvl = current_level() or "A2"
    ui.agent_banner(a, f"Niveau de référence : {lvl}. Les exercices sont choisis par le modèle de traçage des "
                       "connaissances pour viser ~70 % de réussite : assez facile pour rester motivé, assez dur pour progresser.")
    t1, t2, t3, t4 = st.tabs(["🎯 Entraînement ciblé", "🔁 Révision espacée", "🃏 Flashcards", "🎮 Arcade"])
    att = S.user_rows("attempts", ss.user["user_id"], ss.lang)
    with t1:
        sk = st.segmented_control("Compétence", ["Toutes", "grammaire", "vocabulaire"], default="Toutes",
                                  format_func=lambda s: S.SKILLS.get(s, s), key="nova_sk")
        bank = BANK[(BANK.lang == ss.lang) & BANK.skill.isin(["grammaire", "vocabulaire"])]
        sel = ML.recommend_questions(models(), bank, att, lvl, n=8, skill=None if sk in (None, "Toutes") else sk)
        quiz_runner(f"nova_{ss.lang}_{sk}", prep(sel), "nova", "Session Nova ·")
        with st.expander("📘 Conseils de Nova"):
            for s_ in ("grammaire", "vocabulaire"):
                st.markdown(f"**{S.SKILLS[s_]}**")
                for t in AG.advice_for(s_, lvl, ss.lang):
                    st.markdown(f"- {t}")
            ui.resource_list(AG.resources_for(ss.lang, "grammaire", lvl, 4))
    with t2:
        wrong = att[att.correct == "0"].question_id.unique() if not att.empty else []
        right_after = set(att[att.correct == "1"].question_id) if not att.empty else set()
        due = [w for w in wrong if w not in right_after] or list(wrong)
        st.caption("Répétition espacée : les items ratés reviennent jusqu'à ce qu'ils soient maîtrisés.")
        if len(due) == 0:
            st.success("Rien à réviser pour le moment — bravo ! 🎉")
        else:
            quiz_runner(f"rev_{ss.lang}", prep(BANK[BANK.id.isin(due)].head(10)), "revision", "Révision ·")
    with t3:
        voc = C("vocabulaire")
        voc = voc[voc.lang == ss.lang].reset_index(drop=True)
        ss.setdefault("fc_i", 0)
        ss.setdefault("fc_show", False)
        w = voc.iloc[ss.fc_i % len(voc)]
        st.markdown(f'<div class="qcard" style="text-align:center;padding:40px"><div class="small">{ss.fc_i % len(voc) + 1} / {len(voc)}</div>'
                    f'<div style="font-size:2.2rem;font-weight:800;color:#14213D">{ui.esc(w.word)}</div>'
                    f'<div style="font-size:1.3rem;color:#0E7490;margin-top:10px;min-height:30px">{ui.esc(w.traduction) if ss.fc_show else "…"}</div></div>',
                    unsafe_allow_html=True)
        b = st.columns(3)
        if b[0].button("👁️ Retourner", width="stretch"):
            ss.fc_show = not ss.fc_show; st.rerun()
        if b[1].button("✅ Je savais", width="stretch"):
            G.add_xp(ss.user["user_id"], 2, "flashcard", ss.lang); ss.fc_i += 1; ss.fc_show = False; st.rerun()
        if b[2].button("🔁 À revoir", width="stretch"):
            ss.fc_i += 1; ss.fc_show = False; st.rerun()
    with t4:
        voc = C("vocabulaire")
        pairs = voc[voc.lang == ss.lang][["word", "traduction"]].values.tolist()
        html = open(S.ROOT / "components" / "arcade.html", encoding="utf-8").read()
        page = html.replace("__DATA__", json.dumps({"lang": ss.lang, "pairs": pairs}, ensure_ascii=False))
        if hasattr(st, "iframe"):
            st.iframe(page, height=560)
        else:
            components.html(page, height=560, scrolling=False)
        k = f"arcade_{datetime.now().date()}_{ss.lang}"
        if not ss.get(k) and st.button("🎁 Réclamer mes XP Arcade du jour (+25)"):
            G.add_xp(ss.user["user_id"], G.XP["arcade"], "arcade", ss.lang); ss[k] = True
            st.toast("+25 XP ! 🎮"); st.rerun()


# --------------------------------------------------------------- Griot
def page_griot():
    a = AG.AGENTS["griot"]
    lvl = current_level() or "B1"
    ui.agent_banner(a, "Apprendre une langue, c'est entrer dans une culture : discours historiques, histoires, "
                       "chansons populaires, proverbes et faits culturels.")
    t1, t2, t3, t4, t5 = st.tabs(["🎤 Grands discours", "📖 Histoires", "🎵 Chansons", "🎭 Culture & proverbes",
                                  "🎧 Compréhension"])
    uid = ss.user["user_id"]
    with t1:
        d = C("discours")
        d = d[d.lang == ss.lang]
        st.caption("Textes et enregistrements sur les sites de référence (American Rhetoric, Miller Center, Vie publique, "
                   "Nobel Prize…). Méthode : écoute globale → lecture du texte → repérage des figures de style → "
                   "imitation à voix haute (shadowing).")
        cols = st.columns(3)
        for i, (_, r) in enumerate(d.iterrows()):
            with cols[i % 3]:
                yr = f" · {r.annee}" if str(r.annee) != "0" else ""
                st.markdown(f'<div class="card"><h4>🎤 {ui.esc(r.titre)}</h4><p><b>{ui.esc(r.orateur)}</b>{yr}</p>'
                            f'<div style="margin:8px 0"><span class="tag teal">{r.level}</span><span class="tag gold">{ui.esc(r.registre)}</span></div>'
                            f'<p class="small">{ui.esc(r.themes)}</p>'
                            f'<p style="margin-top:8px"><a href="{ui.esc(r.url)}" target="_blank">📜 Texte / source ↗</a>'
                            + (f' &nbsp;·&nbsp; <a href="{ui.esc(r.ecouter)}" target="_blank">▶ Écouter</a>' if r.ecouter else "")
                            + '</p></div>',
                            unsafe_allow_html=True)
                st.write("")
        if st.button("✅ J'ai étudié un discours aujourd'hui (+15 XP)"):
            G.add_xp(uid, G.XP["culture"], "culture", ss.lang); st.toast("+15 XP 🎤")
    with t2:
        h = C("histoires")
        h = h[h.lang == ss.lang]
        for _, r in h.iterrows():
            with st.expander(f"📖 {r.title}  ·  {r.level}"):
                st.markdown(f'<div class="card" style="font-size:1.05rem;line-height:1.7"><p style="color:#1F2937">{ui.esc(r.text)}</p></div>',
                            unsafe_allow_html=True)
                opts = r.options.split("|")
                random.Random(r.title).shuffle(opts)
                ch = st.radio(r.question, opts, index=None, key=f"st_{r.title}")
                if st.button("Vérifier", key=f"stb_{r.title}"):
                    if ch == r.answer:
                        st.success(G.cheer(True)); G.add_xp(uid, G.XP["story"], "story", ss.lang)
                    else:
                        st.warning(f"{G.cheer(False)} Réponse : {r.answer}")
    with t3:
        so = C("chansons")
        so = so[so.lang == ss.lang]
        st.info("🎵 Les paroles sont protégées par le droit d'auteur : LinguaPilot ne les reproduit pas. Écoutez la chanson "
                "et lisez les paroles sur une plateforme licenciée, puis faites l'activité proposée par Griot.")
        cols = st.columns(2)
        for i, (_, r) in enumerate(so.iterrows()):
            with cols[i % 2]:
                yr = f" ({r.annee})" if str(r.annee) != "0" else ""
                st.markdown(f'<div class="card"><h4>🎵 {ui.esc(r.titre)}</h4><p><b>{ui.esc(r.artiste)}</b>{yr}</p>'
                            f'<div style="margin:8px 0"><span class="tag teal">{r.level}</span><span class="tag pink">{ui.esc(r.registre)}</span>'
                            f'<span class="tag">{ui.esc(r.themes)}</span></div>'
                            f'<p><b>Activité :</b> {ui.esc(r.activite)}</p>'
                            f'<p style="margin-top:8px"><a href="{ui.esc(r.ecouter)}" target="_blank">▶ Écouter</a> &nbsp;·&nbsp; '
                            f'<a href="{ui.esc(r.paroles_licenciees)}" target="_blank">📝 Paroles (Genius)</a></p></div>',
                            unsafe_allow_html=True)
                st.write("")
    with t4:
        cu = C("culture")
        cu = cu[cu.lang == ss.lang]
        cols = st.columns(3)
        for i, (_, r) in enumerate(cu.iterrows()):
            icon = {"proverbe": "🪶", "expression": "💬", "fait": "🌍"}[r.type]
            with cols[i % 3]:
                st.markdown(f'<div class="card"><span class="tag gold">{icon} {r.type}</span><span class="tag teal">{r.level}</span>'
                            f'<h4 style="margin-top:8px">{ui.esc(r["item"])}</h4><p>{ui.esc(r.signification)}</p></div>',
                            unsafe_allow_html=True)
                st.write("")
        st.markdown("#### 🧩 Mini-défi : que signifie cette expression ?")
        exp = cu[cu.type != "fait"]
        if len(exp) >= 3:
            seed = ss.setdefault("cu_seed", random.randint(0, 9999))
            row = exp.sample(1, random_state=seed).iloc[0]
            opts = [row.signification] + exp[exp["item"] != row["item"]].sample(min(3, len(exp) - 1), random_state=seed).signification.tolist()
            random.Random(seed).shuffle(opts)
            ch = st.radio(f"« {row['item']} »", opts, index=None, key=f"cu_{seed}")
            c = st.columns(2)
            if c[0].button("Vérifier ma réponse", key="cu_v"):
                if ch == row.signification:
                    st.success(G.cheer(True) + " +15 XP"); G.add_xp(uid, G.XP["culture"], "culture", ss.lang)
                else:
                    st.warning(f"{G.cheer(False)} Réponse : {row.signification}")
            if c[1].button("Autre expression 🔄", key="cu_n"):
                ss.cu_seed = random.randint(0, 9999); st.rerun()
    with t5:
        bank = BANK[(BANK.lang == ss.lang) & BANK.skill.isin(["comprehension", "culture"])]
        sel = ML.recommend_questions(models(), bank, S.user_rows("attempts", uid, ss.lang), lvl, n=6)
        quiz_runner(f"griot_{ss.lang}", prep(sel), "griot", "Session Griot ·")
        with st.expander("🎧 Ressources de Griot"):
            ui.resource_list(AG.resources_for(ss.lang, "comprehension", lvl, 6))


# --------------------------------------------------------------- Plume
PROMPTS = {
    "A1": "Présentez-vous : nom, ville, famille, ce que vous aimez.",
    "A2": "Racontez votre dernier week-end.",
    "B1": "Décrivez un voyage marquant et ce qu'il vous a appris.",
    "B2": "Rédigez un e-mail professionnel pour demander un rendez-vous à un client.",
    "C1": "Argumentez : le télétravail améliore-t-il la productivité ?",
    "C2": "Rédigez un éditorial sur la place des langues créoles dans l'éducation.",
}


def page_plume():
    a = AG.AGENTS["plume"]
    lvl = current_level() or "B1"
    uid = ss.user["user_id"]
    ui.agent_banner(a, "Grille d'évaluation inspirée des critères qualitatifs du CECRL : étendue, correction, "
                       "cohérence et adéquation sociolinguistique (registre).")
    t1, t2, t3 = st.tabs(["📝 Analyse de mon texte", "🎩 Table des registres", "🎯 Défis registres"])
    with t1:
        c1, c2 = st.columns([1.4, 1])
        with c1:
            st.markdown(f"**Sujet suggéré ({lvl}) :** {PROMPTS[lvl]}")
            reg = st.segmented_control("Registre visé", ["courant", "soutenu", "professionnel", "familier"],
                                       default="professionnel" if lvl in ("B2", "C1", "C2") else "courant",
                                       format_func=lambda r: AN.REG_LABEL[r], key="plume_reg")
            text = st.text_area(f"Écrivez en {lang_name()} (80 à 250 mots recommandés)", height=230, key="plume_txt")
            go_ = st.button("Analyser avec Plume ✍️", type="primary", disabled=len(text.split()) < 5)
        with c2:
            st.markdown("**Ce que Plume évalue**")
            st.markdown("- **Étendue** : richesse et précision du lexique\n- **Correction** : erreurs fréquentes, "
                        "ponctuation\n- **Cohérence** : connecteurs, organisation\n- **Adéquation** : le ton "
                        "correspond-il au registre visé ?")
            st.caption("Analyse automatique indicative. Pour un retour génératif, lancez Ollama en local et "
                       "définissez la variable OLLAMA_URL.")
        if go_:
            r = AN.analyze(text, ss.lang, reg or "courant")
            ss.plume_res = (r, text, reg)
            S.append("writings", dict(ts=S.now(), user_id=uid, lang=ss.lang, register_target=reg, words=str(r["words"]),
                     level_est=r["level"], etendue=str(r["etendue"]), correction=str(r["correction"]),
                     coherence=str(r["coherence"]), adequation=str(r["adequation"]), **{"global": str(r["global_score"])},
                     register_detected=r["register_detected"]))
            G.add_xp(uid, G.XP["writing"], "writing", ss.lang)
        if ss.get("plume_res"):
            r, text, reg = ss.plume_res
            st.divider()
            m = st.columns(5)
            m[0].metric("Niveau estimé", r["level"])
            m[1].metric("Score global", f"{r['global_score']}/100")
            m[2].metric("Mots", r["words"])
            m[3].metric("Diversité lexicale", r["ttr"])
            m[4].metric("Registre détecté", AN.REG_LABEL[r["register_detected"]])
            crit = pd.DataFrame({"Critère": ["Étendue", "Correction", "Cohérence", "Adéquation"],
                                 "Score": [r["etendue"], r["correction"], r["coherence"], r["adequation"]]})
            fig = px.bar(crit, x="Score", y="Critère", orientation="h", range_x=[0, 100], text="Score",
                         color="Score", color_continuous_scale=["#FDBA74", "#FDE68A", "#5EEAD4", "#0E7490"])
            fig.update_layout(height=230, margin=dict(t=10, b=10), coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.plotly_chart(fig, width="stretch")
            with c2:
                st.markdown("**🔧 Points à corriger**")
                for i in r["issues"] or ["Aucune erreur fréquente détectée 👏"]:
                    st.markdown(f"- {i}")
                st.markdown("**🌱 Conseils de Plume**")
                for t in r["advice"]:
                    st.markdown(f"- {t}")
            fb = AN.ollama_feedback(text, lang_name(), reg)
            if fb:
                st.markdown("**🤖 Retour génératif (Ollama)**")
                st.info(fb)
            ui.resource_list(AG.resources_for(ss.lang, "registre", lvl, 3))
    with t2:
        rg = C("registres")
        rg = rg[rg.lang == ss.lang].drop(columns="lang").rename(columns={
            "sens": "Sens (FR)", "soutenu": "🎩 Soutenu", "courant": "🙂 Courant", "familier": "😎 Familier",
            "professionnel": "💼 Professionnel"})
        st.dataframe(rg, hide_index=True, width="stretch")
        st.caption("Règle d'or : on choisit le registre selon l'interlocuteur, le canal (oral/écrit) et l'enjeu. "
                   "Le registre professionnel est neutre, précis et courtois ; le soutenu est réservé à l'écrit formel et aux discours.")
    with t3:
        rg = C("registres")
        rg = rg[rg.lang == ss.lang]
        seed = ss.setdefault("rg_seed", random.randint(0, 9999))
        row = rg.sample(1, random_state=seed).iloc[0]
        col = random.Random(seed).choice(["soutenu", "courant", "familier", "professionnel"])
        st.markdown(f'<div class="qcard"><span class="tag pink">Défi registre</span><div class="q" style="margin-top:8px">'
                    f'« {ui.esc(row[col])} »</div><p class="small">À quel registre appartient cette formulation ? (sens : {ui.esc(row.sens)})</p></div>',
                    unsafe_allow_html=True)
        ch = st.radio("Registre", ["soutenu", "courant", "familier", "professionnel"], index=None, horizontal=True,
                      format_func=lambda r: AN.REG_LABEL[r], key=f"rg_{seed}")
        c = st.columns(2)
        if c[0].button("Vérifier", key="rg_v", type="primary", disabled=ch is None):
            if ch == col:
                st.success(G.cheer(True) + " +10 XP"); G.add_xp(uid, 10, "correct", ss.lang)
            else:
                st.warning(f"{G.cheer(False)} C'était : {AN.REG_LABEL[col]}.")
            st.markdown(f"**Les 4 versions :** 🎩 {row.soutenu} · 🙂 {row.courant} · 😎 {row.familier} · 💼 {row.professionnel}")
        if c[1].button("Défi suivant 🔄", key="rg_n"):
            ss.rg_seed = random.randint(0, 9999); st.rerun()
        st.divider()
        bank = BANK[(BANK.lang == ss.lang) & (BANK.skill == "registre")]
        quiz_runner(f"plume_{ss.lang}", prep(bank.sample(frac=1, random_state=1)), "plume", "Registres ·")


# --------------------------------------------------------------- Lumi
def page_lumi():
    a = AG.AGENTS["lumi"]
    uid = ss.user["user_id"]
    ui.agent_banner(a, "Votre tableau de bord d'apprentissage : chaque réponse alimente les modèles de machine learning "
                       "qui personnalisent votre parcours.")
    att = S.user_rows("attempts", uid, ss.lang)
    diags = S.user_rows("diagnostics", uid, ss.lang)
    mast = ML.skill_mastery(att)
    t1, t2, t3, t4 = st.tabs(["📈 Progression", "🧠 Machine learning", "🏅 Badges & quêtes", "💾 Mes données"])
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Maîtrise par compétence")
            radar(mast) if mast else st.info("Pas encore de données.")
        with c2:
            st.markdown("#### Précision quotidienne")
            if not att.empty:
                a2 = att.assign(day=pd.to_datetime(att.ts).dt.date, c=pd.to_numeric(att.correct))
                daily = a2.groupby("day").agg(precision=("c", "mean"), reponses=("c", "size")).reset_index()
                fig = go.Figure()
                fig.add_bar(x=daily.day, y=daily.reponses, name="Réponses", marker_color="#E7E5DF", yaxis="y2")
                fig.add_scatter(x=daily.day, y=daily.precision, name="Précision", line=dict(color="#0E7490", width=3),
                                mode="lines+markers")
                fig.update_layout(height=330, yaxis=dict(tickformat=".0%", range=[0, 1]),
                                  yaxis2=dict(overlaying="y", side="right", showgrid=False),
                                  margin=dict(t=10, b=10), legend=dict(orientation="h"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Répondez à quelques exercices pour voir votre courbe.")
        if not diags.empty:
            st.markdown("#### Historique des diagnostics")
            dd = diags.assign(score=pd.to_numeric(diags.score))
            fig = px.line(dd, x="ts", y="score", markers=True, text="level", color_discrete_sequence=["#C9A227"])
            fig.update_traces(textposition="top center")
            fig.update_layout(height=260, margin=dict(t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch")
            fc = ML.forecast_progress(diags)
            if fc:
                msg = (f"Tendance : {fc['slope_per_week']:+} points/semaine."
                       + (f" À ce rythme, prochain palier ({fc['next_threshold']} %) dans ~{fc['days_to_next']} jours."
                          if fc["days_to_next"] else " Accélérez avec 10 minutes par jour pour lancer la courbe !"))
                st.success("🔮 Prévision (régression linéaire) — " + msg)
    with t2:
        m = models()
        prof, strong, weak = ML.learner_profile(mast)
        c1, c2, c3 = st.columns(3)
        c1.metric("Profil d'apprenant", prof)
        c2.metric("Précision du classifieur de niveau", f"{int(m['metrics']['rf_accuracy'] * 100)} %")
        c3.metric("AUC traçage des connaissances", m["metrics"]["kt_auc"])
        st.markdown("""
| Modèle | Rôle | Données |
|---|---|---|
| **RandomForest** (200 arbres) | Affiner le niveau CECRL du diagnostic | `synthetic_learners.csv` + `diagnostics.csv` |
| **Régression logistique** | Probabilité de réussir un item → zone proximale ~70 % | `synthetic_attempts.csv` + `attempts.csv` |
| **KMeans** (4 clusters) | Profils de forces / faiblesses | profils de compétences |
| **Régression linéaire** | Prévision de progression | historique des diagnostics |
| **Lissage bayésien + oubli exponentiel** (demi-vie 14 j) | Maîtrise par compétence | `attempts.csv` |
""")
        imp = pd.DataFrame({"Variable": list(m["importances"]), "Importance": list(m["importances"].values())})
        fig = px.bar(imp.sort_values("Importance"), x="Importance", y="Variable", orientation="h",
                     color_discrete_sequence=["#14213D"], title="Importance des variables (classifieur de niveau)")
        fig.update_layout(height=320, margin=dict(t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")
        if st.button("🔁 Réentraîner les modèles avec les nouvelles données"):
            models.clear(); st.toast("Modèles réentraînés ✔"); st.rerun()
    with t3:
        got = G.badges(uid)
        cols = st.columns(5)
        for i, (_, b) in enumerate(BADGES.iterrows()):
            with cols[i % 5]:
                st.markdown(f'<div class="badge {"" if b.code in got else "off"}"><div class="i">{b.icon}</div>'
                            f'<b>{ui.esc(b.nom)}</b><div class="small">{ui.esc(b.condition)}</div></div>', unsafe_allow_html=True)
                st.write("")
        st.markdown("#### Quêtes du jour")
        for q in G.daily_quests(uid):
            st.markdown(f'<div class="quest {"done" if q["done"] else ""}"><span>{q["icon"]} {q["label"]}</span>'
                        f'<b>{"✅" if q["done"] else str(q["progress"]) + "/" + str(q["goal"])}</b></div>', unsafe_allow_html=True)
        if all(q["done"] for q in G.daily_quests(uid)):
            k = f"quest_bonus_{datetime.now().date()}"
            if not ss.get(k) and st.button("🎁 Récupérer le bonus de quêtes (+50 XP)", type="primary"):
                G.add_xp(uid, G.XP["quest"], "quest"); ss[k] = True; st.balloons()
    with t4:
        st.caption("Vos données vous appartiennent : téléchargez-les au format CSV (RGPD – droit à la portabilité).")
        cols = st.columns(4)
        for i, t in enumerate(["attempts", "diagnostics", "writings", "xp_log"]):
            df = S.user_rows(t, uid)
            cols[i].download_button(f"⬇ {t}.csv ({len(df)})", df.to_csv(index=False).encode(), f"{t}.csv",
                                    "text/csv", width="stretch")


# --------------------------------------------------------------- Certificats
def page_certs():
    uid = ss.user["user_id"]
    ui.agent_banner(AG.AGENTS["atlas"], "Évaluation certifiante : questions du niveau visé, du niveau inférieur et deux "
                    "items du niveau supérieur. Réussite : ≥ 70 % au global et ≥ 60 % sur les items du niveau visé.")
    t1, t2, t3 = st.tabs(["📝 Passer une évaluation", "🗂️ Mes certificats", "🔎 Vérifier un certificat"])
    with t1:
        lvl0 = current_level() or "A1"
        lvl = st.select_slider("Niveau visé", S.LEVELS, value=lvl0)
        st.caption(f"Niveau recommandé d'après votre diagnostic : {lvl0}")
        key = f"exam_{ss.lang}_{lvl}"
        if key not in ss:
            if st.button(f"Commencer l'évaluation {lang_name()} {lvl}", type="primary"):
                ss[key] = dict(items=D.build_exam(BANK, ss.lang, lvl), result=None)
                st.rerun()
        else:
            ex = ss[key]
            if ex["result"] is None:
                with st.form(f"f_{key}"):
                    answers = {}
                    for i, q in enumerate(ex["items"], 1):
                        answers[q["id"]] = st.radio(f"**{i}.** {q['question']}", q["shuffled"], index=None, key=f"{key}_{q['id']}")
                    if st.form_submit_button("Remettre ma copie", type="primary"):
                        if any(v is None for v in answers.values()):
                            st.warning("Répondez à toutes les questions avant de remettre votre copie.")
                        else:
                            for q in ex["items"]:
                                record(q, answers[q["id"]] == q["answer"], 15, "exam")
                            ex["result"] = D.grade_exam(ex["items"], answers, lvl)
                            ex["answers"] = answers
                            st.rerun()
            else:
                r = ex["result"]
                c1, c2 = st.columns([1, 1.3])
                with c1:
                    ui.level_badge(lvl, CEFR.loc[lvl, "label"], CEFR.loc[lvl, "usage"])
                    st.metric("Score global", f"{r['score']} %", f"niveau visé : {r['target_score']} %")
                with c2:
                    for sk, v in r["per_skill"].items():
                        st.progress(v / 100, text=f"{S.SKILLS[sk]} : {v} %")
                if r["passed"]:
                    if "cert" not in ex:
                        cid, pdf = CERT.issue(ss.user, ss.lang, lvl, r, CEFR.loc[lvl].to_dict())
                        ex["cert"] = (cid, pdf)
                        G.add_xp(uid, G.XP["exam"], "exam", ss.lang)
                        N.push(uid, "cert", f"🎓 Certificat {lang_name()} {lvl} obtenu !", f"N° {cid} — mention {r['mention']}.")
                        st.balloons()
                    cid, pdf = ex["cert"]
                    st.success(f"🎓 Félicitations ! Certificat {lvl} obtenu — mention {r['mention']} (N° {cid}).")
                    st.download_button("⬇ Télécharger mon certificat PDF", pdf, f"certificat_{ss.lang}_{lvl}_{cid}.pdf",
                                       "application/pdf", type="primary")
                else:
                    st.warning("Pas encore cette fois — et c'est normal : chaque tentative vous rapproche du but. 🌱 "
                               "Travaillez les compétences les plus basses avec vos agents, puis retentez.")
                    for sk, v in sorted(r["per_skill"].items(), key=lambda x: x[1])[:2]:
                        ag = AG.agent_for_skill(sk)
                        st.markdown(f"**{ag.emoji} {S.SKILLS[sk]} ({v} %)** — avec {ag.name} :")
                        for t in AG.advice_for(sk, lvl, ss.lang)[:2]:
                            st.markdown(f"- {t}")
                with st.expander("Corrigé détaillé"):
                    for q in ex["items"]:
                        ok = ex["answers"][q["id"]] == q["answer"]
                        st.markdown(f"{'✅' if ok else '❌'} **{q['question']}** — {q['answer']}  \n<span class='small'>💡 {q['explanation']}</span>",
                                    unsafe_allow_html=True)
                if st.button("Nouvelle évaluation"):
                    del ss[key]; st.rerun()
    with t2:
        cs = S.user_rows("certificates", uid)
        if cs.empty:
            st.info("Aucun certificat pour le moment. Votre premier est à portée de main ! 🎓")
        for _, c in cs.iterrows():
            cc = st.columns([3, 1])
            cc[0].markdown(f'<div class="card"><h4>🎓 {S.LANGS[c.lang]} — {c.level}</h4><p>{ui.esc(c.usage)} · score {c.score} % · '
                           f'{c.ts[:10]} · N° {c.cert_id}</p></div>', unsafe_allow_html=True)
            sc = int(c.score)
            res = dict(score=sc, mention="Excellence" if sc >= 90 else "Très bien" if sc >= 80 else "Bien", per_skill={})
            att = S.user_rows("attempts", uid, c.lang)
            att = att[att.context == "exam"]
            res["per_skill"] = {s: round(pd.to_numeric(g.correct).mean() * 100) for s, g in att.groupby("skill")}
            pdf = CERT.render(c.cert_id, c["hash"], c.display_name, c.lang, c.level, res, CEFR.loc[c.level].to_dict(),
                              pd.to_datetime(c.ts).date())
            cc[1].download_button("⬇ PDF", pdf, f"certificat_{c.cert_id}.pdf", "application/pdf", key=c.cert_id,
                                  width="stretch")
    with t3:
        cid = st.text_input("Numéro de certificat (ex. LP-1A2B3C4D5E)")
        if cid:
            v = CERT.verify(cid)
            if v:
                st.success(f"✅ Certificat authentique : {v['display_name']} — {S.LANGS[v['lang']]} {v['level']} "
                           f"({v['score']} %), délivré le {v['ts'][:10]}. Empreinte : {v['hash']}")
            else:
                st.error("❌ Aucun certificat ne correspond à ce numéro.")


# --------------------------------------------------------------- Notifications
def page_notifs():
    uid = ss.user["user_id"]
    st.markdown("## 🔔 Notifications")
    n = S.user_rows("notifications", uid).iloc[::-1]
    c = st.columns([1, 1, 3])
    if c[0].button("Tout marquer comme lu"):
        N.mark_all_read(uid); st.rerun()
    smtp = st.secrets.get("smtp") if hasattr(st, "secrets") and _has_secrets() else None
    if smtp and ss.user.get("email") and c[1].button("📧 Recevoir mon récap par e-mail"):
        body = "\n".join(f"- {r.title} : {r.body}" for _, r in n.head(8).iterrows())
        ok, msg = N.send_email(smtp, ss.user["email"], "Votre récap LinguaPilot", body)
        st.toast(msg)
    for _, r in n.iterrows():
        st.markdown(f'<div class="notif {"read" if r.read == "1" else ""}"><b>{ui.esc(r.title)}</b>'
                    f'<span class="small" style="float:right">{r.ts.replace("T", " ")[:16]}</span><br>'
                    f'<span>{ui.esc(r.body)}</span></div>', unsafe_allow_html=True)
    if n.empty:
        st.caption("Aucune notification.")


def _has_secrets() -> bool:
    try:
        return "smtp" in st.secrets
    except Exception:
        return False


# --------------------------------------------------------------- Bibliothèque
def page_library():
    st.markdown("## 📚 Bibliothèque de ressources")
    r = C("ressources")
    c = st.columns(3)
    langs = c[0].multiselect("Langues", list(S.LANGS), default=[ss.lang], format_func=S.LANGS.get)
    skills = c[1].multiselect("Compétences", sorted(r.skill.unique()))
    types = c[2].multiselect("Types", sorted(r.type.unique()))
    f = r[r.lang.isin(langs or list(S.LANGS))]
    if skills: f = f[f.skill.isin(skills)]
    if types: f = f[f.type.isin(types)]
    st.caption(f"{len(f)} ressources")
    ui.resource_list(f)


# --------------------------------------------------------------- Profil
def page_profile():
    u = ss.user
    st.markdown("## 👤 Mon profil")
    with st.form("profile"):
        dn = st.text_input("Nom affiché (certificats)", u["display_name"])
        em = st.text_input("E-mail", u.get("email", ""))
        goals = ["Carrière professionnelle", "Études", "Voyage", "Racines & culture", "Plaisir"]
        goal = st.selectbox("Objectif", goals, index=goals.index(u["goal"]) if u.get("goal") in goals else 0)
        if st.form_submit_button("Enregistrer", type="primary"):
            users = S.read("users")
            m = users.user_id == u["user_id"]
            users.loc[m, ["display_name", "email", "goal"]] = [dn, em, goal]
            S.write("users", users)
            ss.user = auth.get_user(u["user_id"])
            st.success("Profil mis à jour ✔")
    st.caption(f"Membre depuis le {u['created_at'][:10]} · identifiant : {u['username']}")


# =============================================================== routeur
if ss.user is None:
    auth_screen()
else:
    sidebar()
    {
        PAGES[0]: page_dashboard, PAGES[1]: page_atlas, PAGES[2]: page_nova, PAGES[3]: page_griot,
        PAGES[4]: page_plume, PAGES[5]: page_lumi, PAGES[6]: page_certs, PAGES[7]: page_notifs,
        PAGES[8]: page_library, PAGES[9]: page_profile,
    }[ss.page]()
