import itertools
import os

import numpy as np
import pandas as pd
import pytest
import vcr
import yaml

from . import utils
from contiamo.data import DataClient, select_date_columns, select_int_columns, preformat, slice_in_chunks
from contiamo.errors import InvalidRequestError
from contiamo.public import query


try:
    config = yaml.safe_load(open(utils.file_test_data('test_config.yml')))
except OSError:
    raise RuntimeError("Test config file not found. Email brandon@contiamo.com.")

api_base = config['api_base']
contract_id = config['contract_id']
contract_token = config['contract_token']
query_id = config['query_id']

data_client = DataClient(contract_id, contract_token, api_base=api_base)


class TestRequests:

    def test_select_dates(self):
        df = pd.DataFrame(
            {'date': pd.date_range('2016-01-01', periods=2)})
        df['datetime'] = pd.to_datetime(df['date'].astype(str) + 'T01:00')
        df.loc[3] = None  # test NaT datetime
        assert select_date_columns(df) == ['date']
        df = pd.DataFrame(
            {'int': [0, 1], 'float': [0.1, 0.2], 'str': ['a', 'b']})
        assert select_date_columns(df) == []

    def test_select_integers(self):
        df = pd.DataFrame({
            'int': list(range(4)),
            'int2': [3, np.nan, 58, np.nan],
            'int3': [2, 57, np.nan, np.nan],
            'float': [2.5, 2.6, 2.7, 2.0],
        })
        assert set(select_int_columns(df)) == {'int2', 'int3'}

    def test_preformat(self):
        df = pd.DataFrame({
            'int': [3, np.nan, 58],
            'date': pd.date_range('2016-01-01', periods=3),
        })
        preformat(df)
        expected = pd.DataFrame({
            'int': ['3', np.nan, '58'],
            'date': ['2016-01-01', '2016-01-02', '2016-01-03'],
        })
        assert df.equals(expected)

    @vcr.use_cassette(utils.file_test_cassette('test_purge.yaml'))
    def test_purge(self):
        response = data_client.purge()
        assert 'status' in response
        assert response['status'] == 'ok'

    @vcr.use_cassette(utils.file_test_cassette('test_discover.yaml'))
    def test_discover(self):
        # need to purge data before discovering
        if not os.path.isfile(utils.file_test_cassette('test_discover.yaml')):
            data_client.purge()
        response = data_client.discover(filename=utils.file_test_data('mock_data.csv'))
        assert 'status' in response
        assert response['status'] == 'ok'

    @vcr.use_cassette(utils.file_test_cassette('test_upload.yaml'))
    def test_upload(self):
        response = data_client.upload(filename=utils.file_test_data('mock_data.csv'))
        assert 'status' in response
        assert response['status'] == 'ok'

    @vcr.use_cassette(utils.file_test_cassette('test_upload.yaml'))
    def test_upload_dataframe(self):
        df = pd.DataFrame({'a': [1, 3], 'b': [2, 4]})
        response = data_client.upload(dataframe=df)
        assert 'status' in response
        assert response['status'] == 'ok'

    @vcr.use_cassette(utils.file_test_cassette('test_query.yaml'))
    def test_query(self):
        response = query(query_id, api_base=api_base)
        assert isinstance(response, pd.DataFrame)

    def test_slice_in_chunks(self):
        def reconstitute_list(l, slices):
            return list(itertools.chain.from_iterable((l[sl] for sl in slices)))
        for length, chunk_size in zip([113, 100, 100, 1, 0], [7, 100, 1, 10, 10]):
            data = list(range(length))  # we test slicing on a list
            assert data == reconstitute_list(data, slice_in_chunks(len(data), chunk_size))


class TestErrors:

    def file_test_dataframe(self):
        df = {'a': [1, 2, 3], 'b': [4, 5, 6]}
        with pytest.raises(InvalidRequestError):
            data_client.upload(dataframe=df)

    def test_no_argument(self):
        with pytest.raises(InvalidRequestError):
            data_client.upload()

    def test_two_arguments(self):
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        with pytest.raises(InvalidRequestError):
            data_client.upload(dataframe=df, filename=utils.file_test_data('mock_data.csv'))
