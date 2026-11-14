/* SpiritualVibz original reflective meanings. Historical names are reconstructed where noted.
 * Elder Futhark is an ancient writing system; these divination readings are MODERN adaptations.
 * Shared without modification by browser and React Native. */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.SpiritualRuneLibrary=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const RUNES=[
  {
    "id": 1,
    "name": "Fehu",
    "symbol": "ᚠ",
    "historic": "Cattle, movable wealth",
    "reversible": true,
    "upright": {
      "keywords": [
        "Resources",
        "generosity",
        "earning"
      ],
      "meaning": "Notice resources you already have and how you might use or share them wisely."
    },
    "reversed": {
      "keywords": [
        "Scarcity",
        "overextension"
      ],
      "meaning": "Reconsider what drains your resources and what support would help."
    }
  },
  {
    "id": 2,
    "name": "Uruz",
    "symbol": "ᚢ",
    "historic": "Aurochs, strength",
    "reversible": true,
    "upright": {
      "keywords": [
        "Vitality",
        "resilience",
        "courage"
      ],
      "meaning": "Notice where steady effort and patient strength could help you."
    },
    "reversed": {
      "keywords": [
        "Exhaustion",
        "resistance"
      ],
      "meaning": "Rest and rebuild before pushing ahead."
    }
  },
  {
    "id": 3,
    "name": "Thurisaz",
    "symbol": "ᚦ",
    "historic": "Thorn or giant (reconstructed name)",
    "reversible": true,
    "upright": {
      "keywords": [
        "Protection",
        "pause",
        "discernment"
      ],
      "meaning": "Pause before reacting; consider your boundaries and their purpose."
    },
    "reversed": {
      "keywords": [
        "Impulsiveness",
        "conflict"
      ],
      "meaning": "Choose care over a hasty confrontation."
    }
  },
  {
    "id": 4,
    "name": "Ansuz",
    "symbol": "ᚨ",
    "historic": "Deity, associated with speech in later rune traditions",
    "reversible": true,
    "upright": {
      "keywords": [
        "Communication",
        "insight",
        "listening"
      ],
      "meaning": "Speak honestly and make room to listen."
    },
    "reversed": {
      "keywords": [
        "Misunderstanding",
        "noise"
      ],
      "meaning": "Clarify what was heard and ask one more question."
    }
  },
  {
    "id": 5,
    "name": "Raidho",
    "symbol": "ᚱ",
    "historic": "Riding, journey",
    "reversible": true,
    "upright": {
      "keywords": [
        "Direction",
        "rhythm",
        "movement"
      ],
      "meaning": "Take a thoughtful next step on a path that matters."
    },
    "reversed": {
      "keywords": [
        "Delay",
        "loss of direction"
      ],
      "meaning": "Recheck the route instead of rushing."
    }
  },
  {
    "id": 6,
    "name": "Kenaz",
    "symbol": "ᚲ",
    "historic": "Torch/ulcer (later name traditions differ)",
    "reversible": true,
    "upright": {
      "keywords": [
        "Skill",
        "illumination",
        "learning"
      ],
      "meaning": "Learn something that brings a confusing situation into focus."
    },
    "reversed": {
      "keywords": [
        "Burnout",
        "obscurity"
      ],
      "meaning": "Find a small light rather than forcing an answer."
    }
  },
  {
    "id": 7,
    "name": "Gebo",
    "symbol": "ᚷ",
    "historic": "Gift",
    "reversible": false,
    "upright": {
      "keywords": [
        "Exchange",
        "mutuality",
        "generosity"
      ],
      "meaning": "Consider whether giving and receiving feel balanced."
    },
    "reversed": null
  },
  {
    "id": 8,
    "name": "Wunjo",
    "symbol": "ᚹ",
    "historic": "Joy",
    "reversible": true,
    "upright": {
      "keywords": [
        "Joy",
        "belonging",
        "appreciation"
      ],
      "meaning": "Make room for ordinary joy and trusted community."
    },
    "reversed": {
      "keywords": [
        "Disconnection",
        "dissatisfaction"
      ],
      "meaning": "Notice where connection needs repair."
    }
  },
  {
    "id": 9,
    "name": "Hagalaz",
    "symbol": "ᚺ",
    "historic": "Hail",
    "reversible": false,
    "upright": {
      "keywords": [
        "Disruption",
        "weathering change"
      ],
      "meaning": "Name what has changed and what helps you endure it."
    },
    "reversed": null
  },
  {
    "id": 10,
    "name": "Nauthiz",
    "symbol": "ᚾ",
    "historic": "Need, constraint",
    "reversible": false,
    "upright": {
      "keywords": [
        "Needs",
        "patience",
        "priorities"
      ],
      "meaning": "Identify a real need beneath the pressure."
    },
    "reversed": null
  },
  {
    "id": 11,
    "name": "Isa",
    "symbol": "ᛁ",
    "historic": "Ice",
    "reversible": false,
    "upright": {
      "keywords": [
        "Stillness",
        "pause",
        "clarity"
      ],
      "meaning": "Use the pause to notice what is stable."
    },
    "reversed": null
  },
  {
    "id": 12,
    "name": "Jera",
    "symbol": "ᛃ",
    "historic": "Year, harvest",
    "reversible": false,
    "upright": {
      "keywords": [
        "Timing",
        "cycles",
        "steady growth"
      ],
      "meaning": "Recognize slow progress and what needs more time."
    },
    "reversed": null
  },
  {
    "id": 13,
    "name": "Eihwaz",
    "symbol": "ᛇ",
    "historic": "Yew tree (reconstructed)",
    "reversible": false,
    "upright": {
      "keywords": [
        "Endurance",
        "transition",
        "rootedness"
      ],
      "meaning": "Hold steady while you make a thoughtful transition."
    },
    "reversed": null
  },
  {
    "id": 14,
    "name": "Perthro",
    "symbol": "ᛈ",
    "historic": "Meaning uncertain (later rune-poem association debated)",
    "reversible": true,
    "upright": {
      "keywords": [
        "Mystery",
        "chance",
        "unanswered questions"
      ],
      "meaning": "Allow uncertainty; not everything needs an immediate answer."
    },
    "reversed": {
      "keywords": [
        "Control",
        "confusion"
      ],
      "meaning": "Avoid forcing meaning where the evidence is unclear."
    }
  },
  {
    "id": 15,
    "name": "Algiz",
    "symbol": "ᛉ",
    "historic": "Reconstructed name; ancient interpretation uncertain",
    "reversible": true,
    "upright": {
      "keywords": [
        "Awareness",
        "boundaries",
        "protection"
      ],
      "meaning": "Notice what helps you feel safe and attentive."
    },
    "reversed": {
      "keywords": [
        "Hypervigilance",
        "isolation"
      ],
      "meaning": "Find a balance between protection and connection."
    }
  },
  {
    "id": 16,
    "name": "Sowilo",
    "symbol": "ᛊ",
    "historic": "Sun",
    "reversible": false,
    "upright": {
      "keywords": [
        "Clarity",
        "vitality",
        "direction"
      ],
      "meaning": "Look for one clear and constructive direction."
    },
    "reversed": null
  },
  {
    "id": 17,
    "name": "Tiwaz",
    "symbol": "ᛏ",
    "historic": "Týr (reconstructed)",
    "reversible": true,
    "upright": {
      "keywords": [
        "Integrity",
        "courage",
        "fairness"
      ],
      "meaning": "Act in line with a value even when it's difficult."
    },
    "reversed": {
      "keywords": [
        "Self-sacrifice",
        "rigidity"
      ],
      "meaning": "Ask whether the burden is yours to carry."
    }
  },
  {
    "id": 18,
    "name": "Berkano",
    "symbol": "ᛒ",
    "historic": "Birch",
    "reversible": true,
    "upright": {
      "keywords": [
        "Renewal",
        "care",
        "growth"
      ],
      "meaning": "Support a beginning with steady care."
    },
    "reversed": {
      "keywords": [
        "Stalled growth",
        "neglect"
      ],
      "meaning": "Notice what needs nurturing rather than pressure."
    }
  },
  {
    "id": 19,
    "name": "Ehwaz",
    "symbol": "ᛖ",
    "historic": "Horse",
    "reversible": true,
    "upright": {
      "keywords": [
        "Partnership",
        "movement",
        "trust"
      ],
      "meaning": "Consider what good cooperation looks like."
    },
    "reversed": {
      "keywords": [
        "Disharmony",
        "hesitation"
      ],
      "meaning": "Talk openly about pace and expectations."
    }
  },
  {
    "id": 20,
    "name": "Mannaz",
    "symbol": "ᛗ",
    "historic": "Human being",
    "reversible": true,
    "upright": {
      "keywords": [
        "Self-awareness",
        "community",
        "perspective"
      ],
      "meaning": "Notice how your choices relate to others."
    },
    "reversed": {
      "keywords": [
        "Isolation",
        "comparison"
      ],
      "meaning": "Try connection rather than self-criticism."
    }
  },
  {
    "id": 21,
    "name": "Laguz",
    "symbol": "ᛚ",
    "historic": "Water",
    "reversible": true,
    "upright": {
      "keywords": [
        "Emotion",
        "flow",
        "intuition"
      ],
      "meaning": "Check in with your feelings without letting them make every decision."
    },
    "reversed": {
      "keywords": [
        "Overwhelm",
        "avoidance"
      ],
      "meaning": "Find a steadier current by naming the feeling."
    }
  },
  {
    "id": 22,
    "name": "Ingwaz",
    "symbol": "ᛜ",
    "historic": "Ing / fertility deity (name reconstructed)",
    "reversible": false,
    "upright": {
      "keywords": [
        "Potential",
        "incubation",
        "completion"
      ],
      "meaning": "Give a developing idea the space it needs."
    },
    "reversed": null
  },
  {
    "id": 23,
    "name": "Dagaz",
    "symbol": "ᛞ",
    "historic": "Day",
    "reversible": false,
    "upright": {
      "keywords": [
        "Breakthrough",
        "perspective",
        "transition"
      ],
      "meaning": "Notice one way your understanding is changing."
    },
    "reversed": null
  },
  {
    "id": 24,
    "name": "Othala",
    "symbol": "ᛟ",
    "historic": "Inherited estate, ancestral property",
    "reversible": true,
    "upright": {
      "keywords": [
        "Belonging",
        "heritage",
        "home"
      ],
      "meaning": "Reflect on what belonging means to you without excluding others."
    },
    "reversed": {
      "keywords": [
        "Exclusion",
        "rigid traditions"
      ],
      "meaning": "Keep what is life-giving while questioning harmful rules."
    }
  }
];
const LAYOUTS={
 daily:{title:'Daily Rune',count:1,positions:['Your theme today']},
 three:{title:'Past · Present · Possibility',count:3,positions:['What has shaped you','What matters now','What you might explore next']},
 cross:{title:'Five-Rune Cross',count:5,positions:['Central question','What came before','What may develop','Underlying support','A constructive next step']},
 handful:{title:'Bone-Style Scatter',count:7,positions:[]}
};
function randomInt(max){
 if(!Number.isSafeInteger(max)||max<=0)throw Error('Invalid random range');
 const cryptoAPI=typeof globalThis!=='undefined'?globalThis.crypto:null;
 if(cryptoAPI&&typeof cryptoAPI.getRandomValues==='function'){
  const limit=Math.floor(4294967296/max)*max;const sample=new Uint32Array(1);
  do{cryptoAPI.getRandomValues(sample)}while(sample[0]>=limit);
  return sample[0]%max;
 }
 return Math.floor(Math.random()*max);
}
function cast(key='three',reversals=false){
 const layout=LAYOUTS[key]||LAYOUTS.three,deck=RUNES.slice();
 for(let i=deck.length-1;i>0;i--){const j=randomInt(i+1);[deck[i],deck[j]]=[deck[j],deck[i]];}
 return deck.slice(0,layout.count).map((rune,index)=>{
  const reversed=!!reversals&&rune.reversible&&randomInt(2)===1;
  return {...rune,position:index+1,positionName:layout.positions[index]||'Rune '+(index+1),orientation:reversed?'reversed':'upright',reading:reversed?rune.reversed:rune.upright};
 });
}
return {RUNES,LAYOUTS,cast};
});
