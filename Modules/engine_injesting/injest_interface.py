#==== This is the interface for the injestion engine



#=========== Libraries and install code
# pip3 install ollama --break-system-packages 


from abc import ABC, abstractmethod

CONST={
     #==== Error codes
     "ERR_CODE":-1,
     "ERR_TXT":"Error occured", 
     
     #==== Document type supported
     "DOCUMENT_TYPES":{
          ".PDF":[],
          ".DOCX":[],
          ".CSV":[],
          ".EML":[],
          ".TXT":[],
          ".PPTX":[],
          ".ZIP":[],
          # "":[],
     },

     #===== AI instructions
     "MODEL_NAME":"deepseek-r1:14b",
     "PROMPT": """
          read the following document and generate SEO meta tags for it. 
          Return ONLY JSON OBJECTS with the fileds:
          
               -1_Title: under 50 word. 
               -2_Summary: 100 word summary of the document's content.     
               -3_Description: up to 300 word description of the content. 
               -4_Why was the communication sent: use up to 150 words to describe why the communication was sent. 
               -5_Keywords: list up to 15 relevant key words. 
               -6_Meta Data: who sent it, when,, when was the doucment created  

               -7_original document title: include the document's original title in the response. 
               -8_original doucment description: include the document's original description in the response. 

          ONLY JSON OBJECTS will be accepted. 
               
          Document:                         
     """,
     
}




class Interface_InjestionEngine():
     pass
     #====== Getters ======

     #===== setters ====
