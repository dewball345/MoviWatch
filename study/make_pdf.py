#!/usr/bin/env python3
# Generates a fillable Spanish practice-test PDF (typeable answer boxes)
# plus a separate answer-key PDF.
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = letter
L = 0.75 * inch          # left margin
R = PAGE_W - 0.75 * inch # right margin
TOP = PAGE_H - 0.7 * inch
BOTTOM = 0.7 * inch
WIDTH = R - L

BODY = "Helvetica"; BOLD = "Helvetica-Bold"; ITAL = "Helvetica-Oblique"
GRAY = HexColor("#555555")
BOX_BORDER = HexColor("#9aa0a6")
BOX_FILL = HexColor("#f3f6fb")

class Doc:
    def __init__(self, path, fillable=True):
        self.c = canvas.Canvas(path, pagesize=letter)
        self.fillable = fillable
        self.y = TOP
        self.fid = 0

    def wrap(self, text, font, size, maxw):
        words = text.split(" ")
        lines, cur = [], ""
        for w in words:
            test = w if not cur else cur + " " + w
            if stringWidth(test, font, size) <= maxw:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines

    def ensure(self, need):
        if self.y - need < BOTTOM:
            self.c.showPage(); self.y = TOP

    def text(self, s, font=BODY, size=11, leading=15, indent=0, color=None, gap=0):
        for line in self.wrap(s, font, size, WIDTH - indent):
            self.ensure(leading)
            self.c.setFont(font, size)
            self.c.setFillColor(color if color else HexColor("#000000"))
            self.c.drawString(L + indent, self.y - size, line)
            self.y -= leading
        self.c.setFillColor(HexColor("#000000"))
        self.y -= gap

    def space(self, amt): self.y -= amt

    def rule(self):
        self.ensure(10)
        self.c.setStrokeColor(HexColor("#cccccc"))
        self.c.line(L, self.y, R, self.y); self.y -= 12

    def title(self, s):
        self.ensure(26); self.c.setFont(BOLD, 16)
        self.c.drawString(L, self.y - 16, s); self.y -= 26

    def h2(self, s):
        self.space(6); self.ensure(20); self.c.setFont(BOLD, 12.5)
        self.c.setFillColor(HexColor("#1a3b6e"))
        self.c.drawString(L, self.y - 13, s)
        self.c.setFillColor(HexColor("#000000")); self.y -= 19

    def instr(self, s):
        self.text(s, font=ITAL, size=9.5, leading=12.5, color=GRAY, gap=3)

    def field(self, w, h, multiline=False, indent=0):
        self.ensure(h + 6)
        self.fid += 1
        bottom = self.y - h
        if self.fillable:
            flags = "multiline" if multiline else ""
            self.c.acroForm.textfield(
                name=f"f{self.fid}", x=L + indent, y=bottom, width=w, height=h,
                borderStyle="inset", borderColor=BOX_BORDER, fillColor=BOX_FILL,
                borderWidth=0.7, forceBorder=True, fontName=BODY, fontSize=11,
                fieldFlags=flags)
        else:
            self.c.setStrokeColor(BOX_BORDER); self.c.setFillColor(BOX_FILL)
            self.c.rect(L + indent, bottom, w, h, stroke=1, fill=1)
            self.c.setFillColor(HexColor("#000000"))
        self.y = bottom - 9

    # a numbered short-answer question: text then a box below
    def q(self, num, body, boxw=2.2*inch, h=20, multiline=False, lines=1):
        self.ensure(34)
        self.text(f"{num}. {body}", gap=2)
        self.field(boxw, h if not multiline else 16*lines, multiline=multiline, indent=12)

    # label and box on the SAME line (e.g. "32. dormir -> nosotros: [ ]")
    def q_inline(self, num, label, boxw=1.9*inch, h=18):
        self.ensure(h + 8)
        self.c.setFont(BODY, 11)
        lab = f"{num}. {label}"
        self.c.drawString(L, self.y - 12, lab)
        lw = stringWidth(lab, BODY, 11)
        x = L + lw + 8
        self.fid += 1
        bottom = self.y - h
        if self.fillable:
            self.c.acroForm.textfield(name=f"f{self.fid}", x=x, y=bottom, width=boxw,
                height=h, borderStyle="inset", borderColor=BOX_BORDER, fillColor=BOX_FILL,
                borderWidth=0.7, forceBorder=True, fontName=BODY, fontSize=11)
        else:
            self.c.setStrokeColor(BOX_BORDER); self.c.setFillColor(BOX_FILL)
            self.c.rect(x, bottom, boxw, h, stroke=1, fill=1); self.c.setFillColor(HexColor("#000000"))
        self.y = bottom - 8

    def save(self): self.c.save()


