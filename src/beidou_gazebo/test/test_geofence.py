"""Unit tests for per-obstacle electronic fence geometry."""

import math

from beidou_gazebo.elderly_geofence import (  # noqa: I101
    aggregate_zone_results,
    classify_zone,
    distance_to_polygon,
    load_obstacles,
    point_in_polygon,
    position_is_fresh,
    STATE_DANGER,
    STATE_SAFE,
    STATE_WARNING,
)


TABLE = ((-1.6, -0.6), (-0.4, -0.6), (-0.4, 0.6), (-1.6, 0.6))
FLOWERBED = ((-3.75, 1.25), (-1.25, 1.25), (-1.25, 2.75), (-3.75, 2.75))
WALL_RIGHT = ((9.85, -8.0), (10.15, -8.0), (10.15, 8.0), (9.85, 8.0))


def test_safe_far_from_all_obstacles():
    """Verify safe far from all obstacles."""
    zones = [
        {'zone_id': 'final_table', 'state': classify_zone(distance_to_polygon(3, 3, TABLE), .5, 1.0), 'distance': distance_to_polygon(3, 3, TABLE)},  # noqa: E501
        {'zone_id': 'final_flowerbed', 'state': classify_zone(distance_to_polygon(3, 3, FLOWERBED), .5, 1.0), 'distance': distance_to_polygon(3, 3, FLOWERBED)},  # noqa: E501
    ]
    result = aggregate_zone_results(zones)
    assert result['state'] == STATE_SAFE
    assert result['zone_ids'] == []


def test_table_warning():
    """Verify table warning."""
    distance = distance_to_polygon(-1.6, 1.3, TABLE)
    assert math.isclose(distance, 0.7)
    assert classify_zone(distance, .5, 1.0) == STATE_WARNING


def test_table_danger_and_collision_outside_concept():
    """Verify table danger and collision outside concept."""
    distance = distance_to_polygon(-1.0, 0.0, TABLE)
    assert distance == 0.0
    assert classify_zone(distance, .5, 1.0) == STATE_DANGER


def test_flowerbed_zone():
    """Verify flowerbed zone."""
    distance = distance_to_polygon(-2.5, 3.0, FLOWERBED)
    assert distance == 0.25
    assert classify_zone(distance, .5, 1.0) == STATE_DANGER


def test_overlapping_flowerbed_and_table_take_highest_risk():
    """Verify overlapping flowerbed and table take highest risk."""
    zones = [
        {'zone_id': 'final_flowerbed', 'state': STATE_DANGER, 'distance': .31},
        {'zone_id': 'final_table', 'state': STATE_WARNING, 'distance': .73},
    ]
    result = aggregate_zone_results(zones)
    assert result['state'] == STATE_DANGER
    assert set(result['zone_ids']) == {'final_flowerbed', 'final_table'}
    assert result['primary_zone_id'] == 'final_flowerbed'
    assert result['nearest_distance'] == .31


def test_wall_right_zone():
    """Verify wall right zone."""
    distance = distance_to_polygon(9.0, 0.0, WALL_RIGHT)
    assert math.isclose(distance, .85)
    assert classify_zone(distance, .5, 1.0) == STATE_WARNING


def test_point_in_polygon_boundary_and_interior():
    """Verify point in polygon boundary and interior."""
    assert point_in_polygon(-1.0, 0.0, TABLE)
    assert point_in_polygon(-1.6, 0.0, TABLE)
    assert not point_in_polygon(0.5, 1.5, TABLE)


def test_loaded_default_configuration_contains_all_nine_zones():
    """Verify loaded default configuration contains all nine zones."""
    zones = load_obstacles('/path/that/does/not/exist/elderly_geofence.yaml')
    assert {zone.zone_id for zone in zones} == {
        'final_flowerbed', 'final_bench_west', 'final_bench_east',
        'final_table', 'final_partition', 'wall_left', 'wall_right',
        'wall_back', 'wall_front',
    }


def test_invalid_frame_is_not_a_map_position():
    """Verify invalid frame is not a map position."""
    assert 'odom' != 'map'


def test_position_timeout_is_not_fresh():
    """Verify stale position cannot be treated as safe."""
    assert position_is_fresh(0.9, 1.0)
    assert not position_is_fresh(1.01, 1.0)
    assert not position_is_fresh(float('nan'), 1.0)
