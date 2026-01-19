#!/usr/bin/env python3
"""
Seed script to add initial TV shows with A ratings.
Run this after the backend is running to populate initial data.
"""

import requests
import os
import sys

# Use local API by default, can override with environment variable
API_URL = os.getenv('API_URL', 'http://localhost:5001/api')

# Initial shows with A ratings
INITIAL_SHOWS = [
    {
        'title': 'Breaking Bad',
        'j_rayting': 'A',
        'a_grade_rank': 1
    },
    {
        'title': 'The Wire',
        'j_rayting': 'A',
        'a_grade_rank': 2
    },
    {
        'title': 'The Office',  # UK version
        'j_rayting': 'A',
        'a_grade_rank': 3,
        'start_year': 2001  # Helps TMDB find the UK version
    },
    {
        'title': 'The Office',  # US version
        'j_rayting': 'A',
        'a_grade_rank': 4,
        'start_year': 2005  # Helps TMDB find the US version
    },
    {
        'title': 'Fleabag',
        'j_rayting': 'A',
        'a_grade_rank': 5
    },
    {
        'title': 'Succession',
        'j_rayting': 'A',
        'a_grade_rank': 6
    },
    {
        'title': 'Arrested Development',
        'j_rayting': 'A',
        'a_grade_rank': 7
    },
    {
        'title': 'Silo',
        'j_rayting': 'B+/A-',
        'details_commentary': "One rung below my absolute favourites, but a nice blend of thought-provoking and exciting. Just a bit too slow-paced for my tastes."
    },
    {
        'title': 'Stick',
        'j_rayting': 'B/B+',
        'details_commentary': "An easy, fun watch that's just a bit too formulaic to \"hit the pin.\" I watched most of it at the gym, which is a perfect environment for it."
    },
    {
        'title': 'Slow Horses',
        'j_rayting': 'B+/A-',
        'details_commentary': "A little bit up-and-down - I thought Season 3 was sub-par relatively speaking - but a great cast of characters and Gary Oldman's Jackson Lamb is a nicely familiar \"comfort food,\" pulling it all together."
    },
    {
        'title': 'The Studio',
        'j_rayting': 'B+',
        'details_commentary': "A few spectacular scenes - building as the show progresses - and enough cameos to bring back some of Entourage's \"Who will show up next?\""
    },
    {
        'title': 'Entourage',
        'j_rayting': 'B+/A-',
        'details_commentary': "Some of my highest TV highs - especially in the early seasons, with Johnny Drama - where anytime the plot got more depressing, I found it far less enjoyable."
    },
    {
        'title': 'Shrinking',
        'j_rayting': 'B+/A-',
        'details_commentary': "A bit too depressing sometimes, but the spirit of hope and positivity largely pulls through, with a deft blend of humour and drama."
    },
    {
        'title': 'Platonic',
        'j_rayting': 'B/B+',
        'details_commentary': "Just enough self-sabotage to be annoying, just enough laughs and zaniness for me to continue to enjoy it regardless."
    },
    {
        'title': 'Loot',
        'j_rayting': 'B/B+',
        'details_commentary': "I really want to love the show - and I do love Maya Rudolph in general - but I find myself not especially liking the full cast, which makes it less fun. Feels like it it's 2 changes away from being an excellent comedy."
    },
    {
        'title': 'Unstable',
        'j_rayting': 'B+',
        'details_commentary': "I've always been a big Rob Lowe fan, so I think I like this more than the average person (it was cancelled after 2 seasons); silly, but warm-hearted (a bit like Rob Lowe's underrated podcast \"Literally\")."
    },
    {
        'title': 'Cobra Kai',
        'j_rayting': 'B+',
        'details_commentary': "A hard one to judge because I truly loved Season 1 - one of my favourite series of tv - and then it got progressively worse and worse as it veered further from Johnny and Daniel; I didn't even finish the final season."
    },
    {
        'title': 'Emily in Paris',
        'j_rayting': 'B-/B',
        'details_commentary': "Lots of beautiful people and places, but so lightweight and repetitive that I stopped after 3 seasons."
    },
    {
        'title': '13 Reasons Why',
        'j_rayting': 'B-',
        'details_commentary': "I'm probably not the right demographic, just didn't work for me at all, so I stopped after a few episodes."
    },
    {
        'title': 'Easy',
        'j_rayting': 'B/B+',
        'details_commentary': "I enjoyed some of the plots, but it never sunk its hooks into me enough to have a stronger opinion or enjoyment."
    },
    {
        'title': 'Silicon Valley',
        'j_rayting': 'B+/A-',
        'details_commentary': "Responsible for some of my biggest laughs ever; would probably be even more compelling now that we're in the AI age."
    },
    {
        'title': 'Billions',
        'j_rayting': 'B+',
        'details_commentary': "Some moments I loved - who doesn't love ultra rich bravado - but I progressively lost interest and bailed after Season 3 or 4."
    },
    {
        'title': 'Californication',
        'j_rayting': 'B+',
        'details_commentary': "I like Hank Moody quite a bit, even though I appreciate his character (literally and figuratively) has some pretty serious gaps; consistently made me laugh."
    },
    {
        'title': 'Weeds',
        'j_rayting': 'B/B+',
        'details_commentary': "Was a top show for me briefly, but it seemed more up-and-down, and I thought the cartel plot was jumping the shark and simply less interesting."
    },
    {
        'title': 'Never Have I Ever',
        'j_rayting': 'B/B+',
        'details_commentary': "Really enjoyed the first season - especially the Johnny Mac narrator - where her self-sabotage just got old as they took a good initial idea and continued to extend it beyond what was necessary."
    },
    {
        'title': 'Dexter: New Blood',
        'j_rayting': 'B-/B',
        'details_commentary': "Better than seasons 7 and 8 of the original series, but still far from the quality level of the first 4 - even 5 - seasons, so probably not worth the reboot."
    },
    {
        'title': 'Parenthood',
        'j_rayting': 'B+',
        'details_commentary': "I'd probably like even more now I have older children; nice mix of heart, drama, and humour, where the Bay Area location didn't hurt."
    }
]

def seed_shows():
    """Add initial shows to the database."""
    print(f"Seeding shows to {API_URL}/shows...")
    print("-" * 50)

    success_count = 0
    error_count = 0

    for show in INITIAL_SHOWS:
        try:
            response = requests.post(
                f"{API_URL}/shows",
                json=show,
                headers={'Content-Type': 'application/json'},
                timeout=30  # Longer timeout for TMDB/IMDB fetching
            )

            if response.status_code == 201:
                result = response.json()
                metadata_msg = " (metadata fetched)" if result.get('metadata_fetched') else ""
                print(f"[OK] Added: {show['title']}{metadata_msg}")
                success_count += 1
            elif response.status_code == 409:
                print(f"[SKIP] Already exists: {show['title']}")
            else:
                print(f"[ERROR] Failed to add {show['title']}: {response.status_code} - {response.text}")
                error_count += 1

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to add {show['title']}: {e}")
            error_count += 1

    print("-" * 50)
    print(f"Done! Added {success_count} shows, {error_count} errors.")

    if error_count > 0:
        sys.exit(1)

if __name__ == '__main__':
    seed_shows()
