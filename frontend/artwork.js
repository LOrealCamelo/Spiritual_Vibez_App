/* Original illustration artwork with live, accessible panel text. */
const CARD_PANELS={
  "home_daily_card": {
    "title": "Daily Card",
    "description": "Get today’s insight",
    "pack": "cosmic",
    "cell": 0,
    "theme": "pink",
    "kind": "card"
  },
  "home_shuffle_spread": {
    "title": "Shuffle a Spread",
    "description": "Find the perfect spread",
    "pack": "cosmic",
    "cell": 1,
    "theme": "aqua",
    "kind": "card"
  },
  "home_learn_tarot": {
    "title": "Learn Tarot",
    "description": "Build your knowledge",
    "pack": "cosmic",
    "cell": 2,
    "theme": "lilac",
    "kind": "card"
  },
  "home_birth_chart": {
    "title": "Birth Chart",
    "description": "Explore your cosmic blueprint",
    "pack": "cosmic",
    "cell": 3,
    "theme": "peach",
    "kind": "card"
  },
  "journal_header": {
    "title": "My Journal",
    "description": "Reflect, track your journey & explore your insights.",
    "pack": "journal",
    "cell": 0,
    "theme": "purple",
    "kind": "header"
  },
  "journal_mood_checkin": {
    "title": "Mood Check-In",
    "description": "Tune in to how you’re feeling right now",
    "pack": "journal",
    "cell": 2,
    "theme": "aqua",
    "kind": "card"
  },
  "journal_moon_phase": {
    "title": "Moon Phase",
    "description": "See the current moon & its energy",
    "pack": "journal",
    "cell": 3,
    "theme": "lilac",
    "kind": "card"
  },
  "journal_numerology": {
    "title": "Numerology",
    "description": "Explore your life path, angel numbers & more",
    "pack": "ritual",
    "cell": 0,
    "theme": "peach",
    "kind": "card"
  },
  "journal_rituals": {
    "title": "Rituals",
    "description": "Simple rituals for manifestation, self-care & alignment",
    "pack": "ritual",
    "cell": 1,
    "theme": "lilac",
    "kind": "card"
  },
  "journal_saved_readings": {
    "title": "Saved Readings",
    "description": "Revisit your past spreads & insights",
    "pack": "journal",
    "cell": 1,
    "theme": "pink",
    "kind": "card"
  },
  "journal_today": {
    "title": "Today’s Journal",
    "description": "A space for your readings, reflections & manifestations.",
    "pack": "journal",
    "cell": 0,
    "theme": "cream",
    "kind": "card"
  },
  "learn_card_meanings": {
    "title": "Card Meanings",
    "description": "Symbols, keywords & real-life interpretations",
    "pack": "study",
    "cell": 1,
    "theme": "cream",
    "kind": "card"
  },
  "learn_header": {
    "title": "Learn Tarot",
    "description": "Build your tarot knowledge, one fun lesson at a time.",
    "pack": "study",
    "cell": 1,
    "theme": "purple",
    "kind": "header"
  },
  "learn_major_arcana": {
    "title": "Major Arcana",
    "description": "Explore the big themes & turning points",
    "pack": "cosmic",
    "cell": 0,
    "theme": "lilac",
    "kind": "card"
  },
  "learn_minor_arcana": {
    "title": "Minor Arcana",
    "description": "Discover the magic in everyday moments",
    "pack": "cosmic",
    "cell": 1,
    "theme": "pink",
    "kind": "card"
  },
  "learn_progress": {
    "title": "Your Learning Journey",
    "description": "A little more magic with every card",
    "pack": "study",
    "cell": 0,
    "theme": "cream",
    "kind": "progress"
  },
  "learn_quiz_me": {
    "title": "Quiz Me",
    "description": "Test your tarot knowledge",
    "pack": "study",
    "cell": 3,
    "theme": "peach",
    "kind": "card"
  },
  "learn_reversed_cards": {
    "title": "Reversed Cards",
    "description": "Discover a different perspective",
    "pack": "study",
    "cell": 2,
    "theme": "aqua",
    "kind": "card"
  },
  "spreads_crossroads": {
    "title": "At a Crossroads",
    "description": "Discover your direction",
    "pack": "ritual",
    "cell": 2,
    "theme": "purple",
    "kind": "card"
  },
  "spreads_filters": {
    "title": "Filter by Vibe",
    "description": "All, Love, Career & Growth",
    "pack": "journal",
    "cell": 2,
    "theme": "cream",
    "kind": "filter"
  },
  "spreads_header": {
    "title": "Spreads",
    "description": "Discover tarot spreads for any vibe, question or life moment.",
    "pack": "cosmic",
    "cell": 1,
    "theme": "purple",
    "kind": "header"
  },
  "spreads_next_phase": {
    "title": "The Next Phase",
    "description": "Growth & what’s next",
    "pack": "ritual",
    "cell": 3,
    "theme": "purple",
    "kind": "card"
  },
  "spreads_randomize": {
    "title": "Randomize a Spread",
    "description": "Let a little magic choose your next reading",
    "pack": "cosmic",
    "cell": 1,
    "theme": "hotpink",
    "kind": "randomize"
  },
  "spreads_trust_gut": {
    "title": "Trust Your Gut",
    "description": "Intuition & clarity",
    "pack": "journal",
    "cell": 1,
    "theme": "purple",
    "kind": "card"
  }
};
function panelIllustration(pack,cell){return '<span class="panel-illustration" aria-hidden="true"><img src="assets/illustrations/'+pack+'.png" alt="" style="--cell-x:'+(cell%2)+';--cell-y:'+Math.floor(cell/2)+'"></span>'}
function panelContents(key,extra=''){
 const p=CARD_PANELS[key];if(!p)throw Error('Unknown panel '+key);
 return panelIllustration(p.pack,p.cell)+'<span class="panel-copy"><span class="panel-title"'+(p.kind==='header'?' role="heading" aria-level="2"':'')+'>'+e(p.title)+'</span><span class="panel-description">'+e(p.description)+'</span>'+extra+'</span>'+(p.kind==='header'?'':'<span class="panel-arrow" aria-hidden="true">›</span>');
}
function panelClasses(key){const p=CARD_PANELS[key];return 'fresh-panel panel-theme-'+p.theme+' panel-kind-'+p.kind}

