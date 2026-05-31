

from abc import ABC, abstractmethod

CONST={
     "TEST":"",
     
}


class Embedding_interface(ABC):

     @abstractmethod
     def controller(self): pass