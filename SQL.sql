CREATE TABLE article (
id INT PRIMARY KEY,
title VARCHAR(400),
writer VARCHAR(300),
date VARCHAR(20),
file_URL VARCHAR(500),
file_Name VARCHAR(400),
inst_Name VARCHAR(400),
inst_URL VARCHAR(400)
);
CREATE TABLE contents (
id INT,
body VARCHAR(10000),
FOREIGN KEY (id) REFERENCES article(id) on delete cascade
);
show indexes from article;

CREATE TABLE inverted (
word VARCHAR(100),
id INT,
search_count INT,
PRIMARY KEY(word, id)
);
CREATE TABLE view (
id INT PRIMARY KEY,
view_count INT
);

CREATE INDEX title_index on article(title);
CREATE INDEX writer_index on article(writer);