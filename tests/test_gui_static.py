from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tributary_geometry.config import TributaryConfig
from tributary_geometry.gui_app import NUMERIC_PARAMS, PARAM_SPECS, WAVEFORMS


class TestGuiStaticContract(unittest.TestCase):
    def test_gui_exposes_all_config_parameters(self) -> None:
        config_fields = set(TributaryConfig.__dataclass_fields__.keys())
        self.assertEqual(config_fields, set(PARAM_SPECS.keys()))

    def test_lfo_parameter_list_is_numeric_only(self) -> None:
        self.assertIn("channel_num_snakes", NUMERIC_PARAMS)
        self.assertNotIn("top_bottom_feed_left_shift", NUMERIC_PARAMS)
        self.assertTrue({"sin", "square", "saw", "triangle", "random_hold", "noise"}.issubset(set(WAVEFORMS)))


if __name__ == "__main__":
    unittest.main()
