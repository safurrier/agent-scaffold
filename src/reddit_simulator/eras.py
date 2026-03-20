"""Historical era definitions with event seeds, context, and style guides."""

from __future__ import annotations

from typing import TypedDict


class EraDefinition(TypedDict):
    name: str
    date: str
    subreddit: str
    event: str
    context: str
    style_guide: str
    post_seeds: list[str]
    forbidden_concepts: list[str]


ERAS: dict[str, EraDefinition] = {
    "pompeii": {
        "name": "Pompeii, 79 AD",
        "date": "August 24, 79 AD",
        "subreddit": "r/Pompeii",
        "event": "Mount Vesuvius eruption",
        "context": """
Pompeii is a prosperous Roman city of ~11,000 people near the Bay of Naples.
Residents are Roman citizens, freedmen, slaves, merchants, gladiators, priests, and craftsmen.
The city has a forum, amphitheater, temples, bathhouses (thermae), taverns (cauponae),
fast-food stalls (thermopolia), and brothels (lupanare).
People worship Jupiter, Venus (patron goddess of Pompeii), Mercury, Isis, and other gods.
Local concerns: upcoming gladiatorial games, the upcoming harvest, trade disputes, omens.
The city has been experiencing tremors for several weeks. Today, Vesuvius is spewing smoke.
Currency: sestertii, denarii, asses. Wealthy citizens have slaves and country estates.
Graffiti on walls is a normal form of public communication.
Time is measured in watches (horae). It is the 9th hour (mid-afternoon).
        """,
        "style_guide": """
Write in English but with Roman sensibility — formal with patrons/clients, casual with friends.
Use some Latin terms naturally: vale (farewell), salve (greetings), amici (friends),
thermopolium (snack bar), insula (apartment block), dominus (master), libertas (freedom).
Common exclamations: 'By Jupiter!', 'By the gods!', 'May the Fates be kind', 'As Juno is my witness'.
Reference local landmarks: the Forum, the Basilica, the amphitheater, the Temple of Venus.
People are pragmatic, superstitious, and very concerned about omens and divine will.
Merchants worry about money. Slaves worry about freedom. Citizens worry about status.
Nobody has seen a volcanic eruption before — there is confusion about what is happening.
        """,
        "post_seeds": [
            "The smoke from Vesuvius and strange sulfur smell",
            "The tremors that have been shaking the city for weeks",
            "Upcoming gladiatorial games in the amphitheater",
            "The shortage of fresh water after recent tremors broke aqueducts",
            "Strange behavior of animals — horses and dogs fleeing the city",
            "An omen seen at the Temple of Jupiter",
            "The harvest and whether the gods are angry",
            "A merchant's goods destroyed in the latest tremor",
        ],
        "forbidden_concepts": [
            "electricity",
            "guns",
            "photography",
            "internet",
            "telephone",
            "Christianity as mainstream religion",
            "gunpowder",
            "printing press",
            "compass",
            "telescope",
            "anything from after 79 AD",
        ],
    },
    "medieval_plague": {
        "name": "Medieval England, 1348",
        "date": "Summer 1348",
        "subreddit": "r/England1348",
        "event": "The Black Death arrives in England",
        "context": """
England in 1348. King Edward III rules. The Black Death (bubonic plague) has arrived
from the continent and is spreading rapidly from Bristol and Southampton.
Society is feudal: nobility, clergy, knights, freemen, serfs.
The Church (Catholic) dominates spiritual and intellectual life. Latin is for scholars;
English dialects are spoken by common people.
People believe illness comes from bad air (miasma), divine punishment, or Jewish conspiracy.
Physicians recommend bloodletting, herbs, prayer, and fleeing the infected areas.
The plague kills 30-60% of those infected. Symptoms: swollen lymph nodes (buboes),
black skin, fever, death within days. Terror is widespread.
Village life: farming, markets, local lord's manor, parish church.
        """,
        "style_guide": """
Write in modern English but with medieval sensibility — pious, superstitious, community-focused.
Reference God, saints, the Church, divine punishment constantly.
Common phrases: 'God preserve us', 'pray for our souls', 'the Lord's will', 'a pox upon it'.
People would refer to the plague as 'the pestilence', 'the great mortality', or 'God's visitation'.
No scientific germ theory — people believe in miasma, sin, and celestial causes.
Class matters enormously: serfs address lords respectfully, clergy are respected.
Reference local concerns: the harvest, the lord's taxes, the village priest, neighboring villages.
There is genuine terror and confusion — nobody understands what is happening.
        """,
        "post_seeds": [
            "The pestilence has reached our village — what should we do",
            "The priests say this is God's punishment for our sins",
            "Should we flee to the countryside or stay",
            "Strange remedies people are trying against the pestilence",
            "The gravediggers cannot keep up — what is to be done",
            "My neighbor's entire family has been taken in a fortnight",
            "The market has closed — how will we feed our families",
            "The flagellants have come to our town",
        ],
        "forbidden_concepts": [
            "germ theory",
            "bacteria",
            "antibiotics",
            "hospitals",
            "doctors as modern",
            "Protestantism",
            "printing press",
            "gunpowder widespread",
            "anything from after 1348",
        ],
    },
    "moon_landing": {
        "name": "Earth, July 20, 1969",
        "date": "July 20, 1969",
        "subreddit": "r/MoonLanding1969",
        "event": "Apollo 11 Moon Landing",
        "context": """
July 20, 1969. Apollo 11 is landing on the Moon. Neil Armstrong and Buzz Aldrin
are about to become the first humans to walk on the lunar surface.
The Cold War is at full intensity. Americans are beating the Soviets in the Space Race.
People are watching on black-and-white TV sets. Walter Cronkite is broadcasting.
Context: JFK's 1961 challenge, the Apollo 1 fire, Gemini missions, Soviet Sputnik.
American society: Vietnam War protests, civil rights movement, Woodstock upcoming.
The counterculture is questioning whether the moon money could feed the poor.
Average Americans are watching in living rooms, bars, airports around the world.
Technology: rotary phones, TV, radio, newspapers. No internet, no mobile phones.
The broadcast has occasional static. NASA is in Houston. EST timezone.
        """,
        "style_guide": """
Write in authentic 1969 American vernacular — enthusiastic, patriotic, Cold War mindset.
Use period slang: 'groovy', 'far out', 'out of sight', 'right on', 'hip', 'square'.
Period concerns: Vietnam, hippies, Nixon's presidency, the draft, civil rights.
People are genuinely awestruck — this has never happened before in human history.
Some are skeptical or cynical: 'why spend the money when people are starving'.
Reference: Tang (the drink), freeze-dried food, Walter Cronkite, CBS News, Houston.
No internet, no social media, no smartphones, no personal computers, no cable TV.
People are calling each other on landlines, gathering around TVs in public spaces.
Some reference the USSR — competitive pride against the Soviets is a major theme.
        """,
        "post_seeds": [
            "HOLY COW they actually landed — watching on TV right now",
            "The landing! Eagle has landed! They really did it!",
            "My thoughts watching Armstrong step onto the Moon",
            "Anyone else thinking about how we beat the Soviets today",
            "This is what JFK died believing in — we made it",
            "Counterpoint: we could have fed thousands with this money",
            "Technical breakdown: how the LEM guidance computer worked",
            "Watching in Times Square with hundreds of strangers",
        ],
        "forbidden_concepts": [
            "internet",
            "smartphones",
            "social media",
            "cable TV",
            "personal computers",
            "AIDS",
            "fall of Berlin Wall",
            "anything from after July 1969",
        ],
    },
    "berlin_wall": {
        "name": "Berlin, November 9, 1989",
        "date": "November 9, 1989",
        "subreddit": "r/Berlin1989",
        "event": "Fall of the Berlin Wall",
        "context": """
November 9, 1989, Berlin. The East German government has announced citizens can
cross the border freely. Crowds are gathering at checkpoints. People are climbing
the Wall with hammers and pickaxes. East and West Germans are embracing.
This is the end of 28 years of division. The Cold War is effectively over.
Context: Gorbachev's glasnost/perestroika, protests across Eastern Europe,
Hungary opened its border, Soviet empire crumbling.
In East Berlin: Trabants (small cars), limited goods, Stasi secret police,
travel restrictions, state-controlled media, collective housing.
In West Berlin: capitalism, rock music, American influence, neon lights, freedom.
Berliners are crying, drinking champagne, singing, hugging strangers.
The world is watching on CNN, which is providing live coverage.
        """,
        "style_guide": """
Write in English with period-appropriate voice — raw emotion, disbelief, joy, fear, hope.
Mix West German and East German perspectives. East Germans are stunned, overwhelmed.
West Germans are celebratory but also uncertain about what reunification means.
Political discussions: Gorbachev, Honecker just resigned, Kohl's Germany, NATO.
Period references: Trabant cars, Checkpoint Charlie, Brandenburg Gate, Alexanderplatz.
Some are fearful — what does this mean for jobs? For housing? For the future?
Party/celebration atmosphere mixed with serious political commentary.
No smartphones, no social media. People are watching CNN or at the Wall itself.
East Germans may use slightly different phrasing — more formal German sensibility.
The sense of history being made RIGHT NOW is overwhelming to everyone.
        """,
        "post_seeds": [
            "I just climbed the Wall — this is really happening",
            "The border guard just waved us through at Checkpoint Charlie",
            "My family was separated for 20 years — tonight we reunite",
            "What does this mean for Germany? Will we reunify?",
            "Watching CNN coverage — is this real life",
            "The Trabant driving through to West Berlin — we are free",
            "Some thoughts from an East Berliner who doesn't know what comes next",
            "The hammers and pickaxes are out — everyone is a piece of history",
        ],
        "forbidden_concepts": [
            "internet",
            "smartphones",
            "social media",
            "email",
            "EU expansion",
            "9/11",
            "euro currency",
            "anything from after November 1989",
        ],
    },
    "titanic": {
        "name": "RMS Titanic, April 14–15, 1912",
        "date": "April 14, 1912, 11:40 PM",
        "subreddit": "r/TitanicVoyage",
        "event": "RMS Titanic strikes iceberg",
        "context": """
April 14, 1912, 11:40 PM ship's time. The RMS Titanic has struck an iceberg
in the North Atlantic, about 400 miles south of Newfoundland.
The ship is on its maiden voyage from Southampton to New York City.
On board: 2,224 people. 1st class passengers (wealthy Americans and British),
2nd class (middle class), 3rd class / steerage (immigrants to America, mostly).
The ship's officers know it will sink. There are not enough lifeboats for everyone.
The band is playing. The first lifeboats are being lowered — most are not full.
Wireless operators are sending SOS/CQD distress calls. The Carpathia is responding.
1st class: opulent dining rooms, private promenades, reading rooms.
3rd class: crowded dormitories, communal dining, gates separating them from upper decks.
The ship is titled 'unsinkable' — many passengers do not believe it's serious.
        """,
        "style_guide": """
Write in Edwardian English — formal, class-conscious, with period-appropriate anxiety.
1st class passengers: more formal, entitled, disbelieving this could happen.
2nd class: practical, community-minded, helpful.
3rd class/steerage: frightened, many non-English speakers (Polish, Irish, Italian).
Period phrases: 'I say', 'rather', 'bally', 'dreadful', 'By Jove', 'capital'.
Class divisions matter enormously — a 1st class passenger and a steerage passenger
would have very different experiences and voices.
Nobody knows yet whether they will survive. There is confusion, denial, fear.
Reference: the lifeboats, the band playing, the tilt of the deck, the cold air.
Wireless telegram communication is cutting-edge technology.
        """,
        "post_seeds": [
            "The ship has struck something — there is a scraping sound",
            "An officer just told us to put on our life belts",
            "The lifeboats are being lowered — but women and children first",
            "The band is still playing — can you believe it",
            "We are locked below decks — someone please help us",
            "I sent a wireless telegram to my family in New York",
            "The ship is tilting badly now — this is serious",
            "An officer says we have two hours — two hours!",
        ],
        "forbidden_concepts": [
            "smartphones",
            "radio (as common)",
            "television",
            "internet",
            "GPS",
            "anything about the wreck discovery in 1985",
            "anything from after 1912",
        ],
    },
}


def get_era(key: str) -> EraDefinition:
    """Retrieve an era definition by key."""
    if key not in ERAS:
        available = ", ".join(ERAS.keys())
        raise ValueError(f"Unknown era '{key}'. Available: {available}")
    return ERAS[key]


def list_eras() -> list[tuple[str, str, str]]:
    """Return list of (key, name, event) tuples."""
    return [(k, v["name"], v["event"]) for k, v in ERAS.items()]
