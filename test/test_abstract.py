"""Test methods in abstract.py. Uses hypothesis"""

from datetime import date
from datetime import datetime
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic_aioredis.model import Model


class SimpleModel(Model):
    _primary_key_field: str = "test_str"
    test_str: str
    test_int: int
    test_float: float
    test_date: date
    test_datetime: datetime
    test_ip_v4: IPv4Address
    test_ip_v6: IPv6Address
    test_list: List
    test_dict: Dict[str, Union[int, float]]
    test_tuple: Tuple[str]


def test_serialize_partially_skip_missing_field():
    serialized = SimpleModel.serialize_partially({"unknown": "test"})
    assert serialized["unknown"] == "test"


parameters = [
    (st.text, [], {}, "test_str", str, False),
    (st.dates, [], {}, "test_date", str, False),
    (st.datetimes, [], {}, "test_datetime", str, False),
    (st.ip_addresses, [], {"v": 4}, "test_ip_v4", str, False),
    (st.ip_addresses, [], {"v": 6}, "test_ip_v4", str, False),
    (st.lists, [st.tuples(st.integers(), st.floats())], {}, "test_list", str, False),
    (
        st.dictionaries,
        [st.text(), st.tuples(st.integers(), st.floats())],
        {},
        "test_dict",
        str,
        False,
    ),
    (st.tuples, [st.text()], {}, "test_tuple", str, False),
    (st.floats, [], {"allow_nan": False}, "test_float", float, True),
    (st.integers, [], {}, "test_int", int, True),
]


@pytest.mark.flaky(retruns=3)
@pytest.mark.parametrize(
    "strategy, strategy_args, strategy_kwargs, model_field, expected_type, equality_expected",
    parameters,
)
@given(st.data())
def test_serialize_partially(
    strategy,
    strategy_args,
    strategy_kwargs,
    model_field,
    expected_type,
    equality_expected,
    data,
):
    value = data.draw(strategy(*strategy_args, **strategy_kwargs))
    serialized = SimpleModel.serialize_partially({model_field: value})
    assert isinstance(serialized.get(model_field), expected_type)
    if equality_expected:
        assert serialized.get(model_field) == value
