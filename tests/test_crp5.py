"""
Automated unit tests for CRP-5 / ASA CX-3 flight computer calculations.
"""

from app import (
    execute_slide_rule_conversions,
    solve_crp5_wind_triangle,
    solve_point_of_safe_return,
    solve_top_of_descent,
)


def test_wind_triangle():
  res = solve_crp5_wind_triangle(360.0, 400.0, 360.0, 50.0)
  assert res["ground_speed_kts"] == 350.0
  assert res["wca_deg"] == 0.0


def test_top_of_descent():
  res = solve_top_of_descent(370, 5330, 360.0, descent_angle_deg=3.0)
  assert 90.0 < res["tod_distance_exact_nm"] < 105.0


def test_psr_and_etp():
  res = solve_point_of_safe_return(4.0, 400.0, 0.0, 1000.0)
  assert res["psr_distance_nm"] == 800.0
  assert res["etp_distance_nm"] == 500.0


def test_conversions():
  res = execute_slide_rule_conversions(100.0, "NM to Kilometers (km)")
  assert res["converted_value"] == 185.2


if __name__ == "__main__":
  test_wind_triangle()
  test_top_of_descent()
  test_psr_and_etp()
  test_conversions()
  print("All CRP-5 / ASA CX-3 tests passed successfully!")
