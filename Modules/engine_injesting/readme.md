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

## 2026/05/27
### Requirements
- Docker Desktop installed and running

### First Time Setup
docker-compose build
docker-compose exec ollama ollama pull llama3.2

### Run (first time or after code changes)
docker-compose up --build

### Run (no code changes)
docker-compose up

### Stop
docker-compose down

