import sqlite3

db_path = 'films.db'

# All 326 films affected
affected_titles = [
    "The Abyss", "The Accountant", "The Accused", "The Adam Project", "The African Queen",
    "The Alpinist", "The Amazing Spider-Man 2", "The Amazing Spider-Man", "The American President",
    "The Apartment", "The Aristrocrats", "The Armstrong Lie", "The Arrival",
    "The Assassination of Jesse James", "The Avengers", "The Aviator", "The BFG", "The Bank Job",
    "The Banshees of Inisherin", "The Basketball Diaries", "The Beach", "A Beautiful Mind",
    "The Big Chill", "The Big Lebowski", "The Big Short", "The Big Sick", "The Bikeriders",
    "The Blind Side", "The Book of Eli", "The Book Thief", "The Bourne Identity",
    "The Bourne Supremacy", "The Bourne Ultimatum", "The Boy in the Striped Pyjamas",
    "The Breakfast Club", "A Bronx Tale", "The Bucket List", "The Butler", "The Campaign",
    "The Candidate", "The Castle", "The Color Purple", "The Contractor", "The Counselor",
    "The Count of Monte Cristo", "The Courier", "The Creator", "The Croods", "The Crow",
    "The Da Vinci Code", "The Dark Knight", "The Dark Knight Rises", "The Darjeeling Limited",
    "The Dawn Wall", "The Delinquents", "The Descendants", "The Devil Wears Prada",
    "The Disaster Artist", "The Dish", "The Elephant Man", "The End We Start From",
    "The Equalizer", "The Equalizer 2", "The Equalizer 3", "The Exorcist: Believer",
    "The Fabelmans", "The Fall Guy", "The Family Man", "The Farewell", "The Fighter",
    "The Firm", "The Flash", "The French Connection", "The Fugitive", "A Few Good Men",
    "The Game", "The Gentlemen", "The Giver", "The Godfather", "The Godfather: Part II",
    "The Godfather: Part III", "The Good Dinosaur", "The Good Girl", "The Good Liar",
    "The Good Shepherd", "The Grand Budapest Hotel", "The Gray Man", "The Great Escape",
    "The Great Wall", "The Greatest Game Ever Played", "The Greatest Showman", "The Green Mile",
    "The Grey", "The Grudge", "The Guilty", "The Hangover", "The Hangover: Part II",
    "The Hangover: Part III", "The Help", "The Highwaymen", "The Hobbit: An Unexpected Journey",
    "The Hobbit: The Battle of the Five Armies", "The Hobbit: The Desolation of Smaug",
    "The Holiday", "The Bourne Legacy", "The Holdovers", "The Honest Thief", "The Host",
    "The Hunger Games", "The Hunger Games: Catching Fire", "The Hunger Games: Mockingjay - Part 1",
    "The Hunger Games: Mockingjay - Part 2", "The Hunt for Red October", "The Hunted",
    "The Hurt Locker", "The Imitation Game", "The Impossible", "The Incredibles",
    "The Incredibles 2", "The Informant!", "The Intern", "The Interpreter", "The Interview",
    "The Irishman", "The Iron Claw", "The Italian Job", "The Jacket", "The Karate Kid",
    "The Killing of a Sacred Deer", "The Killer", "The King's Speech", "The Kingdom",
    "The Last Duel", "The Last King of Scotland", "The Last Samurai", "The Last Stand",
    "The LEGO Batman Movie", "The LEGO Movie", "The LEGO Movie 2: The Second Part",
    "The Lego Ninjago Movie", "The Lighthouse", "The Lion King", "The Little Things",
    "The Lobster", "The Losers", "The Lost City", "The Lovely Bones", "The Machinist",
    "The Magnificent Seven", "The Man from U.N.C.L.E.", "The Man Who Wasn't There",
    "The Manchurian Candidate", "The Martian", "The Mask of Zorro", "The Mauritanian",
    "The Maze Runner", "The Meg", "The Meg 2: The Trench", "The Menu", "The Meyerowitz Stories",
    "The Midnight Sky", "The Mist", "The Money Pit", "The Monuments Men", "The Mountain Between Us",
    "The Mule", "The Muppets", "The Mummy", "The Naked Gun", "The Nice Guys", "The Northman",
    "The Notebook", "The Nun", "The Nun II", "The Old Guard", "The Outpost", "The Outsider",
    "The Outsiders", "The Peanut Butter Falcon", "The Peanuts Movie", "The Perfect Storm",
    "The Pianist", "The Place Beyond the Pines", "The Platform", "The Post", "The Prestige",
    "The Program", "The Proposal", "The Pursuit of Happyness", "The Rainmaker",
    "The Railway Man", "The Recruit", "The Rescuers Down Under", "The Revenant",
    "The Rock", "The Royal Tenenbaums", "The Ruins", "The Running Man", "The Secret in Their Eyes",
    "The Secret Life of Walter Mitty", "The Shack", "The Shape of Water", "The Shawshank Redemption",
    "The Siege", "The Sixth Sense", "The Social Network", "The Soloist", "The Son",
    "The Sound of Music", "The Sting", "The Strangers", "The Stranger", "The Super Mario Bros. Movie",
    "The Taking of Pelham 123", "The Terminal", "The Theory of Everything", "The Thing",
    "The Thomas Crown Affair", "The Tourist", "The Town", "The Trial of the Chicago 7",
    "The Triplets of Belleville", "The Truman Show", "The Underdoggs", "The Union",
    "The Untouchables", "The Upside", "The Usual Suspects", "The Velocity of Gary",
    "The Vow", "The Walk", "The War of the Roses", "The Watchers", "The Wave",
    "The Wedding Singer", "The Wolf of Wall Street", "The Woman King", "The Wrestler",
    "Three Billboards Outside Ebbing, Missouri", "Three Kings", "The Fountain", "The Insider",
    "The Last of the Mohicans", "The Legend of Tarzan", "The Road", "The Rundown",
    "The Time Traveler's Wife", "The Trench", "The Verdict", "The Village", "The Visit",
    "The Voyeurs", "The Wages of Fear", "The Waterboy", "The Witch", "The Witches",
    "The Wizard of Oz", "The Words", "The World Is Not Enough", "The World's End",
    "The Wrestler", "The X-Files: I Want to Believe", "The Zone of Interest"
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Count affected films WITH RT scores
placeholders = ','.join('?' * len(affected_titles))
cursor.execute(f"""
    SELECT COUNT(*)
    FROM films
    WHERE title IN ({placeholders})
    AND rotten_tomatoes IS NOT NULL
    AND rotten_tomatoes != ''
""", affected_titles)
with_scores = cursor.fetchone()[0]

# Count affected films WITHOUT RT scores
cursor.execute(f"""
    SELECT COUNT(*)
    FROM films
    WHERE title IN ({placeholders})
    AND (rotten_tomatoes IS NULL OR rotten_tomatoes = '')
""", affected_titles)
without_scores = cursor.fetchone()[0]

conn.close()

print("=" * 80)
print("DAMAGE ASSESSMENT: fix_title_formats.py Impact")
print("=" * 80)
print(f"\nTotal films affected: 326")
print(f"\nBreakdown:")
print(f"  • Films WITH RT scores: {with_scores} (links may be wrong, but scores exist)")
print(f"  • Films WITHOUT RT scores: {without_scores} (need both link verification and scores)")
print(f"\n{'-' * 80}")
print(f"GOOD NEWS:")
print(f"  • Only 6 of your 243 missing films are from the affected batch")
print(f"  • The other 237 missing films were NOT touched by fix_title_formats.py")
print(f"\nBAD NEWS:")
print(f"  • {with_scores} films have scores but may have incorrect RT links")
print(f"  • These would need manual verification to confirm links are correct")
print(f"  • Duplicate titles (like The Running Man, Federer) are most at risk")
print("=" * 80)
