"""Test methods in abstract.py. Uses hypothesis"""
import json
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


parameters = [
    (st.text, [], {}, "test_str", None),
    (st.integers, [], {}, "test_int", None),
    (st.floats, [], {"allow_nan": False}, "test_float", None),
    (st.dates, [], {}, "test_date", lambda x: json.dumps(x.isoformat())),
    (st.datetimes, [], {}, "test_datetime", lambda x: json.dumps(x.isoformat())),
    (st.ip_addresses, [], {"v": 4}, "test_ip_v4", lambda x: json.dumps(str(x))),
    (st.ip_addresses, [], {"v": 6}, "test_ip_v4", lambda x: json.dumps(str(x))),
    (
        st.lists,
        [st.tuples(st.integers(), st.floats())],
        {},
        "test_list",
        lambda x: json.dumps(x),
    ),
    (
        st.dictionaries,
        [st.text(), st.tuples(st.integers(), st.floats())],
        {},
        "test_dict",
        lambda x: json.dumps(x),
    ),
    (st.tuples, [st.text()], {}, "test_tuple", lambda x: json.dumps(x)),
]


@pytest.mark.parametrize(
    "strategy, strategy_args, strategy_kwargs, model_field, serialize_callable",
    parameters,
)
@given(st.data())
def test_serialize_partially(
    strategy, strategy_args, strategy_kwargs, model_field, serialize_callable, data
):
    value = data.draw(strategy(*strategy_args, **strategy_kwargs))
    serialized = SimpleModel.serialize_partially({model_field: value})
    if serialize_callable is None:
        assert serialized[model_field] == value
    else:
        assert serialized[model_field] == serialize_callable(value)


def test_serialize_partially_skip_missing_filed():
    serialized = SimpleModel.serialize_partially({"unknown": "test"})
    assert serialized["unknown"] == "test"
