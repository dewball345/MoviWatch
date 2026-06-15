#!/usr/bin/env python3
# Fillable PDF + answer-key PDF for Spanish Practice Test #2.
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = letter
L = 0.75 * inch
R = PAGE_W - 0.75 * inch
TOP = PAGE_H - 0.7 * inch
BOTTOM = 0.7 * inch
WIDTH = R - L
BODY = "Helvetica"; BOLD = "Helvetica-Bold"; ITAL = "Helvetica-Oblique"
GRAY = HexColor("#555555")
BOX_BORDER = HexColor("#9aa0a6")
BOX_FILL = HexColor("#f3f6fb")

class Doc:
    def __init__(self, path, fillable=True):
        self.c = canvas.Canvas(path, pagesize=letter); self.fillable = fillable
        self.y = TOP; self.fid = 0
    def wrap(self, text, font, size, maxw):
        words = text.split(" "); lines, cur = [], ""
        for w in words:
            test = w if not cur else cur + " " + w
            if stringWidth(test, font, size) <= maxw: cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines
    def ensure(self, need):
        if self.y - need < BOTTOM: self.c.showPage(); self.y = TOP
    def text(self, s, font=BODY, size=11, leading=15, indent=0, color=None, gap=0):
        for line in self.wrap(s, font, size, WIDTH - indent):
            self.ensure(leading); self.c.setFont(font, size)
            self.c.setFillColor(color if color else HexColor("#000000"))
            self.c.drawString(L + indent, self.y - size, line); self.y -= leading
        self.c.setFillColor(HexColor("#000000")); self.y -= gap
    def space(self, amt): self.y -= amt
    def rule(self):
        self.ensure(10); self.c.setStrokeColor(HexColor("#cccccc"))
        self.c.line(L, self.y, R, self.y); self.y -= 12
    def title(self, s):
        self.ensure(26); self.c.setFont(BOLD, 16); self.c.drawString(L, self.y - 16, s); self.y -= 26
    def h2(self, s):
        self.space(6); self.ensure(20); self.c.setFont(BOLD, 12.5)
        self.c.setFillColor(HexColor("#1a3b6e")); self.c.drawString(L, self.y - 13, s)
        self.c.setFillColor(HexColor("#000000")); self.y -= 19
    def instr(self, s):
        self.text(s, font=ITAL, size=9.5, leading=12.5, color=GRAY, gap=3)
    def field(self, w, h, multiline=False, indent=0):
        self.ensure(h + 6); self.fid += 1; bottom = self.y - h
        if self.fillable:
            self.c.acroForm.textfield(name=f"f{self.fid}", x=L + indent, y=bottom, width=w,
                height=h, borderStyle="inset", borderColor=BOX_BORDER, fillColor=BOX_FILL,
                borderWidth=0.7, forceBorder=True, fontName=BODY, fontSize=11,
                fieldFlags="multiline" if multiline else "")
        else:
            self.c.setStrokeColor(BOX_BORDER); self.c.setFillColor(BOX_FILL)
            self.c.rect(L + indent, bottom, w, h, stroke=1, fill=1); self.c.setFillColor(HexColor("#000000"))
        self.y = bottom - 9
    def q(self, num, body, boxw=2.2*inch, h=20, multiline=False, lines=1):
        self.ensure(34); self.text(f"{num}. {body}", gap=2)
        self.field(boxw, h if not multiline else 16*lines, multiline=multiline, indent=12)
    def q_inline(self, num, label, boxw=1.9*inch, h=18):
        self.ensure(h + 8); self.c.setFont(BODY, 11)
        lab = f"{num}. {label}"; self.c.drawString(L, self.y - 12, lab)
        x = L + stringWidth(lab, BODY, 11) + 8; self.fid += 1; bottom = self.y - h
        if self.fillable:
            self.c.acroForm.textfield(name=f"f{self.fid}", x=x, y=bottom, width=boxw, height=h,
                borderStyle="inset", borderColor=BOX_BORDER, fillColor=BOX_FILL, borderWidth=0.7,
                forceBorder=True, fontName=BODY, fontSize=11)
        else:
            self.c.setStrokeColor(BOX_BORDER); self.c.setFillColor(BOX_FILL)
            self.c.rect(x, bottom, boxw, h, stroke=1, fill=1); self.c.setFillColor(HexColor("#000000"))
        self.y = bottom - 8
    def save(self): self.c.save()


