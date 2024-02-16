from abc import ABC, abstractmethod

class DataType(ABC):
    @classmethod
    @abstractmethod
    def map(cls):
        pass

class FloatType(DataType):
    @classmethod
    def map(cls):
        return {'type': 'number'}
    
class StringType(DataType):
    @classmethod
    def map(cls):
        return {'type': 'text'}
    
class KeywordType(DataType):
    @classmethod
    def map(cls):
        return {'type': 'keyword'}
    
class SmallEmbeddingType(DataType):
    @classmethod
    def map(cls):
        return {
            'type': 'dense_vector',
            'dims': 1536,
            'index': 'true',
            'similarity': 'cosine'  
        }
    
class LargeEmbeddingType(DataType):
    @classmethod
    def map(cls):
        return {
            'type': 'dense_vector',
            'dims': 3072,
            'index': 'true',
            'similarity': 'cosine'  
        }