import unittest

from tributary_geometry import Point2, TributaryConfig, build_tributary_layout, compute_layout_metrics, connect_bezier_rect


class TestBezierHelpers(unittest.TestCase):
    def test_connect_bezier_rect_endpoints_and_horizontal_handles(self):
        p0 = Point2(0.0, 0.0)
        p3 = Point2(10.0, 4.0)
        curve = connect_bezier_rect(p0, p3, 2.0, 3.0, 1.0)
        self.assertEqual(curve.point(0.0), p0)
        self.assertEqual(curve.point(1.0), p3)
        self.assertAlmostEqual(curve.p1.x, 2.0)
        self.assertAlmostEqual(curve.p1.y, 0.0)
        self.assertAlmostEqual(curve.p2.x, 7.0)
        self.assertAlmostEqual(curve.p2.y, 4.0)

    def test_identical_points_rejected(self):
        p = Point2(1.0, 1.0)
        with self.assertRaises(ValueError):
            connect_bezier_rect(p, p, 1.0, 1.0, 1.0)


class TestTributaryLayout(unittest.TestCase):
    def test_layout_counts_follow_recovered_docx_grid(self):
        config = TributaryConfig(channel_num_snakes=5)
        layout = build_tributary_layout(config)
        self.assertEqual(len(layout.circles_by_role("snake")), 6)
        self.assertEqual(len(layout.circles_by_role("ladder")), 5)
        self.assertEqual(len(layout.circles_by_role("feed")), 4)
        self.assertEqual(len(layout.circles_by_role("dump")), 5)
        self.assertEqual(len(layout.branches), 9)

    def test_default_pairing_is_y_aligned_and_symmetric(self):
        config = TributaryConfig(channel_num_snakes=6)
        layout = build_tributary_layout(config)
        self.assertEqual(config.pairing_mode, "y_aligned_physical")
        self.assertTrue(any(branch.branch_type == "feed_to_snake" for branch in layout.branches))
        self.assertTrue(any(branch.branch_type == "dump_to_ladder" for branch in layout.branches))
        metrics = compute_layout_metrics(layout)
        self.assertLess(metrics.symmetry_mean_error, 1e-8)
        self.assertEqual(metrics.symmetry_unpaired_count, 0)

    def test_top_bottom_feed_shift(self):
        config = TributaryConfig(channel_num_snakes=4, feed_diameter=10.0, top_bottom_feed_left_shift=True)
        layout = build_tributary_layout(config)
        feeds = layout.circles_by_role("feed")
        self.assertLess(feeds[0].center.x, feeds[1].center.x)
        self.assertLess(feeds[-1].center.x, feeds[1].center.x)

    def test_invalid_config(self):
        config = TributaryConfig(channel_num_snakes=1)
        with self.assertRaises(ValueError):
            build_tributary_layout(config)


if __name__ == "__main__":
    unittest.main()
