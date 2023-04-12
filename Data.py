from dotenv import load_dotenv
from supabase import create_client, Client
import os
import pandas as pd
import numpy as np

class Data():

    def __init__(self):
        load_dotenv()
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        self.supabase = create_client(url, key)
        self.data = self.retrieve_data()

    def retrieve_data(self):
        response = self.supabase.table('encodings').select("*").execute()
        if len(response.data) > 0:
            dfItem = pd.DataFrame.from_records(response.data, index="id")
            return dfItem
        return pd.DataFrame([], columns=['id', 'name', 'encoding'])

    def insert_data(self, encoding, name):
        list_encoding = list(encoding)
        data, count = self.supabase.table('encodings').insert({"name": name, "encoding": list_encoding}).execute()


if __name__ == '__main__':
    data = Data()
    data.retrieve_data()
