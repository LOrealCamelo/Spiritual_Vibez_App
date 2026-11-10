# Header tagline placement

The marked-up header design now appears on the website: the full portrait is at
the upper left, and the adjacent two-line tagline reads “Track your Daily Vibz”
and “with Zodiac, Tarot, & More.” The Spiritual Vibez wordmark and journey heading
remain in the home welcome box; the former smaller tagline has been removed.

Screenshots: [desktop](web/desktop/header-tagline.png) and
[phone website](web/phone/header-tagline.png).

Browser layout checks passed at 1448, 1100, 1024, 900, 800, 751, 750, 390, and
320px. The tagline stays beside the portrait, the desktop navigation does not
overlap it, and there is no horizontal overflow. The journey heading remains a
single line. Web asset checks and native TypeScript checking passed; existing
blurred text shadows were removed as in the earlier typography preview.
