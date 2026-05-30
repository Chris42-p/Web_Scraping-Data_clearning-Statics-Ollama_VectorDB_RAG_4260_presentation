#==== This is the interface for the injestion engine



#=========== Libraries and install code


from abc import ABC, abstractmethod

CONST={
     #==== Error codes
     "ERR_CODE":2,
     "ERR_TXT":"Err in Injestion engine ", 
     "MODEL_CRASH_RETRY":3,

     #==== Document processing. 
     #-- docs supported
     "DOCUMENT_TYPES":{
          ".PDF":[],
          ".DOCX":[],
          ".CSV":[],
          ".TXT":[],
          ".PPTX":[],

          ".EML":[],
          ".ZIP":[],

     },

     #===== AI instructions
     # "MODEL_NAME":"deepseek-r1:latest", #prod AI  
     "MODEL_NAME":"llama3.2:latest", #dev AI 
     "PROMPT": """
Read the following document and return ONLY a raw JSON object (no markdown, no backticks, no explanation).

Required fields:
- "summary":          100 words max. Overview of the document content.
- "description":      300 words max. Detailed description of the content.
- "send_reason":      150 words max. Why this communication was sent.
- "keywords":         List of up to 15 relevant keywords (array of strings).
- "topics":           List of up to 5 broad topic categories (array of strings).
- "entities":         Named entities found in the document (people, orgs, places, dates).
- "document_type":    Single label e.g. "invoice", "legal", "email", "report".
- "sentiment":        Overall tone: "positive", "neutral", or "negative".
- "language":         Language the document is written in e.g. "en", "fr".
- "date_references":  Any dates mentioned or implied in the document (array of strings).

Rules:
- Output must be valid JSON only.
- Do not wrap in markdown code blocks.
- Do not use ```json or ``` anywhere in your response.
- Do not prefix lines with # or any other character.
- Do not include any text before or after the JSON.
- Your response must start with { and end with }

Document:
     """,
     
}




class Interface_InjestionEngine(ABC):

     @abstractmethod
     def controller(self):
         pass

     @abstractmethod
     def injest_local_file(self):
         pass

     @abstractmethod
     def injest_gmail(self, max_emails=10):
         pass
     #====== Getters ======

     #===== setters ====
