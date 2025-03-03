DROP TABLE IF EXISTS items;

CREATE TABLE items
(
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    item_description TEXT,
    item_price DECEMAL NOT NULL,
    is_vegetarian BOOLEAN,
    is_vegan BOOLEAN,
    is_gluten_free BOOLEAN,
    is_member_discount_allowed BOOLEAN,
    is_coupon_allowed BOOLEAN,
    is_delivery_allowed BOOLEAN,
    is_pickup_allowed BOOLEAN,
    number_of_sold INTEGER,
    amount_available INTEGER,
    compulsory_option TEXT,
    supplementary_option TEXT
);

INSERT INTO items (item_name,item_description,item_price,is_vegetarian,is_vegan,is_gluten_free,is_member_discount_allowed,is_coupon_allowed,is_delivery_allowed,is_pickup_allowed,number_of_sold,amount_available)
VALUES ('Chicken Balls','Battered chicken balled served with a dip of curry.',10,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,1,100),
    ('Veggie Spring Rolls','Home made crispy rolls served with light soya or sweet chilli.',9.5,TRUE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,0,100),
    ('Wonton Soup','Pork and prawns delicately wrapped in wonton pastry.',10,FALSE,FALSE,TRUE,TRUE,TRUE,FALSE,TRUE,0,100),
    ('Chow Mein Noodles','Classic Thick noodles tossed in a drizzle of sauces, thinly sliced vegetables and protein.',16,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,TRUE,3,100),
    ('Spice Cone','Crispy chilli chicken strips, sliced peppers and onion, tossed in our homemade spices.',15.9,FALSE,FALSE,FALSE,TRUE,FALSE,FALSE,TRUE,2,100),
    ('Vegetarian Thai Fried Rice','Pineapple, tofu and seasonal vegetables.',15.9,TRUE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,0,100),
    ('Vegan Yellow Curry','Homemade yellow curry, red lentils, mixed vegetables, and tofu served with boiled rice.',16.5,TRUE,TRUE,FALSE,TRUE,FALSE,TRUE,TRUE,0,100),
    ('Coke Zero 330ml','',3.2,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,0,300),
    ('Fanta 330ml','',3.2,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,0,300),
    ('Sprite Zero 330ml','',3.2,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,0,300);

UPDATE items SET compulsory_option='["Chinese Style","Darkside Style"]' WHERE item_id NOT IN (7,8,9,10);
UPDATE items SET supplementary_option='{"Beijing Dip":1,"Shanghai Dip":1,"Guangzhou Dip":1,"Lao Gan Ma":2,"Sweet Chiilli":10}' WHERE item_id NOT IN (6,8,9,10);
-- (Highly recommended if you dont know any of those above)

DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    real_user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT, 
    password TEXT NOT NULL,
    country TEXT,
    address TEXT,
    is_member INTEGER,
    is_admin INTEGER,
    failed_day DATE

);

UPDATE users SET is_admin=1, is_member=1 WHERE user_id = "admin";

DROP TABLE IF EXISTS orders;
CREATE TABLE orders
(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    real_user_id INTEGER NOT NULL,
    order_timestamp DATETIME NOT NULL,
    receive_timestamp DATETIME NOT NULL,
    delivery_option TEXT NOT NULL,
    order_content TEXT NOT NULL,
    paid_amount NUMERIC NOT NULL,
    currency TEXT NOT NULL,
    paid_eur NUMERIC NOT NULL,
    note TEXT
);


DROP TABLE IF EXISTS winners;

CREATE TABLE winners 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    country TEXT NOT NULL,
    song TEXT NOT NULL,
    performer TEXT NOT NULL,
    points INTEGER
);

