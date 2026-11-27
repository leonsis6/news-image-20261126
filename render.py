#!/usr/bin/env python3
"""Render news-image-20261126: 'Thursday 26 November 2026: 50 stories, 10 regions, 21 fields'.

Code-rendered newspaper front page, 1024x1024, Python + PIL only.
All content comes from STORIES.md (verified wire reporting, Thursday 26 Nov
2026 UTC) — nothing invented.
Layout: revised winner spec — kicker, count line, masthead, subhead, region
+ field strips, numbers strip, UTC timeline, 3 illustrated leads with WHY IT
MATTERS, 12 illustrated cards, 35 briefs, world map with pins 1-15 + legend,
red-boxed DATE CHECK, source footer. Adapted from the 25 Nov renderer.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968 content width

PAPER = (247, 242, 231)
INK = (20, 18, 16)
RED = (179, 35, 27)
NAVY = (31, 58, 95)
TEAL = (31, 110, 110)
OCHRE = (196, 138, 30)
PURPLE = (120, 70, 140)
GREEN = (40, 120, 60)
BROWN = (140, 90, 40)
GREY = (110, 104, 94)
FAINT = (232, 224, 208)
LAND = (222, 214, 196)
LAND_EDGE = (90, 80, 66)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(text, font, width):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_h(font):
    return int(round(font.size * 1.24))


# ---------------------------------------------------------------- data
# (headline, body, why, tag) — facts from STORIES.md, shortened for layout only.
LEADS = [
    ("GULF ON FIRE",
     "Iranian drone kills two Italians in Kuwait; tankers hit mines in "
     "Hormuz; Houthis strike Jazan refinery, one worker killed.",
     "First deaths from Iranian strikes since the US\u2013Iran war resumed; "
     "the war now kills Europeans on Gulf soil.",
     "CONFIRMED / REPORTED \u00b7 Reuters"),
    ("MACY'S 100TH PARADE GROUNDED",
     "A nor'easter postpones the 100th Macy's Thanksgiving Day Parade \u2014 "
     "the first weather postponement in its 100-year history.",
     "Thanksgiving itself was the story in America \u2014 the parade, the "
     "travel, the power \u2014 all stopped by one storm.",
     "CONFIRMED \u00b7 AP"),
    ("18 YEARS SINCE 26/11",
     "India marks 18 years since the 26/11 Mumbai attacks that killed 166 "
     "\u2014 and 77 years of its Constitution, adopted 26 Nov 1949.",
     "The date itself is the story \u2014 26/11 is remembered every 26 "
     "November, and this year it falls on the edition's day.",
     "CONFIRMED \u00b7 PTI/AP"),
]

CARDS = [
    ("GUKESH\u2013SINDAROV: 60-MOVE DRAW",
     "Game 3 in Geneva ends level 1.5\u20131.5. Game 4 Saturday, Gukesh has White.",
     "ONGOING \u00b7 Chess.com/FIDE"),
    ("WORLD HITS BACK AT US TARIFFS",
     "China, Brazil, EU hit back: 20% China, 15% Japan, Korea, EU.",
     "CONFIRMED \u00b7 Reuters/AP"),
    ("ISRAEL KILLS HAMAS MINISTER",
     "Nine killed in Gaza, incl. Hamas deputy minister Abu Nada and his wife.",
     "CONFIRMED \u00b7 Reuters/BBC"),
    ("KYIV HIT: 7 WOUNDED",
     "Missiles hit a shopping centre; defences down 87 of 113 Shahed drones.",
     "CONFIRMED \u00b7 Reuters"),
    ("CAIRO TANKER INFERNO: 31 DEAD",
     "Tanker explodes on Ring Road, 31 dead, 21 hurt; driver detained Thursday.",
     "CONFIRMED \u00b7 AP/Reuters"),
    ("BANGKOK REFINERY BLAST HURTS 9",
     "Blast at Bangchak refinery injures nine, three critical; production shut.",
     "CONFIRMED \u00b7 AP"),
    ("EBOLA IN CONGO PASSES 12,000",
     "12,021 cases, 5,904 dead \u2014 fastest Ebola outbreak in history.",
     "CONFIRMED \u00b7 AP"),
    ("EU SPLIT OVER UKRAINE LOAN",
     "Leaders struggle over \u20ac45bn loan and \u20ac1.582tn budget; Merz threatens veto.",
     "CONFIRMED \u00b7 AP"),
    ("ECB PICKS DE COS, FIRST SPANIARD",
     "De Cos chosen as next ECB president; Lagarde steps down 7 Feb 2027.",
     "CONFIRMED \u00b7 AP/Reuters"),
    ("UK NET MIGRATION FALLS TO 77,000",
     "Net migration 77,000, down 62% \u2014 lowest since 1997, ~90% below 2023 peak.",
     "CONFIRMED \u00b7 ONS/Reuters"),
    ("BANGLADESH WAGE UP, PROTESTS",
     "Wage up 36% to Tk17,000; workers reject it, tear gas in Gazipur.",
     "CONFIRMED \u00b7 AFP/Reuters"),
    ("TRUMP CALLS GDP FIGURES 'FAKE'",
     "Trump demands probe, claiming 'fake' growth figures before the midterms.",
     "CONFIRMED \u00b7 AP/Reuters"),
]

# (number, body, tag) — one line each in the brief columns.
# tag: C = CONFIRMED, R = REPORTED, CL = CLAIM.
BRIEFS = [
    (16, "Ras Tanura: Houthis claim hit on Saudi's biggest refinery",
     "CL \u00b7 Reuters/CNN"),
    (17, "Ukraine laser downs jet-powered drone \u2014 first claimed kill",
     "CL \u00b7 CBS"),
    (18, "Russian strikes cut power across five Ukrainian regions",
     "R \u00b7 Reuters"),
    (19, "Serbia calls presidential election for 27 Dec",
     "C \u00b7 AP/Reuters"),
    (20, "Germany arrests two Iraqis over Cologne synagogue plot",
     "C \u00b7 dpa/CBS"),
    (21, "Depardieu ordered to stand trial for rape",
     "C \u00b7 AP/Reuters"),
    (22, "Taiwan votes in 2 days: 11,051 offices, 19.65m voters",
     "C \u00b7 AP/CSIS"),
    (23, "FedEx plane overruns runway at Miami airport",
     "C \u00b7 AP"),
    (24, "Judge blocks FCC early review of ABC licence",
     "C \u00b7 AP"),
    (25, "Steelers cut Aaron Rodgers after TV blast at coach",
     "C \u00b7 AP"),
    (26, "Sinner out for extended spell after knee surgery",
     "C \u00b7 Reuters"),
    (27, "NFL Thanksgiving tripleheader: Lions\u2013Bears, Bills\u2013Chiefs",
     "C \u00b7 AP"),
    (28, "Kenya court halts US-backed Ebola quarantine site",
     "C \u00b7 Reuters"),
    (29, "India announces Rs15,000-crore Nepal package",
     "C \u00b7 PTI"),
    (30, "IPL 2027 auction draws 1,220 players",
     "C"),
    (31, "Hera reveals DART crater on asteroid Dimorphos",
     "C \u00b7 ESA"),
    (32, "Brazil: Wolbachia mosquitoes cut infections 68%",
     "C"),
    (33, "Palm Beach ferries strike shuts services",
     "C \u00b7 NSW Govt"),
    (34, "Sydney: Inglis, Carey put Australia on top in decider",
     "C"),
    (35, "Dubai: Emirates tops global airline rankings",
     "C"),
    (36, "Mexico: cartels adapt as arrests reshape ranks",
     "C"),
    (37, "Bogot\u00e1: UN chief praises Colombia peace progress",
     "C"),
    (38, "Sudan drone strikes kill 19 in Blue Nile",
     "C \u00b7 Reuters"),
    (39, "Colombia police free 29 supermarket hostages",
     "C \u00b7 AP"),
    (40, "Saudi national kidnapped by IS men in Niger",
     "C \u00b7 Reuters"),
    (41, "EU imposes visa bans, quotas on Chinese cars",
     "C \u00b7 Reuters"),
    (42, "Plane crashes into Gulf of Mexico, six aboard",
     "C \u00b7 AP"),
    (43, "Army blows up 5 tonnes of explosives in Iowa",
     "C \u00b7 Al Jazeera"),
    (44, "UN: Gaza staff sacked on unproven claims",
     "R \u00b7 Guardian"),
    (45, "US stock futures rebound after AI rout",
     "C \u00b7 CNBC"),
    (46, "Ghana unveils Heritage banknotes",
     "C"),
    (47, "Nigeria starts building naval ships",
     "C"),
    (48, "S\u00e3o Tom\u00e9: Ramos reappointed prime minister",
     "C"),
    (49, "Johannesburg police bar anti-migrant rallies",
     "C"),
    (50, "Xi probe hits Shanghai chief Chen Jining",
     "R \u00b7 Reuters"),
]

UTC_ITEMS = [
    ("04:28", "Kyiv: 7 hurt in missile strike"),
    ("07:45", "Bangchak refinery blast, Bangkok"),
    ("11:00", "Serbia calls election for 27 Dec"),
    ("13:21", "ONS: UK migration 77,000"),
    ("13:30", "Macy's parade was due to step off"),
    ("14:00", "Gukesh\u2013Sindarov Game 3 begins"),
    ("19:30", "Saudi confirms Jazan refinery hit"),
    ("21:20", "Trump demands GDP figures probe"),
]

NUMBERS = [
    ("2", "Italians killed in Kuwait drone strike"),
    ("31", "dead in Cairo tanker inferno"),
    ("12,021", "DRC Ebola cases; 5,904 dead"),
    ("77,000", "UK net migration, lowest since 1997"),
    ("800,000+", "homes & businesses without power in storm"),
    ("60", "moves in Gukesh\u2013Sindarov Game 3 draw"),
]

REGION_STRIP = ("N. AMERICA 8 \u00b7 LATIN AMERICA 4 \u00b7 EUROPE 11 \u00b7 "
                "MIDDLE EAST 4 \u00b7 N. AFRICA 1 \u00b7 SUB-SAHARAN AFRICA 8 \u00b7 "
                "SOUTH ASIA 5 \u00b7 EAST & SE ASIA 3 \u00b7 OCEANIA 2 \u00b7 GLOBAL 4")

FIELD_STRIP = ("WAR 6 \u00b7 SPORT 6 \u00b7 POLITICS 5 \u00b7 DIPLOMACY 4 \u00b7 "
               "DISASTER 3 \u00b7 DEFENCE 3 \u00b7 TRADE 2 \u00b7 HEALTH 2 \u00b7 "
               "ECONOMY 2 \u00b7 SECURITY 2 \u00b7 JUSTICE 2 \u00b7 TRANSPORT 2 \u00b7 "
               "CRIME 2 \u00b7 CULTURE 2 \u00b7 WEATHER 1 \u00b7 MIGRATION 1 \u00b7 "
               "LABOUR 1 \u00b7 MEDIA 1 \u00b7 SPACE 1 \u00b7 BUSINESS 1 \u00b7 PROTEST 1")

SUBHEAD = "GULF ON FIRE \u00b7 MACY'S 100TH PARADE GROUNDED \u00b7 18 YEARS SINCE 26/11"

DATE_CHECK_HEAD = "DATE CHECK \u2014 EVERY STORY ABOVE HAPPENED OR WAS FIRST REPORTED ON THURSDAY 26 NOVEMBER 2026."
DATE_CHECK_LEFT = ("LEFT OUT, NOT 26 NOVEMBER: \u00d7 Shenzhou-24 docks, first "
                   "Pakistani in orbit (Wed 25) \u00b7 \u00d7 US tariff plan announced "
                   "(Wed 25) \u00b7 \u00d7 Solomon Islands security pact (Wed 25) \u00b7 "
                   "\u00d7 Miss Universe crowned (Tue 24) \u00b7 \u00d7 Rosstat leak: "
                   "490,334 Russian war dead (Wed 25) \u00b7 \u00d7 Norway court voids "
                   "oil licences (13 Nov)")
DATE_CHECK_NOTYET = ("NOT YET: Taiwan votes (Sat 28) \u00b7 Chess Game 4 (Sat 28) "
                     "\u00b7 Macy's parade (Sat 28) \u00b7 EU budget summit (Fri 27) "
                     "\u00b7 NZ election result (Fri 27) \u00b7 Fed decision (8\u20139 Dec)")

FOOTER = ("Every story happened or was first reported on Thursday 26 November "
          "2026. Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Xinhua \u00b7 ONS \u00b7 PTI \u00b7 "
          "FIDE \u00b7 BBC \u00b7 CBS \u00b7 dpa \u00b7 ESA \u00b7 CSIS. C = CONFIRMED \u00b7 "
          "R = REPORTED \u00b7 CL = CLAIM. Every drawing original.")

# pins: (number, lon, lat, dx, dy, colour) — offsets declutter clusters.
PINS = [
    (1, 47.5, 29.4, 0, 0, RED),          # Kuwait
    (2, -74, 40.7, 0, -14, NAVY),        # New York
    (3, 72.8, 19.0, 0, 0, OCHRE),        # Mumbai
    (4, 6.1, 46.2, -8, 6, TEAL),         # Geneva
    (5, -77, 39.0, -12, -2, NAVY),       # Washington (tariffs)
    (6, 34.5, 31.5, -8, -6, RED),        # Gaza
    (7, 30.5, 50.4, 0, 0, TEAL),         # Kyiv
    (8, 31.2, 30.0, 8, 6, BROWN),        # Cairo
    (9, 100.5, 13.7, 0, 0, PURPLE),      # Bangkok
    (10, 30.2, 1.6, 0, 0, GREEN),        # Bunia, DRC
    (11, 4.4, 50.8, 0, -10, TEAL),       # Brussels
    (12, 8.7, 50.1, 10, 0, TEAL),        # Frankfurt
    (13, -0.1, 51.5, -10, -4, TEAL),     # London
    (14, 90.4, 23.8, 0, 0, OCHRE),       # Gazipur, Bangladesh
    (15, -77, 39.0, 12, 8, NAVY),        # Washington (Trump)
]

LEGEND = [
    ("MIDDLE EAST", RED), ("N. AMERICA", NAVY), ("SOUTH ASIA", OCHRE),
    ("EUROPE", TEAL), ("EAST & SE ASIA", PURPLE),
    ("SUB-SAHARAN AFRICA", GREEN), ("N. AFRICA", BROWN),
]

# CONTINENTS — see below (polygons copied from the 25 Nov renderer).

CONTINENTS = [
    # North America
    [(-168, 66), (-158, 71), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
     (-85, 76), (-80, 73), (-70, 62), (-60, 55), (-55, 47), (-65, 44),
     (-70, 42), (-75, 35), (-80, 26), (-84, 30), (-90, 21), (-97, 16),
     (-105, 20), (-110, 24), (-120, 32), (-125, 40), (-125, 49), (-135, 58),
     (-150, 60), (-165, 60)],
    # South America
    [(-80, 10), (-75, 11), (-65, 10), (-60, 5), (-52, 4), (-50, 0),
     (-44, -3), (-35, -6), (-38, -15), (-40, -22), (-48, -28), (-55, -35),
     (-62, -41), (-68, -50), (-70, -54), (-73, -45), (-73, -35), (-71, -20),
     (-77, -12), (-80, -5), (-81, 0)],
    # Africa
    [(-17, 15), (-15, 25), (-10, 31), (-5, 35), (0, 36), (10, 37), (15, 32),
     (20, 32), (30, 31), (33, 27), (37, 22), (39, 18), (43, 12), (48, 11),
     (51, 12), (46, 5), (41, -2), (40, -10), (36, -18), (33, -26), (28, -33),
     (20, -35), (17, -30), (14, -22), (12, -12), (9, 4), (0, 6), (-8, 5),
     (-13, 8), (-17, 12)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (-4, 50), (0, 51),
     (3, 53), (7, 54), (8, 57), (10, 59), (12, 56), (18, 56), (21, 55),
     (24, 58), (28, 60), (30, 62), (30, 66), (25, 70), (20, 70), (15, 68),
     (12, 65), (10, 62), (5, 58), (5, 55), (0, 52), (-3, 48), (-5, 43),
     (-9, 38)],
    # Asia
    [(30, 62), (35, 66), (45, 68), (55, 69), (65, 69), (75, 72), (85, 74),
     (95, 76), (105, 77), (115, 73), (125, 72), (135, 72), (145, 72),
     (155, 70), (165, 69), (175, 66), (178, 65), (170, 60), (162, 58),
     (158, 52), (150, 59), (142, 52), (141, 45), (138, 38), (132, 35),
     (128, 33), (122, 30), (118, 25), (112, 22), (108, 18), (105, 10),
     (103, 8), (100, 6), (98, 10), (95, 16), (92, 21), (89, 22), (86, 20),
     (82, 15), (80, 10), (77, 8), (74, 12), (72, 20), (68, 22), (65, 25),
     (60, 25), (57, 26), (54, 27), (51, 28), (48, 29), (45, 30), (42, 31),
     (38, 32), (36, 36), (33, 36), (30, 36), (28, 40), (27, 41), (23, 40),
     (22, 37), (26, 39), (30, 41), (30, 46), (30, 52), (28, 56), (28, 60)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76),
     (-35, 80), (-45, 79), (-55, 76), (-58, 72), (-55, 68), (-52, 64),
     (-48, 60)],
    # Japan
    [(130, 31), (131, 33), (134, 34), (137, 35), (139, 35), (140, 38),
     (141, 40), (142, 43), (144, 44), (143, 42), (141, 39), (140, 36),
     (137, 34), (134, 33), (131, 32)],
    # UK
    [(-5, 50), (-3, 53), (-5, 55), (-3, 58), (-1, 57), (1, 53), (1, 51),
     (-2, 50), (-4, 50)],
    # SE Asia islands (rough)
    [(95, 5), (98, 2), (100, -2), (103, -4), (106, -6), (110, -7),
     (114, -8), (118, -9), (120, -10), (119, -5), (116, -2), (112, 1),
     (108, 2), (104, 1), (101, 3), (98, 6), (95, 6)],
    [(117, -1), (120, 0), (123, 1), (122, 4), (120, 6), (118, 5),
     (116, 3), (115, 0), (116, -3)],
    [(131, -1), (133, -2), (136, -3), (139, -4), (141, -6), (138, -8),
     (134, -7), (132, -4)],
]

# ---------------------------------------------------------------- illustrations
# Each takes (d, x0, y0, x1, y1) and draws one flat geometric scene.
# All geometry is fractions of the box (w, h) plus a unit u = h/80, so the
# same drawing works in a tall lead box and a short card strip. No photos.


def _sky(d, x0, y0, x1, y1, top, bot):
    d.rectangle([x0, y0, x1, y1], fill=top)
    d.rectangle([x0, (y0 + y1) // 2, x1, y1], fill=bot)


def illo_L1(d, x0, y0, x1, y1):  # Gulf on fire: refinery + tanker + mines
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (216, 226, 232), (200, 192, 172))
    wy = y0 + int(h * 0.58)
    d.rectangle([x0, wy, x1, y1], fill=(70, 120, 150))
    # sun, hazy
    sr = max(4, int(h * 0.10))
    d.ellipse([x1 - int(w * 0.22) - sr, y0 + int(h * 0.08) - sr,
               x1 - int(w * 0.22) + sr, y0 + int(h * 0.08) + sr], fill=(235, 200, 120))
    # refinery towers, left
    gy = wy
    for i, tw in enumerate((0.13, 0.10, 0.11)):
        tx = x0 + int(w * (0.05 + i * 0.13))
        twpx = int(w * tw)
        d.rectangle([tx, y0 + int(h * 0.28), tx + twpx, gy], fill=NAVY)
        d.rectangle([tx - 3, y0 + int(h * 0.24), tx + twpx + 3, y0 + int(h * 0.28)],
                    fill=(60, 80, 115))
        fx = tx + twpx // 2
        d.polygon([(fx - int(8 * u), y0 + int(h * 0.24)),
                   (fx + int(8 * u), y0 + int(h * 0.24)),
                   (fx, y0 + int(h * 0.05))], fill=(230, 120, 30))
        d.polygon([(fx - int(4 * u), y0 + int(h * 0.24)),
                   (fx + int(4 * u), y0 + int(h * 0.24)),
                   (fx, y0 + int(h * 0.13))], fill=(245, 200, 60))
    # smoke clouds over the towers
    for cx, cy, r in ((0.16, 0.14, 6), (0.24, 0.09, 7), (0.33, 0.15, 5)):
        rr = int(r * u)
        d.ellipse([x0 + int(w * cx) - rr, y0 + int(h * cy) - rr,
                   x0 + int(w * cx) + rr, y0 + int(h * cy) + rr], fill=(150, 148, 142))
    # tanker, right, on the sea
    hx0, hx1 = x0 + int(w * 0.48), x0 + int(w * 0.88)
    d.polygon([(hx0, wy - int(h * 0.12)), (hx1, wy - int(h * 0.12)),
               (hx1 + 12, wy + 2), (hx0, wy + 2)], fill=(30, 40, 60))
    for i, c in enumerate((RED, TEAL, OCHRE)):
        d.rectangle([hx0 + 8 + i * 24, wy - int(h * 0.30),
                     hx0 + 28 + i * 24, wy - int(h * 0.12)], fill=c)
    d.rectangle([hx0 + 8, wy - int(h * 0.42), hx0 + 32, wy - int(h * 0.30)],
                fill=(240, 238, 230))
    # naval mine ahead of the tanker
    mx, my = x0 + int(w * 0.94), y0 + int(h * 0.46)
    spike = max(6, int(16 * u))
    for k in range(8):
        a = math.radians(k * 45)
        d.line([mx, my, mx + int(spike * math.cos(a)), my + int(spike * math.sin(a))],
               fill=(30, 30, 30), width=max(2, int(3 * u)))
    rr = max(3, int(9 * u))
    d.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=(30, 30, 30))
    # waves
    for yy in (wy + int(h * 0.14), wy + int(h * 0.28)):
        for xx in range(x0 + 4, x1 - 10, 22):
            d.arc([xx, yy, xx + 20, yy + max(4, int(10 * u))], 180, 360,
                  fill=(240, 244, 246), width=2)


def illo_L2(d, x0, y0, x1, y1):  # Macy's parade balloon, grounded by storm
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (150, 160, 175), (180, 185, 190))
    # storm clouds
    for cx, cy, rx, ry in ((0.18, 0.14, 0.16, 0.07), (0.55, 0.08, 0.18, 0.06),
                           (0.86, 0.16, 0.14, 0.07)):
        d.ellipse([x0 + int(w * (cx - rx)), y0 + int(h * (cy - ry)),
                   x0 + int(w * (cx + rx)), y0 + int(h * (cy + ry))],
                  fill=(110, 118, 130))
    # big parade balloon, tethered low
    bx, by = x0 + int(w * 0.42), y0 + int(h * 0.38)
    brx, bry = int(w * 0.20), int(h * 0.24)
    d.ellipse([bx - brx, by - bry, bx + brx, by + bry], fill=RED)
    d.ellipse([bx - brx, by - bry, bx + brx, by + bry], outline=(255, 255, 255), width=2)
    d.arc([bx - brx, by - bry, bx + brx, by + bry], 200, 340,
          fill=(255, 255, 255), width=2)
    d.ellipse([bx - int(brx * 0.35), by - bry, bx + int(brx * 0.35), by + bry],
              fill=(240, 238, 230))
    # ropes from balloon to the street
    gy = y1 - int(h * 0.16)
    d.line([bx - int(brx * 0.7), by + bry, bx - int(w * 0.05), gy],
           fill=(60, 60, 60), width=max(2, int(3 * u)))
    d.line([bx + int(brx * 0.7), by + bry, bx + int(w * 0.22), gy],
           fill=(60, 60, 60), width=max(2, int(3 * u)))
    # buildings along the street
    d.rectangle([x0, gy, x1, y1], fill=(120, 110, 90))
    for i, (bw, bh) in enumerate(((0.16, 0.30), (0.12, 0.38), (0.14, 0.26))):
        bx0 = x0 + int(w * (0.62 + i * 0.13))
        d.rectangle([bx0, gy - int(h * bh), bx0 + int(w * bw), gy], fill=NAVY)
        for r in range(2):
            for c in range(2):
                wx = bx0 + 4 + c * max(6, int(w * 0.05))
                wy = gy - int(h * bh) + 5 + r * max(6, int(h * 0.10))
                d.rectangle([wx, wy, wx + 4, wy + 4], fill=(240, 232, 200))
    # rain streaks
    for i in range(7):
        rx = x0 + int(w * (0.06 + i * 0.13))
        ry = y0 + int(h * (0.20 + (i % 3) * 0.12))
        d.line([rx, ry, rx - 5, ry + 12], fill=(200, 210, 220), width=2)
    # wind gusts
    for yy in (0.62, 0.72):
        d.arc([x0 + int(w * 0.70), y0 + int(h * yy), x0 + int(w * 0.95),
               y0 + int(h * (yy + 0.16))], 180, 360, fill=(255, 255, 255), width=2)


def illo_L3(d, x0, y0, x1, y1):  # Mumbai: Gateway arch + memorial candles
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (238, 200, 150), (222, 180, 140))
    gy = y1 - int(h * 0.18)
    d.rectangle([x0, gy, x1, y1], fill=(90, 110, 140))
    # skyline towers behind the arch
    for i, (bw, bh) in enumerate(((0.10, 0.34), (0.08, 0.44), (0.09, 0.30))):
        bx0 = x0 + int(w * (0.06 + i * 0.10))
        d.rectangle([bx0, gy - int(h * bh), bx0 + int(w * bw), gy], fill=(120, 100, 90))
    for i, (bw, bh) in enumerate(((0.08, 0.30), (0.10, 0.40))):
        bx0 = x0 + int(w * (0.78 + i * 0.10))
        d.rectangle([bx0, gy - int(h * bh), bx0 + int(w * bw), gy], fill=(120, 100, 90))
    # Gateway of India: base + big dome + turrets
    cx = x0 + int(w * 0.50)
    base_w = int(w * 0.34)
    base_h = int(h * 0.34)
    d.rectangle([cx - base_w // 2, gy - base_h, cx + base_w // 2, gy],
                fill=(232, 214, 180), outline=NAVY, width=2)
    d.pieslice([cx - int(base_w * 0.30), gy - base_h - int(h * 0.30),
                cx + int(base_w * 0.30), gy - base_h + int(h * 0.10)],
               180, 360, fill=(232, 214, 180), outline=NAVY, width=2)
    d.rectangle([cx - 3, gy - base_h - int(h * 0.34), cx + 3, gy - base_h - int(h * 0.28)],
                fill=NAVY)
    for sx in (-1, 1):
        tx = cx + sx * int(base_w * 0.42)
        d.rectangle([tx - 4, gy - int(h * 0.22), tx + 4, gy], fill=(232, 214, 180),
                    outline=NAVY, width=1)
        d.ellipse([tx - 6, gy - int(h * 0.26), tx + 6, gy - int(h * 0.20)],
                  fill=(232, 214, 180), outline=NAVY, width=1)
    # arch opening: shallow arched doorway
    aw = int(base_w * 0.22)
    ah = int(base_h * 0.72)
    d.pieslice([cx - aw, gy - ah, cx + aw, gy], 180, 360, fill=NAVY)
    d.rectangle([cx - aw, gy - ah // 2, cx + aw, gy], fill=NAVY)
    # memorial candles in front
    for i in range(3):
        ccx = x0 + int(w * (0.30 + i * 0.20))
        ch = int(h * 0.10)
        d.rectangle([ccx - 3, gy - ch, ccx + 3, gy], fill=(250, 248, 242))
        d.polygon([(ccx - 4, gy - ch), (ccx + 4, gy - ch), (ccx, gy - ch - 9)],
                  fill=(245, 200, 60))
    # flowers
    for px, py, c in ((0.14, 0.86, RED), (0.86, 0.84, OCHRE), (0.68, 0.90, RED)):
        rr = max(2, int(3 * u))
        d.ellipse([x0 + int(w * px) - rr, y0 + int(h * py) - rr,
                   x0 + int(w * px) + rr, y0 + int(h * py) + rr], fill=c)


def illo_C4(d, x0, y0, x1, y1):  # chess: board + king + clock
    w, h = x1 - x0, y1 - y0
    _sky(d, x0, y0, x1, y1, (236, 232, 222), (226, 220, 204))
    bx0, by0 = x0 + int(w * 0.05), y0 + 2
    cell = max(4, (h - 4) // 3)
    for r in range(3):
        for c in range(5):
            fill = NAVY if (r + c) % 2 == 0 else (244, 238, 224)
            d.rectangle([bx0 + c * cell, by0 + r * cell,
                         bx0 + (c + 1) * cell, by0 + (r + 1) * cell], fill=fill)
    # white king on the board
    kx, ky = bx0 + int(2.5 * cell), by0 + int(1.5 * cell)
    kr = max(3, cell // 2)
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(255, 255, 255),
              outline=NAVY, width=2)
    d.line([kx, ky - kr - 3, kx, ky + kr + 1], fill=NAVY, width=2)
    d.line([kx - 3, ky - kr, kx + 3, ky - kr], fill=NAVY, width=2)
    # black pawn
    px, py = bx0 + int(4.2 * cell), by0 + int(2.4 * cell)
    pr = max(2, cell // 3)
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=INK)
    # chess clock, right
    cx0 = x1 - int(w * 0.22)
    cy0 = y0 + int(h * 0.15)
    cw, chh = int(w * 0.15), int(h * 0.50)
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + chh], fill=(250, 248, 242),
                outline=INK, width=2)
    ccx, ccy = cx0 + cw // 2, cy0 + chh // 2
    d.ellipse([ccx - 2, ccy - 2, ccx + 2, ccy + 2], fill=RED)
    d.line([ccx, ccy, ccx, cy0 + 3], fill=RED, width=2)
    d.line([ccx, ccy, cx0 + cw - 4, ccy - 1], fill=INK, width=2)


def illo_C5(d, x0, y0, x1, y1):  # tariff document + percent + bars
    w, h = x1 - x0, y1 - y0
    _sky(d, x0, y0, x1, y1, (236, 230, 220), (228, 220, 206))
    dx0, dy0 = x0 + int(w * 0.08), y0 + int(h * 0.10)
    dx1, dy1 = x0 + int(w * 0.58), y1 - int(h * 0.10)
    d.rectangle([dx0, dy0, dx1, dy1], fill=(250, 248, 242), outline=NAVY, width=2)
    d.polygon([(dx1 - 14, dy0), (dx1, dy0), (dx1, dy0 + 14)], fill=FAINT)
    for i in range(4):
        yy = dy0 + 16 + i * 12
        if yy > dy1 - 6:
            break
        d.rectangle([dx0 + 8, yy, dx1 - 8 - (10 if i == 3 else 0), yy + 4],
                    fill=(160, 154, 142))
    d.rectangle([dx0 + 8, dy0 + 8, dx0 + 26, dy0 + 8], fill=RED)
    pct = F(SERIF_B, max(9, int(h * 0.52)))
    d.text((x0 + int(w * 0.60), y0 + int(h * 0.16)), "%", font=pct, fill=RED)
    bx = x0 + int(w * 0.62)
    for i, bh in enumerate((0.16, 0.26, 0.38)):
        d.rectangle([bx + i * 16, y1 - int(h * 0.12) - int(h * bh),
                     bx + i * 16 + 11, y1 - int(h * 0.12)], fill=NAVY if i < 2 else RED)


def illo_C6(d, x0, y0, x1, y1):  # Gaza: apartment block + strike burst
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (232, 226, 214), (220, 212, 196))
    bx0, bx1 = x0 + int(w * 0.10), x0 + int(w * 0.62)
    by0, by1 = y0 + int(h * 0.18), y1 - int(h * 0.08)
    d.rectangle([bx0, by0, bx1, by1], fill=(200, 190, 170), outline=NAVY, width=2)
    cell_w = (bx1 - bx0) / 3.0
    cell_h = (by1 - by0) / 3.0
    for r in range(3):
        for c in range(3):
            wx = int(bx0 + c * cell_w + 3)
            wy = int(by0 + r * cell_h + 2)
            d.rectangle([wx, wy, wx + max(3, int(cell_w) - 6),
                         wy + max(2, int(cell_h) - 3)],
                        fill=(240, 232, 200))
    # impact burst, top right
    ix, iy = x0 + int(w * 0.80), y0 + int(h * 0.30)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line([ix, iy, ix + int(14 * u * math.cos(a)), iy + int(14 * u * math.sin(a))],
               fill=(230, 120, 30), width=2)
    rr = max(3, int(6 * u))
    d.ellipse([ix - rr, iy - rr, ix + rr, iy + rr], fill=RED)
    # smoke
    for cx, cy, r in ((0.78, 0.14, 5), (0.88, 0.10, 6)):
        rrr = int(r * u)
        d.ellipse([x0 + int(w * cx) - rrr, y0 + int(h * cy) - rrr,
                   x0 + int(w * cx) + rrr, y0 + int(h * cy) + rrr], fill=(150, 148, 142))
    # debris dots
    for px, py in ((0.68, 0.62), (0.74, 0.72), (0.90, 0.66)):
        rrr = max(1, int(2 * u))
        d.ellipse([x0 + int(w * px) - rrr, y0 + int(h * py) - rrr,
                   x0 + int(w * px) + rrr, y0 + int(h * py) + rrr], fill=(90, 88, 84))


def illo_C7(d, x0, y0, x1, y1):  # Kyiv: shopping centre + missile streak
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (210, 220, 232), (196, 208, 222))
    gy = y1 - int(h * 0.12)
    d.rectangle([x0, gy, x1, y1], fill=(120, 110, 90))
    # shopping centre, low and wide
    bx0, bx1 = x0 + int(w * 0.08), x0 + int(w * 0.66)
    by0 = gy - int(h * 0.42)
    d.rectangle([bx0, by0, bx1, gy], fill=(240, 238, 230), outline=NAVY, width=2)
    wh = max(2, (gy - by0) - 6)
    for i in range(4):
        wx = bx0 + 5 + i * max(8, int(w * 0.12))
        d.rectangle([wx, by0 + 3, wx + max(4, int(w * 0.07)), by0 + 3 + wh],
                    fill=(160, 190, 210))
    d.rectangle([bx0, by0 - 4, bx1, by0], fill=RED)
    # missile streak from the sky
    d.line([x1 - int(w * 0.04), y0 + int(h * 0.10),
            x0 + int(w * 0.66), y0 + int(h * 0.44)], fill=RED, width=max(2, int(4 * u)))
    bx, by = x0 + int(w * 0.66), y0 + int(h * 0.44)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([bx, by, bx + int(10 * u * math.cos(a)), by + int(10 * u * math.sin(a))],
               fill=(230, 120, 30), width=2)
    rr = max(2, int(4 * u))
    d.ellipse([bx - rr, by - rr, bx + rr, by + rr], fill=RED)
    # smoke + drone dots
    for cx, cy, r in ((0.80, 0.18, 5), (0.88, 0.26, 4)):
        rrr = int(r * u)
        d.ellipse([x0 + int(w * cx) - rrr, y0 + int(h * cy) - rrr,
                   x0 + int(w * cx) + rrr, y0 + int(h * cy) + rrr], fill=(150, 148, 142))
    for sx, sy in ((0.16, 0.20), (0.30, 0.12)):
        px, py = x0 + int(w * sx), y0 + int(h * sy)
        sl = max(2, int(4 * u))
        d.line([px - sl, py, px + sl, py], fill=INK, width=2)
        d.line([px, py - sl, px, py + sl], fill=INK, width=2)


def illo_C8(d, x0, y0, x1, y1):  # Cairo: fuel tanker truck + flames
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (238, 228, 205), (226, 210, 180))
    gy = y1 - int(h * 0.22)
    d.rectangle([x0, gy, x1, y1], fill=(110, 104, 94))
    d.line([x0, gy + int(h * 0.10), x1, gy + int(h * 0.10)],
           fill=(250, 250, 248), width=2)
    # tanker truck
    tx0 = x0 + int(w * 0.08)
    tw = int(w * 0.52)
    ty = gy - int(h * 0.30)
    d.rounded_rectangle([tx0, ty, tx0 + tw, gy - int(h * 0.08)], radius=8,
                        fill=(240, 238, 230), outline=NAVY, width=2)
    d.rectangle([tx0 + tw, ty + int(h * 0.08), tx0 + tw + int(w * 0.16), gy - int(h * 0.08)],
                fill=RED)
    d.rectangle([tx0 + tw + int(w * 0.03), ty + int(h * 0.12),
                 tx0 + tw + int(w * 0.13), ty + int(h * 0.22)], fill=(200, 220, 235))
    for wx in (tx0 + int(w * 0.10), tx0 + int(w * 0.34),
               tx0 + tw + int(w * 0.08)):
        wr = max(3, int(h * 0.09))
        d.ellipse([wx - wr, gy - int(h * 0.08) - wr, wx + wr, gy - int(h * 0.08) + wr],
                  fill=(30, 30, 30))
    # flames over the tank
    for fx in (0.24, 0.40):
        fxx = x0 + int(w * fx)
        d.polygon([(fxx - int(8 * u), ty), (fxx + int(8 * u), ty),
                   (fxx, ty - int(h * 0.26))], fill=(230, 120, 30))
        d.polygon([(fxx - int(4 * u), ty), (fxx + int(4 * u), ty),
                   (fxx, ty - int(h * 0.16))], fill=(245, 200, 60))
    # smoke
    for cx, cy, r in ((0.30, 0.12, 6), (0.42, 0.08, 7)):
        rr = int(r * u)
        d.ellipse([x0 + int(w * cx) - rr, y0 + int(h * cy) - rr,
                   x0 + int(w * cx) + rr, y0 + int(h * cy) + rr], fill=(150, 148, 142))
    # small car behind
    cx0 = x0 + int(w * 0.80)
    d.rectangle([cx0, gy - int(h * 0.16), cx0 + int(w * 0.14), gy - int(h * 0.08)],
                fill=NAVY)


def illo_C9(d, x0, y0, x1, y1):  # oil refinery, flames (Bangkok)
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (214, 226, 232), (196, 188, 168))
    gy = y1 - int(h * 0.16)
    d.rectangle([x0, gy, x1, y1], fill=(120, 110, 90))
    for i, tw in enumerate((0.16, 0.11, 0.13)):
        tx = x0 + int(w * (0.14 + i * 0.28))
        twpx = int(w * tw)
        d.rectangle([tx, y0 + int(h * 0.30), tx + twpx, gy], fill=NAVY)
        d.rectangle([tx - 3, y0 + int(h * 0.26), tx + twpx + 3, y0 + int(h * 0.30)],
                    fill=(60, 80, 115))
        fx = tx + twpx // 2
        d.polygon([(fx - int(9 * u), y0 + int(h * 0.26)),
                   (fx + int(9 * u), y0 + int(h * 0.26)),
                   (fx, y0 + int(h * 0.06))], fill=(230, 120, 30))
        d.polygon([(fx - int(4 * u), y0 + int(h * 0.26)),
                   (fx + int(4 * u), y0 + int(h * 0.26)),
                   (fx, y0 + int(h * 0.14))], fill=(245, 200, 60))
    d.rectangle([x0 + int(w * 0.10), gy - int(6 * u), x1 - int(w * 0.08), gy - int(2 * u)],
                fill=(90, 84, 74))
    for cx, cy, r in ((0.72, 0.16, 6), (0.80, 0.11, 7), (0.88, 0.18, 5)):
        rr = int(r * u)
        d.ellipse([x0 + int(w * cx) - rr, y0 + int(h * cy) - rr,
                   x0 + int(w * cx) + rr, y0 + int(h * cy) + rr], fill=(150, 148, 142))


def illo_C10(d, x0, y0, x1, y1):  # Ebola: virus + medical cross
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (40, 90, 90), (30, 70, 70))
    for cx, cy, rf, c in ((0.28, 0.42, 0.18, (180, 60, 60)),
                         (0.62, 0.30, 0.13, (220, 120, 60)),
                         (0.78, 0.62, 0.11, (180, 60, 60))):
        mx, my = x0 + int(w * cx), y0 + int(h * cy)
        rr = max(3, int(h * rf))
        spike = rr + max(3, int(8 * u))
        for k in range(8):
            a = math.radians(k * 45)
            d.line([mx, my, mx + int(spike * math.cos(a)), my + int(spike * math.sin(a))],
                   fill=c, width=max(2, int(3 * u)))
        d.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=c)
        d.ellipse([mx - rr // 2, my - rr // 2, mx + rr // 2, my + rr // 2],
                  fill=(240, 200, 200))
    # medical cross, bottom right
    cx0 = x1 - int(w * 0.24)
    cy0 = y1 - int(h * 0.24)
    cs = max(5, int(h * 0.18))
    d.rectangle([cx0 - cs, cy0 - cs, cx0 + cs, cy0 + cs], fill=(250, 248, 242))
    d.rectangle([cx0 - 3, cy0 - cs + 3, cx0 + 3, cy0 + cs - 3], fill=RED)
    d.rectangle([cx0 - cs + 3, cy0 - 3, cx0 + cs - 3, cy0 + 3], fill=RED)
    for px, py in ((0.12, 0.18), (0.88, 0.16), (0.20, 0.80)):
        rr = max(1, int(2 * u))
        d.ellipse([x0 + int(w * px) - rr, y0 + int(h * py) - rr,
                   x0 + int(w * px) + rr, y0 + int(h * py) + rr], fill=(240, 240, 240))


def illo_C11(d, x0, y0, x1, y1):  # EU: circle of stars + budget document
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (31, 58, 95), (40, 70, 110))
    cx, cy = x0 + int(w * 0.30), y0 + int(h * 0.50)
    rad = int(min(w, h) * 0.30)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        sx = cx + int(rad * math.cos(a))
        sy = cy + int(rad * math.sin(a))
        sl = max(2, int(4 * u))
        d.line([sx - sl, sy, sx + sl, sy], fill=(240, 220, 80), width=2)
        d.line([sx, sy - sl, sx, sy + sl], fill=(240, 220, 80), width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(240, 220, 80))
    # budget document, right
    dx0, dy0 = x0 + int(w * 0.60), y0 + int(h * 0.12)
    dx1, dy1 = x0 + int(w * 0.92), y1 - int(h * 0.12)
    d.rectangle([dx0, dy0, dx1, dy1], fill=(250, 248, 242), outline=NAVY, width=2)
    for i in range(3):
        yy = dy0 + 10 + i * 10
        if yy > dy1 - 5:
            break
        d.rectangle([dx0 + 6, yy, dx1 - 6 - (8 if i == 2 else 0), yy + 3],
                    fill=(160, 154, 142))
    d.rectangle([dx0 + 6, dy0 + 4, dx0 + 20, dy0 + 4], fill=RED)
    # coins
    for i in range(3):
        ex = x0 + int(w * 0.58)
        ey = y1 - int(h * (0.14 + i * 0.10))
        d.ellipse([ex, ey - 3, ex + 16, ey + 3], fill=(212, 160, 40),
                  outline=(160, 110, 20), width=1)


def illo_C12(d, x0, y0, x1, y1):  # ECB: bank building + euro sign
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (234, 230, 224), (222, 216, 202))
    cx = x0 + int(w * 0.36)
    d.polygon([(cx - int(w * 0.28), y0 + int(h * 0.34)),
               (cx + int(w * 0.28), y0 + int(h * 0.34)),
               (cx, y0 + int(h * 0.10))], fill=NAVY)
    for i in range(3):
        colx = x0 + int(w * (0.14 + i * 0.15))
        d.rectangle([colx, y0 + int(h * 0.36), colx + int(w * 0.07), y1 - int(h * 0.16)],
                    fill=(244, 238, 224), outline=NAVY, width=2)
    d.rectangle([x0 + int(w * 0.06), y1 - int(h * 0.16), x1 - int(w * 0.40), y1 - int(h * 0.10)],
                fill=NAVY)
    d.rectangle([x0 + int(w * 0.04), y1 - int(h * 0.09), x1 - int(w * 0.38), y1 - int(h * 0.04)],
                fill=NAVY)
    # euro symbol, right
    ef = F(SERIF_B, max(9, int(h * 0.62)))
    d.text((x0 + int(w * 0.66), y0 + int(h * 0.18)), "\u20ac", font=ef, fill=NAVY)
    d.ellipse([x0 + int(w * 0.90), y0 + int(h * 0.16), x0 + int(w * 0.94),
               y0 + int(h * 0.22)], fill=OCHRE)


def illo_C13(d, x0, y0, x1, y1):  # UK migration: falling bars + down arrow
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (236, 232, 226), (228, 222, 210))
    ax0, ay1 = x0 + int(w * 0.10), y1 - int(h * 0.14)
    ax1 = x0 + int(w * 0.88)
    ay0 = y0 + int(h * 0.16)
    d.line([ax0, ay0, ax0, ay1], fill=INK, width=2)
    d.line([ax0, ay1, ax1, ay1], fill=INK, width=2)
    for i, bh in enumerate((0.62, 0.42, 0.20)):
        bx0 = ax0 + 8 + i * int(w * 0.20)
        d.rectangle([bx0, ay1 - int(h * bh), bx0 + int(w * 0.12), ay1],
                    fill=NAVY if i < 2 else RED)
    # down arrow across the bars
    d.line([ax0 + 6, ay0 + 4, ax1 - 6, ay1 - 6], fill=RED, width=max(2, int(4 * u)))
    ex, ey = ax1 - 6, ay1 - 6
    ah = max(5, int(10 * u))
    d.polygon([(ex, ey), (ex - ah, ey - 2), (ex - 2, ey - ah)], fill=RED)
    # small plane, top right
    px, py = x0 + int(w * 0.80), y0 + int(h * 0.18)
    d.polygon([(px - 12, py), (px + 12, py), (px + 16, py + 3), (px - 8, py + 3)],
              fill=(60, 80, 115))
    d.polygon([(px - 2, py - 2), (px + 4, py - 2), (px + 8, py - 8), (px + 2, py - 8)],
              fill=(60, 80, 115))


def illo_C14(d, x0, y0, x1, y1):  # Bangladesh: factory + protest placards
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (240, 228, 200), (228, 210, 172))
    gy = y1 - int(h * 0.14)
    d.rectangle([x0, gy, x1, y1], fill=(150, 128, 92))
    # factory with sawtooth roof
    fx0 = x0 + int(w * 0.06)
    fx1 = x0 + int(w * 0.52)
    fy0 = gy - int(h * 0.42)
    d.rectangle([fx0, fy0, fx1, gy], fill=(200, 190, 170), outline=NAVY, width=2)
    d.polygon([(fx0, fy0), (fx0 + 10, fy0 - 8), (fx0 + 20, fy0),
               (fx0 + 30, fy0 - 8), (fx0 + 40, fy0), (fx0 + 50, fy0 - 8),
               (fx1, fy0)], fill=NAVY)
    for i in range(3):
        wx = fx0 + 6 + i * max(8, int(w * 0.12))
        d.rectangle([wx, fy0 + 4, wx + max(4, int(w * 0.06)), fy0 + 8],
                    fill=(240, 232, 200))
    # chimney + smoke
    chx = x0 + int(w * 0.56)
    d.rectangle([chx, y0 + int(h * 0.16), chx + 8, gy], fill=(120, 110, 100))
    for cx, cy, r in ((0.60, 0.10, 5), (0.66, 0.06, 6)):
        rr = int(r * u)
        d.ellipse([x0 + int(w * cx) - rr, y0 + int(h * cy) - rr,
                   x0 + int(w * cx) + rr, y0 + int(h * cy) + rr], fill=(150, 148, 142))
    # protest placards
    for i, px in enumerate((0.70, 0.84)):
        sx = x0 + int(w * px)
        sy = gy - int(h * 0.30)
        d.line([sx, sy, sx, gy], fill=(60, 60, 60), width=2)
        d.rectangle([sx - 10, sy - 12, sx + 10, sy], fill=RED if i == 0 else NAVY)
    # crowd dots
    for px in (0.68, 0.76, 0.92):
        rr = max(2, int(3 * u))
        d.ellipse([x0 + int(w * px) - rr, gy - int(h * 0.06) - rr,
                   x0 + int(w * px) + rr, gy - int(h * 0.06) + rr], fill=INK)


def illo_C15(d, x0, y0, x1, y1):  # GDP figures: bar chart + magnifier
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (236, 232, 226), (228, 222, 210))
    ax0, ay1 = x0 + int(w * 0.10), y1 - int(h * 0.14)
    ax1 = x0 + int(w * 0.88)
    ay0 = y0 + int(h * 0.16)
    d.line([ax0, ay0, ax0, ay1], fill=INK, width=2)
    d.line([ax0, ay1, ax1, ay1], fill=INK, width=2)
    for i, bh in enumerate((0.24, 0.40, 0.56)):
        bx0 = ax0 + 8 + i * int(w * 0.20)
        d.rectangle([bx0, ay1 - int(h * bh), bx0 + int(w * 0.12), ay1],
                    fill=TEAL if i < 2 else RED)
    # magnifier over the middle bar
    mx, my = ax0 + int(w * 0.42), y0 + int(h * 0.42)
    mr = max(6, int(h * 0.24))
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=NAVY, width=max(2, int(3 * u)))
    d.line([mx + int(mr * 0.7), my + int(mr * 0.7),
            mx + int(mr * 1.3), my + int(mr * 1.3)], fill=NAVY,
           width=max(2, int(4 * u)))
    d.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=RED)


ILLOS = [illo_L1, illo_L2, illo_L3, illo_C4, illo_C5, illo_C6, illo_C7,
         illo_C8, illo_C9, illo_C10, illo_C11, illo_C12, illo_C13,
         illo_C14, illo_C15]

# ---------------------------------------------------------------- layout

def fs(base, s):
    return max(7, int(round(base * s)))


def section_header(d, y, text, s, right=None):
    f = F(SANS_B, fs(12, s))
    d.text((MARGIN, y), text, font=f, fill=RED)
    tw = f.getlength(text)
    ry = y + f.size // 2
    x_end = W - MARGIN
    if right:
        fr = F(SANS, fs(10, s))
        rw = fr.getlength(right)
        d.text((x_end - rw, y + 1), right, font=fr, fill=INK)
        x_end = x_end - rw - 10
    d.line([MARGIN + tw + 8, ry, x_end, ry], fill=INK, width=1)
    return y + fs(12, s) + 4


def draw_centered(d, y, text, font, fill):
    w = font.getlength(text)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)
    return y + font.size + 2


def render_page(s):
    warns = []
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 10

    # kicker + count line + masthead + subhead
    y = draw_centered(d, y, "THE WORLD IN ONE DAY",
                      F(SANS_B, fs(13, s)), RED)
    y = draw_centered(d, y, "50 STORIES \u00b7 10 REGIONS \u00b7 "
                      "21 FIELDS \u00b7 ALL FIRST REPORTED ON THURSDAY "
                      "26 NOVEMBER 2026", F(SANS, fs(11, s)), INK)
    y += 1
    y = draw_centered(d, y, "Thursday 26 November 2026",
                      F(SERIF_B, fs(38, s)), INK)
    y += 1
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)
    y += 4
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 6
    y = draw_centered(d, y, SUBHEAD, F(SANS_B, fs(11, s)), RED)
    y += 3

    # ---- REGION + FIELD strips
    f_strip = F(SANS, fs(10, s))
    f_strip_b = F(SANS_B, fs(10, s))
    lab_r = "REGIONS  "
    d.text((MARGIN, y), lab_r, font=f_strip_b, fill=RED)
    d.text((MARGIN + f_strip_b.getlength(lab_r), y), REGION_STRIP,
           font=f_strip, fill=INK)
    y += text_h(f_strip) + 2
    lab_f = "FIELDS  "
    flines = wrap(FIELD_STRIP, f_strip, CW - f_strip_b.getlength(lab_f))
    d.text((MARGIN, y), lab_f, font=f_strip_b, fill=RED)
    for j, ln in enumerate(flines):
        d.text((MARGIN + (f_strip_b.getlength(lab_f) if j == 0 else 0), y),
               ln, font=f_strip, fill=INK)
        y += text_h(f_strip)
    y += 5
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 7

    # ---- THE DAY IN NUMBERS
    y = section_header(d, y, "THE DAY IN NUMBERS", s)
    ncol_w = CW / 6.0
    f_val = F(SERIF_B, fs(22, s))
    f_nlab = F(SANS, fs(10, s))
    nlh = text_h(f_nlab)
    num_h = text_h(f_val) + 2 * nlh
    for i, (val, label) in enumerate(NUMBERS):
        x = MARGIN + i * ncol_w
        d.text((x + 2, y), val, font=f_val, fill=RED)
        lines = wrap(label, f_nlab, ncol_w - 6)
        if len(lines) > 2:
            warns.append(f"number {i + 1} label wraps to {len(lines)} lines")
        for j, ln in enumerate(lines[:2]):
            d.text((x + 2, y + text_h(f_val) + j * nlh), ln, font=f_nlab, fill=INK)
    y += num_h + 5

    # ---- THE DAY IN UTC
    y = section_header(d, y, "THE DAY IN UTC", s)
    col_w = CW / 8.0
    f_time = F(SANS_B, fs(11, s))
    f_lab = F(SANS, fs(10, s))
    lh = text_h(f_lab)
    utc_h = text_h(f_time) + 2 * lh
    for i, (t, label) in enumerate(UTC_ITEMS):
        x = MARGIN + i * col_w
        d.text((x + 2, y), t, font=f_time, fill=RED)
        lines = wrap(label, f_lab, col_w - 6)
        if len(lines) > 2:
            warns.append(f"UTC item {i + 1} wraps to {len(lines)} lines")
        for j, ln in enumerate(lines[:2]):
            d.text((x + 2, y + text_h(f_time) + j * lh), ln, font=f_lab, fill=INK)
    y += utc_h + 5
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 7

    # ---- 3 LEADS
    lead_gap = 10
    lead_w = (CW - 2 * lead_gap) // 3
    pad = 8
    illo_h = int(62 * s)
    f_lhead = F(SERIF_B, fs(19, s))
    f_lbody = F(SANS, fs(11, s))
    f_why = F(SANS, fs(10, s))
    f_why_b = F(SANS_B, fs(10, s))
    f_ltag = F(SANS_B, fs(10, s))
    why_prefix = "WHY IT MATTERS \u2014 "
    lead_blocks = []
    for n, (head, body, why, tag) in enumerate(LEADS, start=1):
        hl = wrap(head, f_lhead, lead_w - 2 * pad)
        bl = wrap(body, f_lbody, lead_w - 2 * pad)
        wl = wrap(why, f_why, lead_w - 2 * pad - f_why_b.getlength(why_prefix))
        if len(hl) > 2:
            warns.append(f"lead {n} headline wraps to {len(hl)} lines")
        if len(bl) > 3:
            warns.append(f"lead {n} body wraps to {len(bl)} lines")
        if len(wl) > 3:
            warns.append(f"lead {n} why wraps to {len(wl)} lines")
        if f_ltag.getlength(tag) > lead_w - 2 * pad:
            warns.append(f"lead {n} tag too wide")
        bh = (pad + illo_h + 5 + len(hl) * text_h(f_lhead) + 4
              + len(bl) * text_h(f_lbody) + 4
              + len(wl) * text_h(f_why) + 6 + text_h(f_ltag) + pad)
        lead_blocks.append((n, head, body, why, tag, hl, bl, wl, bh))
    box_h = max(b[8] for b in lead_blocks)
    for i, (n, head, body, why, tag, hl, bl, wl, bh) in enumerate(lead_blocks):
        x = MARGIN + i * (lead_w + lead_gap)
        d.rectangle([x, y, x + lead_w, y + box_h], outline=INK, width=1)
        ix0, iy0 = x + 1, y + 1
        ILLOS[n - 1](d, ix0, iy0, x + lead_w - 1, iy0 + illo_h)
        # number badge
        d.rectangle([ix0, iy0, ix0 + 22, iy0 + 22], fill=RED)
        fb = F(SANS_B, fs(13, s))
        d.text((ix0 + 11 - fb.getlength(str(n)) / 2, iy0 + 3), str(n),
               font=fb, fill=(255, 255, 255))
        ty = iy0 + illo_h + 5
        for ln in hl:
            d.text((x + pad, ty), ln, font=f_lhead, fill=INK)
            ty += text_h(f_lhead)
        ty += 4
        for ln in bl:
            d.text((x + pad, ty), ln, font=f_lbody, fill=INK)
            ty += text_h(f_lbody)
        ty += 4
        for j, ln in enumerate(wl):
            if j == 0:
                d.text((x + pad, ty), why_prefix, font=f_why_b, fill=RED)
                d.text((x + pad + f_why_b.getlength(why_prefix), ty), ln,
                       font=f_why, fill=INK)
            else:
                d.text((x + pad, ty), ln, font=f_why, fill=INK)
            ty += text_h(f_why)
        d.text((x + pad, y + box_h - pad - text_h(f_ltag)), tag,
               font=f_ltag, fill=RED)
    y += box_h + 7

    # ---- 12 SMALL CARDS (6 x 2)
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 6
    card_gap = 8
    card_w = (CW - 5 * card_gap) // 6
    cpad = 6
    cillo_h = int(22 * s)
    f_chead = F(SANS_B, fs(13, s))
    f_cbody = F(SANS, fs(10, s))
    f_ctag = F(SANS_B, fs(9, s))
    for row in range(2):
        row_cards = CARDS[row * 6:(row + 1) * 6]
        blocks = []
        for k, (head, body, tag) in enumerate(row_cards):
            n = row * 6 + k + 4
            hl = wrap(head, f_chead, card_w - 2 * cpad)
            bl = wrap(body, f_cbody, card_w - 2 * cpad)
            if len(hl) > 2:
                warns.append(f"card {n} headline wraps to {len(hl)} lines")
            if len(bl) > 3:
                warns.append(f"card {n} body wraps to {len(bl)} lines")
            if f_ctag.getlength(tag) > card_w - 2 * cpad:
                warns.append(f"card {n} tag too wide")
            bh = (cpad + cillo_h + 4 + len(hl) * text_h(f_chead) + 3
                  + len(bl) * text_h(f_cbody) + 5 + text_h(f_ctag) + cpad)
            blocks.append((n, hl, bl, tag, bh))
        row_h = max(b[4] for b in blocks)
        for i, (n, hl, bl, tag, bh) in enumerate(blocks):
            x = MARGIN + i * (card_w + card_gap)
            d.rectangle([x, y, x + card_w, y + row_h], outline=INK, width=1)
            ix0, iy0 = x + 1, y + 1
            ILLOS[n - 1](d, ix0, iy0, x + card_w - 1, iy0 + cillo_h)
            d.rectangle([ix0, iy0, ix0 + 16, iy0 + 16], fill=RED)
            fb = F(SANS_B, fs(10, s))
            d.text((ix0 + 8 - fb.getlength(str(n)) / 2, iy0 + 2), str(n),
                   font=fb, fill=(255, 255, 255))
            ty = iy0 + cillo_h + 4
            for ln in hl:
                d.text((x + cpad, ty), ln, font=f_chead, fill=INK)
                ty += text_h(f_chead)
            ty += 3
            for ln in bl:
                d.text((x + cpad, ty), ln, font=f_cbody, fill=INK)
                ty += text_h(f_cbody)
            d.text((x + cpad, y + row_h - cpad - text_h(f_ctag)), tag,
                   font=f_ctag, fill=RED)
        y += row_h + 6

    # ---- ALSO ON THURSDAY (briefs 16-50)
    y = section_header(d, y, "ALSO ON THURSDAY", s)
    f_bnum = F(SANS_B, fs(10, s))
    f_bbody = F(SANS, fs(10, s))
    f_btag = F(SANS_B, fs(10, s))
    brow_h = text_h(f_bbody) + 1
    bcol_w = (CW - 16) // 2
    for idx, (num, body, tag) in enumerate(BRIEFS):
        col = idx // 18
        row = idx % 18
        x = MARGIN + col * (bcol_w + 16)
        yy = y + row * brow_h
        num_s = f"{num} "
        tag_s = f" [{tag}]"
        total = (f_bnum.getlength(num_s) + f_bbody.getlength(body)
                 + f_btag.getlength(tag_s))
        if total > bcol_w:
            warns.append(f"brief {num} too wide by {int(total - bcol_w)}px")
        d.text((x, yy), num_s, font=f_bnum, fill=RED)
        bx = x + f_bnum.getlength(num_s)
        d.text((bx, yy), body, font=f_bbody, fill=INK)
        d.text((bx + f_bbody.getlength(body), yy), tag_s, font=f_btag, fill=RED)
    y += 18 * brow_h + 3

    # ---- WHERE IT HAPPENED (map)
    y = section_header(d, y, "WHERE IT HAPPENED", s)
    map_h = int(84 * s)
    map_y0 = y
    d.rectangle([MARGIN, map_y0, W - MARGIN, map_y0 + map_h], outline=INK, width=1)

    def proj(lon, lat):
        px = MARGIN + (lon + 180.0) / 360.0 * CW
        py = map_y0 + (78.0 - lat) / 140.0 * map_h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f_pin = F(SANS_B, fs(9, s))
    for num, lon, lat, dx, dy, colour in PINS:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        if dx or dy:
            d.line([px, py, cx, cy], fill=colour, width=1)
        r = 8
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour,
                  outline=(255, 255, 255), width=1)
        nw = f_pin.getlength(str(num))
        d.text((cx - nw / 2, cy - f_pin.size / 2 - 1), str(num),
               font=f_pin, fill=(255, 255, 255))
    y = map_y0 + map_h + 4
    # legend
    f_leg = F(SANS, fs(9, s))
    lx = MARGIN
    for name, colour in LEGEND:
        d.rectangle([lx, y + 2, lx + 8, y + 10], fill=colour)
        lx += 11
        d.text((lx, y), name, font=f_leg, fill=INK)
        lx += f_leg.getlength(name) + 12
    y += text_h(f_leg) + 6

    # ---- DATE CHECK (red box)
    f_dc_h = F(SANS_B, fs(11, s))
    f_dc = F(SANS, fs(10, s))
    dc_lines = []
    dc_lines.append(("head", DATE_CHECK_HEAD))
    dc_lines += [("body", ln) for ln in wrap(DATE_CHECK_LEFT, f_dc, CW - 16)]
    dc_lines += [("body", ln) for ln in wrap(DATE_CHECK_NOTYET, f_dc, CW - 16)]
    box_h = 8 + text_h(f_dc_h) + 2 + (len(dc_lines) - 1) * text_h(f_dc) + 8
    d.rectangle([MARGIN, y, W - MARGIN, y + box_h], outline=RED, width=2)
    ty = y + 8
    for kind, ln in dc_lines:
        if kind == "head":
            d.text((MARGIN + 8, ty), ln, font=f_dc_h, fill=RED)
            ty += text_h(f_dc_h) + 2
        else:
            d.text((MARGIN + 8, ty), ln, font=f_dc, fill=INK)
            ty += text_h(f_dc)
    y += box_h + 6

    # ---- footer
    f_ft = F(SANS, fs(9, s))
    ft_lines = wrap(FOOTER, f_ft, CW)
    for ln in ft_lines:
        d.text((MARGIN, y), ln, font=f_ft, fill=GREY)
        y += text_h(f_ft)

    return img, y, warns


def main():
    assert len(LEADS) == 3, f"leads {len(LEADS)} != 3"
    assert len(CARDS) == 12, f"cards {len(CARDS)} != 12"
    assert len(BRIEFS) == 35, f"briefs {len(BRIEFS)} != 35"
    assert len(UTC_ITEMS) == 8, f"utc {len(UTC_ITEMS)} != 8"
    assert len(NUMBERS) == 6, f"numbers {len(NUMBERS)} != 6"
    assert len(PINS) == 15, f"pins {len(PINS)} != 15"
    print("counts: leads 3, cards 12, briefs 35, total",
          3 + 12 + 35, "| utc 8 | numbers 6 | pins 15")
    chosen = None
    for s in (1.0, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76, 0.72):
        img, fy, warns = render_page(s)
        print(f"scale={s} final y = {fy}")
        if fy <= 1016:
            chosen = (s, img, fy, warns)
            break
    if chosen is None:
        s, img, fy, warns = 0.72, img, fy, warns
        print("WARNING: still over 1016 at smallest scale")
    else:
        s, img, fy, warns = chosen
    for wmsg in warns:
        print("WARN:", wmsg)
    img.save("entry.png", optimize=True)
    print("scale =", s)
    print("final y =", fy)
    print("entry.png bytes =", os.path.getsize("entry.png"))


if __name__ == "__main__":
    main()
