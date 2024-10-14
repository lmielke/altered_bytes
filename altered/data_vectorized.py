"""
rag_data.py
Handles RAG (Retrieval Augmented Generation) data for the agents.

Run like: 
se = WebSearch(name="TestSearchEngine", *args, **kwargs)
print(f"ldf: \n{se.data.show()}")
"""
import hashlib, json, os, re, time
from tabulate import tabulate as tb
from typing import Dict, Any, List, Union
import pandas as pd
import numpy as np
from numpy.linalg import norm as np_norm
from colorama import Fore, Style

# needed for semantic chunking and query preparation
from altered.data import Data
# ModelConnect is needed to prompt the Model directly for embeddings
from altered.model_connect import SingleModelConnect
import altered.hlp_printing as hlpp
import altered.settings as sts
import altered.model_params as msts


class VecDB(Data):
    """
    VecDB stores content as vectors and retrieves similar content
    based on cosine similarity.
    It maintains two storage components:
    - DataFrame storing data (inherit from class Data), and a hash to map embeddings to data.
    - NumPy array for storing the embeddings of the data.
    """
    mem_file_ext = 'npy'
    embedding_model = msts.config.overwrites.get('get_embeddings').get('model')
    # default_data_dir handles where table data are stored and loaded
    default_data_dir = os.path.join(sts.resources_dir, 'vec_db')
    # vec_fields_path is the path to the fields file for the table creator
    vec_fields_path = os.path.join(sts.data_dir, "data_VecDB_required_fields.yml")
    service_endpoint = 'get_embeddings'
    embed_match_len = 30


    def __init__(self, *args, name:str, u_fields_paths:list=[], **kwargs ):
        """Initializes the VecDB with the given model, setting up storage and server connection.
        Args:
            model (str): The model name for generating embeddings.
        """
        u_fields_paths = self.load_vec_fields(*args, u_fields_paths=u_fields_paths, **kwargs)
        super().__init__(*args, name=name, u_fields_paths=u_fields_paths, **kwargs, )
        self.dtype = np.float32
        self.assi = SingleModelConnect(*args, **kwargs)
        # self.vectors = self.load_vector_data(*args, **kwargs)
        if self.vectors is None:
            self.setup_storage(*args, **kwargs)

    def load_vec_fields(self, *args, fields_paths:list=None, u_fields_paths:list=[], **kwargs):
        """
        Loads the fields for the VecDB from the given paths and extends it by
        whatever fields come from upstram objects such as search_engine.py
        these fielspaths will be used in Data to load the fields
        """
        fields_paths = fields_paths if fields_paths is not None else [self.vec_fields_path]
        fields_paths.extend(u_fields_paths)
        return fields_paths

    def load_from_disk(self, *args, **kwargs) -> None:
        super().load_from_disk(*args, **kwargs)
        self.vectors = self.fs.load_from_disk(*args, file_ext='npy', **kwargs)
        return self.vectors

    def save_to_disk(self, *args, **kwargs) -> None:
        self.fs.save_to_disk(data=self.vectors, *args, **kwargs)
        # Data class has no save_to_disk, so we call it directly
        super().save_to_disk(*args, **kwargs)

    def setup_storage(self, *args, verbose:int=0, **kwargs):
        """
        Sets up the initial storage for the VecDB, including content data and vector embeddings.
        The VecDB utilizes two components for storage: 
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
        if verbose >= 2:
            print(f"{Fore.CYAN}VecDB.setup_storage: {Fore.RESET} {kwargs = }, {verbose = }")
        embedding = np.array(self.embedds(self.name, *args, verbose=verbose, **kwargs))
        normalized = self.normalize(embedding)
        self.vectors = np.stack((embedding, normalized)).astype(self.dtype)[None, ...]
        self.ldf.set_index('hash', inplace=True, drop=False)
        # To update the row where the index is NA
        self.ldf.loc[self.ldf.index.isna(), 'hash'] = self.hashify(normalized)
        self.ldf.loc[self.ldf.index.isna(), 'tools'] = str(self)
        self.ldf.loc[self.ldf.index.isna(), 'content'] = 'zero init'
        if 'embedd_match' in self.columns:
            # we convert the first 30 elements to a list for display
            embedd_match = json.dumps(self.vectors[0, 0, :self.embed_match_len].tolist())
            self.ldf.at[0, 'embedd_match'] = embedd_match
        if verbose:
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
        return hashlib.sha256(vector[:self.embed_match_len].tobytes()).hexdigest()[:num]

    def embedds(self, contents: List[str], *args, model:str=None, **kwargs) -> np.ndarray:
        """
        Retrieves embeddings for the given contents from the server.
        Args:
            contents: The contents to be embedded.
        Returns:
            An ndarray representing the embeddings.
        """
        # add this for getting the embedding directly
        assert contents, f"{Fore.RED}ERROR: VecDB.embedds: Contents is empty !{Fore.RESET}"
        if (self.embedding_model != model) and (model is not None):
            print(  f"{Fore.YELLOW}WARNING: VecDB.embedds.embedding_model: "
                    f"{model} != {self.embedding_model} {Fore.RESET}"
                    f"continuing with {self.embedding_model = }")
        return self.assi.post(
                                contents, 
                                service_endpoint=self.service_endpoint,
                                model=self.embedding_model,
                                **kwargs
                ).get('responses')[0].get('embedding')

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

    def mk_new_vector(self, record:str, *args, **kwargs):
        embedded = self.embedds(record, *args, **kwargs)
        normalized = self.normalize(embedded)
        return np.stack((embedded, normalized))[None, ...]

    def append(self, record:Dict[str, Any], *args, **kwargs) -> None:
        # first we create a new vector to be added to self.vectors
        new_vec = self.mk_new_vector(record['content'], *args, **kwargs)
        # then we update the record to be added, with the generated hash (normalized)
        record['name'], record['hash'] = self.name, self.hashify(new_vec[0, 1])
        # we want to avoid table inconsistencies (unlikely but possible)
        if self.check_hash_exists_in_df(record['hash'], *args, **kwargs): return
        # Here we update the database DataFrame
        super().append(record, *args, **kwargs)
        # finally we update the vectors with the newly embedded content token
        self.vectors = np.concatenate((self.vectors, new_vec), axis=0)
        self.ldf.set_index('hash', inplace=True, drop=False)

    def check_hash_exists_in_df(self, hash, *args, **kwargs):
        # currently self.ldf sometimes looses its 'hash' index, its not yet clear why.
        if hash in self.ldf['hash'].values:
            print(  f"{Fore.RED}IndexError: Record already exists!{Fore.RESET}\n"
                    f"{hash} in self.ldf['hash'].values\n"
                    f"{Fore.RED}Record has not been saved.{Fore.RESET}")
            return True
        else:
            return False

    def get(self, query:str, *args, num:int=5, **kwargs):
        start = time.time()
        print(f"{Fore.CYAN}VecDB.get: {Fore.RESET} {kwargs = }")
        # Find the idxs for num most similar vectors to the query vector inside self.vectors
        top_num_ixs, top_num_dists = self.find_nearest(
                                        np.array(self.embedds( query, *args, **kwargs )), 
                                        num,
                                    )
        # Get the records for num most similar records to the query inside rag_data
        hashes = [self.hashify(self.vectors[ix, 1, :]) for ix in top_num_ixs]
        nearest = self.ldf.loc[hashes]
        nearest['distances'] = top_num_dists
        return self.get_stats(nearest, query, start, *args, **kwargs )

    def get_stats(self, nearest, query, *args, verbose:int=0, **kwargs):
        nearest['num_tokens'] = nearest['content'].apply(lambda x: len(x) // 4)
        records = self.to_records(nearest, *args, **kwargs)
        # Add the 'num_tokens' column to the DataFrame (should be the content length // 4)
        records['stats']['total_tokens'] = sum(r['num_tokens'] for r in records['records'])
        self.mk_stats_table(records, *args, **kwargs)
        if verbose: 
            print(
                        f"{Fore.CYAN}\nResults/Stats for rag search: {Fore.RESET}\n"
                        f"{Fore.CYAN}Query: {Fore.RESET}{query}\n"
                        f"{tb(self.stats_tbl, headers='keys', tablefmt='grid')}"
                        f"\nStats: {records['stats']}\n"
                    )
        return records

    def mk_stats_table(self, records:list[dict], *args, **kwargs):
        self.stats_tbl, color, quartil = [], '', ''
        for i, r in enumerate(records['records']):
            content, dists, num_tokens = r['content'], r['distances'], r['num_tokens']
            if dists <= records['stats']['25%']:
                color = Fore.GREEN
                quartil = '25%'
            elif dists <= records['stats']['50%']:
                color = Fore.YELLOW
                quartil = '50%'
            else:
                color = Fore.RED
                quartil = '75%'
            self.stats_tbl.append({
                f"Top {len(records['records'])} RAG results": f"{color}{content}{Fore.RESET}", 
                f"distance": f"{color}{dists}{Fore.RESET}", 
                f"quartil": f"{color}{quartil}{Fore.RESET}",
                f"z_score": f"{color}{dists / records['stats']['std']:.2f}{Fore.RESET}",
                f"num_tokens": f"{color}{num_tokens}{Fore.RESET}", })

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

    def find_nearest(self, v, n, *args, **kwargs):
        # Calculate cosine similarity: dot product of normalized vectors
        top = np.argsort(-(self.vectors[:, 1, :] @ self.normalize(v)))[:max(20, len(v)//100)]
        # get L2 norm distances for ranking and sorting using pre consolidated self.vectors
        distances = np_norm(self.vectors[top, 0, :] - v, axis=1)[:n]
        return top[np.argsort(distances)], distances

    def __str__(self, *args, **kwargs):
        return f"VecDB(name={self.name}, fields=self.columns.keys(), )"

    def explain(self, vectors:np.ndarray, *args, verbose:int=0, **kwargs):
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
            'total_memory_usage (bytes)': vectors.nbytes,  # Total rag_data usage in bytes
        }

        # Print the explanation in a formatted way
        if verbose >= 2:
            hlpp.dict_to_table(f'{self.name}.explain', explains, *args, **kwargs)
            print('\n')
