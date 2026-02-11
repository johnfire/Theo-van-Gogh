"""Cara platform integration (not yet implemented)."""

from pathlib import Path
from src.social.base import SocialPlatform, PostResult


class CaraPlatform(SocialPlatform):
    name = "cara"
    display_name = "Cara"
    supports_video = False
    supports_images = True
    max_text_length = 2000
    _is_stub = True

    def verify_credentials(self) -> bool:
        raise NotImplementedError("Cara integration not yet implemented")

    def post_image(self, image_path: Path, text: str, alt_text: str = "") -> PostResult:
        raise NotImplementedError("Cara integration not yet implemented")

    def post_video(self, video_path: Path, text: str) -> PostResult:
        raise NotImplementedError("Cara integration not yet implemented")

    def is_configured(self) -> bool:
        return False
