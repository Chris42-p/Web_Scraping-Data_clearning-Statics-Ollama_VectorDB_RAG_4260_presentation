ollama_response={
     "summary": "This document is a placeholder structure with empty fields except for a brief text in the paragraphs section mentioning 'secret data' and containing numerical text. It appears to be a template or mock-up with no substantive content.",
     "description": "The document provided is structured as a dictionary with several standard fields (title, paragraphs, header/footer, table content, author, creation/modification dates, computer ID, and document hash) which are all empty except for the 'paragraphs' field. The paragraphs contain placeholder text discussing 'secret data' and includes arbitrary numerical text ('12 4'). There is no author, creation date, or other metadata. The content is minimal and serves as a template or example, lacking specific information or context about its origin or purpose.",
     "send_reason": "This communication was sent because a representative of the organization needs to provide an example or template document for processing or analysis. The document represents a generic structure, possibly to test systems or to illustrate a point about handling certain types of data. The content itself is intentionally vague, referring to 'secret data' without specifics.",
     "keywords": ["placeholder", "document", "template", "secret", "example"],
     "topics": ["Data", "Document Structure", "Placeholder"],
     "entities": [],
     "document_type": "placeholder",
     "sentiment": "neutral",
     "language": "en",
     "date_references": []
}
print(ollama_response["summary"])
# AI_Processed_Document_Obj()



class AI_Processed_Document_Obj:
     #== Inheretence
     doc_obj="" #processed_doc_obj -- instances. 

     #AI processed objects. 
     ai_summary=""
     ai_description=""
     ai_send_reason=""
     ai_keywords=""
     ai_topics=""
     ai_entities=""
     ai_document_type=""
     ai_sentiment=""
     ai_language=""
     ai_date_references=""

     def __init__(self,
               #    doc_obj:Processed_Document_Obj
          doc_obj,ai_summary, ai_description, ai_send_reason, ai_keywords, ai_topics, ai_entities, ai_document_type, ai_sentiment, ai_language, ai_date_references):
          self.doc_obj= doc_obj
          self.ai_summary=ai_summary
          self.ai_description=ai_description
          self.ai_send_reason=ai_send_reason
          self.ai_keywords=ai_keywords
          self.ai_topics=ai_topics
          self.ai_entities=ai_entities
          self.ai_document_type=ai_document_type
          self.ai_sentiment=ai_sentiment
          self.ai_language=ai_language
          self.ai_date_references=ai_date_references

          pass
     


AI_Processed_Document_Obj(
ollama_response["summary"] ,
ollama_response["description"] ,
ollama_response["send_reason"] ,
ollama_response["keywords"] ,
ollama_response["topics"] ,
ollama_response["entities"] ,
ollama_response["document_type"] ,
ollama_response["sentiment"] ,
ollama_response["language"] ,
ollama_response["date_references"] ,
)
