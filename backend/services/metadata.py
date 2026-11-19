"""Traceable Pythagorean name/date metadata and original symbolic readings.

No web requests, language-model calls, biographical inference or database writes.
"""
from collections import Counter
from datetime import date
from html import escape
import re
import unicodedata

MASTERS={11,22,33}
DEBTS={13:'Steady effort and sustainable structure',14:'Freedom with consistency and responsibility',
       16:'Humility, honest self-examination and rebuilding perspective',19:'Independence that leaves room for cooperation'}
PROFILES={
 1:dict(title='The Initiator',gift='independence, originality and the courage to begin',edge='turning self-reliance into isolation, impatience or a need to control the outcome',practice='choose one direction of your own while leaving room for feedback',service='give an idea a clear beginning and help others trust their own agency',question='Where can I lead without having to do everything alone?'),
 2:dict(title='The Bridge',gift='cooperation, listening and sensitivity to relationships',edge='silencing your needs to keep the peace or letting approval make the decision',practice='name your preference clearly before looking for a compromise',service='create the conditions for honest cooperation, rather than carrying both sides of a relationship',question='Can I make room for another person without disappearing?'),
 3:dict(title='The Voice',gift='communication, imagination, play and creative expression',edge='hiding behind performance, scattering your attention or waiting to feel perfectly ready to be seen',practice='finish and share one small piece of honest expression',service='translate an experience into language, art or connection that gives someone else permission to feel',question='What wants a voice, even if it comes out imperfectly?'),
 4:dict(title='The Builder',gift='reliability, practical skill and the ability to make something last',edge='confusing safety with rigidity or treating rest as something that has to be earned',practice='build a repeatable rhythm with enough flexibility for real life',service='turn an intention into a structure people can actually use and trust',question='Which structure supports me, and which one merely keeps me busy?'),
 5:dict(title='The Explorer',gift='adaptability, curiosity and learning through experience',edge='using constant change to avoid an uncomfortable commitment or unfinished feeling',practice='create a small container for experimentation, then review what the experience taught you',service='open possibilities and help a stale situation discover a workable alternative',question='Am I moving toward something alive, or only away from discomfort?'),
 6:dict(title='The Keeper of the Hearth',gift='care, responsibility, beauty and a sense of belonging',edge='over-giving, guilt, rescuing or trying to control what you feel responsible for',practice='make one caring commitment with an explicit boundary around time, energy or money',service='make care sustainable: build homes, relationships, creative work or communities where love includes self-respect',question='What would love look like if my needs belonged in the room too?'),
 7:dict(title='The Seeker',gift='inquiry, discernment, contemplation and a hunger for understanding',edge='withdrawing indefinitely, demanding certainty before participating or mistaking distance for wisdom',practice='balance time alone with one grounded conversation or direct experience',service='ask the question that deepens understanding and separate a compelling impression from a checked conclusion',question='What can I investigate without needing to know everything first?'),
 8:dict(title='The Steward',gift='organization, leadership, resourcefulness and practical influence',edge='measuring worth through achievement or using control to manage uncertainty',practice='make agreements explicit and connect ambition to a definition of enough',service='use authority and resources in a way that is effective, transparent and fair',question='How can I hold power without making it the measure of my worth?'),
 9:dict(title='The Humanitarian',gift='compassion, perspective, completion and concern beyond the individual',edge='rescuing without limits, idealizing people or staying attached to a chapter that has finished',practice='complete one act of service and one act of release, allowing both to have an ending',service='hold a wide perspective while choosing a concrete contribution you can sustain',question='What is mine to contribute, and what is mine to release?'),
 11:dict(title='The Intuitive Bridge',gift='sensitivity, inspiration, imagination and translating subtle impressions into expression',edge='overstimulation, idealizing a hunch or feeling obliged to be a source of insight for everyone',practice='write down an impression, check it against experience, and give your attention time to settle',service='bring an imaginative or inward insight into a form other people can understand and use',question='How can I honor sensitivity while staying grounded in what I can observe?'),
 22:dict(title='The Vision Builder',gift='large-scale imagination paired with practical organization',edge='perfectionism, becoming overwhelmed by scale or carrying a vision as a personal burden',practice='translate the vision into one testable next step and invite suitable collaborators',service='create a durable system that can work beyond your own constant effort',question='What is the smallest honest version of the larger vision?'),
 33:dict(title='The Compassionate Teacher',gift='teaching through care, creativity and lived example',edge='believing that service requires endless availability or a flawless example',practice='teach one thing you have practiced while admitting what you are still learning',service='make compassionate knowledge accessible without turning yourself into the permanent rescuer',question='Can service include limits, reciprocity and room for my own humanity?')}