def build_test(path):
    d = Doc(path, fillable=True)
    d.title("Spanish 1 - Practice Final (Mock Test)")
    d.text("Name: ______________________________        Date: ________________",
           size=11, leading=16, gap=2)
    d.instr("Present tense only - no preterite. Suggested time: 45-60 minutes. "
            "Type your answers in the boxes, then check the separate answer-key PDF.")
    d.rule()

    d.h2("Part 1 - Completar: Verbos (present tense)")
    d.instr("Fill each blank with the correct present-tense form of the verb in parentheses.")
    d.q(1, "Mi profesor siempre ______ (decir) que debemos estudiar.")
    d.q(2, "Cuando no entiendo la tarea, yo ______ (pedir) ayuda.")
    d.q(3, "Si nosotros ______ (seguir) las instrucciones, todo sale bien.")
    d.q(4, "La maestra ______ (repetir) las palabras para que aprendamos.")
    d.q(5, "Mis amigos ______ (conseguir) buenas notas porque estudian.")

    d.h2("Part 2 - El presente progresivo")
    d.instr("Fill in each blank with the present progressive form of the verb in parentheses. (Type both words.)")
    d.q(6, "Yo ______ (estudiar) para el examen.", boxw=2.9*inch)
    d.q(7, "Mi hermano ______ (comer) en la cocina.", boxw=2.9*inch)
    d.q(8, "Nosotros ______ (ver) una película.", boxw=2.9*inch)
    d.q(9, "Mis padres ______ (dormir) ahora mismo.", boxw=2.9*inch)
    d.q(10, "¿Tú qué ______ (leer)?", boxw=2.9*inch)
    d.q(11, "Mis amigos ______ (jugar) al fútbol.", boxw=2.9*inch)

    d.h2("Part 3 - Ser vs. Estar")
    d.instr("Fill each blank with the correct form of SER or ESTAR.")
    d.q(12, "Nosotros ______ de México.")
    d.q(13, "La biblioteca ______ cerca del parque.")
    d.q(14, "Hoy ______ lunes.")
    d.q(15, "Mi madre ______ cansada hoy.")
    d.q(16, "Los estudiantes ______ inteligentes.")
    d.q(17, "El libro ______ muy interesante.")
    d.q(18, "Yo ______ nervioso porque hay un examen.")
    d.q(19, "La puerta ______ abierta.")
    d.q(20, "Mi amigo y yo ______ en la escuela.")
    d.q(21, "El carro de mi papá ______ nuevo.")

    d.h2("Part 4 - Ser vs. Estar (párrafo)")
    d.instr("Read the paragraph and fill each numbered box below with SER or ESTAR.")
    d.text("Hola. Me llamo Ana. Yo (22)___ estudiante en una escuela grande. Mi escuela "
           "(23)___ en el centro de la ciudad. Hoy (24)___ viernes y mis amigos y yo "
           "(25)___ muy contentos porque mañana no hay clases. Ahora nosotros (26)___ "
           "en la cafetería. La cafetería (27)___ limpia y la comida (28)___ deliciosa. "
           "Mi amiga Lucía (29)___ cansada. Los profesores (30)___ simpáticos. "
           "¡La vida (31)___ buena!", size=11, leading=15, gap=6)
    for n in range(22, 32):
        d.q_inline(n, "", boxw=1.5*inch, h=18)

    d.h2("Part 5 - Verbos (conjugar)")
    d.instr("Write the correct present-tense form for the subject shown.")
    d.q_inline(32, "dormir  ->  nosotros:")
    d.q_inline(33, "dormir  ->  ellos:")
    d.q_inline(34, "poder  ->  yo:")
    d.q_inline(35, "volver  ->  nosotros:")
    d.q_inline(36, "preferir  ->  nosotros:")
    d.q_inline(37, "preferir  ->  ella:")
    d.q_inline(38, "jugar  ->  nosotros:")
    d.q_inline(39, "querer  ->  yo:")
    d.q_inline(40, "pedir  ->  nosotros:")
    d.q_inline(41, "almorzar  ->  ellos:")

    d.h2("Part 6 - Situaciones (write your own sentences)")
    d.instr("Write a complete Spanish sentence using each verb. Use a different subject each time.")
    for n, v in [(42,"almorzar"),(43,"dormir"),(44,"poder + another verb"),
                 (45,"querer"),(46,"preferir"),(47,"volver"),(48,"jugar"),(49,"pensar")]:
        d.q(n, f"({v})", boxw=WIDTH-12, h=20)

    d.h2("Part 7 - Traducción (English -> Spanish)")
    d.instr("Translate each sentence into Spanish.")
    sents = [
        (50,"My sister and I play soccer in the park."),
        (51,"I am eating breakfast. (use present progressive)"),
        (52,"He can drive a car."),
        (53,"We are from Spain."),
        (54,"The students are tired."),
        (55,"They return from the store."),
        (56,"My mom prefers the blue dress."),
        (57,"I want to sleep."),
        (58,"The library is clean."),
        (59,"What are you doing? (use present progressive)"),
    ]
    for n, s in sents:
        d.q(n, s, boxw=WIDTH-12, h=20)

    d.h2("Part 8 - Escribir (paragraph)")
    d.instr("Write 5-7 sentences about what you usually do on the weekend, and mention two things you and your "
            "family want to do next weekend. Use at least FOUR different stem-changing verbs "
            "(dormir, jugar, querer, preferir, poder, volver, almorzar, pensar).")
    d.field(WIDTH, 110, multiline=True)

    d.h2("Bonus - Object pronouns (only if your class covered these)")
    d.instr("Translate into Spanish.")
    for n, s in [(1,"I see it. (it = la película)"),(2,"I give him the book."),
                 (3,"I like pizza. (use gustar)"),(4,"We like sports. (use gustar)"),
                 (5,"She buys it. (it = la camisa)")]:
        d.q(f"B{n}", s, boxw=WIDTH-12, h=20)

    d.save()


