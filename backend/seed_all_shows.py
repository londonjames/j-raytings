#!/usr/bin/env python3
"""
Seed script to add/update all TV shows with ratings and thoughts.
This will add new shows and update existing ones with commentary.
"""

import requests
import os
import sys
import time

# Use production API - can override with environment variable
API_URL = os.getenv('API_URL', 'https://web-production-01d1.up.railway.app/api')

# All 49 shows with ratings and verbatim thoughts
ALL_SHOWS = [
    # From ChatGPT Transcript
    {
        'title': 'Breaking Bad',
        'j_rayting': 'A',
        'details_commentary': "Starts slow. Season one isn't great, and even season two has its moments. But then it builds to probably my favourite show of all time across seasons three, especially season four, and also season five. Love this show."
    },
    {
        'title': 'Succession',
        'j_rayting': 'A',
        'details_commentary': "The last show I regularly watched every single week and couldn't wait for it to arrive, especially in seasons three and four. Funny, clever, unpredictable, amazing acting, and who doesn't like seeing incredibly rich, dysfunctional people? Highly recommended."
    },
    {
        'title': 'The Office (UK)',
        'start_year': 2001,
        'j_rayting': 'A',
        'details_commentary': "If you like slightly uncomfortable humour, it doesn't get anything better than British Office."
    },
    {
        'title': 'A Man on the Inside',
        'j_rayting': 'B+',
        'details_commentary': "First season, probably almost an A-, second season, more of like a B, B+, but overall, if you like Ted Danson and you want something that makes you think a little bit, makes you laugh a little bit, and makes you feel good through most of it, I like this show."
    },
    {
        'title': 'Dexter',
        'j_rayting': 'A-',
        'details_commentary': "Slightly hard one because seasons 1 and 4 are about as good as TV gets. And then 2 and 3 aren't bad. 5 is not bad. And then 6, 7, 8 are borderline and aberration. So it's one of those shows that the average is tough. The highs are very high. The lows are about as low as you get. But overall, if you stick with seasons 1 through 4, maybe even 5 as well, you're in a good place."
    },
    {
        'title': 'The Sopranos',
        'j_rayting': 'B',
        'details_commentary': "Admittedly, I've only watched the first two seasons, but for whatever reason, it didn't get me. Like most others react to the show, I'll give it another shot. But usually, when I love a show, I binge the whole thing. Sopranos, I stop watching it. By the way, same with Game of Thrones. So sometimes HBO shows don't rhyme with me."
    },
    {
        'title': 'The Wire',
        'j_rayting': 'A',
        'details_commentary': "About as good as TV gets. I think season four might be my favourite TV series ever. Note, season four, Breaking Bad, and season four of Dexter might be the next competitors. So there's something odd about season fours. Not the most uplifting show, but if you don't mind a bit of depressing-ness, you're going to like this show. By the way, Season 2 is quite poor. 1 is great, 3 is great, 4 is great, 5 is good too, but 2 is poor, so just be aware of that."
    },
    {
        'title': 'Mad Men',
        'j_rayting': 'B+',
        'details_commentary': "Definitely a great show. Although oddly enough, I never watched the final season. So I can only give so high a rating for a show where I decided for whatever reason not to watch the final season. I've never gotten back to it. I probably will watch it at some point, but my absolute favourite shows, I would be knocking them off in a day. Mad Men last season, I haven't knocked off in a decade."
    },
    {
        'title': 'Stranger Things',
        'j_rayting': 'B',
        'details_commentary': "Really liked the first season. I think I watched through seasons three, perhaps, but got less and less interesting to me with occasional moments of hilarity. As it got more and more dark and less and less 80s, I lost interest. Therefore, I haven't watched the final, I think, seasons four and five."
    },
    {
        'title': 'The West Wing',
        'j_rayting': 'A-',
        'details_commentary': "Watched it in 2023, so well after it was actually shown and still held up. Oddly enough, I watched it in a cold soak. I was training for swimming, so I watched every episode in 53 degree water, getting progressively more and more freezing. So very odd environment for it, but especially seasons one through four, it's really, really good. And even the later seasons, when Aaron Sorkin departs, are still pretty solid."
    },
    {
        'title': "Schitt's Creek",
        'j_rayting': 'B',
        'details_commentary': "Watched the first season, maybe season and a half, liked it, but never got into it to the same degree that I know everyone else has. So it's one of those didn't hit me where it hits others."
    },
    {
        'title': 'Cheers',
        'j_rayting': 'A-',
        'details_commentary': "A little bit tricky since I watched it as a teenager, so a bit hard to know my take today, but great characters, always enjoyed the Boston environment, loved Ted Danson, Shelley Long, Woody Harrelson, the whole crew, and it's definitely got the best theme song of any show ever, so might even be more than A-, so I'll give it A- for now."
    },
    {
        'title': 'The Office (US)',
        'start_year': 2005,
        'j_rayting': 'A',
        'details_commentary': "My favourite show to re-watch, where I would say I watch between 10 and 20 episodes a year, in random circumstances, maybe on the plane, or if I'm just feeling like something mindless to do in the background, especially seasons 2 through 6 or 7, it's just incredible. Mainly funny, occasionally uncomfortably funny, but feels like apple pie or whatever phrase you want to use for just feeling comfort and familiarity."
    },
    {
        'title': 'Fleabag',
        'j_rayting': 'A',
        'details_commentary': "Both seasons exceptional. Bit hard to describe why it's so good but definitely resonated with me and sad there isn't more but like the British office. It's always nice when a show goes out on top."
    },
    {
        'title': 'The Marvelous Mrs. Maisel',
        'j_rayting': 'B',
        'details_commentary': "Liked it, think I watched the first two seasons but then didn't watch season three and much of the season four, so didn't hit me to the point where I felt I had to go back to it, and maybe I should."
    },
    {
        'title': 'Ted Lasso',
        'j_rayting': 'B',
        'details_commentary': "Like everyone, I really enjoyed season 1. I thought season 2, or maybe season 2 and 3, I can't remember if there's 2 or 3 seasons, not as good, where I like the general feel-goodness of the show, but it got less and less compelling to me. It felt to me like I should have exited after season 1."
    },
    {
        'title': 'Parks and Recreation',
        'j_rayting': 'A-',
        'details_commentary': "Oddly enough, I haven't watched the final season, don't have a good reason for it, but the first few seasons were my must-watch viewing every Thursday on NBC. Love the cast, especially Tom Haverford and Ron Swanson, and definitely a show that I reference and return to, especially because YouTube has some great bloopers."
    },
    {
        'title': 'Arrested Development',
        'j_rayting': 'A-',
        'details_commentary': "Such a different show versus pretty much everything else where the highs on Arrested Development are about as laugh-out-loud funny and laugh-out-loud clever as I've seen on TV. A bit inconsistent here and there. I can't remember if I watched the final shows on Netflix or not, but one of my all-time top 20, possibly top 10."
    },
    {
        'title': 'House of Cards',
        'j_rayting': 'B+',
        'details_commentary': "Like everyone, got swept away by the first season, maybe season one and two, and then found it got more and more preposterous and less and less interesting. I don't think I watched the last season without Kevin Spacey."
    },
    {
        'title': 'The Good Place',
        'j_rayting': 'B+',
        'details_commentary': "Odd one because I love season one, I think I even love season two, but I don't think I've actually finished the whole show for no reason other than life getting in the way. But there's nothing pulling me back to go finish it, which is a bit odd given I love Ted Danson, I like Kristen Bell, and I like the show overall. So maybe one to go back to."
    },
    {
        'title': 'Better Call Saul',
        'j_rayting': 'B+',
        'details_commentary': "For some odd reason, even though I liked season one and maybe the first half of season two, I never got back to it. I probably should, given how much I like Breaking Bad, but it hasn't drawn me back."
    },
    {
        'title': 'Westworld',
        'j_rayting': 'B',
        'details_commentary': "Got swept away in season one like everyone else. Think I watched season two. No idea what happened after that. I'm not even sure how many seasons there were. Something about the later seasons didn't hit me."
    },
    {
        'title': 'Ozark',
        'j_rayting': 'B+',
        'details_commentary': "Never quite hit the peaks of my favourite shows, but certainly was something I watched straight through. Actually, I watched as soon as the seasons were released, and I thought it held up pretty well given that the premise seemed hard to keep going for five seasons."
    },
    {
        'title': 'Friends',
        'j_rayting': 'A-',
        'details_commentary': "An odd one because I find it almost unwatchable these days. I've tried rewatching it in the last decade and can't bring myself to do it. I'll occasionally watch clips on YouTube, but in the 90s and early 2000s, it was my favourite show. So it's kind of an odd one where I'm looking back much less favourably now than I experienced it live."
    },
    {
        'title': 'Homeland',
        'j_rayting': 'B+',
        'details_commentary': "Got swept up in season one, I think even season two as well. I can't remember if I stopped watching at season three or season four when it got less and less plausible, but the first season was quite exciting and definitely a cultural moment I enjoyed too."
    },
    {
        'title': 'The Morning Show',
        'j_rayting': 'B',
        'details_commentary': "Watched the first two seasons. Enjoyed parts of it, but had less and less interest as we became closer and closer to revisiting COVID. I've heard seasons three and four are quite good, but I haven't gotten around to it yet. I probably won't."
    },
    {
        'title': 'The Good Wife',
        'j_rayting': 'B+',
        'details_commentary': "Got very into it around season three and four, but can't remember if I even finished the entire show—I think I did. Fun, good performances, not completely preposterous. Few twists here and there. Quite good."
    },
    # From Perplexity Transcript
    {
        'title': 'Game of Thrones',
        'j_rayting': 'B',
        'details_commentary': "Watched the first two, maybe into the first three seasons, and it never quite hooked me. There were moments of real highs, like the end of season one, but overall it didn't hook me like it hooked almost everybody else, and I haven't watched most of the show and probably won't."
    },
    {
        'title': 'True Detective',
        'j_rayting': 'B+',
        'details_commentary': "First season's straight A-, second season more like a B. Never watched the Jodie Foster one, but definitely had moments in season one, especially toward the end of the season, where it was must-see TV and was really intrigued by where it was going. So, highly recommend season one."
    },
    {
        'title': 'Black Mirror',
        'j_rayting': 'B+',
        'details_commentary': "Odd in that I really like the show, and I've watched most of, I think, seasons one and two, but despite really liking it, I haven't returned to it in recent years. Maybe I will now, it's actually a good reminder to do that."
    },
    {
        'title': 'Community',
        'j_rayting': 'B+',
        'details_commentary': "At one point, it was must-see TV for me, but like a lot of shows, the momentum of trying to keep doing season after season seemed to wear off a little bit. And so it went from one of my favourite shows to a show I liked, and I'm not sure I actually finished watching the final seasons or not."
    },
    {
        'title': 'Barry',
        'j_rayting': 'B',
        'details_commentary': "Partially was a challenge around expectations. I thought it was going to be funny, where the first season I liked more because it was funny. As it got darker and darker and darker, I found the show much harder to watch. I think there were four seasons, and I ended at the end of season three. It just— all the fun was gone, and it just became plain dark. Maybe I should have reset my expectations, but I much preferred the fun, silliness almost, of season one than the increasing darkness of the last seasons, and I have no intention of watching season four."
    },
    {
        'title': 'Veep',
        'j_rayting': 'A-',
        'details_commentary': "Loved the show because it was so unpredictable, and so silly, and so clever, where maybe I should even give it a slightly higher grade. It really was a show I loved, and I wish it were still going."
    },
    {
        'title': 'Sirens',
        'j_rayting': 'B+',
        'details_commentary': "Good acting, beautiful location, who doesn't like rich, crazy people? It never reached an incredible level, but solid, and it was fun, and it's fairly short."
    },
    {
        'title': 'Dead to Me',
        'j_rayting': 'B',
        'details_commentary': "They have to keep making it up as they're going, and it gets more and more implausible and less and less enjoyable. Not bad overall, but probably could have stopped after season one."
    },
    {
        'title': 'Severance',
        'j_rayting': 'B',
        'details_commentary': "Interesting because I haven't finished season two, but the speed it's taken me to get through the middle of season two and obviously season one has been much slower than you'd expect. I don't dislike the show, but I'm mainly watching because the plaudits are so high that I'm supposed to like the show, but so far I don't, and I don't think I will."
    },
    {
        'title': 'White Lotus',
        'j_rayting': 'B+',
        'details_commentary': "Haven't watched season three yet, but really enjoyed seasons one and two, probably even more so season two, where the characters, the cleverness and silliness in combination, and just the overall brevity mean they're all really fun."
    },
    {
        'title': 'Friday Night Lights',
        'j_rayting': 'B+',
        'details_commentary': "Binged the whole thing fairly quickly. Think it was season two that was bad, but overall pretty impressive job of going through different phases of the team while keeping the through-line of the coach and his wife. Highly recommend."
    },
    {
        'title': 'Sex Education',
        'j_rayting': 'B',
        'details_commentary': "First season fairly good, especially given it's so novel, but as it gets progressively more and more graphic and more and more it feels like they're just adding stuff on, I lost interest. So I think I stopped somewhere in either late season three or maybe the middle of season four, can't remember, but I haven't finished it yet. And won't."
    },
    {
        'title': 'The O.C.',
        'j_rayting': 'B+',
        'details_commentary': "Hard one to look back on because it was such a cultural zeitgeist, and I watched it with my roommates and we'd look forward to it every week. The season one, in some ways, might be the most fun season of TV I've ever seen. That said, not a great show, and I think I stopped watching at the end of season two or maybe even season three. So, kind of a... it's more about 2003 and what a cultural zeitgeist it was than it is that I would recommend it to anyone now."
    },
    {
        'title': 'Big Little Lies',
        'j_rayting': 'B',
        'details_commentary': "Obviously a top caliber cast. Where I actually haven't watched season two, but season one was not quite as good as it could have been, but kept the momentum and the intrigue going and has a pretty nice close. So not in my top tier, but not something I regret watching either."
    },
    {
        'title': 'Squid Game',
        'j_rayting': 'B-',
        'details_commentary': "Tried to get into it but quit after episode four or five. It just wasn't interesting enough. Maybe it was going to go somewhere, but I just couldn't get into it and quit midway through."
    },
    {
        'title': 'Mare of Easttown',
        'j_rayting': 'A-',
        'details_commentary': "Not exactly uplifting, but keeps you captivated and has some moments of genuine thrills and just enough twists and turns that you don't see exactly where it's going."
    },
    {
        'title': 'The Night Manager',
        'j_rayting': 'B+',
        'details_commentary': "Don't remember it especially well beyond being exciting, good performances, and being worthy of finishing, but a decade later don't remember much."
    },
    {
        'title': 'Lupin',
        'j_rayting': 'B',
        'details_commentary': "Watched season 1 only, which was fairly entertaining, but not entertaining enough to warrant continuing to pursue it. It felt like it was close to being a great show, but was very uneven. Now just ... that's it."
    },
    {
        'title': 'Bodyguard',
        'j_rayting': 'B',
        'details_commentary': "Has moments of terror and excitement, a few twists you didn't see coming, but overall never gets beyond kind of a solid show."
    },
    {
        'title': 'Narcos',
        'j_rayting': 'B',
        'details_commentary': "Pretty captivating from the get-go, especially the first season and maybe even through season two. But once Escobar exited the show, my interest started to wane and I stopped somewhere in season 3."
    },
    {
        'title': 'Reacher',
        'j_rayting': 'B+',
        'details_commentary': "I've only done seasons one and two, which is not nuanced and surprisingly graphic in terms of violence sometimes, but maintains momentum and is fairly fun to watch."
    },
    {
        'title': 'Downton Abbey',
        'j_rayting': 'B+',
        'details_commentary': "Loved season one, I think I even loved season two as well, but it petered out in my mind after that. I don't think it went and got bad as much as I just stopped watching it. But everything I watched I enjoyed, and there were some moments of complete hilarity that I really recommend."
    },
    {
        'title': 'Orange Is the New Black',
        'j_rayting': 'B',
        'details_commentary': "A little bit like a lot of Netflix shows—comes out of the gate strong where I enjoyed season one, and I think I'd given up by the end of season two. It wasn't bad, it just wasn't as good, and there's so much alternative programming at this point."
    },
    {
        'title': 'The Fresh Prince of Bel-Air',
        'j_rayting': 'A-',
        'details_commentary': "My favourite show as a teenager; and, even today, it's aged relatively well; twice a year when I'm sitting in a hotel room flipping channel, I'm always happy to see if Fresh Prince is on and I get to take a trip back 25 years."
    },
    {
        'title': 'The Wonder Years',
        'j_rayting': 'A-',
        'details_commentary': "I was almost exactly the same age as Kevin - Fred Savage was the year above me at Stanford - so it hit extra hard, with its blend of nostalgia, drama, and humour."
    },
    {
        'title': 'Happy Days',
        'j_rayting': 'B+',
        'details_commentary': "A bit hard to judge because I did the majority of my watching aged 10-15, but there's a reason it's such an iconic show."
    },
    {
        'title': 'Saturday Night Live',
        'j_rayting': 'B+',
        'details_commentary': "Not always consistent, but the highs create as much joy as just about anything else. I LOVE the 40-year and 50-years specials because of the nostalgia they provide."
    },
    {
        'title': 'Roseanne',
        'j_rayting': 'B+',
        'details_commentary': "A bit like Cheers, I'm reacting to my pre-teen and teen reactions, but was a key part of my Friday nights growing up."
    },
    {
        'title': 'Freaks and Geeks',
        'j_rayting': 'B+',
        'details_commentary': "I watched after it had become a cult show - with most of its cast having moved on to bigger and better things - but I'm a sucker for a thoughtful high school show, so enjoyed quite a bit."
    },
    {
        'title': '30 Rock',
        'j_rayting': 'B+',
        'details_commentary': "The episode with Alec Baldwin impersonating Tracy Morgan's dad might be my favourite scene of TV ever; the rest was generally good, but a bit more up-and-down."
    },
    {
        'title': 'Frasier',
        'j_rayting': 'B+',
        'details_commentary': "I mainly watched as a kid, so likely missed most of the references, but alongside Cheers, will always have a special place in my heart."
    },
    {
        'title': 'The Golden Girls',
        'j_rayting': 'B+',
        'details_commentary': "Watched with my mum as a kid, so looking back I have mainly a nostalgic reaction, but I remember it was both ground-breaking and clever."
    },
    {
        'title': 'Atypical',
        'j_rayting': 'B',
        'details_commentary': "Nice blend of humour and drama, where it felt like it was looking to manufacture drama one season at a time versus having a well thought-out overall arc; stopped somewhere in season 3 or 4."
    },
    {
        'title': 'The Sex Lives of College Girls',
        'j_rayting': 'B+',
        'details_commentary': "I'm not the demographic, but I'm always a sucker for elite college settings, and the first two seasons kept the momentum pretty smoothly between silly and more serious topics."
    },
    {
        'title': 'Buffy the Vampire Slayer',
        'j_rayting': 'B',
        'details_commentary': "I watched in my 40s, so pretty far from the target audience. Had its moments, but felt a bit too dated and I didn't especially like the supernatural elements."
    },
    {
        'title': 'Adolescence',
        'j_rayting': 'A-',
        'details_commentary': "The opposite of uplifting, but it certainly makes you feel. Amazing acting, one camera shot per episode, and a weighty topic, especially for the dad of an 11-year-old boy (at the time of viewing)."
    }
]