INSERT INTO winners (year, country, song, performer, points)
VALUES
    (1956, "Switzerland", "Refrain", "Lys Assia", NULL),
    (1957, "Netherlands", "Net Als Toen", "Corry Brokken", 31),
    (1958, "France", "Dors, Mon Amour", "Andre Claveau", 27),
    (1959, "Netherlands", "Een Beetje", "Teddy Scholten", 21),
    (1960, "France", "Tom Pillibi", "Jacqueline Boyer", 32),
    (1961, "Luxembourg", "Nous les amoureux", "Jean-Claude Pascal", 31),
    (1962, "France", "Un premier amour", "Isabelle Aubret", 26),
    (1963, "Denmark", "Dansevise", "Grethe & Jorgen Ingmann", 42),
    (1964, "Italy", "Non ho l'eta (per amarti)", "Gigliola Cinquetti", 49),
    (1965, "Luxembourg", "Poupee de cire, poupee de son", "France Gall", 32),
    (1966, "Austria", "Merci Cherie", "Udo Jurgens", 31),
    (1967, "United Kingdom", "Puppet on a String", "Sandie Shaw", 42),
    (1968, "Spain", "La, la, la", "Massiel", 29),
    (1969, "Spain", "Vivo Cantando", "Salome", 18),
    (1969, "United Kingdom", "Boom Bang-a-Bang", "Lulu", 18),
    (1969, "Netherlands", "De Troubadour", "Lennie Kuhr", 18),
    (1969, "France", "Un jour, un enfant", "Frida Boccara", 18),
    (1970, "Ireland", "All Kinds of Everything", "Dana (nasty lady)", 32),
    (1971, "Monaco", "Un banc, un arbre, une rue", "Severine", 128),
    (1972, "Luxembourg", "Apres Toi", "Vicky Leandros", 128),
    (1973, "Luxembourg", "Tu Te Reconnaitras", "Anne-Marie David", 129),
    (1974, "Sweden", "Waterloo", "ABBA", 24),
    (1975, "Netherlands", "Ding-A-Dong", "Teach-In", 152),
    (1976, "United Kingdom", "Save Your Kisses for Me", "Brotherhood of Man", 164),
    (1977, "France", "L'Oiseau Et L'Enfant", "Marie Myriam", 136),
    (1978, "Israel", "A-Ba-Ni-Bi", "Izhar Cohen & Alphabeta", 157),
    (1979, "Israel", "Hallelujah", "Gali Atari & Milk and Honey", 125),
    (1980, "Ireland", "What's Another Year?", "Johnny Logan", 143),
    (1981, "United Kingdom", "Making Your Mind Up", "Bucks Fizz", 136),
    (1982, "Germany", "Ein Bisschen Frieden", "Nicole", 161),
    (1983, "Luxembourg", "Si la vie est cadeau", "Corinne Hermes", 142),
    (1984, "Sweden", "Diggi-Loo Diggi-Ley", "Herreys", 145),
    (1985, "Norway", "La det swinge", "Bobbysocks", 123),
    (1986, "Belgium", "J'aime la vie", "Sandra Kim", 176),
    (1987, "Ireland", "Hold Me Now", "Johnny Logan", 172),
    (1988, "Switzerland", "Ne partez pas sans moi", "Celine Dion", 137),
    (1989, "Yugoslavia", "Rock Me", "Riva", 137),
    (1990, "Italy", "Insieme: (1992)", "Toto Cutugno", 149),
    (1991, "Sweden", "Fangad av en stormvind", "Carola", 146),
    (1992, "Ireland", "Why Me", "Linda Martin", 155),
    (1993, "Ireland", "In Your Eyes", "Niamh Kavanagh", 187),
    (1994, "Ireland", "Rock 'n' Roll Kids", "Paul Harrington & Charlie McGettigan", 226),
    (1995, "Norway", "Nocturne", "Secret Garden", 148),
    (1996, "Ireland", "The Voice", "Eimear Quinn", 162),
    (1997, "United Kingdom", "Love Shine a Light", "Katrina and the Waves", 227),
    (1998, "Israel", "Diva", "Dana International", 172),
    (1999, "Sweden", "Take Me to Your Heaven", "Charlotte Nilsson", 163),
    (2000, "Denmark", "Fly on the Wings of Love", "Olsen Brothers", 195),
    (2001, "Estonia", "Everybody", "Tanel Padar, Dave Benton & 2XL", 198),
    (2002, "Latvia", "I Wanna", "Marie N", 176),
    (2003, "Turkey", "Everyway That I Can", "Sertab Erener", 167),
    (2004, "Ukraine", "Wild Dances", "Ruslana", 280),
    (2005, "Greece", "My Number One", "Helena Paparizou", 230),
    (2006, "Finland", "Hard Rock Hallelujah", "Lordi", 292),
    (2007, "Serbia", "Molitva", "Marija Serifovic", 268),
    (2008, "Russia", "Believe", "Dima Bilan", 272),
    (2009, "Norway", "Fairytale", "Alexander Rybak", 387),
    (2010, "Germany", "Satellite", "Lena", 246),
    (2011, "Azerbaijan", "Running Scared", "Ell/Nikki", 221),
    (2012, "Sweden", "Euphoria", "Loreen", 372),
    (2013, "Denmark", "Only Teardrops", "Emmelie de Forest", 281),
    (2014, "Austria", "Rise Like a Phoenix", "Conchita Wurst", 290),
    (2015, "Sweden", "Heroes", "Mans Zelmerlow", 365),
    (2016, "Ukraine", "1944", "Jamala", 534),
    (2017, "Portugal", "Amar pelos dois", "Salvador Sobral", 758),
    (2018, "Israel", "Toy", "Netta", 529),
    (2019, "Netherlands", "Arcade", "Duncan Laurence", 498),
    (2021, "Italy", "Zitti e buoni", "Maneskin", 524),
    (2022, "Ukraine", "Stefania", "Kalush Orchestra", 631),
    (2023, "Sweden", "Tattoo", "Loreen", 583)
;

DROP TABLE IF EXISTS coupons;

CREATE TABLE coupons 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    discount_amount INTEGER NOT NULL,
    description TEXT
);

INSERT INTO coupons (code,discount_amount,description)
VALUES ('LOVEFOOD',5,''),
    ('USERBEST',10,'')
;