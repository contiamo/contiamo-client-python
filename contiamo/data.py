import datetime
import logging
import numpy
import pandas as pd
import tempfile

from contiamo.http_client import HTTPClient
from contiamo.utils import contract_url_template_from_identifier, raise_response_error
from contiamo.utils import get_file_extension
from contiamo.errors import InvalidRequestError


logger = logging.getLogger(__name__)


ALLOWED_UPLOAD_FILETYPES = {'csv', 'jsonl'}


def select_date_columns(df):
    """Indentify datetime columns with dates only."""
    date_cols = []
    for col in df.select_dtypes(include=['datetime']).columns:
        if (df[col].dropna().dt.time == datetime.time(0)).all():
            date_cols.append(col)
    return date_cols


def select_int_columns(df):
    """Identify float columns with integer values only."""
    int_cols = []
    for col in df.select_dtypes(include=['float']).columns:
        if numpy.isclose(df[col].round(0), df[col], equal_nan=True).all():
            int_cols.append(col)
    return int_cols


def preformat(df):
    """
    Preprocess to improve default JSON serialization:
    - dates: serialize without time when represented as datetime
    - integers: serialize as string when represented as float
    """
    # dates
    date_cols = select_date_columns(df)
    if date_cols:
        df[date_cols] = df[date_cols].apply(
            lambda column: column.dt.strftime('%Y-%m-%d'))
    # integers
    int_cols = select_int_columns(df)
    for col in int_cols:
        # pandas assignment by index will fill NaN values back in their original locations
        df[col] = df.loc[df[col].notnull(), col].astype(int).astype(str)


class DataClient:

    def __init__(self, contract_id, token, api_base='https://api.contiamo.com'):
        self.api_base = api_base
        self.token = token
        self.url_template = contract_url_template_from_identifier(
            contract_id, api_base)
        self.client = HTTPClient()

    def _make_request(self, url, file_object=None, file_type=None):
        kwargs = {'params': {'resource_token': self.token}}

        if file_object:
            if not file_type:
                raise ValueError(
                    'file_type must be specified if file_object is present')

            param_name = 'file-json' if file_type == 'jsonl' else 'file'
            kwargs.update({'files': {param_name: file_object}})

        response = self.client.request('post', url, **kwargs)
        try:
            json_response = response.json()
        except ValueError as e:  # JSONDecodeError inherits from ValueError
            raise_response_error(e, response, logger)

        return json_response

    def post_df(self, url, dataframe, include_index=False):
        if include_index:
            dataframe = dataframe.reset_index(drop=False)

        with tempfile.NamedTemporaryFile() as f:
            dataframe.to_json(f.name, orient='records',
                              lines=True, date_format='iso', date_unit='s')
            f.seek(0)
            result = self._make_request(url, f, file_type='jsonl')
        return result

    def post_file(self, url, filename):
        extension = get_file_extension(filename).lower()

        if extension not in ALLOWED_UPLOAD_FILETYPES:
            raise InvalidRequestError(
                'Unsupported file type \'%s\' to upload. Allowed formats: %s' %
                (extension, ', '.join(ALLOWED_UPLOAD_FILETYPES))
            )

        with open(filename, 'rb') as f:
            result = self._make_request(url, f, file_type=extension)
        return result

    def _post_data(self, url, dataframe, filename, include_index):
        # sanity checks
        if dataframe is None and filename is None:
            raise InvalidRequestError(
                'You need to specify at least a dataframe or a file to upload.')
        if dataframe is not None and filename is not None:
            raise InvalidRequestError(
                'Ambiguous request: You cannot provide both a dataframe and a file to upload.')
        if dataframe is not None and not isinstance(dataframe, pd.DataFrame):
            raise InvalidRequestError(
                'The argument you passed is a %s, not a pandas dataframe:\n%s'
                % (type(dataframe).__name__, str(dataframe)))

        if dataframe is not None:
            return self.post_df(url, dataframe, include_index)
        else:
            return self.post_file(url, filename)

    ###
    # Public methods

    # Any dataframe passed to these methods is copied so it will not be modified.
    # Private methods can therefore modify the dataframe they receive.
    # We can address memory issues by adding a flag later on.

    def discover(self, dataframe=None, filename=None, include_index=False):
        if dataframe is not None:
            # no need to upload full dataframe for discovery
            dataframe = dataframe.sample(min(100, len(dataframe)))
            preformat(dataframe)
        url = self.url_template.format(action='upload/discover')
        return self._post_data(url, dataframe, filename, include_index)

    def upload(self, dataframe=None, filename=None, include_index=False):
        if dataframe is not None:
            dataframe = dataframe.copy()
        url = self.url_template.format(action='upload/process')
        return self._post_data(url, dataframe, filename, include_index)

    def purge(self):
        url = self.url_template.format(action='data_purge')
        return self._make_request(url)