// Shared once per document, instead of repeating the same SVG id in each button.
function clearGlassFilter(){return '<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute;pointer-events:none"><defs><filter id="liquid-refraction" x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency="0.018 0.025" numOctaves="1" seed="1" result="noise"/><feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="B"/></filter></defs></svg>'}

// Both clients reuse the original high-resolution illustrations for their complete directories.
const ILLUSTRATION_BINDINGS={
  "tools": {
    "natal": {
      "pack": "cosmic",
      "cell": 3
    },
    "moon": {
      "pack": "journal",
      "cell": 3
    },
    "bazi": {
      "pack": "cosmic",
      "cell": 3
    },
    "houses": {
      "pack": "cosmic",
      "cell": 3
    },
    "asteroids": {
      "pack": "cosmic",
      "cell": 3
    },
    "astro": {
      "pack": "ritual",
      "cell": 2
    },
    "calendar": {
      "pack": "journal",
      "cell": 3
    },
    "life": {
      "pack": "ritual",
      "cell": 0
    },
    "numbers": {
      "pack": "ritual",
      "cell": 0
    },
    "love": {
      "pack": "journal",
      "cell": 2
    },
    "sound": {
      "pack": "ritual",
      "cell": 3
    },
    "rituals": {
      "pack": "ritual",
      "cell": 1
    },
    "cycle": {
      "pack": "journal",
      "cell": 3
    },
    "shadow": {
      "pack": "journal",
      "cell": 0
    },
    "runes": {
      "pack": "study",
      "cell": 3
    },
    "pendulum": {
      "pack": "ritual",
      "cell": 0
    },
    "oracle": {
      "pack": "study",
      "cell": 3
    },
    "store": {
      "pack": "study",
      "cell": 0
    }
  },
  "spreads": {
    "daily": {
      "pack": "cosmic",
      "cell": 0
    },
    "wellbeing": {
      "pack": "ritual",
      "cell": 1
    },
    "love": {
      "pack": "journal",
      "cell": 2
    },
    "shadow": {
      "pack": "journal",
      "cell": 0
    },
    "crossroads": {
      "pack": "ritual",
      "cell": 2
    },
    "purpose": {
      "pack": "ritual",
      "cell": 0
    },
    "spirit": {
      "pack": "study",
      "cell": 3
    },
    "default": {
      "pack": "cosmic",
      "cell": 1
    }
  }
};
function toolCard(id,title,description){const art=ILLUSTRATION_BINDINGS.tools[id];
 if(!art)throw Error('Missing tool illustration: '+id);
 return '<button class="fresh-panel explore-card" data-tool="'+id+'" data-action="tool:'+id+'" aria-label="'+e(title)+'">'+panelIllustration(art.pack,art.cell)+'<span class="panel-copy"><span class="panel-title">'+e(title)+'</span><span class="panel-description">'+e(description)+'</span></span><span class="panel-arrow" aria-hidden="true">›</span></button>';
}
function spreadIllustration(category){const art=ILLUSTRATION_BINDINGS.spreads[category]||ILLUSTRATION_BINDINGS.spreads.default;return panelIllustration(art.pack,art.cell)}
