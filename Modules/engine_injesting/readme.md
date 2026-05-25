## scope 

Hard coded values go into the config for the object

create the interace at the end after finishing the object 

injestion engine -- stage 2
   - will take all documents in the __injest file  
   - break the fils down into their content  (images, text, tables, headers, footers, ... )
   - feed one big string object into a local LLM for processing (not CLOUD sensetive work!!! )
   
   stage 3
   - get the output from AI and embed all the response objects into a vector Database (sample files) YT link:https://www.youtube.com/watch?v=god8Pox1laE 
   
   stage 4
   - front end: let the user send a query
   - backend: catch the query and send it to the database. return obj.

## 2026/05/24
## Docker Setup
- Dockerfile located in sample_files/
- Build: `docker build -t 4260-presentation -f sample_files/Dockerfile .`
- Run: `docker run 4260-presentation`

## Bug Fixes (yung branch)
- Fixed DocxReader → Document (python-docx correct import)
- Fixed f-string with nested quotes in __call_ollama_on_a_file
- Fixed .items() on dictionary iteration in controller()
- Fixed range(num_pages) for PDF page loop
- Fixed Processed_Document_Obj parameters now optional (=None)
- Fixed hash_document() calculates hash internally using hashlib
- Fixed CSV file path hardcoded 'Giants.csv' → use docuemnt parameter
- Fixed doc_content initialized as "" instead of None for CSV