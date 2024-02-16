import json 
from dataclasses import dataclass
from PIL import Image

from elasticsearch import Elasticsearch, helpers
from embed import Embedder


@dataclass
class Index:
    embedder: Embedder
    es: Elasticsearch
    name: str
    mapping: dict
    Records: list['Record']

    @classmethod
    def create_index_from_properties(cls, embedder: Embedder, es: Elasticsearch, name: str, properties: dict) -> 'Index':
        mapping = {
            'properties': properties
        }
        return cls(embedder, es, name, mapping, [])
    
    @property
    def size(self):
        return len(self.Records)
    
    def __repr__(self):
        return f'Index({self.name}, {self.mapping}, size={self.size})'
    
    def __str__(self):
        return f'Index({self.name}, {self.mapping}, size={self.size})'
    
    def add_record(self, id: int, source: list | tuple):
        record_source = RecordSource(*source)
        self.Records.append(Record(self, id, record_source))
        return self.Records[-1]
    
    def add_records_from_dataframe(self, df):
        for i, row in df.iterrows():
            record = self.add_record(i, row)
            yield record.data

    def save_records(self, df, batch_size : int=100):
        for batch in range(0, len(df), batch_size):
            sub_df = df.iloc[batch:batch+batch_size]
            actions = self.add_records_from_dataframe(sub_df)
            helpers.bulk(self.es, actions)
        print(f'Saved {self.size} records to index {self.name}')

    def make_record_source_from_response(self, response: dict) -> 'RecordSource':
        return RecordSource(
            response['_source']['name'],
            response['_source']['description'],
            response['_source']['price'],
            response['_source']['img'],
            response['_source']['name_vector'],
            response['_source']['description_vector']
        )

    def search(self, search_field: str, query: str):
        embedded_query = self.embedder.embed(query)
        if search_field + '_vector' not in self.mapping['properties']:
            raise ValueError(f'{search_field} is not an embedding field')
        response = self.es.search(
            index=self.name,
            knn={
                "field": search_field + '_vector',
                "query_vector": embedded_query,
                "k": 1,
                "num_candidates": 100
            }
        )
        score = response['hits']['hits'][0]['_score']
        record = self.make_record_source_from_response(response['hits']['hits'][0])
        return record, score


@dataclass
class Record:
    index: Index
    _id: str
    _source: 'RecordSource'

    @property
    def name(self):
        return self._source.name
    
    @property
    def description(self):
        return self._source.description
    
    @property
    def price(self):
        return self._source.price
    
    @property
    def img(self):
        return self._source.img
    
    @property
    def name_vector(self):
        return self._source.name_vector
    
    @property
    def description_vector(self):
        return self._source.description_vector 
    
    def show_img(self):
        img = Image.open(self.img)
        img.show()
    
    @property
    def data(self):
        return {
            '_index': self.index.name,
            '_id': self._id,
            '_source': {
                'name': self.name,
                'description': self.description,
                'price': self.price,
                'img': self.img,
                'name_vector': self.name_vector,
                'description_vector': self.description_vector
            }
        }
    
    @property
    def json(self):
        return json.dumps(self.data)
        
    def __repr__(self):
        return f'Record({self.index.name}, {self._id}, {self._source.__repr__()})'
    
    def __str__(self):
        return f'Record({self.index.name}, {self._id}, {self._source.__str__()})'
    

@dataclass
class RecordSource:
    name: str
    description: str
    price: float
    img: str
    name_vector: list[float]
    description_vector: list[float]
    
    def __repr__(self):
        return f'RecordSource({self.name}, {self.description}, {self.price}, {self.img}, {self.name_vector}, {self.description_vector})'
    
    def __str__(self):
        return f'RecordSource({self.name}, {self.description}, {self.price}, {self.img}, {self.name_vector}, {self.description_vector})'
    

            
    
    



