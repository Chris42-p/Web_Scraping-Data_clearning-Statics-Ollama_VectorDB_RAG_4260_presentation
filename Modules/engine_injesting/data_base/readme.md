# why do we need a DB ?


The documents can be GB in size and processing a few can fill ram thus need to write each object to a DB for higher reliability and workload robustness. 


going to allow duplicate entries since ai can produce new interpretations per run which can still be helpful for embedding document??


FIFO DB 


there might be an issue with the db's get_first_item, when a new obj is created that'll be 0...