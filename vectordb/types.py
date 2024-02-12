from abc import ABC, abstractmethod

class DataType(ABC):
    @abstractmethod
    def map(self):
        pass

class FloatType(DataType):
    def map(self):
        return {'type': 'number'}
    
class StringType(DataType):
    def map(self):
        return {'type': 'text'}
    
class KeywordType(DataType):
    def map(self):
        return {'type': 'keyword'}
    
class SmallEmbeddingType(DataType):
    def map(self):
        return {
            'type': 'dense_vector',
            'dims': 1536,
            'index': 'true',
            'similarity': 'cosine'  
        }
    
class LargeEmbeddingType(DataType):
    def map(self):
        return {
            'type': 'dense_vector',
            'dims': 3072,
            'index': 'true',
            'similarity': 'cosine'  
        }