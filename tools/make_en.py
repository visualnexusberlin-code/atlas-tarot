# -*- coding: utf-8 -*-
"""Generate public/en/index.html from the Spanish public/index.html.

Run from the repository root:  python3 tools/make_en.py
Every replacement must match exactly once (or the declared count); if the
Spanish page changes and a text no longer matches, the script stops and says
which one, so the English version never drifts silently.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import i18n_en as T

SRC, DST = "public/index.html", "public/en/index.html"
s = open(SRC, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"[make_en] expected {count}, found {n}: {old[:90]!r}")
    s = s.replace(old, new)


def js(v):
    return json.dumps(v, ensure_ascii=False)


def block(start, end):
    """Return (a, b) indices of the text between `start` and the first `end` after it."""
    a = s.index(start)
    b = s.index(end, a) + len(end)
    return a, b


def parse_js_literal(txt, keys):
    q = re.sub(r'([{,]\s*)(%s):' % "|".join(keys), r'\1"\2":', txt)
    return json.loads(q)


# ======================================================================= data
# --- cards
a, b = block("const ARC=[", "\n];")
arc = parse_js_literal(s[a + len("const ARC="):b - 1].strip().rstrip(";"),
                       ["n", "es", "hist", "kw", "sombra", "gaze", "img", "mirar", "amp", "q", "hs", "x", "y", "t", "d", "col", "r", "c"])
assert len(arc) == len(T.ARC) == 22
out = []
for card, en in zip(arc, T.ARC):
    assert len(card["hs"]) == len(en["hs"]), card["n"]
    card.update({k: en[k] for k in ("es", "kw", "sombra", "mirar", "amp", "q")})
    for h, (t, d) in zip(card["hs"], en["hs"]):
        h["t"], h["d"] = t, d
    for z in card["col"]:
        z["c"] = T.COLOR[z["c"]]
    card["img"] = "/" + card["img"]
    hs = ",".join("{x:%s,y:%s,t:%s,d:%s}" % (h["x"], h["y"], js(h["t"]), js(h["d"])) for h in card["hs"])
    col = ",".join("{x:%s,y:%s,r:%s,c:%s}" % (z["x"], z["y"], z["r"], js(z["c"])) for z in card["col"])
    out.append('{n:%d,es:%s,hist:%s,kw:%s,sombra:%s,gaze:%s,img:%s,\nmirar:%s,\namp:%s,\nq:%s,\nhs:[%s],col:[%s]}' % (
        card["n"], js(card["es"]), js(card["hist"]), js(card["kw"]), js(card["sombra"]), js(card["gaze"]), js(card["img"]),
        js(card["mirar"]), js(card["amp"]), js(card["q"]), hs, col))
s = s[:a] + "const ARC=[\n" + ",\n".join(out) + "\n];" + s[b:]

# --- relation texts
for name, d in (("PAREJA_TXT", T.PAREJA_TXT), ("DUO_TXT", T.DUO_TXT), ("GRADO_TXT", T.GRADO_TXT)):
    a, b = block("const %s={" % name, "};")
    if name == "PAREJA_TXT":
        body = ",".join("%s:%s" % (js(k), js(v)) for k, v in d.items())
    else:
        body = ",".join("%d:%s" % (k, js(v)) for k, v in d.items())
    s = s[:a] + "const %s={%s};" % (name, body) + s[b:]

# --- secrets
a, b = block("const SECRETOS=[", "\n];")
assert s[a:b].count("{t:") == len(T.SECRETOS)
s = s[:a] + "const SECRETOS=[\n" + ",\n".join("{t:%s,d:%s}" % (js(t), js(d)) for t, d in T.SECRETOS) + "\n];" + s[b:]

# --- timeline (keeps the category key of each entry)
a, b = block("const MITO=[", "\n];")
mito = parse_js_literal(s[a + len("const MITO="):b].strip().rstrip(";"), ["y", "k", "t", "d"])
assert len(mito) == len(T.MITO)
s = s[:a] + "const MITO=[\n" + ",\n".join("{y:%s,k:%s,t:%s,d:%s}" % (js(y), js(m["k"]), js(t), js(d)) for m, (y, t, d) in zip(mito, T.MITO)) + "\n];" + s[b:]

# --- colours
a, b = block("const COLORES=[", "\n];")
cols = parse_js_literal(s[a + len("const COLORES="):b].strip().rstrip(";"), ["n", "h", "p", "m"])
lines = []
for c in cols:
    n = T.COLOR[c["n"]]
    p, m = T.COLORES[n]
    lines.append("{n:%s,h:%s,p:%s,m:%s}" % (js(n), js(c["h"]), js(p), js(m)))
s = s[:a] + "const COLORES=[\n" + ",\n".join(lines) + "\n];" + s[b:]

# --- reading strategies
a, b = block("const ESTR={", "\n};")
keys = re.findall(r'\n  (\w+):\{d:', s[a:b])
assert keys == list(T.ESTR), keys
s = s[:a] + "const ESTR={\n" + ",\n".join("  %s:{d:%s,roles:%s}" % (k, js(d), js(r)) for k, (d, r) in T.ESTR.items()) + "\n};" + s[b:]

# --- archetypes (keeps glyphs and card links)
a, b = block("const ARQ=[", "\n];")
arq = parse_js_literal(s[a + len("const ARQ="):b].strip().rstrip(";"), ["t", "g", "ess", "j", "f", "src", "cards"])
assert len(arq) == len(T.ARQ)
s = s[:a] + "const ARQ=[\n" + ",\n".join(
    "{t:%s,g:%s,ess:%s,\n j:%s,\n f:%s,\n src:%s,cards:%s}" % (js(t), js(q["g"]), js(e), js(j), js(f), js(src), js(q["cards"]))
    for q, (t, e, j, f, src) in zip(arq, T.ARQ)) + "\n];" + s[b:]

# ======================================================================= head
rep('<html lang="es">', '<html lang="en">')
rep('<title>Speculum Arcanorum · El tarot como espejo</title>', '<title>Speculum Arcanorum · The tarot as a mirror</title>')
rep('<meta name="description" content="Una experiencia interactiva sobre los 22 Arcanos Mayores del Tarot de Marsella, leídos a través de Jung, Sallie Nichols y Alejandro Jodorowsky. Una herramienta de reflexión, no de predicción.">',
    '<meta name="description" content="An interactive experience of the 22 Major Arcana of the Tarot de Marseille, read through Jung, Sallie Nichols and Alejandro Jodorowsky. A tool for reflection, not prediction.">')
rep('<link rel="canonical" href="https://atlas-tarot.web.app/">', '<link rel="canonical" href="https://atlas-tarot.web.app/en">')
rep('<meta property="og:title" content="Speculum Arcanorum · El tarot como espejo">', '<meta property="og:title" content="Speculum Arcanorum · The tarot as a mirror">')
rep('<meta property="og:description" content="Los 22 Arcanos Mayores del Tarot de Marsella leídos con Jung, Nichols y Jodorowsky. Una experiencia de reflexión, no de predicción.">',
    '<meta property="og:description" content="The 22 Major Arcana of the Tarot de Marseille read with Jung, Nichols and Jodorowsky. An experience of reflection, not prediction.">')
rep('<meta property="og:locale" content="es_ES">', '<meta property="og:locale" content="en_GB">\n<meta property="og:locale:alternate" content="es_ES">')

# ======================================================================= header and sections
rep('aria-controls="nav">Menú</button>', 'aria-controls="nav">Menu</button>')
rep('aria-label="Secciones"', 'aria-label="Sections"')
rep('<a href="#nube">La nube</a>', '<a href="#nube">The cloud</a>')
rep('<a href="#viaje">Las cartas</a>', '<a href="#viaje">The cards</a>')
rep('<a href="#arquetipos">Los arquetipos</a>', '<a href="#arquetipos">Archetypes</a>')
rep('<a href="#mesa">La mesa</a>', '<a href="#mesa">The table</a>')
rep('<a href="#grafo">El grafo</a>', '<a href="#grafo">The graph</a>')
rep('<a href="#laboratorio">Trasfondo</a>', '<a href="#laboratorio">Background</a>')
rep('<a class="lang" href="/en" hreflang="en" lang="en" title="English version">EN</a>', '<a class="lang" href="/" hreflang="es" lang="es" title="Versión en español">ES</a>')

rep('aria-label="La nube de los arcanos"', 'aria-label="The cloud of the arcana"')
rep('<h1>Speculum Arcanorum<span>El tarot como espejo</span></h1>', '<h1>Speculum Arcanorum<span>The tarot as a mirror</span></h1>')
rep('<p>Veintidós arcanos dispersos en la nube del inconsciente. Pasa la lente: donde mira la consciencia, el caos se ordena en figura. Algunos puntos esconden secretos.</p>',
    '<p>Twenty-two arcana scattered in the cloud of the unconscious. Move the lens: wherever consciousness looks, chaos orders itself into a figure. Some points hide secrets.</p>')
rep('<a class="btn primary" href="#viaje">Ver las cartas ↓</a><span>o mueve la lente y toca una figura para abrirla</span>',
    '<a class="btn primary" href="#viaje">See the cards ↓</a><span>or move the lens and tap a figure to open it</span>')
rep('aria-label="Cerrar" data-close="panelNube"', 'aria-label="Close" data-close="panelNube"')
rep('aria-label="Índice de arcanos"', 'aria-label="Index of the arcana"')
rep('<label class="sr" for="proyectaIn">Proyecta una palabra o una pregunta</label>', '<label class="sr" for="proyectaIn">Project a word or a question</label>')
rep('placeholder="Proyecta una palabra, una pregunta, un sueño…"', 'placeholder="Project a word, a question, a dream…"')
rep('<button type="submit">Proyectar</button>', '<button type="submit">Project</button>')
rep('aria-controls="indice">Índice</button>', 'aria-controls="indice">Index</button>')
rep('id="secretosCount">Secretos <b>0</b> / 9</div>', 'id="secretosCount">Secrets <b>0</b> / 9</div>')

rep('<p class="kicker">I · El viaje del Loco</p>', '<p class="kicker">I · The Fool’s journey</p>')
rep('<h2>Veintidós estaciones de un mismo camino</h2>', '<h2>Twenty-two stations on a single path</h2>')
rep('<p class="lede">Los Arcanos Mayores pueden leerse en secuencia, como una historia sin palabras. Aquí siguen la disposición que propuso <em>Sallie Nichols</em>: el Loco fuera de la serie, como viajero, y tres filas de siete. <em>Toca una carta para entrar en ella.</em> Dentro, la lente revela detalles y colores escondidos.</p>',
    '<p class="lede">The Major Arcana can be read in sequence, like a story without words. Here they follow the layout proposed by <em>Sallie Nichols</em>: the Fool outside the series, as a traveller, and three rows of seven. <em>Tap a card to step inside it.</em> Inside, the lens reveals hidden details and colours.</p>')

rep('aria-label="Los arquetipos de Jung"', 'aria-label="Jung’s archetypes"')
rep('<p class="kicker">II · Los arquetipos</p>', '<p class="kicker">II · The archetypes</p>')
rep('<h2>Formas que se repiten en todos nosotros</h2>', '<h2>Forms that recur in all of us</h2>')
rep('<p class="lede">Para Jung, debajo de la memoria personal hay un fondo común, lo <em>inconsciente colectivo</em>, organizado por arquetipos: disposiciones que no vemos directamente, pero que generan las mismas figuras en mitos, sueños y cartas. Aquí cada arquetipo es una nube de puntos que <em>se transforma para mostrarse a sí misma</em>. Elige uno o deja que el camino avance solo.</p>',
    '<p class="lede">For Jung, beneath personal memory lies a common ground, the <em>collective unconscious</em>, organised by archetypes: dispositions we never see directly, but which generate the same figures in myths, dreams and cards. Here each archetype is a cloud of points that <em>transforms itself in order to show itself</em>. Choose one, or let the path move on by itself.</p>')
rep('<div class="arq-drag">Arrastra para girar</div>', '<div class="arq-drag">Drag to rotate</div>')
rep('aria-label="Arquetipos"></div>', 'aria-label="Archetypes"></div>')
rep('id="arqPlay" aria-label="Pausar el recorrido"', 'id="arqPlay" aria-label="Pause the sequence"')

rep('<p class="kicker">III · La mesa de lectura</p>', '<p class="kicker">III · The reading table</p>')
rep('<h2>Echar las cartas, leerse a uno mismo</h2>', '<h2>Laying out the cards, reading yourself</h2>')
rep('<p class="lede">Cuatro maneras de tender los arcanos, tomadas de Jodorowsky y de Houdouin. Ninguna predice: todas ponen imágenes frente a una pregunta para que la mirada encuentre lo que ya sabía.</p>',
    '<p class="lede">Four ways of laying out the arcana, taken from Jodorowsky and Houdouin. None of them predicts: all of them set images before a question so that the eye can find what it already knew.</p>')
rep('<label class="sr" for="estrategia">Estrategia de lectura</label>', '<label class="sr" for="estrategia">Reading strategy</label>')
rep('<option value="pma">Tres cartas · protagonista, mediador, antagonista</option>', '<option value="pma">Three cards · protagonist, mediator, antagonist</option>')
rep('<option value="pregunta">Tres cartas · el tarot hace la pregunta</option>', '<option value="pregunta">Three cards · the tarot asks the question</option>')
rep('<option value="viva">Tirada viva · seguir las miradas</option>', '<option value="viva">Living spread · follow the gazes</option>')
rep('<option value="cruz">Tirada en cruz · el centro por aritmética</option>', '<option value="cruz">Cross spread · the centre by arithmetic</option>')
rep('id="barajar">Barajar y tender</button>', 'id="barajar">Shuffle and deal</button>')
rep('id="revelar" disabled>Revelar todas</button>', 'id="revelar" disabled>Reveal all</button>')
rep('id="diarioBtn">Mi diario</button>', 'id="diarioBtn">My journal</button>')
rep('<p class="note">Piensa en una pregunta, o en ninguna. Después, baraja.</p>', '<p class="note">Think of a question, or of none. Then shuffle.</p>')
rep('class="note">¿Qué ves tú en esta tirada? (Se guarda solo en este navegador.)</label>', 'class="note">What do you see in this spread? (It is saved only in this browser.)</label>')
rep('placeholder="Escribe lo que te sugiere, sin censura. Asociación libre: la primera palabra, la primera imagen."', 'placeholder="Write what it suggests to you, without censoring. Free association: the first word, the first image."')
rep('id="guardarLectura">Guardar en mi diario</button><span class="saved" id="savedLectura">Guardado</span>', 'id="guardarLectura">Save to my journal</button><span class="saved" id="savedLectura">Saved</span>')
rep('<p class="aviso">El tarot de esta web es un instrumento de reflexión y autoconocimiento. No predice el futuro y no sustituye el consejo médico, psicológico, legal ni financiero. Si atraviesas un momento difícil, busca apoyo profesional o en personas de confianza.</p>',
    '<p class="aviso">The tarot on this website is a tool for reflection and self-knowledge. It does not predict the future and does not replace medical, psychological, legal or financial advice. If you are going through a difficult time, seek professional support or turn to people you trust.</p>')

rep('<p class="kicker">IV · El grafo de las relaciones</p>', '<p class="kicker">IV · The graph of relations</p>')
rep('<h2>Ninguna carta está sola</h2>', '<h2>No card stands alone</h2>')
rep('<p class="lede">Jodorowsky y Costa leen el tarot como una red: dos series de diez grados, dúos que repiten el mismo grado en dos niveles, parejas complementarias y pares que suman XXI. Toca un arcano para encender sus relaciones. Cambia de geometría para verlo con los ojos de Nichols.</p>',
    '<p class="lede">Jodorowsky and Costa read the tarot as a network: two series of ten degrees, duos that repeat the same degree on two levels, complementary couples and pairs that add up to XXI. Tap an arcanum to light up its relations. Switch geometry to see it through Nichols’s eyes.</p>')
rep('aria-label="Disposición"', 'aria-label="Layout"')
rep('data-lay="jodo">Dos series · Jodorowsky</button>', 'data-lay="jodo">Two series · Jodorowsky</button>')
rep('data-lay="nichols">Tres filas · Nichols</button>', 'data-lay="nichols">Three rows · Nichols</button>')
rep('></i>Dúos</label>', '></i>Duos</label>')
rep('></i>Parejas</label>', '></i>Couples</label>')
rep('></i>Suman XXI</label>', '></i>Add up to XXI</label>')
rep('></i>Sucesión</label>', '></i>Sequence</label>')
rep('aria-label="Grafo de relaciones entre los 22 arcanos mayores"', 'aria-label="Graph of the relations between the 22 major arcana"')
rep('''        <h3>Elige un arcano</h3>
        <p class="note">Las aristas no son decorativas: cada una es una regla de lectura. Si en una tirada aparecen dos cartas unidas aquí, su relación forma parte del mensaje.</p>''',
    '''        <h3>Choose an arcanum</h3>
        <p class="note">The edges are not decorative: each one is a reading rule. If two cards joined here turn up in a spread, their relation is part of the message.</p>''')

rep('<p class="kicker">Trasfondo · Laboratorio probabilístico</p>', '<p class="kicker">Background · Probability laboratory</p>')
rep('<h2>¿Habla de ti o de la aritmética?</h2>', '<h2>Is it about you, or about arithmetic?</h2>')
rep('<p class="lede">El azar también tiene forma. Mirarla no le quita sentido al tarot; le quita la ilusión de que la carta "eligió" llegar. Lo que queda es lo importante: qué haces tú con la imagen que salió.</p>',
    '<p class="lede">Chance has a shape too. Looking at it does not take meaning away from the tarot; it takes away the illusion that the card "chose" to arrive. What remains is what matters: what you do with the image that came up.</p>')
rep('<h3>El centro de la cruz no es azaroso</h3>', '<h3>The centre of the cross is not random</h3>')
rep('<p>En la tirada en cruz de Houdouin, el arcano central no se elige: se calcula sumando las cuatro cartas y reduciendo la suma. Hay <b id="nCombos">7.315</b> combinaciones posibles de cuatro arcanos, y las hemos contado todas.</p>',
    '<p>In Houdouin’s cross spread, the central arcanum is not chosen: it is calculated by adding the four cards and reducing the sum. There are <b id="nCombos">7,315</b> possible combinations of four arcana, and we have counted them all.</p>')
rep('<p>Con la regla básica, <em>el Mago y la Papisa no pueden salir nunca</em>: la suma mínima es 1 + 2 + 3 + 4 = 10. Y cinco cartas centrales concentran más de la mitad de los resultados.</p>',
    '<p>With the basic rule, <em>the Magician and the Popess can never come up</em>: the minimum sum is 1 + 2 + 3 + 4 = 10. And five central cards account for more than half of all outcomes.</p>')
rep('aria-label="Regla de reducción"', 'aria-label="Reduction rule"')
rep('data-regla="A">Reducir dígitos</button>', 'data-regla="A">Add the digits</button>')
rep('data-regla="B">Restar 22</button>', 'data-regla="B">Subtract 22</button>')
rep('aria-label="Distribución del arcano central en la tirada en cruz"', 'aria-label="Distribution of the central arcanum in the cross spread"')
rep('<h3>La ley de los grandes números</h3>', '<h3>The law of large numbers</h3>')
rep('<p>Si se echan muchas tiradas de tres cartas, cada arcano tiende a salir el mismo número de veces. En pocas tiradas, en cambio, aparecen rachas: cartas que "insisten". Son normales. Simula y compruébalo.</p>',
    '<p>Over many three-card spreads, each arcanum tends to come up the same number of times. Over just a few, on the other hand, streaks appear: cards that "insist". They are normal. Simulate it and see.</p>')
rep('aria-label="Número de tiradas"', 'aria-label="Number of spreads"')
rep('<button data-sim="3000">3.000</button><button data-sim="30000">30.000</button>', '<button data-sim="3000">3,000</button><button data-sim="30000">30,000</button>')
rep('id="simTxt" style="margin-top:12px">Elige cuántas tiradas simular.</p>', 'id="simTxt" style="margin-top:12px">Choose how many spreads to simulate.</p>')
rep('aria-label="Frecuencia simulada de cada arcano"', 'aria-label="Simulated frequency of each arcanum"')
rep('<h3>Cómo responde la nube</h3>', '<h3>How the cloud answers</h3>')
rep('<p>Cuando proyectas una palabra en la nube, no hay oráculo: el texto se convierte en un número (una función hash, FNV-1a) y ese número, dividido entre 22, deja un resto. Ese resto es la carta. La misma palabra da siempre la misma carta; una letra distinta lo cambia todo.</p>',
    '<p>When you project a word into the cloud, there is no oracle: the text is turned into a number (a hash function, FNV-1a) and that number, divided by 22, leaves a remainder. That remainder is the card. The same word always gives the same card; a single different letter changes everything.</p>')
rep('<p>Es una máquina de sincronicidad honesta: el sentido no está en el cálculo, sino en lo que la imagen te despierta.</p>',
    '<p>It is an honest synchronicity machine: the meaning is not in the calculation, but in what the image awakens in you.</p>')
rep('<label class="sr" for="seedIn">Texto de prueba</label><input id="seedIn" placeholder="Escribe cualquier palabra" value="espejo">',
    '<label class="sr" for="seedIn">Test text</label><input id="seedIn" placeholder="Type any word" value="mirror">')

rep('<p class="kicker">Trasfondo · Capas del mito</p>', '<p class="kicker">Background · Layers of myth</p>')
rep('<h2>Cada época proyecta su origen</h2>', '<h2>Every age projects its own origin</h2>')
rep('<p class="lede">El tarot nació como juego de naipes en el norte de Italia hacia 1440. Desde entonces, cada época le ha inventado un origen a la medida de su anhelo: Egipto, la Cábala, los gitanos, los cátaros, la geometría sagrada. Esas leyendas no son verdad histórica, pero sí son datos psicológicos: muestran cómo funcionan las cartas como pantalla de proyección. Separar las capas es el primer ejercicio de discernimiento.</p>',
    '<p class="lede">The tarot was born as a card game in northern Italy around 1440. Since then, every age has invented an origin for it to suit its own longing: Egypt, the Kabbalah, the Romani, the Cathars, sacred geometry. These legends are not historical truth, but they are psychological data: they show how the cards work as a screen for projection. Telling the layers apart is the first exercise in discernment.</p>')
rep('<span class="d">Dato documentado</span><span class="h">Hipótesis razonable</span><span class="s">Sistema simbólico</span><span class="m">Mito de origen</span>',
    '<span class="d">Documented fact</span><span class="h">Reasonable hypothesis</span><span class="s">Symbolic system</span><span class="m">Origin myth</span>')

rep('<p class="kicker">Trasfondo · Los once colores</p>', '<p class="kicker">Background · The eleven colours</p>')
rep('<h2>El color también habla</h2>', '<h2>Colour speaks too</h2>')
rep('<p class="lede">Jodorowsky distingue once colores en el Tarot de Marsella restaurado y propone para cada uno un sentido luminoso y otro sombrío. No es un código cerrado: es una pista para mirar. Las estampas de esta web son grabados casi en blanco y negro: <em>el color no se ve, se descubre</em>. Dentro de cada carta, la lente lo hace aparecer allí donde la tradición lo pone, y te dice qué significa.</p>',
    '<p class="lede">Jodorowsky distinguishes eleven colours in the restored Tarot de Marseille and proposes a luminous and a shadow meaning for each. It is not a closed code: it is a clue for looking. The prints on this website are engravings in almost black and white: <em>colour is not seen, it is discovered</em>. Inside each card, the lens makes it appear where tradition places it, and tells you what it means.</p>')

# ======================================================================= footer and dialogs
rep('<p style="margin:0 0 10px">Una experiencia sobre los Arcanos Mayores del Tarot de Marsella, en diálogo con C. G. Jung, Sallie Nichols (<i>Jung y el Tarot</i>), Alejandro Jodorowsky y Marianne Costa (<i>La vía del Tarot</i>) y Wilfried Houdouin. Los textos son propios; las ideas de cada autor se citan y se reformulan.</p>',
    '<p style="margin:0 0 10px">An experience of the Major Arcana of the Tarot de Marseille, in dialogue with C. G. Jung, Sallie Nichols (<i>Jung and Tarot</i>), Alejandro Jodorowsky and Marianne Costa (<i>The Way of Tarot</i>) and Wilfried Houdouin. The texts are original; each author’s ideas are cited and reworded.</p>')
rep('<p style="margin:0">Sin cookies, sin seguimiento, sin conexiones externas. Lo que escribes se queda en tu navegador.</p>',
    '<p style="margin:0">No cookies, no tracking, no external connections. What you write stays in your browser.</p>')
rep('<button id="diarioBtn2">Mi diario</button>', '<button id="diarioBtn2">My journal</button>')
rep('<button data-dlg="dlgFuentes">Fuentes</button>', '<button data-dlg="dlgFuentes">Sources</button>')
rep('<button data-dlg="dlgIA">Transparencia IA</button>', '<button data-dlg="dlgIA">AI transparency</button>')
rep('<button data-dlg="dlgImpressum">Aviso legal</button>', '<button data-dlg="dlgImpressum">Legal notice</button>')
rep('<button data-dlg="dlgDatenschutz">Protección de datos</button>', '<button data-dlg="dlgDatenschutz">Privacy</button>')
rep('<p>Proyecto personal, artístico y educativo, sin ánimo comercial: no vende productos ni servicios, no contiene publicidad y no recoge datos de quien lo visita.</p>',
    '<p>A personal, artistic and educational project with no commercial purpose: it sells no products or services, carries no advertising and collects no data from its visitors.</p>')
rep('<p>Contacto: <a href="mailto:', '<p>Contact: <a href="mailto:')

rep('<dialog id="camara" aria-label="Cámara del arcano">', '<dialog id="camara" aria-label="Chamber of the arcanum">')
rep('id="camPrev" aria-label="Arcano anterior"', 'id="camPrev" aria-label="Previous arcanum"')
rep('id="camNext" aria-label="Arcano siguiente"', 'id="camNext" aria-label="Next arcanum"')
rep('id="camClose" aria-label="Cerrar"', 'id="camClose" aria-label="Close"')
rep('<button class="x-close" data-close-dlg aria-label="Cerrar">×</button>', '<button class="x-close" data-close-dlg aria-label="Close">×</button>', count=5)

rep('''  <h2>Mi diario</h2>
  <p class="note">Tus reflejos y lecturas guardados. Viven solo en este navegador: no se envían a ningún sitio. Si borras los datos del navegador, desaparecen.</p>
  <p><button class="btn" id="diarioDescargar">Descargar (.txt)</button> <button class="btn" id="diarioBorrar">Borrar todo</button></p>''',
    '''  <h2>My journal</h2>
  <p class="note">Your saved reflections and readings. They live only in this browser: they are not sent anywhere. If you clear your browser data, they disappear.</p>
  <p><button class="btn" id="diarioDescargar">Download (.txt)</button> <button class="btn" id="diarioBorrar">Delete all</button></p>''')

a, b = block('<dialog class="dlg" id="dlgFuentes">', '</div></dialog>')
s = s[:a] + '''<dialog class="dlg" id="dlgFuentes"><div class="dlg-in">
  <button class="x-close" data-close-dlg aria-label="Close">×</button>
  <h2>Sources</h2>
  <h3>Reference books</h3>
  <ul>
    <li>Sallie Nichols, <i>Jung and Tarot: An Archetypal Journey</i>. Introduction by Laurens van der Post. Weiser, 1980; later editions with a foreword by Mary K. Greer.</li>
    <li>Alejandro Jodorowsky and Marianne Costa, <i>The Way of Tarot: The Spiritual Teacher in the Cards</i>. Destiny Books, 2009 (original French edition <i>La voie du Tarot</i>, 2004).</li>
    <li>Wilfried Houdouin, <i>Tarot de Marseille Édition Millennium. Compendium Tarologicum</i>, 2017.</li>
    <li>C. G. Jung, <i>The Archetypes and the Collective Unconscious</i> (Collected Works, vol. 9/i), <i>Aion</i> (vol. 9/ii), <i>Two Essays on Analytical Psychology</i> (vol. 7) and <i>Psychology and Alchemy</i> (vol. 12). Princeton University Press / Routledge.</li>
  </ul>
  <h3>The archetypes</h3>
  <p>The definitions in the archetypes section are our own paraphrases of Jung’s ideas, with the reference work given for each. The three-dimensional forms are this project’s visual interpretation, not Jung’s.</p>
  <h3>Code</h3>
  <p>The archetypes section uses <a href="https://threejs.org" rel="noopener">Three.js</a> (MIT licence), hosted on this same server.</p>
  <h3>How they are used</h3>
  <p>From Nichols we take the Jungian reading by amplification and the layout of the journey in three rows. From Jodorowsky and Costa, the visual grammar, the numerology in two series of ten degrees, the duos, the couples, the pairs that add up to XXI, the eleven colours and the reading strategies. From Houdouin, the historical names of the cards, the living spread and the cross spread. His theses on the origin of the tarot (sacred geometry, initiatory transmission) are presented in "Layers of myth" as what they are: hypotheses without documentary support.</p>
  <p>No passage from these works is reproduced: the texts on this website are original. References to Nichols’s chapter themes ("creator and trickster", "dark angel"…) are cited as such.</p>
  <h3>History</h3>
  <p>For the history of the tarot we follow the consensus of current research (origin as a trump card game in northern Italy, c. 1440; divinatory reading documented in the late eighteenth century), as Mary K. Greer also summarises in her foreword to Nichols.</p>
</div></dialog>''' + s[b:]

a, b = block('<dialog class="dlg" id="dlgIA">', '</div></dialog>')
s = s[:a] + '''<dialog class="dlg" id="dlgIA"><div class="dlg-in">
  <button class="x-close" data-close-dlg aria-label="Close">×</button>
  <h2>Transparency on the use of AI</h2>
  <p>In line with Article 50 of the European Artificial Intelligence Act (EU AI Act), here is how AI has been used in this project.</p>
  <h3>Images</h3>
  <p>The prints of the 22 arcana are <b>AI-generated images</b> (Midjourney) made under human artistic direction, based on the traditional iconography of the Tarot de Marseille and in a style inspired by Gustave Doré’s engravings. Each image has been reviewed and selected by hand. The colour zones revealed by the lens are a layer added on the website, not part of the generated image.</p>
  <h3>Texts and code</h3>
  <p>The texts and code were developed with the assistance of Claude (Anthropic) and have been reviewed, corrected and approved by the project’s human author, who takes responsibility for them. The English version is a translation of the Spanish original, made with the same assistance.</p>
  <h3>On the page</h3>
  <p>This website does not run any AI model while you use it. The cloud’s answer and the spreads are calculated with transparent mathematical functions, explained in the Laboratory.</p>
</div></dialog>''' + s[b:]

a, b = block('<dialog class="dlg" id="dlgImpressum">', '</div></dialog>')
s = s[:a] + '''<dialog class="dlg" id="dlgImpressum"><div class="dlg-in">
  <button class="x-close" data-close-dlg aria-label="Close">×</button>
  <h2>Legal notice</h2>
  <h3>Nature of the project</h3>
  <p>Speculum Arcanorum is a personal, artistic and educational project with no commercial purpose. It sells no products or services, carries no advertising, uses no tracking tools and collects no data from its visitors.</p>
  <h3>Contact</h3>
  <p><a href="mailto:visual.nexus.berlin@gmail.com">visual.nexus.berlin@gmail.com</a></p>
  <h3>Content</h3>
  <p>The texts are original and rework, with citation, ideas from the works listed under "Sources". The prints are AI-generated images made under human artistic direction (see "AI transparency"). The tarot is presented as a tool for reflection, not prediction, and does not replace any professional advice.</p>
</div></dialog>''' + s[b:]

a, b = block('<dialog class="dlg" id="dlgDatenschutz">', '</div></dialog>')
s = s[:a] + '''<dialog class="dlg" id="dlgDatenschutz"><div class="dlg-in">
  <button class="x-close" data-close-dlg aria-label="Close">×</button>
  <h2>Privacy · Datenschutzerklärung</h2>
  <h3>Controller</h3>
  <p>Controller within the meaning of the GDPR (DSGVO): the author of this personal project, whom you can contact at <a href="mailto:visual.nexus.berlin@gmail.com">visual.nexus.berlin@gmail.com</a>.</p>
  <h3>What this website does not do</h3>
  <p>It uses no cookies, no analytics or tracking tools, loads no fonts, scripts or images from external servers and does not send anything you write to any server.</p>
  <h3>Local storage</h3>
  <p>Your reflections, saved readings and discovered secrets are stored only in your browser’s local storage (localStorage), on your device. We have no access to them. You can delete them at any time from "My journal" or from your browser settings. Legal basis: § 25 (2) no. 2 TDDDG (storage strictly necessary for a function you have requested).</p>
  <h3>Hosting</h3>
  <p>The website is hosted on Firebase Hosting, a service of Google Ireland Limited (Gordon House, Barrow Street, Dublin 4, Ireland). When you visit it, the server technically processes your IP address and request data in order to deliver the page and keep it secure. Legal basis: Art. 6(1)(f) GDPR (legitimate interest in secure operation). Data may be transferred to the USA, covered by the EU-U.S. Data Privacy Framework.</p>
  <h3>Your rights</h3>
  <p>You have the right of access, rectification, erasure, restriction, portability and objection (Arts. 15 to 21 GDPR), and the right to lodge a complaint with a supervisory authority, for example the Berliner Beauftragte für Datenschutz und Informationsfreiheit.</p>
</div></dialog>''' + s[b:]

# ======================================================================= scripts: inline strings
rep('const fmt=n=>n.toLocaleString("es-ES");', 'const fmt=n=>n.toLocaleString("en-GB");')
rep('estampa generada con IA bajo dirección artística humana, en estilo de grabado inspirado en Doré', 'AI-generated print made under human artistic direction, in an engraving style inspired by Doré')
rep('$("#secretosCount").innerHTML=`Secretos <b>', '$("#secretosCount").innerHTML=`Secrets <b>')
rep('style="margin:0 0 6px">Secreto ${found.size} de ${SECRETOS.length}</p>', 'style="margin:0 0 6px">Secret ${found.size} of ${SECRETOS.length}</p>')
rep("'<p><i>Has encontrado todos los secretos. La lente ya no tiene nada más que enseñarte: ahora mira tú.</i></p>'", "'<p><i>You have found all the secrets. The lens has nothing more to show you: now it is your turn to look.</i></p>'")
rep('style="margin:0 0 6px">La nube responde</p>', 'style="margin:0 0 6px">The cloud answers</p>')
rep('<p class="note">Proyectaste «${esc(v)}». Sin oráculo: tu texto se convirtió en un número (${fmt(h)}) y su resto entre 22 es ${n}.</p><p><button class="btn primary" data-open="${n}">Entrar en la carta</button></p>',
    '<p class="note">You projected “${esc(v)}”. No oracle: your text became a number (${fmt(h)}) and its remainder when divided by 22 is ${n}.</p><p><button class="btn primary" data-open="${n}">Enter the card</button></p>')
rep('const HINT=COARSE?"Desliza el dedo sobre la carta: la lente revela detalles y colores.":"Pasa la lente sobre la carta: revela los detalles que hablan y el color escondido.";',
    'const HINT=COARSE?"Slide your finger over the card: the lens reveals details and colours.":"Move the lens over the card: it reveals the details that speak and the hidden colour.";')
rep('${cur===0?"SIN NÚMERO":"ARCANO "+ROMAN[cur]}${gr?" · GRADO "+gr+" DE LA "+(cur<=10?"PRIMERA":"SEGUNDA")+" SERIE":""}',
    '${cur===0?"NO NUMBER":"ARCANUM "+ROMAN[cur]}${gr?" · DEGREE "+gr+" OF THE "+(cur<=10?"FIRST":"SECOND")+" SERIES":""}')
rep('${a.hist?esc(a.hist):"(sin nombre)"}', '${a.hist?esc(a.hist):"(nameless)"}')
rep('<p class="sombra">Sombra: ${esc(a.sombra)}</p>', '<p class="sombra">Shadow: ${esc(a.sombra)}</p>')
rep('[["mirar","Mirar"],["comprender","Comprender"],["dialogar","Dialogar"]]', '[["mirar","Look"],["comprender","Understand"],["dialogar","Dialogue"]]')
rep('style="margin-bottom:6px">Colores que esconde esta carta. Búscalos con la lente:</p>', 'style="margin-bottom:6px">Colours hidden in this card. Look for them with the lens:</p>')
rep('<p class="note">Mirar antes de interpretar, en la línea de Jodorowsky y Costa. La estampa reinterpreta la iconografía de Marsella; donde se aparta, el texto describe la carta tradicional.</p>',
    '<p class="note">Look before interpreting, in the spirit of Jodorowsky and Costa. The print reinterprets the Marseille iconography; where it departs from it, the text describes the traditional card.</p>')
rep('style="margin-bottom:22px">Amplificación junguiana en la línea de Sallie Nichols: rodear la imagen de mitos, arte e historia hasta que muestre su fuerza.</p>',
    'style="margin-bottom:22px">Jungian amplification in the spirit of Sallie Nichols: surrounding the image with myth, art and history until it shows its power.</p>')
rep('<span class="t">Grado ${gr}</span>', '<span class="t">Degree ${gr}</span>')
rep('<span class="t">Fuera de los grados</span>${cur===0?"El Loco es energía pura, anterior a toda serie.":"El Mundo es la realización: cierra las dos series."}',
    '<span class="t">Outside the degrees</span>${cur===0?"The Fool is pure energy, prior to any series.":"The World is fulfilment: it closes both series."}')
rep('<div class="rel-row"><span class="t">Dúo</span>${chip(dn)}', '<div class="rel-row"><span class="t">Duo</span>${chip(dn)}')
rep('<div class="rel-row"><span class="t">Pareja</span>${chip(pn)}', '<div class="rel-row"><span class="t">Couple</span>${chip(pn)}')
rep('<span class="t">Suman XXI</span>${chip(sm)} ${cur} + ${sm} = 21: se reflejan como en un espejo.', '<span class="t">Add up to XXI</span>${chip(sm)} ${cur} + ${sm} = 21: they mirror each other.')
rep('<span class="t">Arquetipo</span>', '<span class="t">Archetype</span>')
rep('style="margin-top:14px">Relaciones según la estructura de Jodorowsky y Costa. Toca una carta para ir a ella.</p>', 'style="margin-top:14px">Relations according to Jodorowsky and Costa’s structure. Tap a card to go to it.</p>')
rep('<p class="note"><b>Imaginación activa.</b> Mira la carta un minuto sin pensar. Después, pregúntale a la figura qué quiere de ti y escribe la respuesta sin corregirla. No interpretes todavía: deja que hable.</p>',
    '<p class="note"><b>Active imagination.</b> Look at the card for a minute without thinking. Then ask the figure what it wants from you and write down the answer without correcting it. Do not interpret yet: let it speak.</p>')
rep('<p style="margin-top:22px">¿Qué ves tú en esta carta? ¿A quién te recuerda? ¿Qué escena de tu vida se parece a ella?</p>', '<p style="margin-top:22px">What do you see in this card? Who does it remind you of? Which scene from your life resembles it?</p>')
rep('placeholder="Escribe sin censura. Esto no lo lee nadie más: se guarda solo en tu navegador."', 'placeholder="Write without censoring. Nobody else reads this: it is saved only in your browser."')
rep('id="reflejoGuardar">Guardar en mi diario</button><span class="saved" id="reflejoOk">Guardado</span>', 'id="reflejoGuardar">Save to my journal</button><span class="saved" id="reflejoOk">Saved</span>')
rep('Diario.add({tipo:"Reflejo",', 'Diario.add({tipo:"Reflection",')
rep('<span style="opacity:.7">Sombra: ${esc(c.m.toLowerCase())}</span>', '<span style="opacity:.7">Shadow: ${esc(c.m.toLowerCase())}</span>')
rep('(clic para fijar)', '(click to pin)')

rep('<div class="cap"><b>El Loco</b>${esc(ARC[0].kw)}</div></button><p class="note">Fuera de la serie: el viajero que atraviesa las tres filas.</p>',
    '<div class="cap"><b>The Fool</b>${esc(ARC[0].kw)}</div></button><p class="note">Outside the series: the traveller who crosses all three rows.</p>')
rep('[1,7,"El reino de los dioses","Las grandes figuras parentales y espirituales: arquetipos que nos preceden y nos forman, todavía lejos del yo."]',
    '[1,7,"The realm of the gods","The great parental and spiritual figures: archetypes that precede and shape us, still far from the ego."]')
rep('[8,14,"El reino del yo en el mundo","La consciencia se pone a prueba en la realidad terrenal: equilibrio, crisis, ciclos, sacrificio y transformación."]',
    '[8,14,"The realm of the ego in the world","Consciousness is put to the test in earthly reality: balance, crisis, cycles, sacrifice and transformation."]')
rep('[15,21,"El reino de la iluminación","La sombra, la irrupción y los astros: el camino hacia la realización del sí-mismo."]',
    '[15,21,"The realm of illumination","The shadow, the irruption and the heavenly bodies: the path towards the realisation of the Self."]')
rep('<p class="note">Disposición en tres filas de siete según la estructura propuesta por Sallie Nichols en <i>Jung y el Tarot</i>. Los títulos de las filas son una paráfrasis.</p>',
    '<p class="note">Layout in three rows of seven following the structure proposed by Sallie Nichols in <i>Jung and Tarot</i>. The row titles are a paraphrase.</p>')

rep('slots.push({n:cn,role:"Clave",', 'slots.push({n:cn,role:"Key",')
rep('aria-label="Revelar carta"', 'aria-label="Reveal card"')
rep('<span class="note">Sombra: ${esc(a.sombra)}.</span>', '<span class="note">Shadow: ${esc(a.sombra)}.</span>')
rep('${esc(s.role||"Carta "+(i+1))}', '${esc(s.role||"Card "+(i+1))}')
rep('notes.push(`${A.es} y ${B.es} se miran: hay diálogo entre ellos.`)', 'notes.push(`${A.es} and ${B.es} look at each other: there is dialogue between them.`)')
rep('notes.push(`${A.es} y ${B.es} se dan la espalda: dos fuerzas que no se encuentran.`)', 'notes.push(`${A.es} and ${B.es} turn their backs on each other: two forces that do not meet.`)')
rep('notes.push(`${ARC[a].es} y ${ARC[b].es} forman un dúo (grado ${grado(a)}): ${DUO_TXT[grado(a)]}.`)', 'notes.push(`${ARC[a].es} and ${ARC[b].es} form a duo (degree ${grado(a)}): ${DUO_TXT[grado(a)]}.`)')
rep('notes.push(`${ARC[a].es} y ${ARC[b].es} son pareja: ${parejaTxt(a,b)}.`)', 'notes.push(`${ARC[a].es} and ${ARC[b].es} are a couple: ${parejaTxt(a,b)}.`)')
rep('notes.push(`${ARC[a].es} y ${ARC[b].es} suman XXI: se reflejan como en un espejo.`)', 'notes.push(`${ARC[a].es} and ${ARC[b].es} add up to XXI: they mirror each other.`)')
rep('notes.unshift(`La tirada creció hasta ${slots.length} cartas siguiendo las miradas de los extremos.`)', 'notes.unshift(`The spread grew to ${slots.length} cards following the gazes at either end.`)')
rep('notes.push(`La clave repite una carta de la cruz: según Houdouin, eso confirma su importancia.`)', 'notes.push(`The key repeats a card from the cross: according to Houdouin, that confirms its importance.`)')
rep('notes.push(`Probabilidad de que la clave sea ${ARC[c.n].es}: ${(Lab.cruzDist("A")[c.n]*100).toFixed(2)} %. Al sumar cuatro cartas, unos centros salen mucho más que otros, y el Mago y la Papisa no salen nunca.`)',
    'notes.push(`Probability that the key is ${ARC[c.n].es}: ${(Lab.cruzDist("A")[c.n]*100).toFixed(2)}%. When four cards are added up, some centres come up far more often than others, and the Magician and the Popess never do.`)')
rep('`<p style="margin:0">Ninguna relación estructural entre estas cartas: cada una habla por sí misma. Busca tú los puentes.</p>`', '`<p style="margin:0">No structural relation between these cards: each one speaks for itself. Look for the bridges yourself.</p>`')
rep('Diario.add({tipo:"Lectura",', 'Diario.add({tipo:"Reading",')

rep('toLocaleString("es-ES")', 'toLocaleString("en-GB")', count=2)
rep('`<p class="note">Todavía no hay entradas. Guarda un reflejo desde una carta o una lectura desde la mesa.</p>`', '`<p class="note">No entries yet. Save a reflection from a card or a reading from the table.</p>`')
rep('confirm("¿Borrar todo el diario, los reflejos y los secretos de este navegador?")', 'confirm("Delete the whole journal, your reflections and your secrets from this browser?")')
rep('||"Diario vacío"', '||"Empty journal"')
rep('"Speculum Arcanorum · Mi diario\\n\\n"', '"Speculum Arcanorum · My journal\\n\\n"')
rep('l.download="speculum-diario.txt"', 'l.download="speculum-journal.txt"')

rep('${esc(a.es.replace(/^(El|La) /,""))}', '${esc(a.es.replace(/^The /,""))}')
rep('<text class="rowlbl" x="150" y="120">Primera serie · grados 1 a 10</text><text class="rowlbl" x="150" y="470">Segunda serie · grados 1 a 10</text>',
    '<text class="rowlbl" x="150" y="120">First series · degrees 1 to 10</text><text class="rowlbl" x="150" y="470">Second series · degrees 1 to 10</text>')
rep('<text class="rowlbl" x="80" y="195">Dioses</text><text class="rowlbl" x="80" y="325">Yo en el mundo</text><text class="rowlbl" x="80" y="455">Iluminación</text>',
    '<text class="rowlbl" x="80" y="195">Gods</text><text class="rowlbl" x="80" y="325">Ego in the world</text><text class="rowlbl" x="80" y="455">Illumination</text>')
rep('`<h3>Elige un arcano</h3><p class="note">Toca de nuevo para soltar.</p>`', '`<h3>Choose an arcanum</h3><p class="note">Tap again to release.</p>`')
rep('${n===0?"Sin número":"Arcano "+ROMAN[n]}${gr?" · grado "+gr:""}', '${n===0?"No number":"Arcanum "+ROMAN[n]}${gr?" · degree "+gr:""}')
rep('style="color:var(--ochre)">Dúo</span>', 'style="color:var(--ochre)">Duo</span>')
rep('style="color:var(--verm)">Pareja</span>', 'style="color:var(--verm)">Couple</span>')
rep('style="color:var(--sky)">Suma XXI</span>', 'style="color:var(--sky)">Adds up to XXI</span>')
rep('data-open="${n}">Entrar en la carta</button></p>`;', 'data-open="${n}">Enter the card</button></p>`;')

rep('function sci(b){const s=b.toString();const exp=s.length-1;return`${s[0]},${s.slice(1,3)} × 10<sup>${exp}</sup>`}',
    'function sci(b){const s=b.toString();const exp=s.length-1;return`${s[0]}.${s.slice(1,3)} × 10<sup>${exp}</sup>`}')
rep('style="text-anchor:end;fill:var(--ochre)">esperado</text>', 'style="text-anchor:end;fill:var(--ochre)">expected</text>')
rep('bars($("#chartCruz"),p,{fmt:v=>(v*100).toFixed(2)+" %",', 'bars($("#chartCruz"),p,{fmt:v=>(v*100).toFixed(2)+"%",')
rep('''`Regla básica: se suma y, si pasa de 22, se suman las cifras hasta bajar de 22 (22 = el Loco). Imposibles: ${zero.map(i=>ARC[i].es).join(" y ")}. Más probable: ${ARC[sorted[0][1]].es} (${(sorted[0][0]*100).toFixed(2)} %). Menos probable de las posibles: ${ARC[sorted.filter(s=>s[0]>0).slice(-1)[0][1]].es} (${(sorted.filter(s=>s[0]>0).slice(-1)[0][0]*100).toFixed(2)} %).`''',
    '''`Basic rule: add up and, if the total exceeds 22, add its digits until it drops to 22 or below (22 = the Fool). Impossible: ${zero.map(i=>ARC[i].es).join(" and ")}. Most likely: ${ARC[sorted[0][1]].es} (${(sorted[0][0]*100).toFixed(2)}%). Least likely of those possible: ${ARC[sorted.filter(s=>s[0]>0).slice(-1)[0][1]].es} (${(sorted.filter(s=>s[0]>0).slice(-1)[0][0]*100).toFixed(2)}%).`''')
rep('''`Variante: se resta 22 tantas veces como haga falta (0 = el Loco). Ninguna carta queda excluida, pero la distribución sigue sin ser uniforme: la más probable sale un ${(sorted[0][0]*100).toFixed(2)} % y la menos un ${(sorted[21][0]*100).toFixed(2)} %. La regla elegida cambia el mensaje.`''',
    '''`Variant: subtract 22 as many times as needed (0 = the Fool). No card is excluded, but the distribution is still not uniform: the most likely comes up ${(sorted[0][0]*100).toFixed(2)}% of the time and the least likely ${(sorted[21][0]*100).toFixed(2)}%. The rule you choose changes the message.`''')
rep('''`${fmt(N)} tiradas, ${fmt(N*3)} cartas. Cada arcano debería salir unas ${fmt(Math.round(exp))} veces. El que más salió, ${max}; el que menos, ${min}. Desviación máxima: <b>${dev.toFixed(1)} %</b>. ${N<=30?"Con tan pocas tiradas, las rachas parecen mensajes.":N>=30000?"Con muchas, el azar se aplana.":""}`''',
    '''`${fmt(N)} spreads, ${fmt(N*3)} cards. Each arcanum should come up about ${fmt(Math.round(exp))} times. The most frequent came up ${max} times; the least, ${min}. Maximum deviation: <b>${dev.toFixed(1)}%</b>. ${N<=30?"With so few spreads, streaks look like messages.":N>=30000?"With many, chance flattens out.":""}`''')
rep('[sci(f22),"órdenes posibles de los 22 Arcanos Mayores al barajar (22!)."]', '[sci(f22),"possible orders of the 22 Major Arcana when shuffled (22!)."]')
rep('[sci(f78),"órdenes posibles de la baraja completa de 78 cartas (78!). Cada barajado es, casi con seguridad, único en la historia."]', '[sci(f78),"possible orders of the full 78-card deck (78!). Every shuffle is almost certainly unique in history."]')
rep('[fmt(22*21*20),"tiradas distintas de tres cartas, contando el orden, con los Arcanos Mayores."]', '[fmt(22*21*20),"different three-card spreads, counting order, with the Major Arcana."]')
rep('[(3/22*100).toFixed(1)+" %","probabilidad de que una carta concreta aparezca en una tirada de tres."]', '[(3/22*100).toFixed(1)+"%","probability that a given card appears in a three-card spread."]')
rep('[((1-C(19,3)/C(22,3))*100).toFixed(1)+" %","probabilidad de que dos tiradas de tres cartas compartan al menos una. Por eso «me vuelve a salir» es tan frecuente."]',
    '[((1-C(19,3)/C(22,3))*100).toFixed(1)+"%","probability that two three-card spreads share at least one card. That is why “it came up again” is so common."]')
rep('[((1-C(75,3)/C(78,3))*100).toFixed(1)+" %","la misma probabilidad con la baraja completa de 78: la repetición se vuelve mucho más rara."]',
    '[((1-C(75,3)/C(78,3))*100).toFixed(1)+"%","the same probability with the full 78-card deck: repetition becomes much rarer."]')

rep('const tag={dato:"Dato",hip:"Hipótesis",sis:"Sistema simbólico",mito:"Mito"};', 'const tag={dato:"Fact",hip:"Hypothesis",sis:"Symbolic system",mito:"Myth"};')
rep('<p class="neg">Sombra: ${esc(c.m)}</p>', '<p class="neg">Shadow: ${esc(c.m)}</p>')
rep('`<p class="note" style="grid-column:1/-1">A partir de la tabla de colores de Jodorowsky y Costa en <i>La vía del Tarot</i>, reformulada.</p>`',
    '`<p class="note" style="grid-column:1/-1">Based on Jodorowsky and Costa’s colour table in <i>The Way of Tarot</i>, reworded.</p>`')

rep('<p class="kicker">Arquetipo ${idx+1} de ${ARQ.length}</p>', '<p class="kicker">Archetype ${idx+1} of ${ARQ.length}</p>')
rep('<p class="forma"><b>La forma</b>', '<p class="forma"><b>The form</b>')
rep('class="note">En el tarot</p>', 'class="note">In the tarot</p>')
rep('b.setAttribute("aria-label",p?"Continuar el recorrido":"Pausar el recorrido")', 'b.setAttribute("aria-label",p?"Resume the sequence":"Pause the sequence")')

rep('THREE=await import("./vendor/three.module.min.js")', 'THREE=await import("/vendor/three.module.min.js")')

# ======================================================================= final checks
leftover = []
body = s.split("</style>", 1)[1]
for m in re.finditer(r"[ÁÉÍÓÚÑáéíóúñ¿¡]", body):
    ctx = body[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
    leftover.append(ctx)
allowed = ("Versión en español", "Éliphas", "Gébelin", "Datenschutzerklärung", "Möbius", "Édition", "für", "Rabelais")
real = [c for c in leftover if not any(w in c for w in allowed)]
# Spanish comments inside the code are harmless; report the rest
real = [c for c in real if not re.search(r"(//|/\*|\*)\s", c)]
if real:
    print("[make_en] possible untranslated text:")
    for c in real[:40]:
        print("   …" + c + "…")

os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8").write(s)
print(f"[make_en] wrote {DST} ({len(s)//1024} KB)")