def reduction(total, preserve=True):
    steps=[total]
    while steps[-1]>9 and not (preserve and steps[-1] in MASTERS):
        steps.append(sum(map(int,str(steps[-1]))))
    number=steps[-1];base=number
    while base>9:base=sum(map(int,str(base)))
    return dict(total=total,steps=steps,number=number,base_number=base,is_master=number in MASTERS,
                display_number=f'{number}/{base}' if number in MASTERS else str(number),
                calculation=' → '.join(map(str,steps)))


def name_letters(name, y_positions):
    folded=''.join(c for c in unicodedata.normalize('NFKD',name.upper()) if not unicodedata.combining(c))
    if any(c.isalpha() and not ('A'<=c<='Z') for c in folded):
        raise ValueError('Use the A–Z spelling or transliteration you want analyzed; this letter table does not assign values to other alphabets.')
    if any(c.isdigit() for c in folded):raise ValueError('Enter a name using letters, rather than numbers.')
    parts=re.findall('[A-Z]+',folded.replace("'",'').replace('’','').replace('‘',''))
    letters=[]
    for part_index,part in enumerate(parts):
        for c in part:
            index=len(letters)+1
            letters.append(dict(letter=c,value=(ord(c)-ord('A'))%9+1,index=index,part_index=part_index,
                                is_vowel=c in 'AEIOU' or (c=='Y' and index in y_positions)))
    if not letters:raise ValueError('Enter at least one A–Z letter in the name.')
    if any(not isinstance(i,int) or i<1 or i>len(letters) or letters[i-1]['letter']!='Y' for i in y_positions):
        raise ValueError('Only positions occupied by Y can be marked as vowel Y.')
    return parts,letters


def core_reading(key,label,number):
    if number is None:return dict(title=label,paragraphs=['This spelling has no letters in this category under the selected vowel rule. No number is invented for it. If Y carries a vowel sound in the name, mark that occurrence and recalculate.'])
    p=PROFILES[number['number']];n=number['display_number']
    opening={
      'life_path':f'Your Life Path {n} is the recurring curriculum in this framework. It invites you to develop {p["gift"]}. Think of it as a theme to explore in your choices, rather than a job title or a duty that somebody else gets to assign you.',
      'expression':f'Your Expression {n} describes the way the complete name is read as a pattern of contribution. Its language is {p["gift"]}. This is the distinction between what you can offer and what you feel obliged to perform: contribution can be chosen, developed and given a form that suits your actual life.',
      'soul_urge':f'Your Soul Urge {n} is the inward-motivation layer: what may feel meaningful when nobody is grading the result. The vowel pattern emphasizes {p["gift"]}. Use it to ask what restores your interest and sense of connection, especially when your public role has grown louder than your own preferences.',
      'personality':f'Your Personality {n} is the outward-presentation layer of the consonants. It suggests a style of {p["gift"]} that you can explore in how you meet people. It does not establish what strangers actually think of you; compare the symbolism with feedback and with the roles you have consciously chosen.',
      'birthday':f'Your Birthday {n} is a focused accent drawn from the day of the month. It spotlights {p["gift"]}. It is useful as a small, accessible doorway into the larger chart: a quality to practice deliberately, rather than a complete description of your identity.',
      'maturity':f'Your Maturity {n} combines Life Path and Expression. It offers an integration theme around {p["gift"]}: how an inner curriculum and an outward contribution might become more coherent with experience. It is not a guaranteed event or an automatic switch at a particular birthday.',
      'personal_year':f'Your Personal Year {n} is a reflection theme for the selected Gregorian year, not a forecast of events. Its emphasis is {p["gift"]}. It can help you choose a question or intention for the year while leaving room for the realities and opportunities that do not follow a number pattern.'}[key]
    paragraph2=f'The constructive expression is to {p["service"]}. The tension to watch is {p["edge"]}. A number does not tell us that you already behave this way: the value of the reading is in noticing which side feels familiar, which does not, and where a small choice would make the quality more useful.'
    paragraph3=f'A practical way to embody this theme is to {p["practice"]}. Keep the action small enough to repeat and clear enough to review. Ask yourself: “{p["question"]}” Your answer, and the result of trying it, carry more personal information than the label alone.'
    if number['is_master']:
        paragraph3+=f' This method keeps the master number {number["number"]} intact and also shows its underlying {number["base_number"]} pattern. “Master” is traditional terminology for a combined theme, not proof of higher rank, special powers or a greater obligation to carry other people.'
    return dict(title=f'{label} {n} · {p["title"]}',paragraphs=[opening,paragraph2,paragraph3])


