#==== This is the interface for the injestion engine



#=========== Libraries and install code
# pip3 install ollama --break-system-packages 


from abc import ABC, abstractmethod

CONST={
     "PROMPT": "",
     "MODEL_NAME":"",
     

     "ERR_CODE":-1,
     "ERR_TXT":"Error occured", 
     
     "DOCUMENT_TYPES":{
          ".PDF":[],
          ".DOCX":[],
          ".CSV":[],
          ".EML":[],
          ".TXT":[],
          ".PPTX":[],
          ".ZIP":[],
          # "":[],
     }
}




class Interface_InjestionEngine():
     pass
     #====== Getters ======

     #===== setters ====
