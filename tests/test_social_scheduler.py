"""Tests for social media scheduler."""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from src.social.scheduler import Scheduler, _get_image_path, _update_social_media_tracking


@pytest.fixture
def schedule_file(tmp_path):
    return tmp_path / "schedule.json"


@pytest.fixture
def scheduler(schedule_file):
    return Scheduler(schedule_file)


class TestScheduler:
    def test_empty_schedule(self, scheduler):
        assert scheduler.get_pending() == []
        assert scheduler.get_upcoming() == []
        assert scheduler.get_history() == []

    def test_add_post(self, scheduler):
        post_id = scheduler.add_post(
            content_id="test_painting",
            metadata_path="/path/to/meta.json",
            platform="mastodon",
            scheduled_time="2030-01-01T10:00:00",
        )
        assert post_id
        assert len(scheduler.data["scheduled_posts"]) == 1

    def test_add_post_persists(self, scheduler, schedule_file):
        scheduler.add_post(
            content_id="test",
            metadata_path="/path/meta.json",
            platform="mastodon",
            scheduled_time="2030-01-01T10:00:00",
        )
        # Reload from file
        new_scheduler = Scheduler(schedule_file)
        assert len(new_scheduler.data["scheduled_posts"]) == 1

    def test_get_pending_past_time(self, scheduler):
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        scheduler.add_post("test", "/path", "mastodon", past)
        assert len(scheduler.get_pending()) == 1

    def test_get_upcoming_future_time(self, scheduler):
        future = (datetime.now() + timedelta(days=1)).isoformat()
        scheduler.add_post("test", "/path", "mastodon", future)
        assert len(scheduler.get_upcoming()) == 1
        assert len(scheduler.get_pending()) == 0

    def test_cancel_post(self, scheduler):
        future = (datetime.now() + timedelta(days=1)).isoformat()
        post_id = scheduler.add_post("test", "/path", "mastodon", future)
        assert scheduler.cancel_post(post_id) is True
        assert len(scheduler.get_upcoming()) == 0

    def test_cancel_nonexistent_post(self, scheduler):
        assert scheduler.cancel_post("nonexistent") is False

    def test_mark_posted(self, scheduler):
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        post_id = scheduler.add_post("test", "/path", "mastodon", past)
        scheduler.mark_posted(post_id, "https://example.com/post/123")
        history = scheduler.get_history()
        assert len(history) == 1
        assert history[0]["status"] == "posted"
        assert history[0]["post_url"] == "https://example.com/post/123"

    def test_mark_failed(self, scheduler):
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        post_id = scheduler.add_post("test", "/path", "mastodon", past)
        scheduler.mark_failed(post_id, "Connection timeout")
        history = scheduler.get_history()
        assert len(history) == 1
        assert history[0]["status"] == "failed"
        assert history[0]["error"] == "Connection timeout"

    def test_history_limit(self, scheduler):
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        for i in range(10):
            post_id = scheduler.add_post(f"test_{i}", "/path", "mastodon", past)
            scheduler.mark_posted(post_id)
        assert len(scheduler.get_history(limit=5)) == 5


class TestGetImagePath:
    def test_instagram_string(self, tmp_path):
        img = tmp_path / "test.jpg"
        img.touch()
        metadata = {"files": {"instagram": str(img), "big": None}}
        assert _get_image_path(metadata) == img

    def test_instagram_list(self, tmp_path):
        img = tmp_path / "test.jpg"
        img.touch()
        metadata = {"files": {"instagram": [str(img)], "big": None}}
        assert _get_image_path(metadata) == img

    def test_fallback_to_big(self, tmp_path):
        # Big files are no longer used for social media (5MB API limit)
        img = tmp_path / "test.jpg"
        img.touch()
        metadata = {"files": {"instagram": None, "big": str(img)}}
        assert _get_image_path(metadata) is None

    def test_big_as_list(self, tmp_path):
        # Big files are no longer used for social media (5MB API limit)
        img = tmp_path / "test.jpg"
        img.touch()
        metadata = {"files": {"instagram": None, "big": [str(img)]}}
        assert _get_image_path(metadata) is None

    def test_no_files(self):
        metadata = {"files": {"instagram": None, "big": None}}
        assert _get_image_path(metadata) is None

    def test_missing_files_key(self):
        assert _get_image_path({}) is None


class TestUpdateSocialMediaTracking:
    def test_updates_existing_metadata(self, tmp_path):
        meta_file = tmp_path / "test.json"
        metadata = {
            "filename_base": "test",
            "social_media": {
                "mastodon": {"last_posted": None, "post_url": None, "post_count": 0}
            }
        }
        with open(meta_file, "w") as f:
            json.dump(metadata, f)

        _update_social_media_tracking(meta_file, metadata, "mastodon", "https://example.com/1")

        with open(meta_file, "r") as f:
            updated = json.load(f)

        assert updated["social_media"]["mastodon"]["post_count"] == 1
        assert updated["social_media"]["mastodon"]["post_url"] == "https://example.com/1"
        assert updated["social_media"]["mastodon"]["last_posted"] is not None

    def test_increments_count(self, tmp_path):
        meta_file = tmp_path / "test.json"
        metadata = {
            "filename_base": "test",
            "social_media": {
                "mastodon": {"last_posted": "2026-01-01", "post_url": "old", "post_count": 3}
            }
        }
        with open(meta_file, "w") as f:
            json.dump(metadata, f)

        _update_social_media_tracking(meta_file, metadata, "mastodon", "https://new")

        with open(meta_file, "r") as f:
            updated = json.load(f)

        assert updated["social_media"]["mastodon"]["post_count"] == 4

    def test_creates_social_media_if_missing(self, tmp_path):
        meta_file = tmp_path / "test.json"
        metadata = {"filename_base": "test"}
        with open(meta_file, "w") as f:
            json.dump(metadata, f)

        _update_social_media_tracking(meta_file, metadata, "mastodon", "https://url")

        with open(meta_file, "r") as f:
            updated = json.load(f)

        assert "social_media" in updated
        assert updated["social_media"]["mastodon"]["post_count"] == 1
