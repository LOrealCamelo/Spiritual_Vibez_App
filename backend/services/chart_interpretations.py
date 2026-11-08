"""Symbolic astrology prose, kept separate from measured sky coordinates."""
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGN_STYLE = [
    'directness, initiative and the willingness to begin before everything is certain',
    'steadiness, sensory awareness and a preference for building something that lasts',
    'curiosity, conversation and the ability to consider more than one perspective',
    'emotional memory, protection and a need for meaningful belonging',
    'creative expression, warmth and the courage to be seen',
    'discernment, practical care and the desire to improve what you encounter',
    'cooperation, aesthetic balance and attention to fairness between people',
    'depth, emotional honesty and an interest in what lies beneath the surface',
    'exploration, conviction and the search for a larger context',
    'patience, responsibility and a commitment to making plans tangible',
    'independent thinking, experimentation and concern for the wider community',
    'imagination, empathy and sensitivity to experiences that resist neat definitions',
]
PLANET_THEMES = {
    'Sun': ('identity and vitality', 'The Sun describes a way of developing confidence and expressing a coherent sense of self. Its sign suggests the qualities you may practice as you become more comfortable choosing your own direction.'),
    'Moon': ('emotional needs and habitual responses', 'The Moon symbolizes familiar responses, sources of comfort and the rhythms that help you feel at home. Its sign offers a vocabulary for emotional needs; it is not a diagnosis or a fixed description of how you must feel.'),
    'Mercury': ('communication and learning', 'Mercury describes how you gather information, make connections and put experience into words. Its placement can be a useful prompt for considering which kinds of conversation, study and decision making suit you.'),
    'Venus': ('values, connection and pleasure', 'Venus symbolizes attraction, enjoyment and the values that guide relationship choices. Consider both what feels beautiful to you and how you negotiate giving, receiving and mutual respect.'),
    'Mars': ('initiative, desire and boundaries', 'Mars describes the expression of effort and desire: how you begin, pursue a goal and respond to friction. Its symbolism can help you distinguish a clear boundary from an impulsive reaction.'),
    'Jupiter': ('growth, meaning and opportunity', 'Jupiter points to the search for possibility, learning and a larger sense of meaning. Its gifts are easier to use when enthusiasm is accompanied by realistic limits rather than assumptions that every opportunity will work out.'),
    'Saturn': ('structure, limits and commitment', 'Saturn symbolizes skills developed through repetition, boundaries and the responsibilities you choose to carry. This placement can describe an area where confidence grows gradually as you gain experience.'),
    'Uranus': ('change, independence and experimentation', 'Uranus is associated with departures from habit and the wish to do things differently. Because it moves slowly, its sign is shared by many people; its house is more specific to the birth time and place.'),
    'Neptune': ('imagination, ideals and ambiguity', 'Neptune symbolizes dreams, inspiration and the difficulty of separating an ideal from what is actually available. Its slow-moving sign is generational; its house can focus reflection on where clarity and compassion need to work together.'),
    'Pluto': ('power, endings and renewal', 'Pluto is associated with deep change, questions of control and the rebuilding that follows an ending. Its sign belongs to a generation, so avoid treating that sign alone as a unique personality label.'),
}
HOUSE_THEMES = [
    ('Self & first impressions', 'how you approach unfamiliar situations, present yourself and begin acting on your own behalf'),
    ('Resources & values', 'money, possessions, practical security and the values that shape your use of resources'),
    ('Communication & learning', 'everyday conversations, siblings, local connections and the skills you practice regularly'),
    ('Home & roots', 'home life, family history, privacy and the foundations that help you feel supported'),
    ('Creativity & enjoyment', 'creative risks, play, romance and the activities you pursue for their own sake'),
    ('Daily life & care', 'routines, work habits, useful service and the practical ways you care for yourself'),
    ('Partnerships', 'one-to-one relationships, agreements, collaboration and the negotiation of differences'),
    ('Shared resources & change', 'shared finances, trust, intimacy and experiences of release or transition'),
    ('Beliefs & exploration', 'higher education, travel, philosophy and the frameworks you use to make meaning'),
    ('Vocation & public life', 'public responsibilities, career direction and the contribution you want others to recognize'),
    ('Community & hopes', 'friendships, groups, shared projects and your hopes for the future'),
    ('Rest & inner life', 'solitude, reflection, hidden patterns and the space you need away from public demands'),
]
ASPECT_TEXT = {
    'Conjunction': 'These two themes occupy nearly the same direction in the zodiac. Their expression may feel closely blended; it can help to notice when one need is taking over the space of the other.',
    'Sextile': 'This relationship is traditionally read as a useful opening between the two themes. It suggests an option to practice cooperation, rather than a benefit that arrives without participation.',
    'Square': 'This angle symbolizes friction between needs that do not automatically fit together. Experiment with a concrete adjustment that gives both themes a role instead of trying to eliminate one.',
    'Trine': 'This relationship is traditionally associated with ease and familiar strengths. Notice what already works, and consider how to use it deliberately rather than taking it for granted.',
    'Opposition': 'These themes face each other across the chart. Their symbolism invites perspective and balance: a relationship or situation may make you more aware of a need you usually place outside yourself.',
}


def planet_report(planet, position, house):
    theme, opening = PLANET_THEMES[planet]
    style = SIGN_STYLE[SIGNS.index(position['sign'])]
    title, area = HOUSE_THEMES[house - 1]
    return [opening, f"In {position['sign']}, {planet}'s themes of {theme} are expressed through {style}. In house {house} ({title}), consider how this relates to {area}.",
            ('Retrograde means the planet appeared to move backward along the zodiac from Earth. Symbolically, you might explore a more reflective or personally defined relationship with these themes; it does not mean the planet is physically moving backward.' if position['retrograde'] else
             'Direct motion means the apparent zodiac longitude was increasing at birth. Read this placement together with the rest of the chart rather than as a standalone verdict.')]


def house_report(number, sign):
    title, area = HOUSE_THEMES[number - 1]
    return f"House {number} concerns {area}. With {sign} on its cusp, its symbolic approach emphasizes {SIGN_STYLE[SIGNS.index(sign)]}. Planets in this house add their own themes; an empty house still has meaning and does not imply that this part of life is missing."


def transit_forecast(sign, positions):
    sign_index = SIGNS.index(sign)
    details = []
    for planet in ('Moon', 'Mercury', 'Venus', 'Mars', 'Saturn'):
        p = positions[planet]
        house = (SIGNS.index(p['sign']) - sign_index) % 12 + 1
        title, area = HOUSE_THEMES[house - 1]
        text = f"{planet} in {p['sign']} falls in your solar house {house}, highlighting {area}."
        if p['retrograde']:
            text += f" {planet} is retrograde: use this symbolism as an invitation to review rather than rush decisions in this area."
        if planet == 'Mercury' and sign in ('Gemini', 'Virgo'):
            text += f" Mercury traditionally rules {sign}, so its communication and planning themes may be especially useful reflection prompts for you."
        if planet == 'Moon':
            text += ' Check what support you actually need today before assuming a particular mood.'
        details.append(dict(planet=planet, solar_house=house, title=title, text=text))
    return dict(sign=sign, header=f'Your {sign} daily reflection',
                content=' '.join(d['text'] for d in details), details=details,
                method='Whole-sign solar houses relative to your chosen Sun sign; this is not a personal natal transit report.',
                note='Astrology is symbolic and does not scientifically predict your feelings or events.')
