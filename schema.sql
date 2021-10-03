PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;
DROP TABLE IF EXISTS followers;
DROP TABLE IF EXISTS tweets;
DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
  id 		INTEGER PRIMARY KEY autoincrement,
  username	TEXT UNIQUE, 
  email  	TEXT unique,
  passwrd	TEXT
);

CREATE TABLE followers (
  id 				INTEGER PRIMARY KEY autoincrement,
  user_account 		TEXT,
  follower_account 	TEXT,
  UNIQUE(user_account, follower_account)
  FOREIGN KEY (user_account) REFERENCES accounts(username)
  FOREIGN KEY (follower_account) REFERENCES accounts(username)
  CONSTRAINT NO_SELF_FOLLOW check (user_account != follower_account) 
);

CREATE TABLE tweets (
  id 		INTEGER PRIMARY KEY autoincrement,
  author 	TEXT,
  content 	TEXT,
  timestmp 	DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN key (author) REFERENCES accounts(username)
);

/* insert into accounts */
INSERT into accounts VALUES (null, "@shakira", "hipsdontlie@gmail.com", "wakawaka");
INSERT into accounts VALUES (null, "@ddlovato", "some_email1@gmail.com", "baloney1");
INSERT into accounts VALUES (null, "@britneyspears", "itsbritneybitch@gmail.com", "blue42");
INSERT into accounts VALUES (null, "@twitter", "some_email2@gmail.com", "password");
INSERT into accounts VALUES (null, "@brucewayne", "notbatman39@gmail.com", "imbatman");

INSERT into accounts VALUES (null, "@ccnbrk", "cnn@gmail.com", "foxsux");
INSERT into accounts VALUES (null, "@narendramodi", "some_email3@gmail.com", "blahblahblah");
INSERT into accounts VALUES (null, "@selenagomez", "idkanythingaboutselena@gmail.com", "password2");
INSERT into accounts VALUES (null, "@jtimberlake", "some_email5@gmail.com", "password420");
INSERT into accounts VALUES (null, "@KimKardashian", "icanteven@gmail.com", "rosebud");

INSERT into accounts VALUES (null, "@YouTube", "youtube@gmail.com", "youtubePassword");
INSERT into accounts VALUES (null, "@ArianaGrande", "agrande@gmail.com", "seven_rings");
INSERT into accounts VALUES (null, "@TheEllenShow", "ellen@gmail.com", "imajerk");
INSERT into accounts VALUES (null, "@ladygaga", "ladygaga@gmail.com", "badromance");
INSERT into accounts VALUES (null, "@realDonaldTrump", "maga@gmail.com", "hamberders");

INSERT into accounts VALUES (null, "@taylorswift13", "generic_email@gmail.com", "red56");
INSERT into accounts VALUES (null, "@Cristiano", "futbolboi@gmail.com", "portugalnumber1");
INSERT into accounts VALUES (null, "@rihanna", "nananacomeon@gmail.com", "idk");
INSERT into accounts VALUES (null, "@katyperry", "ikissedagirl@gmail.com", "tgif");
INSERT into accounts VALUES (null, "@BarackObama", "itsBarack@gmail.com", "elpresidente");

/* insert into followers */

insert into followers values (null, "@shakira", "@Cristiano");
insert into followers values (null, "@shakira", "@rihanna");
insert into followers values (null, "@shakira", "@TheEllenShow");
insert into followers values (null, "@shakira", "@KimKardashian");
insert into followers values (null, "@shakira", "@ddlovato");

insert into followers values (null, "@ArianaGrande", "@ddlovato");
insert into followers values (null, "@ArianaGrande", "@YouTube");
insert into followers values (null, "@ArianaGrande", "@Cristiano");
insert into followers values (null, "@ArianaGrande", "@ladygaga");
insert into followers values (null, "@ArianaGrande", "@katyperry");

insert into followers values (null, "@brucewayne", "@ddlovato");
insert into followers values (null, "@brucewayne", "@YouTube");
insert into followers values (null, "@brucewayne", "@BarackObama");
insert into followers values (null, "@brucewayne", "@narendramodi");
insert into followers values (null, "@brucewayne", "@katyperry");

/* insert into tweets */
insert into tweets values (null, "@shakira", "test tweet 1", "2020-10-09 10:43:02");
insert into tweets values (null, "@shakira", "test tweet 2", "2020-10-08 10:42:06");
insert into tweets values (null, "@shakira", "test tweet 3", "2020-10-07 10:41:07");

insert into tweets values (null, "@ArianaGrande", "test tweet 1", "2020-10-03 11:42:07");
insert into tweets values (null, "@ArianaGrande", "test tweet 2", "2020-09-02 10:42:07");
insert into tweets values (null, "@ArianaGrande", "test tweet 3", "2020-08-01 09:42:07");

insert into tweets values (null, "@brucewayne", "test tweet 1", "2020-03-30 10:22:01");
insert into tweets values (null, "@brucewayne", "test tweet 2", "2020-02-29 11:54:06");
insert into tweets values (null, "@brucewayne", "test tweet 3", "2020-01-25 12:04:03");

insert into tweets values (null, "@ladygaga", "test tweet", "2019-12-30 01:23:07");
insert into tweets values (null, "@realDonaldTrump", "test tweet", "2020-10-01 02:32:07");
insert into tweets values (null, "@jtimberlake", "test tweet", "2020-10-09 03:42:07");

COMMIT;

				
												 
																	  