def build_key(path):
    d = Doc(path, fillable=False)
    d.title("Spanish 1 - Practice Final - ANSWER KEY")
    d.instr("Grade yourself honestly. For every miss, write the rule next to it and redo it from scratch.")
    d.rule()
    blocks = [
        ("Part 1 - Verbos", ["1. dice", "2. pido", "3. seguimos", "4. repite", "5. consiguen"]),
        ("Part 2 - Presente progresivo", [
            "6. estoy estudiando", "7. está comiendo", "8. estamos viendo",
            "9. están durmiendo  (dormir -> durmiendo, o->u)",
            "10. estás leyendo  (leer -> leyendo, i->y)", "11. están jugando"]),
        ("Part 3 - Ser vs. Estar", [
            "12. somos (origin)", "13. está (location)", "14. es (day)",
            "15. está (feeling)", "16. son (trait)", "17. es (trait)",
            "18. estoy (emotion)", "19. está (condition)", "20. estamos (location)",
            "21. es (trait)"]),
        ("Part 4 - Párrafo", [
            "22. soy", "23. está", "24. es", "25. estamos", "26. estamos",
            "27. está", "28. es", "29. está", "30. son", "31. es"]),
        ("Part 5 - Stem-changers  (32,35,36,38,40 = NO change because nosotros)", [
            "32. dormimos", "33. duermen", "34. puedo", "35. volvemos", "36. preferimos",
            "37. prefiere", "38. jugamos", "39. quiero", "40. pedimos", "41. almuerzan"]),
        ("Part 6 - Situaciones  (sample answers; yours can differ)", [
            "42. Yo almuerzo con mis amigos en la cafetería.",
            "43. Mi familia duerme tarde los sábados.",
            "44. Yo puedo jugar al tenis en el parque.",
            "45. Mis hermanos quieren un carro nuevo.",
            "46. Mi madre y yo preferimos la película de acción.",
            "47. Nosotros volvemos a casa a las cinco.",
            "48. Ellos juegan al baloncesto en el gimnasio.",
            "49. Yo pienso en mis vacaciones."]),
        ("Part 7 - Traducción", [
            "50. Mi hermana y yo jugamos al fútbol en el parque.",
            "51. Yo estoy desayunando.",
            "52. Él puede conducir un carro.",
            "53. Nosotros somos de España.",
            "54. Los estudiantes están cansados.",
            "55. Ellos vuelven de la tienda.",
            "56. Mi mamá prefiere el vestido azul.",
            "57. Yo quiero dormir.",
            "58. La biblioteca está limpia.",
            "59. ¿Qué estás haciendo?"]),
        ("Part 8 - Escribir  (sample)", [
            "Los fines de semana yo duermo hasta tarde. Por la mañana mi familia y yo "
            "almorzamos juntos y después yo juego al fútbol con mis amigos. A veces prefiero "
            "ver una película en casa. El próximo fin de semana mi hermana y yo queremos ir a "
            "la playa, y mis padres piensan visitar a mis abuelos. Nosotros volvemos a casa el domingo."]),
        ("Bonus - Object pronouns", [
            "B1. La veo.", "B2. Le doy el libro.", "B3. Me gusta la pizza.",
            "B4. Nos gustan los deportes.", "B5. Ella la compra."]),
    ]
    for header, items in blocks:
        d.h2(header)
        for it in items:
            d.text(it, size=10.5, leading=14, indent=6)
    d.save()


build_test("/home/user/MoviWatch/study/practice-test-fillable.pdf")
build_key("/home/user/MoviWatch/study/practice-test-answer-key.pdf")
print("PDFs generated.")