def build_test(path):
    d = Doc(path, fillable=True)
    d.title("Spanish 1 - Practice Test #2")
    d.text("Name: ______________________________        Date: ________________", size=11, leading=16, gap=2)
    d.instr("Focus: ser vs. estar usage, vocabulary meaning, and o->ue / e->ie stem-changers. "
            "Present tense only - no preterite. Type your answers in the boxes; check the separate answer-key PDF.")
    d.rule()

    d.h2("Part 1 - Vocabulario: what does each verb MEAN?")
    d.instr("Write the English meaning of each verb.")
    verbs = ["pedir","conseguir","seguir","repetir","dormir","volver","almorzar","encontrar",
             "pensar","querer","preferir","entender","perder","empezar","cerrar"]
    for i, v in enumerate(verbs, 1):
        d.q_inline(i, f"{v}", boxw=2.7*inch, h=18)

    d.h2("Part 2 - Ser o Estar (choose the right one AND conjugate)")
    d.instr("Fill each blank with the correct form of SER or ESTAR. Permanent/identity = ser; temporary/location/feeling = estar.")
    p2 = [
        "Yo ______ de Colombia.",
        "Mi padre ______ profesor.",
        "La sopa ______ muy caliente ahora.",
        "Nosotros ______ cansados después del partido.",
        "Madrid ______ en España.",
        "Hoy ______ martes.",
        "Mi hermana ______ muy inteligente.",
        "Los niños ______ en el parque.",
        "El examen ______ a las nueve. (the event happens at 9:00)",
        "La ventana ______ abierta.",
        "Mi abuela ______ enferma esta semana.",
        "El libro ______ interesante.",
        "Mi amigo ______ nervioso por el examen.",
        "Las flores ______ bonitas.",
        "La puerta ______ cerrada.",
    ]
    for i, s in enumerate(p2, 16):
        d.q(i, s, boxw=2.0*inch)

    d.h2("Part 3 - Ser o Estar: the rule")
    d.instr("For each situation, write SER or ESTAR.")
    p3 = ["to tell where you are FROM (origin)", "to say how you FEEL right now",
          "to describe someone's personality", "to say WHERE something is located",
          "to tell the day or the date", "to describe a temporary condition"]
    for i, s in enumerate(p3, 31):
        d.q(i, s, boxw=1.8*inch)

    d.h2("Part 4 - Stem-changers: write your OWN sentences")
    d.instr("Write a complete, original Spanish sentence using each verb. Use a different subject each time.")
    p4 = ["dormir (o->ue)","volver (o->ue)","poder (o->ue) + a 2nd verb","almorzar (o->ue)",
          "pensar (e->ie)","querer (e->ie)","preferir (e->ie)","entender (e->ie)"]
    for i, s in enumerate(p4, 37):
        d.q(i, s, boxw=WIDTH-12, h=20)

    d.h2("Part 5 - Traduccion (English -> Spanish)")
    d.instr("Translate each sentence into Spanish.")
    p5 = ["My family sleeps late on Sundays.","I want to eat lunch now.","We return home at five.",
          "She does not understand the homework.","They prefer the red shirt.","My brother is tired today.",
          "My teacher is from Mexico.","The students are in the library.","I think about my family.",
          "Can you close the door?"]
    for i, s in enumerate(p5, 45):
        d.q(i, s, boxw=WIDTH-12, h=20)

    d.h2("Part 6 - Escribir (paragraph)")
    d.instr("Write 5-6 sentences about your weekend. Use at least THREE stem-changing verbs (o->ue or e->ie) "
            "AND at least TWO sentences that use ser or estar correctly.")
    d.field(WIDTH, 120, multiline=True)
    d.save()


