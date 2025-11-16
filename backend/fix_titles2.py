import sqlite3

DATABASE = 'films.db'

# Comprehensive list of title fixes
fixes = [
    ('Harry Potter III', 'Harry Potter and the Prisoner of Azkaban', 2004),
    ('Harry Potter IV', 'Harry Potter and the Goblet of Fire', 2005),
    ('Star Wars IV (new film #1)', 'Star Wars', 1977),
    ('Star Wars V: (new film #2)', 'The Empire Strikes Back', 1980),
    ('Star Wars VI: (new film #3)', 'Return of the Jedi', 1983),
    ('Lethal Weapon IV', 'Lethal Weapon 4', 1998),
    ('Nightmare on Elm St I', 'A Nightmare on Elm Street', 1984),
    ('Nightmare on Elm St II', 'A Nightmare on Elm Street 2: Freddy\'s Revenge', 1985),
    ('Nightmare on Elm St III', 'A Nightmare on Elm Street 3: Dream Warriors', 1987),
    ('Nightmare on Elm St IV', 'A Nightmare on Elm Street 4: The Dream Master', 1988),
    ('Nightmare on Elm St V', 'A Nightmare on Elm Street 5: The Dream Child', 1989),
    ('American Pie II', 'American Pie 2', 2001),
    ('American Pie III', 'American Pie: The Wedding', 2003),
    ('American Pie IV: American Wedding', 'American Pie: The Wedding', 2003),
    ('Ace Ventura I: Pet Detective', 'Ace Ventura: Pet Detective', 1994),
    ('Ace Ventura II: When Nature Calls', 'Ace Ventura: When Nature Calls', 1995),
    ('Look Whose Talking II', 'Look Who\'s Talking Too', 1990),
    ('Terminator II, The', 'Terminator 2: Judgment Day', 1991),
    ('Matrix II, The', 'The Matrix Reloaded', 2003),
    ('Bill and Ted\'s Excellent Adventure II', 'Bill & Ted\'s Bogus Journey', 1991),
    ('House Party II', 'House Party 2', 1991),
    ('Charlies\'s Angels II', 'Charlie\'s Angels: Full Throttle', 2003),
    ('Wall St 2: Money Never Sleeps', 'Wall Street: Money Never Sleeps', 2010),
    ('Stcar Named Desire, A', 'A Streetcar Named Desire', 1951),
    ('Plains, Trains, and Automobiles', 'Planes, Trains and Automobiles', 1987),
    ('Serendipidity', 'Serendipity', 2001),
    ('Dead Poet\'s Society', 'Dead Poets Society', 1989),
    ('Fast Time at Ridgemont High', 'Fast Times at Ridgemont High', 1982),
    ('First Wive\'s Club, The', 'The First Wives Club', 1996),
    ('Runaway Jury, The', 'Runaway Jury', 2003),
    ('Illusionist, The', 'The Illusionist', 2006),
    ('DaVinci Code, The', 'The Da Vinci Code', 2006),
    ('Breakup, The', 'The Break-Up', 2006),
    ('Bad News Bears, The', 'The Bad News Bears', 1976),
    ('Meyerowitz, Stories, The', 'The Meyerowitz Stories', 2017),
    ('Short  Game, The', 'The Short Game', 2013),
    ('Widow of St. Pierre, The', 'The Widow of St. Pierre', 2000),
    ('Master and Commander', 'Master and Commander: The Far Side of the World', 2003),
    ('Meet the Parents II: Meet the Fockers', 'Meet the Fockers', 2004),
    ('Manchurian Candidate, The (2004)', 'The Manchurian Candidate', 2004),
    ('Nick & Nora\'s Infinite Playlist', 'Nick and Norah\'s Infinite Playlist', 2008),
    ('Mr.Saturday Night', 'Mr. Saturday Night', 1992),
    ('Talladega Nights: The Legend of Ricky Bobby', 'Talladega Nights: The Ballad of Ricky Bobby', 2006),
    ('Eurotrip', 'EuroTrip', 2004),
    ('Miami Vice', 'Miami Vice', 2006),
    ('Driven', 'Driven', 2001),
    ('Hope Springs', 'Hope Springs', 2012),
    ('Billy Elliott', 'Billy Elliott', 2000),
    ('Spencer Confidential', 'Spenser Confidential', 2020),
    ('Triple Frontier', 'Triple Frontier', 2019),
    ('Kodachrome', 'Kodachrome', 2017),
    ('King Jack', 'King Jack', 2015),
    ('Jim and Andy: The Great Beyond', 'Jim & Andy: The Great Beyond', 2017),
    ('Interview with the Vampire', 'Interview with the Vampire', 1994),
    ('Honey, I Blew Up the Kids', 'Honey, I Blew Up the Kid', 1992),
    ('Kim Swims', 'Kim Swims', 2017),
    ('Desert Runners', 'Desert Runners', 2013),
    ('An Honest Liar', 'An Honest Liar', 2014),
    ('Victory', 'Victory', 1981),
    ('Sierra Burgess is a Loser', 'Sierra Burgess Is a Loser', 2018),
    ('Eurovision Song Content: The Story of Fire Saga', 'Eurovision Song Contest: The Story of Fire Saga', 2020),
    ('Flight Plan', 'Flightplan', 2005),
    ('Ronnie Coleman: The King', 'Ronnie Coleman: The King', 2018),
    ('Road House (2024', 'Road House', 2024),
    ('Once Brothers (ESPN 30 for 30)', 'Once Brothers', 2010),
    ('Slaying the Badger (ESPN 30 for 30)', 'Slaying the Badger', 2014),
    ('Against The Tides', 'Against the Tide', 2023),
    ('St Kings', 'Street Kings', 2008),
]

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

fixed_count = 0
for old_title, new_title, year in fixes:
    cursor.execute('UPDATE films SET title = ?, release_year = ? WHERE title = ?', (new_title, year, old_title))
    if cursor.rowcount > 0:
        print(f"✓ Fixed: '{old_title}' → '{new_title}' ({year})")
        fixed_count += cursor.rowcount

conn.commit()
conn.close()

print(f"\n✅ Fixed {fixed_count} titles!")