def seed_shows():
    """Add/update all shows in the database."""
    print(f"Seeding {len(ALL_SHOWS)} shows to {API_URL}/shows...")
    print("=" * 60)

    added = 0
    updated = 0
    errors = 0

    for show in ALL_SHOWS:
        title = show['title']
        start_year = show.get('start_year', '')
        year_suffix = f" ({start_year})" if start_year else ""

        try:
            # First, try to add the show
            response = requests.post(
                f"{API_URL}/shows",
                json=show,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Longer timeout for TMDB/IMDB fetching
            )

            if response.status_code == 201:
                result = response.json()
                metadata = " (with TMDB metadata)" if result.get('metadata_fetched') else ""
                print(f"[ADDED] {title}{year_suffix}{metadata}")
                added += 1

            elif response.status_code == 409:
                # Show exists, try to update it with commentary
                result = response.json()
                existing = result.get('existing_shows', [])

                if existing:
                    show_id = existing[0].get('id')
                    if show_id:
                        # Update with new rating and commentary
                        update_data = {
                            'j_rayting': show['j_rayting'],
                            'details_commentary': show.get('details_commentary', '')
                        }
                        update_response = requests.put(
                            f"{API_URL}/shows/{show_id}",
                            json=update_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=30
                        )
                        if update_response.status_code == 200:
                            print(f"[UPDATED] {title}{year_suffix}")
                            updated += 1
                        else:
                            print(f"[ERROR] Failed to update {title}: {update_response.status_code}")
                            errors += 1
                    else:
                        print(f"[SKIP] {title}{year_suffix} exists but no ID returned")
                else:
                    print(f"[SKIP] {title}{year_suffix} already exists")

            else:
                print(f"[ERROR] Failed to add {title}: {response.status_code} - {response.text[:100]}")
                errors += 1

            # Small delay to avoid overwhelming the API
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] {title}: {e}")
            errors += 1

    print("=" * 60)
    print(f"Done! Added: {added}, Updated: {updated}, Errors: {errors}")
    print(f"Total shows: {added + updated}")

    if errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    seed_shows()
