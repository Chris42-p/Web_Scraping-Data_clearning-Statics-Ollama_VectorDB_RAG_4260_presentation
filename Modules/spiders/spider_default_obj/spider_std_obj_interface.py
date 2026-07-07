#=== This is the interface for th default object 



CONST={
#====== Dev 
     "DISPLAY_TEXT":True,


#======= Custom Errror message text
     "ERR_MSG_1":"Database post inset failed",

#======= Database queries. 
     "SQL_GET_ROW_BY_URL":"SELECT id, street_number, scraped_at FROM listings WHERE post_url = ?",
    
  "GET_ALL_LISTINGS":"SELECT * FROM listings;",



#======= Database configuration 
     "DB_LOCATION":"spider_central_db",
     "DB_NAME":"listings_db.db",

     "FORIGHN_KEYS_ON":"PRAGMA foreign_keys = ON",

     #== DB getters
     "GET_URLS":"SELECT id, post_url, scraped_at from listings;",

     #== insert into DB.  
     "INSERT_LISTING":"""
INSERT OR REPLACE INTO listings (
     post_id,
     post_url,
     source_spider,
     time_of_post,
     leasing_agent,
     general_area,
     street_number,
     city,
     province,
     postal_code,
     price,
     sqr_feet,
     bed,
     bath,
     rent_period,
     user_post_title,
     first_pic,
     user_meta_tags,
     post_description,
     img_url
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", #20 fields that're going to be added -- scraped at is auto generated
     "INSERT_PARSED_POST_DESCRIPTION":"""
INSERT OR REPLACE INTO parsed_descriptions (
     listing_id,
     smoke_free,
     private_room,
     living_situation,
     wheelchair_accessible,
     has_ac,
     w_d_in_unit,
     furnished,
     luxuries,
     sq_footage,
     price_per_month,
     included_utilities,
     utility_cap,
     close_to,
     travel_convenience,
     pets_okay,
     cats_okay,
     dogs_okay,
     parking_included,
     parking_spots,
     parking_ev_charging,
     parking_details,
     damage_deposit,
     other_deposits,
     req_references,
     req_credit_check,
     req_criminal_record_check,
     req_other,
     llm_model_comments
)VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
     "INSERT_POST_STATUS":"""
INSERT OR REPLACE INTO post_status(
     post_status, 
     time_on_market, 
     listing_id

)VALUES(?,?,?)""",

     #== create tables     
     "CREATE_TABLE_LISTINGS":"""
CREATE TABLE IF NOT EXISTS listings (
     id              INTEGER PRIMARY KEY AUTOINCREMENT,
     post_id         TEXT UNIQUE,        -- use to rescrape and check status
     source_spider    TEXT,    -- use to create column for source spider, so we can track which spider scraped the listing
     post_url        TEXT UNIQUE,
     time_of_post    DATETIME,
     leasing_agent   TEXT,
     scraped_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
     

     -- location
     general_area    TEXT,
     street_number   TEXT,
     city            TEXT,
     province        TEXT,
     postal_code     TEXT,
     
     -- pricing
     price           INTEGER,
     sqr_feet        INTEGER,
     bed             TEXT,
     bath            TEXT,
     rent_period     TEXT,
     
     -- descriptives
     user_post_title  TEXT,
     first_pic        TEXT,
     user_meta_tags   TEXT,
     post_description TEXT,
     img_url          TEXT
);""",
     "CREATE_TABLE_POST_DESCRIPTION":"""
CREATE TABLE IF NOT EXISTS parsed_descriptions (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id              INTEGER UNIQUE,
    -- conditions
    smoke_free              BOOLEAN,
    private_room            BOOLEAN,
    living_situation        TEXT,
    wheelchair_accessible   BOOLEAN,
    -- comfort
    has_ac                  BOOLEAN,
    w_d_in_unit             BOOLEAN,
    furnished               BOOLEAN,
    luxuries                TEXT,
    -- price details
    sq_footage              INTEGER,
    price_per_month         INTEGER,
    included_utilities      TEXT,
    utility_cap             INTEGER,
    -- travel
    close_to                TEXT,
    travel_convenience      TEXT,
    -- pets
    pets_okay               BOOLEAN,
    cats_okay               BOOLEAN,
    dogs_okay               BOOLEAN,
    -- parking
    parking_included        BOOLEAN,
    parking_spots           INTEGER,
    parking_ev_charging     BOOLEAN,
    parking_details         TEXT,
    -- deposits
    damage_deposit          INTEGER,
    other_deposits          TEXT,
    -- requirements
    req_references          BOOLEAN,
    req_credit_check        BOOLEAN,
    req_criminal_record_check BOOLEAN,
    req_other               TEXT,
    llm_model_comments      TEXT,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
);
""",
     "CREATE_TABLE_POST_STATUS":"""
CREATE TABLE IF NOT EXISTS post_status(
     id INTEGER PRIMARY KEY AUTOINCREMENT,  
     last_time_scraped   DATETIME DEFAULT CURRENT_TIMESTAMP,
     post_status         BOOLEAN,   
     time_on_market      INTEGER,
     listing_id INTEGER UNIQUE,     
     FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE);
     """,

     #== add listing into db 
     "INSERT_LISTING":"""
INSERT OR REPLACE INTO listings (
     post_id,
     post_url,
     source_spider,
     time_of_post,
     leasing_agent,
     general_area,
     street_number,
     city,
     province,
     postal_code,
     price,
     sqr_feet,
     bed,
     bath,
     rent_period,
     user_post_title,
     first_pic,
     user_meta_tags,
     post_description,
     img_url
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", #20 fields that're going to be added -- scraped at is auto generated
     "INSERT_PARSED_POST_DESCRIPTION":"""
INSERT OR REPLACE INTO parsed_descriptions (
     listing_id,
     smoke_free,
     private_room,
     living_situation,
     wheelchair_accessible,
     has_ac,
     w_d_in_unit,
     furnished,
     luxuries,
     sq_footage,
     price_per_month,
     included_utilities,
     utility_cap,
     close_to,
     travel_convenience,
     pets_okay,
     cats_okay,
     dogs_okay,
     parking_included,
     parking_spots,
     parking_ev_charging,
     parking_details,
     damage_deposit,
     other_deposits,
     req_references,
     req_credit_check,
     req_criminal_record_check,
     req_other,
     llm_model_comments
)VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
     "INSERT_POST_STATUS": """
INSERT OR REPLACE INTO post_status(
    post_status,
    time_on_market,
    listing_id
) VALUES (?, ?, ?)
""",



#======== AI configuration 
     "MODEL_NAME":"llama3.2:latest",#"qwen2.5:1.5b", #, #Select AI model?
     "LLM_CRASH_LIMIT":4,
     "SYSTEM_ROLE": # what is the role given to the system ?
"""
You are a precise data extraction engine.
DENEFITIONS:                              
- "own laundry" and "in-suite laundry" both mean w_d_in_unit: true
- Extract price if mentioned anywhere in the document
- "utilities included" should always populate included_utilities, never left null
- Explicit square footage should always populate sq_footage

BEHAVIOR:
- Return ONLY valid JSON, no preamble, no markdown, no code blocks
- Any observations go ONLY in "llm_model_comments"
- Write values as direct statements, not meta-commentary
- You extract ONLY explicitly stated facts from listing descriptions.
- You NEVER infer, assume, or guess.
- If a field is not clearly mentioned, you return null.


HANDLING MISSING DATA:
- Set field to null if no relevant information is found
- Do not infer or assume information not in the document

OUTPUT FORMAT RULES:
- BAD:  "amenities": "This is a 30 word description of the living space."
- GOOD: "amenities": "Spacious open-concept kitchen with hardwood floors and in-suite laundry."

- BAD:  "close_to": "The document mentions the unit is close to a park."
- GOOD: "close_to": "Located one block from Central Park and near two grocery stores."
""",

     "LLM_OUTPUT_OBJ_INSTRUCTIONS":
"""
JSON structure to return:
{{
    "smoke_free":               true/false/null,
    "private_room":             true/false/null,
    "living_situation":         string or null (e.g. "entire unit", "shared house"),
    "available_from":           string or null (e.g. "July 1st"),
    "property_type":            string or null (e.g. "apartment", "condo", "house"),
    "has_ac":                   true/false/null (look for: "air conditioning", "a/c"),
    "w_d_in_unit":              true/false/null (look for: "washer", "dryer", "laundry in unit"),
    "furnished":                true/false/null,
    "wheelchair_accessible":    true/false/null,
    "sq_footage":               int or null,
    "price_per_month":          int or null,
    "included_utilities":       string or null (e.g. "hydro, water"),
    "utility_cap":              string or null (e.g. "$50/month"),
    "close_to":                 string or null,
    "travel_convenience":       string or null,
    "luxuries":                 string or null,
    "pets_okay":                true/false/null,
    "cats_okay":                true/false/null,
    "dogs_okay":                true/false/null,
    "parking_included":         true/false/null,
    "parking_spots":            int or null,
    "parking_ev_charging":      true/false/null,
    "parking_details":          string or null,
    "damage_deposit":           string or null,
    "other_deposits":           string or null,
    "req_credit_check":         true/false/null,
    "req_references":           true/false/null,
    "req_criminal_record_check": true/false/null,
    "req_other":                string or null,
    "llm_model_comments":       string or null
}}
"""




}

