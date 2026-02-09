"""Tests for the Activity Logger with hash chain integrity"""
import asyncio
import json
import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from activity_logger import ActivityLogger, ActivityEntry


@pytest.fixture
def temp_log_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestActivityEntry:
    def test_compute_hash(self):
        entry = ActivityEntry(
            timestamp=1000.0,
            action="test",
            details={"key": "value"},
            previous_hash="genesis",
            sequence=0,
        )
        hash1 = entry.compute_hash()
        assert len(hash1) == 64
        assert hash1.isalnum()

    def test_hash_deterministic(self):
        entry = ActivityEntry(
            timestamp=1000.0,
            action="test",
            details={"key": "value"},
            previous_hash="genesis",
            sequence=0,
        )
        assert entry.compute_hash() == entry.compute_hash()

    def test_hash_changes_with_data(self):
        entry1 = ActivityEntry(
            timestamp=1000.0, action="test1", details={},
            previous_hash="genesis", sequence=0,
        )
        entry2 = ActivityEntry(
            timestamp=1000.0, action="test2", details={},
            previous_hash="genesis", sequence=0,
        )
        assert entry1.compute_hash() != entry2.compute_hash()

    def test_to_dict(self):
        entry = ActivityEntry(
            timestamp=1000.0, action="test", details={"x": 1},
            entry_hash="abc", previous_hash="genesis", sequence=0,
        )
        d = entry.to_dict()
        assert d["action"] == "test"
        assert d["entry_hash"] == "abc"
        assert d["sequence"] == 0


class TestActivityLogger:
    @pytest.mark.asyncio
    async def test_log_single_entry(self, temp_log_dir):
        logger = ActivityLogger(log_dir=temp_log_dir, agent_name="test")
        entry = await logger.log_activity("test_action", {"key": "value"})

        assert entry.action == "test_action"
        assert entry.sequence == 0
        assert entry.previous_hash == "genesis"
        assert len(entry.entry_hash) == 64

    @pytest.mark.asyncio
    async def test_hash_chain(self, temp_log_dir):
        logger = ActivityLogger(log_dir=temp_log_dir, agent_name="test")

        e1 = await logger.log_activity("action1", {"step": 1})
        e2 = await logger.log_activity("action2", {"step": 2})
        e3 = await logger.log_activity("action3", {"step": 3})

        assert e1.previous_hash == "genesis"
        assert e2.previous_hash == e1.entry_hash
        assert e3.previous_hash == e2.entry_hash

    @pytest.mark.asyncio
    async def test_verify_integrity(self, temp_log_dir):
        logger = ActivityLogger(log_dir=temp_log_dir, agent_name="test")

        await logger.log_activity("a1", {"x": 1})
        await logger.log_activity("a2", {"x": 2})
        await logger.log_activity("a3", {"x": 3})

        is_valid, count = await logger.verify_integrity()
        assert is_valid is True
        assert count == 3

    @pytest.mark.asyncio
    async def test_detect_tampering(self, temp_log_dir):
        logger = ActivityLogger(log_dir=temp_log_dir, agent_name="test")

        await logger.log_activity("a1", {"x": 1})
        await logger.log_activity("a2", {"x": 2})

        # Tamper with the log file
        log_file = os.path.join(temp_log_dir, "test_activity.jsonl")
        with open(log_file, "r") as f:
            lines = f.readlines()

        # Modify the first entry
        entry = json.loads(lines[0])
        entry["details"]["x"] = 999  # Tamper!
        lines[0] = json.dumps(entry) + "\n"

        with open(log_file, "w") as f:
            f.writelines(lines)

        # Re-create logger to re-read
        logger2 = ActivityLogger(log_dir=temp_log_dir, agent_name="test")
        is_valid, count = await logger2.verify_integrity()
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_summary(self, temp_log_dir):
        logger = ActivityLogger(log_dir=temp_log_dir, agent_name="test")

        await logger.log_activity("analysis", {"risk": "high"})
        await logger.log_activity("rebalance", {"amount": 100})
        await logger.log_activity("analysis", {"risk": "low"})

        summary = await logger.get_summary()
        assert summary["total_entries"] == 3
        assert summary["actions"]["analysis"] == 2
        assert summary["actions"]["rebalance"] == 1
        assert summary["integrity_valid"] is True

    @pytest.mark.asyncio
    async def test_persistence(self, temp_log_dir):
        # Write entries
        logger1 = ActivityLogger(log_dir=temp_log_dir, agent_name="test")
        await logger1.log_activity("a1", {})
        await logger1.log_activity("a2", {})
        last_hash = logger1.last_hash

        # New logger should continue chain
        logger2 = ActivityLogger(log_dir=temp_log_dir, agent_name="test")
        assert logger2.sequence == 2
        assert logger2.last_hash == last_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
