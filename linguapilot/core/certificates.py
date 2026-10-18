"""Génération des certificats PDF (fpdf2) + registre de vérification."""
from __future__ import annotations
import hashlib, uuid
from datetime import date
from fpdf import FPDF
from . import storage as S

LANG_NAMES = {"en": "Anglais", "fr": "Français", "es": "Espagnol", "ht": "Créole haïtien"}
NAVY, GOLD, TEAL = (20, 33, 61), (201, 162, 39), (14, 116, 144)


def _t(s: str) -> str:
    """fpdf core fonts = latin-1 : on remplace les caractères hors jeu."""
    rep = {"’": "'", "“": '"', "”": '"', "—": "-", "–": "-", "…": "...", "œ": "oe", "Œ": "OE", "·": "."}
    for a, b in rep.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "ignore").decode("latin-1")


def issue(user: dict, lang: str, level: str, result: dict, cefr: dict) -> tuple[str, bytes]:
    cert_id = "LP-" + uuid.uuid4().hex[:10].upper()
    h = hashlib.sha256(f"{cert_id}|{user['user_id']}|{lang}|{level}|{result['score']}".encode()).hexdigest()[:16]
    pdf = render(cert_id, h, user.get("display_name", ""), lang, level, result, cefr, date.today())
    S.append("certificates", dict(cert_id=cert_id, ts=S.now(), user_id=user["user_id"],
                                  display_name=user.get("display_name", ""), lang=lang, level=level,
                                  score=str(result["score"]), usage=cefr["usage"], hash=h))
    return cert_id, pdf


def render(cert_id, h, name, lang, level, result, cefr, d) -> bytes:
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.add_page()
    W, H = 297, 210
    # fond et cadres
    pdf.set_fill_color(250, 248, 242); pdf.rect(0, 0, W, H, "F")
    pdf.set_draw_color(*NAVY); pdf.set_line_width(2.2); pdf.rect(8, 8, W - 16, H - 16)
    pdf.set_draw_color(*GOLD); pdf.set_line_width(.7); pdf.rect(12, 12, W - 24, H - 24)
    pdf.set_fill_color(*NAVY); pdf.rect(12, 12, W - 24, 26, "F")
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(12, 17); pdf.cell(W - 24, 10, _t("LinguaPilot Academy"), align="C")
    pdf.set_font("Helvetica", "", 10); pdf.set_xy(12, 27)
    pdf.cell(W - 24, 6, _t("Plateforme d'apprentissage multilingue - Anglais . Français . Espagnol . Créole haïtien"), align="C")

    pdf.set_text_color(*NAVY); pdf.set_font("Times", "B", 28); pdf.set_xy(12, 46)
    pdf.cell(W - 24, 12, _t("CERTIFICAT DE COMPÉTENCES LINGUISTIQUES"), align="C")
    pdf.set_font("Times", "I", 13); pdf.set_xy(12, 60); pdf.set_text_color(80, 80, 80)
    pdf.cell(W - 24, 7, _t("Il est certifié que"), align="C")
    pdf.set_font("Times", "B", 26); pdf.set_text_color(*TEAL); pdf.set_xy(12, 69)
    pdf.cell(W - 24, 12, _t(name), align="C")
    pdf.set_draw_color(*GOLD); pdf.set_line_width(.4); pdf.line(90, 83, W - 90, 83)
    pdf.set_font("Times", "", 13); pdf.set_text_color(60, 60, 60); pdf.set_xy(12, 87)
    pdf.cell(W - 24, 7, _t(f"a validé l'évaluation certifiante en {LANG_NAMES[lang]} au niveau"), align="C")

    # médaillon niveau
    cx, cy = W / 2, 112
    pdf.set_fill_color(*GOLD); pdf.ellipse(cx - 17, cy - 17, 34, 34, "F")
    pdf.set_fill_color(*NAVY); pdf.ellipse(cx - 14, cy - 14, 28, 28, "F")
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(cx - 14, cy - 6); pdf.cell(28, 12, level, align="C")
    pdf.set_text_color(*NAVY); pdf.set_font("Helvetica", "B", 13); pdf.set_xy(12, 131)
    pdf.cell(W - 24, 7, _t(f"{cefr['label']}  -  {cefr['usage']}"), align="C")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(70, 70, 70); pdf.set_xy(40, 139)
    pdf.multi_cell(W - 80, 5, _t(f"Descripteur CECRL : {cefr['descripteur']}  (équivalence indicative ACTFL : {cefr['actfl']})"), align="C")

    # scores par compétence
    y0 = 153
    pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(*NAVY); pdf.set_xy(30, y0)
    pdf.cell(80, 5, _t(f"Score global : {result['score']} %   -   Mention : {result['mention']}"))
    x, y = 30, y0 + 8
    for i, (sk, v) in enumerate(result["per_skill"].items()):
        col = x + (i % 3) * 82
        row = y + (i // 3) * 8
        pdf.set_font("Helvetica", "", 9); pdf.set_text_color(60, 60, 60); pdf.set_xy(col, row)
        pdf.cell(28, 4, _t(S.SKILLS[sk]))
        pdf.set_fill_color(225, 225, 225); pdf.rect(col + 28, row + .5, 40, 3, "F")
        pdf.set_fill_color(*TEAL); pdf.rect(col + 28, row + .5, 40 * v / 100, 3, "F")
        pdf.set_xy(col + 70, row); pdf.cell(10, 4, f"{v}%")

    # pied : signature, date, vérification
    pdf.set_font("Helvetica", "", 8); pdf.set_text_color(90, 90, 90)
    pdf.set_xy(22, 180); pdf.cell(80, 4, _t(f"Délivré le {d.strftime('%d/%m/%Y')}"))
    pdf.set_xy(22, 184); pdf.cell(80, 4, _t(f"N° {cert_id}  .  empreinte {h}"))
    pdf.set_xy(22, 188); pdf.cell(80, 4, _t("Vérification : onglet Certificats > Vérifier un certificat"))
    pdf.set_font("Times", "I", 14); pdf.set_text_color(*NAVY); pdf.set_xy(W - 112, 178)
    pdf.cell(90, 6, "Atlas", align="C")
    pdf.set_draw_color(*NAVY); pdf.line(W - 102, 185, W - 32, 185)
    pdf.set_font("Helvetica", "", 8); pdf.set_xy(W - 112, 186)
    pdf.cell(90, 4, _t("Agent d'évaluation - LinguaPilot"), align="C")
    pdf.set_font("Helvetica", "I", 6.5); pdf.set_text_color(130, 130, 130); pdf.set_xy(12, 193)
    pdf.cell(W - 24, 4, _t("Certificat d'évaluation interne référencé sur le CECRL (Conseil de l'Europe). "
                           "Il ne remplace pas les certifications officielles (DELF/DALF, TOEIC/IELTS/Cambridge, DELE/SIELE)."), align="C")
    return bytes(pdf.output())


def verify(cert_id: str) -> dict | None:
    c = S.read("certificates")
    row = c[c.cert_id == cert_id.strip().upper()]
    return None if row.empty else row.iloc[0].to_dict()
