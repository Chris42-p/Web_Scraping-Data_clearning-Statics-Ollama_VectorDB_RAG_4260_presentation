#=== This is the interface for th default object 



CONST={
     "MODEL_NAME":"llama3.2:latest", #what AI model?
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

HANDLING MISSING DATA:
- Set field to null if no relevant information is found
- Do not infer or assume information not in the document

OUTPUT FORMAT RULES:
- BAD:  "amenities": "This is a 30 word description of the living space."
- GOOD: "amenities": "Spacious open-concept kitchen with hardwood floors and in-suite laundry."

- BAD:  "close_to": "The document mentions the unit is close to a park."
- GOOD: "close_to": "Located one block from Central Park and near two grocery stores."
""",

     "LLM_INSTRUCTIONS":
"""
     {{
     "smoke_free": bool or null,
     "pet_friendly": {{
          "pets_okay": bool or null,
          "cats_okay": bool or null,
          "dogs_okay": bool or null
     }},
     "private_room": bool or null,
     "living_situation": "50 word description of the living arrangement or null",
     "available_from": "on which date does the unit become availale or null",
     "property_type":"describe the kind of property it is (room, apartment, townhome, or house) or null",
     "has_ac": bool or null,
     "w_d_in_unit": bool or null,
     "furnished": bool or null,                     
     "wheelchair_accessible": bool or null,         
     "sq_footage": int or null,                     
     "price_per_month": int or null,                
     "parking": {{
          "included": bool or null,
          "spots": int or null,
          "ev_charging": bool or null,               
          "details": "location and cost details or null"
     }},
     "deposit": {{
          "damage_deposit": "amount and conditions or null",
          "other_deposits": "any additional deposits or null"
     }},
     "included_utilities": "list of included utilities (internet, water, heat, etc.) or null",
     "utility_cap": "any conditions on utility inclusion (e.g. capped at X people) or null", # new
     "requirements": {{
          "credit_check": bool or null,
          "references": bool or null,
          "criminal_record_check": bool or null,
          "other": "any other requirements or null"
     }},
     "close_to": "nearby attractions, parks, schools, grocery stores or null",
     "travel_convenience": "proximity to transit (bus, skytrain) or null",
     "luxuries": "100 word summary of premium features, pool, views, appliances, etc. or null",
     "llm_model_comments": "observations, uncertainties, or missing info or null"
     }}
"""




}

