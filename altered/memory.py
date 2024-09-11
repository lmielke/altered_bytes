"""
memory.py
Vector store enhanced Data. Uses Data indirectly via Thought.
Handles RAG (Retrieval Augmented Generation) data for the agents.
"""
import hashlib, json, os, re, time
from tabulate import tabulate as tb
from typing import Dict, Any, List, Union
import pandas as pd
import numpy as np
from numpy.linalg import norm as np_norm

from colorama import Fore, Style

# needed for semantic chunking and query preparation
from altered.thought import Thought
# Memory inherits from Thought
from altered.data import Data
# ModelConnect is needed to prompt the Model directly for embeddings
from altered.model_connect import ModelConnect
import altered.hlp_printing as hlpp


class Memory(Data):
    """
    Memory stores content as vectors and retrieves similar content
    based on cosine similarity.
    """
    service_endpoint = 'get_embeddings'


    def __init__(self, *args, name:str, **kwargs ):
        """Initializes the Memory with the given model, setting up storage and server connection.
        Args:
            model (str): The model name for generating embeddings.
        """
        super().__init__(*args, name=name, **kwargs)
        self.dtype = np.float32
        self.assi = ModelConnect(*args, **kwargs)
        self.setup_storage(*args, **kwargs)
        self.data.set_index('hash', inplace=True, drop=False)


    @property
    def data(self, *args, **kwargs):
        return getattr(self, self.name)

    def setup_storage(self, *args, embedd_size:int=4096, verbose:int=0, **kwargs):
        """
        Sets up the initial storage for the Memory, including content data and vector embeddings.
        The Memory utilizes two components for storage: 
        - DataFrame (`getattr(self, self.name)`) is the actual DB for the textual data and metadata, and
        - NumPy array (`self.vectors`) is the pointer for the corresponding vector embeddings.
        NOTE: self.vectors dim 1 has two rows: the original vector and its normalized version.
        example: np.array([[[0.1, 0.2, 0.3], ... [0.16666666, 0.3333333, 0.5]], ...])
        Each array entry is linked to a record in the DataFrame using a hash of the vector.
        Args:
            model: The name of the embedding model.
            embedd_size: The size of the embedding vectors.

        Returns:
            A tuple of initialized vectors and a storage DataFrame.
        """
        # Create an initial record for the storage
        # define self.vector
        embedding = np.array(self.embedds(self.name)[0].get('embedding'))
        normalized = self.normalize(embedding)
        hashified = self.hashify(normalized)
        self.vectors = np.stack((embedding, normalized)).astype(self.dtype)[None, ...]
        self.data.at[0, 'hash'] = hashified
        self.data.at[0, 'tools'] = str(self)
        self.explain(self.vectors)

    def hashify(self, vector: np.ndarray, num: int = 16) -> str:
        """
        Generates a hash for a vector, used to uniquely identify it.
        Args:
            vector: The vector to hash.
            num: Number of bytes to use from the vector for hashing.
        Returns:
            A hash string representing the vector.
        """
        return hashlib.sha256(vector[:30].tobytes()).hexdigest()[:num]

    def embedds(self, contents: List[str], *args, **kwargs) -> np.ndarray:
        """
        Retrieves embeddings for the given contents from the server.
        Args:
            contents: The contents to be embedded.
        Returns:
            An ndarray representing the embeddings.
        """
        # add this for getting the embedding directly
        return self.assi.post(
                                            contents, 
                                            service_endpoint=self.service_endpoint, 
                                            **kwargs
                            ).get('results')

    def update_vector_store(self, vector: np.ndarray, *args, **kwargs) -> None:
        """
        Updates the vector store with a new vector and its normalized version.
        Args:
            vector: The vector to add.
        """
        new = np.stack((vector, self.normalize(vector).astype(self.dtype)))[None, ...]
        self.vectors = np.concatenate((self.vectors, new), axis=0)
        # we return the normalized vector for further processing
        return self.vectors[-1, 1]

    def normalize(self, vector: np.ndarray, ord: int = 2):
        """
        Normalizes a vector using the L1 norm for cosine similarity calculations.
        Args:
            vector: The vector to normalize.
            ord: The norm order to use for normalization.
        Returns:
            The normalized vector.
        """
        return vector / np_norm(vector, ord)

    def append(self, record:Dict[str, Any], *args, **kwargs) -> None:
        # first we update the vectors with the newly embedded content token
        normalized =    self.update_vector_store(
                                    np.array(
                                        self.embedds( record['content'] )[0].get('embedding')
                                    ), *args, **kwargs,
                                )
        # then we add the record to the storage
        record = {k: record.get(k, None) for k, vs in self.fields.items()}
        record['hash'] = self.hashify(normalized)
        record['name'] = self.name
        super().append(record, *args, **kwargs)
        self.data.set_index('hash', inplace=True, drop=False)

    def get(self, query:str, *args, num:int=5, **kwargs):
        start = time.time()
        # Find the idxs for num most similar vectors to the query vector inside self.vectors
        top_num_ixs, top_num_dists = self.find_nearest(
                                        np.array(self.embedds( query )[0].get('embedding')), 
                                        num,
                                    )
        # Get the records for num most similar records to the query inside memory
        hashes = [self.hashify(self.vectors[ix, 1, :]) for ix in top_num_ixs]
        nearest = self.data.loc[hashes]
        nearest['distances'] = top_num_dists
        return self.get_stats(nearest, query, start, *args, **kwargs )

    def get_stats(self, nearest, query, *args, verbose:int=0, **kwargs):
        nearest['num_tokens'] = nearest['content'].apply(lambda x: len(x) // 4)
        records = self.to_records(nearest, *args, **kwargs)
        # Add the 'num_tokens' column to the DataFrame (should be the content length // 4)
        records['stats']['total_tokens'] = sum(r['num_tokens'] for r in records['records'])
        _25, _50, _75 = records['stats']['25%'], records['stats']['50%'], records['stats']['75%']
        rs = [(
                r['content'].split('\n')[0], 
                r['distances'],
                r['num_tokens']) for r in records['records']]
        if verbose: 
            self.stats_str = ''
            stats_tbl = []
            for i, r in enumerate(rs):
                color = Fore.GREEN if r[1] <= _25 else Fore.YELLOW if r[1] <= _50 else Fore.RED
                quartil = '25%' if r[1] <= _25 else '50%' if r[1] <= _50 else '75%'
                # z_score is the number of standard deviations from the mean
                z_score = r[1] / records['stats']['std']
                stats_tbl.append({
                                    f"Top {len(rs)} RAG results": f"{color}{r[0]}{Fore.RESET}", 
                                    f"distance": f"{color}{r[1]}{Fore.RESET}", 
                                    f"quartil": f"{color}{quartil}{Fore.RESET}",
                                    f"z_score": f"{color}{z_score:.2f}{Fore.RESET}",
                                    f"num_tokens": f"{color}{r[2]}{Fore.RESET}",
                                    })
            self.stats_str += f"{Fore.YELLOW}\nResults/Stats for rag search: {Fore.RESET}\n"
            self.stats_str += f"{Fore.GREEN}Query: {Fore.RESET}{query}\n"
            self.stats_str += tb(stats_tbl, headers="keys", tablefmt="grid")
            self.stats_str += f"\nStats: {records['stats']}\n"
            print(self.stats_str)
        return records

    
    def to_records(self, df: pd.DataFrame, start: float) -> List[Dict[str, Any]]:
        """
        Converts the DataFrame of records into a list of dictionaries.
        Args:
            df: The DataFrame containing the records.
            start: The start time for calculating the total processing time.
        Returns:
            A dictionary with the list of records and performance statistics.
        """
        stats = df['distances'].describe().round(2).to_dict()
        stats['time'] = f"{time.time() - start:.2f}"
        records = df.to_dict(orient='records')
        return {'records': records, 'stats': stats}

    def compare(self, query:str, strings:list, n:int=2):
        """
        Takes a query:string and a list of strings and finds the semantically closest
        representation of the query:stirng inside the list of strings and their distances.
        Example:
        strings = ['Why is the sky blue?', 'How do airplanes fly?', 
                    'What is the theory of relativity?', 'Why do we dream?', 
                    'What causes earthquakes?'] 
        query = 'Why is the sky blue?'

        call like:
        closest = self.stm.compare(query, strings, 2)
        
        returns:
        closest: (['Why is the sky blue?', 'How do airplanes fly?'], 
                    array([  0.        , 140.38395918]))
        """
        
        embeddeds = self.embedds(strings)
        top_nearest, distances = self.find_nearest(
                                                    self.embedds([query])[0], 
                                                    np.stack((
                                                                embeddeds, 
                                                                self.normalize(embeddeds),
                                                                )),
                                                    n,
                                        )
        return [s for i, s in enumerate(strings) if i in top_nearest], distances

    def find_nearest(self, v, n, *args, **kwargs):
        # Calculate cosine similarity: dot product of normalized vectors
        top = np.argsort(-(self.vectors[:, 1, :] @ self.normalize(v)))[:max(20, len(v)//100)]
        # get L2 norm distances for ranking and sorting using pre consolidated self.vectors
        distances = np_norm(self.vectors[top, 0, :] - v, axis=1)[:n]
        return top[np.argsort(distances)], distances

    def __str__(self, *args, **kwargs):
        return f"Memory(name={self.name}, fields=fields_dict, )"

    def explain(self, vectors: np.ndarray, *args, **kwargs):
        """
        Explains the key properties of a NumPy array in an informative way.

        Args:
            vectors (np.ndarray): The numpy array to explain.
        """
        # Check if the input is indeed a NumPy array
        if not isinstance(vectors, np.ndarray):
            raise ValueError("Expected a numpy ndarray.")
        
        # Collect basic properties
        explains = {
            'shape': vectors.shape,  # Dimensions of the array
            'ndim': vectors.ndim,    # Number of dimensions
            'dtype': vectors.dtype,  # Data type of the elements
            'size': vectors.size,    # Total number of elements
            'itemsize': vectors.itemsize,  # Size of each element in bytes
            'total_memory_usage (bytes)': vectors.nbytes,  # Total memory usage in bytes
        }

        # Print the explanation in a formatted way
        hlpp.dict_to_table(f'{self.name}.explain', explains, *args, **kwargs)
        print('\n')
