INSERT INTO category (name) VALUES ('Mixed'), ('Mixed U18'), ('Maenner'), ('Frauen');
INSERT INTO team (name, id_category) VALUES ('The Shuttlekillers', 3), ('Dani u Roman', 3), ('Plauschler', 3), ('TVN D Chorbballer', 3), ('PERLe', 3), ('gagagaga', 3), ('Columbus', 3), ('Roste nicht', 3), ('Old Schmetterhand', 3), ('Duo Cerveza', 3), ('Strickers', 1), ('Pink Panter', 1), ('Bierschweinli', 1), ('Shuttle', 1), ('Federer, Hingis', 1), ('Team Dream Team', 1), ('079 hat sie gseit', 1), ('Weber 1', 1), ('Gian u Giachen', 1), ('Schuppi', 1), ('Dreamteam', 1), ('Team Bauer', 1), ('TVN TeamTurbo', 1), ('Dfifi u Dmischu', 4), ('Duo Zick Zack', 4), ('Salto Ruckwarts', 4), ('TVN Super Blondina', 4), ('Idealos', 2), ('Bundner Fanger', 2), ('2 auf einen Schlag', 2), ('Bonnie u Clyde', 1);
INSERT INTO playround (round_number, id_team_a, id_team_b, points_a, points_b) VALUES (1, 1, 2, 15, 22), (1, 3, 4, 24, 21), (1, 5, 6, 18, 18), (1, 7, 8, 9, 20), (1, 9, 10, 22, 8), (1, 11, 12, 20, 18), (1, 13, 14, 22, 15), (1, 15, 16, 20, 13), (1, 17, 18, 24, 10), (1, 19, 20, 14, 25), (1, 21, 22, 16, 16), (1, 23, 24, 21, 8), (1, 25, 26, 17, 17), (1, 27, 28, 11, 21), (1, 29, 30, 26, 9), (1, 31, NULL, 20, 10);
INSERT INTO playround (round_number, id_team_a, id_team_b, points_a, points_b) VALUES (2, 29, 20, 14, 26), (2, 3, 17, 22, 21), (2, 2, 9, 27, 9), (2, 13, 23, 33, 9), (2, 28, 8, 15, 19), (2, 11, 15, 13, 19), (2, 31, 5, 17, 20), (2, 6, 25, 17, 20), (2, 26, 21, 7, 29), (2, 22, 4, 8, 28), (2, 12, 1, 5, 28), (2, 14, 19, 22, 12), (2, 16, 27, 9, 23), (2, 18, 7, 14, 24), (2, 30, 10, 12, 20), (2, 24, NULL, 1, NULL);