"""Bluesky platform integration (not yet implemented)."""

from pathlib import Path
from src.social.base import SocialPlatform, PostResult


class BlueskyPlatform(SocialPlatform):
    name = "bluesky"
    display_name = "Bluesky"
    supports_video = True
    supports_images = True
    max_text_length = 300
    _is_stub = True

    def verify_credentials(self) -> bool:
        raise NotImplementedError("Bluesky integration not yet implemented")

    def post_image(self, image_path: Path, text: str, alt_text: str = "") -> PostResult:
        raise NotImplementedError("Bluesky integration not yet implemented")

    def post_video(self, video_path: Path, text: str) -> PostResult:
        raise NotImplementedError("Bluesky integration not yet implemented")

    def is_configured(self) -> bool:
        return False