def metadata_report(request):
    try:born=date.fromisoformat(request.birth_date)
    except (ValueError,TypeError) as exc:raise ValueError('Enter a valid Gregorian birth date (YYYY-MM-DD).') from exc
    if not 1900<=born.year<=2100:raise ValueError('Choose a birth date from 1900 through 2100.')
    parts,letters=name_letters(request.full_name,set(request.y_vowel_positions))
    year=request.reference_year or date.today().year
    m,d,y=reduction(born.month),reduction(born.day),reduction(born.year)
    expression=reduction(sum(l['value'] for l in letters))
    vowels=[l for l in letters if l['is_vowel']];consonants=[l for l in letters if not l['is_vowel']]
    life=reduction(m['number']+d['number']+y['number'])
    annual=reduction(year)
    core={'life_path':life,'expression':expression,'soul_urge':reduction(sum(l['value'] for l in vowels)) if vowels else None,
          'personality':reduction(sum(l['value'] for l in consonants)) if consonants else None,'birthday':d,
          'maturity':reduction(life['number']+expression['number']),
          'personal_year':reduction(m['number']+d['number']+annual['number'])}
    labels={'life_path':'Life Path','expression':'Expression / Destiny','soul_urge':'Soul Urge','personality':'Personality','birthday':'Birthday','maturity':'Maturity','personal_year':f'Personal Year {year}'}
    core={key:{**value,'label':labels[key]} if value else None for key,value in core.items()}
    counts=Counter(l['value'] for l in letters);missing=[n for n in range(1,10) if not counts[n]]
    debts=[]
    for key in ['life_path','expression','soul_urge','personality','birthday']:
        if core[key]:
            for total in core[key]['steps']:
                if total in DEBTS:debts.append(dict(core=labels[key],compound=total,number=reduction(total,False)['number'],theme=DEBTS[total]))
    ms,ds,ys=[reduction(n,False)['number'] for n in [born.month,born.day,born.year]]
    p1,p2=reduction(ms+ds),reduction(ds+ys)
    values=[p1,p2,reduction(p1['number']+p2['number']),reduction(ms+ys)]
    first_end=36-life['base_number'];starts=[0,first_end+1,first_end+10,first_end+19];ends=[first_end,first_end+9,first_end+18,None]
    pinnacles=[dict(period=i+1,start_age=starts[i],end_age=ends[i],**r) for i,r in enumerate(values)]
    challenges=[abs(ms-ds),abs(ds-ys),abs(abs(ms-ds)-abs(ds-ys)),abs(ms-ys)]
    sections=[core_reading(k,labels[k],value) for k,value in core.items()]
    lp,ex=PROFILES[life['number']],PROFILES[expression['number']]
    sections.append(dict(title='Your purpose thread: curriculum into contribution',paragraphs=[
      f'Read together, your Life Path invites {lp["gift"]}, while your Expression asks how you might {ex["service"]}. A possible purpose thread is to turn the first quality into the second kind of contribution. This can take many forms: relationships, making things, learning, paid work, a community role or the way you organize an ordinary day. The chart does not choose a career or define your worth.',
      ('The same number appears in Life Path and Expression, so two independently calculated parts repeat a theme. That can be a useful point of coherence: what you practice internally can become what you offer externally. Repetition does not make the theme compulsory or establish that the combination is statistically rare.' if life['number']==expression['number'] else 'The two core numbers are different, which gives you a dialogue rather than a contradiction. Your way of learning need not look identical to your way of contributing. Ask which environment lets both qualities participate, instead of forcing yourself to perform just one.'),
      'Try writing a purpose statement as a working sentence: “I want to bring ___ into the world through ___, while protecting ___.” Use the first blank for a value, the second for an action and the third for a boundary. Review it against lived experience. A purpose can grow with you; you do not need a dramatic destiny story in order for your choices to matter.']))
    if core['soul_urge'] and core['personality']:
        so,pe=PROFILES[core['soul_urge']['number']],PROFILES[core['personality']['number']]
        sections.append(dict(title='The inner life and the outer role',paragraphs=[
          f'The vowels emphasize {so["gift"]}; the consonants emphasize {pe["gift"]}. This gives you two questions to hold together: what is nourishing inwardly, and what role are you showing outwardly? They may reinforce each other, or the public role may need adjustment so the inward quality has room to breathe.',
          f'Instead of assuming that other people can see what you need, translate it into a concrete request or practice. You might {so["practice"]}, then use the outward skill to {pe["service"]}. Notice where this makes your relationships more honest and where the symbolism simply does not fit. Keep the insight that proves useful, rather than forcing yourself into the entire description.']))
    for i,p in enumerate(pinnacles):
        profile=PROFILES[p['number']];span=f'ages {p["start_age"]}–{p["end_age"]}' if p['end_age'] is not None else f'age {p["start_age"]} onward'
        challenge=challenges[i]
        sections.append(dict(title=f'Pinnacle {i+1}: {p["display_number"]} · {span}',paragraphs=[
          f'This conventional chapter places emphasis on {profile["gift"]}. It is an invitation to look for suitable ways to {profile["service"]}, not a claim that a particular event must happen at these ages. The same number in several chapters can be read as revisiting a theme with more experience, rather than being trapped in a repeated lesson.',
          ('Its Challenge is 0. In this convention, zero means there is no single numbered challenge singled out; it can be used as an open field for consciously choosing what to develop. It does not mean a life without difficulty.' if challenge==0 else f'Its Challenge is {challenge}, traditionally linked here to {PROFILES[challenge]["gift"]}. A constructive response is to {PROFILES[challenge]["practice"]}. Challenges are prompts for development, not evidence of a defect or a punishment.'),
          'Use the age range as a journaling lens. What was beginning, what was ending, and which commitments were becoming yours to choose? Write down real examples before interpreting the pattern. A symbolic timeline is most helpful when it opens reflection instead of rewriting your history to match a prediction.']))
    for number in missing:
        p=PROFILES[number]
        sections.append(dict(title=f'Missing name value {number} · a traditional karmic-lesson theme',paragraphs=[
          f'No letter in the analyzed spelling carries the value {number}. The traditional interpretation treats {p["gift"]} as a topic for deliberate practice. An absent letter value is not a missing ability, proof of a past-life failure, or a diagnosis of your present life.',
          f'If you want to work with this theme, {p["practice"]}. Look at the skills and support you already have, then choose one area for learning. The same person can receive a different missing-number pattern under another spelling, so keep the calculation attached to the name actually analyzed.']))
    sections.append(dict(title='Karmic compounds: what the arithmetic supports',paragraphs=[
      ('The selected core calculations contain: '+ '; '.join(f'{r["core"]}: {r["compound"]}/{r["number"]} — {r["theme"]}' for r in debts)+'. These are traditional symbolic themes; they do not demonstrate a debt from a past life or assign blame.' if debts else 'None of 13, 14, 16 or 19 occurs in the reduction chains of the five selected birth/name core numbers. This method therefore assigns no karmic-debt compound to those numbers. A final 4 alone is not enough to label a number 13/4.'),
      'Missing letter values and karmic-debt compounds are separate conventions. Annual cycles, Pinnacles and Maturity are shown separately rather than being used to invent a permanent debt. All of the calculation chains are included so you can see exactly what supports a label.']))
    sections.append(dict(title='A grounded way to live this reading',paragraphs=[
      f'For the next week, focus on one Life Path practice: {lp["practice"]}. For the following week, make one Expression contribution: {ex["service"]}. Choose something modest enough to complete and specific enough to notice. A completed action will tell you more than trying to embody every number at once.',
      f'For a third week, explore the question “{lp["question"]}” in your journal. In a fourth week, ask someone you trust what they actually experience in your contribution. Compare that feedback with your own values. Your Metadata can be a language for reflection, while your choices, relationships and lived results remain yours to evaluate.',
      'You do not have to become indispensable, exceptional or permanently available in order to give your life meaning. Let a useful reading expand your options. It can name a theme, offer a practice and help you ask a better question; it does not take authorship of your life away from you.']))
    report=dict(report_type='metadata',title='Your Metadata',full_name=request.full_name.strip(),normalized_name=' '.join(parts),birth_date=born.isoformat(),reference_year=year,
      method='Pythagorean letter values',letter_values={chr(65+i):i%9+1 for i in range(26)},letters=letters,
      name_parts=[dict(name=part,letters=[l for l in letters if l['part_index']==i],**reduction(sum(l['value'] for l in letters if l['part_index']==i))) for i,part in enumerate(parts)],
      vowel_calculation=' + '.join(f'{l["letter"]}({l["value"]})' for l in vowels),consonant_calculation=' + '.join(f'{l["letter"]}({l["value"]})' for l in consonants),
      y_vowel_positions=sorted(set(request.y_vowel_positions)),core=core,birth_components={'month':m,'day':d,'year':y,'reference_year':annual},
      letter_frequencies={str(n):counts[n] for n in range(1,10)},missing_numbers=missing,karmic_debts=debts,pinnacles=pinnacles,challenges=challenges,sections=sections,
      rules=['A–Z repeat 1–9. Spaces, apostrophes and punctuation carry no value; Latin diacritics are folded to their A–Z spelling.',
             'Soul Urge uses A, E, I, O, U and only the Y occurrences you mark as vowels. Personality uses the remaining letters.',
             'Life Path reduces month, day and year separately. Core reductions preserve 11, 22 and 33; their underlying single digits are also shown.',
             'Pinnacles use single-digit birth components and preserve master numbers in Pinnacle sums. Challenges use absolute differences of single-digit components.',
             'Pinnacle age ranges use 36 minus the single-digit Life Path, then two nine-year bands. Maturity does not supply a fixed activation age.',
             'Personal Year uses the selected Gregorian calendar year, not a birthday-to-birthday or equinox-year convention. Traditions differ; these are the conventions used here.'],
      note='A symbolic Pythagorean profile for reflection, not a factual determination of personality, past lives or a fixed lifetime purpose. No web research or AI service is used, and calculating a chart does not save it to a database.')
    report['report_svg']=metadata_svg(report)
    return report