def build_key(path):
    d = Doc(path, fillable=False)
    d.title("Spanish 1 - Practice Test #2 - ANSWER KEY")
    d.instr("Grade yourself. For ser/estar, the reason is in parentheses - that's the part to master.")
    d.rule()
    blocks = [
        ("Part 1 - Vocabulario", [
            "1. pedir = to ask for / to request", "2. conseguir = to get / to obtain",
            "3. seguir = to follow / to continue", "4. repetir = to repeat", "5. dormir = to sleep",
            "6. volver = to return", "7. almorzar = to have lunch", "8. encontrar = to find",
            "9. pensar = to think", "10. querer = to want / to love", "11. preferir = to prefer",
            "12. entender = to understand", "13. perder = to lose / to miss", "14. empezar = to begin",
            "15. cerrar = to close"]),
        ("Part 2 - Ser o Estar (with the reason)", [
            "16. soy (origin)", "17. es (profession)", "18. está (temporary condition)",
            "19. estamos (feeling)", "20. está (location)", "21. es (day)", "22. es (trait)",
            "23. están (location)", "24. es (time an EVENT takes place -> 'es a las nueve')",
            "25. está (condition)", "26. está (temporary health)", "27. es (trait)",
            "28. está (emotion)", "29. son (trait)", "30. está (condition)"]),
        ("Part 3 - The rule", [
            "31. ser", "32. estar", "33. ser", "34. estar", "35. ser", "36. estar"]),
        ("Part 4 - Stem-changer sentences (samples; yours can differ)", [
            "37. Yo duermo ocho horas cada noche.", "38. Nosotros volvemos a casa después de la escuela.",
            "39. Yo puedo jugar al fútbol los sábados.", "40. Mi familia y yo almorzamos juntos los domingos.",
            "41. Yo pienso en mis vacaciones.", "42. Mis hermanos quieren un perro.",
            "43. Mi madre y yo preferimos el té.", "44. Yo no entiendo la tarea de matemáticas."]),
        ("Part 5 - Traduccion", [
            "45. Mi familia duerme tarde los domingos.", "46. Yo quiero almorzar ahora.",
            "47. Nosotros volvemos a casa a las cinco.", "48. Ella no entiende la tarea.",
            "49. Ellos prefieren la camisa roja.", "50. Mi hermano está cansado hoy. (temporary -> estar)",
            "51. Mi profesor(a) es de México. (origin -> ser)",
            "52. Los estudiantes están en la biblioteca. (location -> estar)",
            "53. Yo pienso en mi familia. (pensar en = to think about)",
            "54. ¿Puedes cerrar la puerta? (poder + infinitive)"]),
        ("Part 6 - Escribir (sample)", [
            "Los fines de semana yo duermo hasta tarde. Mi familia y yo almorzamos juntos y después "
            "yo juego al fútbol. Mi hermana prefiere ver películas en casa. Mis padres están cansados "
            "los sábados, pero están contentos. El próximo fin de semana queremos ir a la playa porque "
            "el clima es bonito."]),
        ("Remember (ser vs estar)", [
            "SER = permanent / identity: origin, profession, personality, traits, dates, event time.",
            "ESTAR = temporary / location: feelings, conditions, health, where something is."]),
    ]
    for header, items in blocks:
        d.h2(header)
        for it in items:
            d.text(it, size=10.5, leading=14, indent=6)
    d.save()


build_test("/home/user/MoviWatch/study/practice-test-2-fillable.pdf")
build_key("/home/user/MoviWatch/study/practice-test-2-answer-key.pdf")
print("done")
