import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set thresholds before importing agent (it reads env at import time)
os.environ["CPU_TEMP_THRESHOLD"] = "80"
os.environ["MEM_PRESSURE_THRESHOLD"] = "90"
os.environ["TCP_RETRANS_THRESHOLD"] = "50000"

from agent import decide


class TestDecideAllWithinThresholds:
    def test_normal_values(self):
        telemetry = {"cpu_temp_c": 45, "mem_pressure_pct": 60, "tcp_retrans_segs": 1000}
        assert decide(telemetry) == []

    def test_at_threshold_boundary(self):
        """Values exactly at threshold should NOT trigger (uses >=)."""
        telemetry = {"cpu_temp_c": 80, "mem_pressure_pct": 90, "tcp_retrans_segs": 50000}
        assert len(decide(telemetry)) == 3

    def test_just_below_threshold(self):
        telemetry = {"cpu_temp_c": 79, "mem_pressure_pct": 89, "tcp_retrans_segs": 49999}
        assert decide(telemetry) == []


class TestDecideCpuThreshold:
    def test_cpu_exceeds(self):
        telemetry = {"cpu_temp_c": 85, "mem_pressure_pct": 50, "tcp_retrans_segs": 100}
        actions = decide(telemetry)
        assert len(actions) == 1
        assert actions[0]["tool"] == "restart_service"
        assert "cpu_temp" in actions[0]["reason"]

    def test_cpu_unavailable(self):
        """Value of -1 means unavailable — should NOT trigger."""
        telemetry = {"cpu_temp_c": -1, "mem_pressure_pct": 50, "tcp_retrans_segs": 100}
        assert decide(telemetry) == []


class TestDecideMemThreshold:
    def test_mem_exceeds(self):
        telemetry = {"cpu_temp_c": 40, "mem_pressure_pct": 95, "tcp_retrans_segs": 100}
        actions = decide(telemetry)
        assert len(actions) == 1
        assert actions[0]["tool"] == "restart_service"
        assert "mem_pressure" in actions[0]["reason"]

    def test_mem_unavailable(self):
        telemetry = {"cpu_temp_c": 40, "mem_pressure_pct": -1, "tcp_retrans_segs": 100}
        assert decide(telemetry) == []


class TestDecideTcpThreshold:
    def test_tcp_exceeds(self):
        telemetry = {"cpu_temp_c": 40, "mem_pressure_pct": 50, "tcp_retrans_segs": 60000}
        actions = decide(telemetry)
        assert len(actions) == 1
        assert actions[0]["tool"] == "check_health"
        assert "tcp_retrans" in actions[0]["reason"]

    def test_tcp_unavailable(self):
        telemetry = {"cpu_temp_c": 40, "mem_pressure_pct": 50, "tcp_retrans_segs": -1}
        assert decide(telemetry) == []


class TestDecideMultipleBreaches:
    def test_all_exceed(self):
        telemetry = {"cpu_temp_c": 95, "mem_pressure_pct": 98, "tcp_retrans_segs": 100000}
        actions = decide(telemetry)
        assert len(actions) == 3

    def test_two_exceed(self):
        telemetry = {"cpu_temp_c": 85, "mem_pressure_pct": 95, "tcp_retrans_segs": 100}
        actions = decide(telemetry)
        assert len(actions) == 2


class TestDecideMissingKeys:
    def test_empty_telemetry(self):
        assert decide({}) == []

    def test_partial_telemetry(self):
        telemetry = {"cpu_temp_c": 85}
        actions = decide(telemetry)
        assert len(actions) == 1
