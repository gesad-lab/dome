/*
DROP TABLE IF EXISTS parser_cache;
CREATE TABLE "parser_cache" (
	"id"	INTEGER NOT NULL UNIQUE,
	"dt_created" INTEGER NOT NULL DEFAULT (datetime('now', 'localtime')),
	"user_msg"	TEXT NOT NULL UNIQUE,
	"user_msg_len"	INTEGER NOT NULL,
	"processed_intent"	TEXT NOT NULL,
	"processed_class"	TEXT,
	"expected_intent"	TEXT,
	"expected_class"	TEXT,
	"similar_msg_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("similar_msg_id") REFERENCES "parser_cache"("id")
);
CREATE UNIQUE INDEX "parser_cache_user_msg_idx" ON "parser_cache" (
	"user_msg"	ASC
);
*/
-- "dt_created"	INTEGER NOT NULL DEFAULT (datetime('now', 'localtime'))

-- views
-- considered parser_cache is the parser that consider the expected_intent/class 
-- when they are valid and the processed_intent/class otherside
/*
CREATE VIEW 'vw_considered_parser_cache' AS
	SELECT id, user_msg, 
	ifnull(expected_intent, processed_intent) as 'considered_intent', 
	ifnull(expected_class, processed_class) as 'considered_class'
	from parser_cache 
*/	
/*
CREATE VIEW IF NOT EXISTS 'vw_validated_parser_cache'AS
	SELECT * from parser_cache 
	where 
	ifnull(expected_class, '') = ifnull(processed_class, '') 
	and 
	ifnull(expected_intent, '') = ifnull(processed_intent, '')
*/

-- update the correct parser_cache registers
/*
update parser_cache set expected_intent=processed_intent
where expected_intent is NULL;
update parser_cache set expected_class=processed_class
where expected_class is NULL;
*/