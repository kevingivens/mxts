import pytest
from pydantic import ValidationError

from mxts.config import OandaConfig

def test_oanda_config_validation():
    # Check validation over publicly exposed options

    with pytest.raises(ValidationError):
        # heartbeat must be nonnegative
        OandaConfig(heartbeat=-1)