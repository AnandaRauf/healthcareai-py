"""Filters for dataframes.

This module contains filters for preprocessing data. Most operate on DataFrames and are named appropriately.
"""

from sklearn.base import TransformerMixin

from healthcareai.common.healthcareai_error import HealthcareAIError
from healthcareai.common.validators import validate_dataframe_input_for_transformer


class DataframeColumnSuffixFilter(TransformerMixin):
    """Remove columns with suffix 'DTS'."""

    def __init__(self):
        """Instantiate the filter."""
        pass

    def fit(self, x, y=None):
        """Fit the dataframe."""
        return self

    def transform(self, x, y=None):
        """Transform the dataframe."""
        validate_dataframe_input_for_transformer(x)

        # Build a list that contains column names that do not end in 'DTS'
        filtered_column_names = [column for column in x.columns if not column.endswith('DTS')]

        # Select all data excluding datetime columns
        return x[filtered_column_names]


class DataFrameColumnDateTimeFilter(TransformerMixin):
    """Remove any columns that has the type datetime."""

    def __init__(self):
        """Instantiate the filter."""
        pass

    def fit(self, x, y=None):
        """Fit the dataframe."""
        return self

    def transform(self, x, y=None):
        """Transform the dataframe."""
        validate_dataframe_input_for_transformer(x)

        # Select all data excluding datetime columns
        return x.select_dtypes(exclude=["datetime"])


class DataframeColumnRemover(TransformerMixin):
    """Remove the given column or columns in list form."""

    def __init__(self, columns_to_remove):
        """Instantiate the filter."""
        self.columns_to_remove = columns_to_remove

    def fit(self, x, y=None):
        """Fit the dataframe."""
        return self

    def transform(self, X, y=None):
        """Transform the dataframe."""
        validate_dataframe_input_for_transformer(X)
        if self.columns_to_remove is None:
            # if there is no grain column, for example
            return X

        # Build a list of all columns except for the grain column'
        filtered_column_names = [c for c in X.columns if c not in self.columns_to_remove]

        # return the filtered dataframe
        return X[filtered_column_names]


class DataframeNullValueFilter(TransformerMixin):
    """Remove any row containing null values not in the excluded columns."""

    def __init__(self, excluded_columns=None):
        """Instantiate the filter."""
        # TODO validate excluded column is a list
        self.excluded_columns = excluded_columns or []

    def fit(self, x, y=None):
        """Fit the dataframe."""
        return self

    def transform(self, x, y=None):
        """
        Transform the dataframe.

        Raises:
            HealthcareAIError: Help the user out on training if they left all
            null columns in by telling them which to remove.
        """
        validate_dataframe_input_for_transformer(x)

        subset = [c for c in x.columns if c not in self.excluded_columns]

        entirely_null_columns = []
        for col in subset:
            if x[col].isnull().all():
                entirely_null_columns.append(col)

        if entirely_null_columns:
            raise HealthcareAIError(
                'Warning! You are about to drop any rows that contain any '
                'null values, you have {} column(s) that are entirely null. '
                'Please consider removing the following columns: {}'.format(
                    len(entirely_null_columns),
                    entirely_null_columns))

        x.dropna(axis=0, how='any', inplace=True, subset=subset)
        x.reset_index(drop=True, inplace=True)

        if x.empty:
            raise HealthcareAIError(
                "Because imputation is set to False, rows with missing or "
                "null/NaN values are being dropped. In this case, all rows "
                "contain null values and therefore were ALL dropped. Please "\
                "consider using imputation or assessing the data quality and "
                "availability.")

        return x