def metadata_svg(o):
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 760" role="img" aria-label="Your Metadata core-number chart"><defs><linearGradient id="metadata-bg" x2="1" y2="1"><stop stop-color="#f3e5fc"/><stop offset="1" stop-color="#f4d7ed"/></linearGradient></defs><rect width="1000" height="760" rx="30" fill="url(#metadata-bg)"/><g fill="#45115e" font-family="sans-serif">'
    svg+='<text x="50" y="66" font-size="38" font-weight="bold">Your Metadata</text><text x="50" y="104" font-size="'+str(min(22,900/max(1,len(o['full_name']))/.65))+'">'+escape(o['full_name'])+'</text><text x="50" y="138" font-size="18">'+escape(o['birth_date'])+' · Pythagorean letter values</text>'
    for i,(key,n) in enumerate(o['core'].items()):
        x=50+(i%2)*460;y=165+(i//2)*115
        svg+=f'<rect x="{x}" y="{y}" width="440" height="98" rx="18" fill="#fff8fb" stroke="#d8ae65"/><text x="{x+20}" y="{y+30}" font-size="17">{escape(n["label"] if n else key.replace("_"," ").title())}</text><text x="{x+20}" y="{y+72}" font-size="36" font-weight="bold">{escape(n["display_number"] if n else "Not assigned")}</text>'
    svg+='<text x="50" y="660" font-size="20">Pinnacles: '+escape(' · '.join(p['display_number'] for p in o['pinnacles']))+'</text><text x="50" y="697" font-size="20">Challenges: '+escape(' · '.join(map(str,o['challenges'])))+'</text><text x="50" y="735" font-size="16">Symbolic themes · visible arithmetic · room for your own meaning</text></g></svg>'
    return svg
