# Art Processor - Changelog

## v6 - File Organization & Upload Tracking (2025-02-08)

### Added
- **User Title Choice**: Ask if user has their own title before generating AI titles
  - If YES: User enters title directly
  - If NO: Generate 5 AI titles for selection
- **Automatic File Organization**: After processing, paintings automatically move to collection folders
  - Reads collection from metadata
  - Sanitizes folder names (lowercase, spaces→dashes)
  - Creates folders if needed
  - Moves both big and Instagram versions
  - Updates metadata with new file paths
- **Upload Status Tracking**: New `upload_status.json` system
  - Tracks which paintings have been processed
  - Tracks upload status per platform (FASO, social media)
  - Lists pending uploads per platform
- **Social Media Platform Management**: Admin mode option to add platforms
  - Add Instagram, TikTok, Mastodon, Bluesky, etc.
  - Unlimited expandable platforms
  - All paintings automatically get new platform added with status: false

### Changed
- **main.py**: Added post-processing organization and upload tracking
- **src/cli_interface.py**: Added `ask_for_user_title()` method
- **src/admin_mode.py**: Added option 5 for social media platform management

### New Files
- **src/upload_tracker.py**: Upload status management module
- **src/file_organizer.py**: File organization and moving module
- **upload_status.json**: Created in project root (tracks all uploads)

### Workflow Changes
After processing all paintings:
1. Automatically organizes into collection folders
2. Updates all metadata paths
3. Adds to upload tracker with pending status
4. Shows summary of organized files and upload status

---

## v5 - Admin Mode (2025-02-08)

### Added
- **Admin Mode**: Interactive configuration management
  - Edit Anthropic API key
  - Edit file paths
  - Toggle dimension units (cm/in)
  - Add to metadata lists (substrates, mediums, subjects, styles, collections)
  - View current settings
- **Admin Command**: `python main.py admin` or prompt at startup

### Changed
- **main.py**: Added admin mode prompt and command
- **src/cli_interface.py**: Removed category selection code (no longer needed)
- **config/settings.py**: Removed legacy CATEGORIES list

### New Files
- **src/admin_mode.py**: Complete admin interface module

---

## v4 - Instagram Analysis (2025-02-08)

### Changed
- **AI Analysis Source**: Now uses Instagram version instead of big version
  - Solves Claude API 5MB image limit
  - Fallback to big version if Instagram missing
  - Tracks which version was analyzed in metadata

### Modified
- **main.py**: Uses Instagram file for AI analysis
- **src/metadata_manager.py**: Added `analyzed_from` parameter

---

## v3 - Simplified Workflow (2025-02-08)

### Removed
- Category selection menu completely removed
- `--category` and `--all` flags removed
- `list-categories` command removed

### Changed
- Hard-coded to only process `Pictures/my-paintings-big/new-paintings/`
- Simplified command: just `python main.py process`

---

## v2 - Extended Metadata (2025-02-08)

### Added
- **Manual Dimension Input**: Width, height, depth entered separately
- **Configurable Units**: Set DIMENSION_UNIT to "cm" or "in" in settings
- **New Metadata Fields**:
  - Substrate (paper, board, canvas, linen)
  - Medium (acrylic, oil, watercolor, pen and ink, pencil)
  - Subject (abstract, landscape, cityscape, etc.)
  - Style (abstract, figurative, surrealism, etc.)
  - Collection (user-defined collections)
  - Depth (for 3D works)

### Changed
- **Dimension Storage**: Now structured with individual width/height/depth values
- **settings.py**: All metadata options now extensible lists

---

## v1 - Initial Release (2025-02-07)

### Features
- AI-powered title generation (5 options)
- AI-powered gallery descriptions
- Manual metadata entry
- File pairing (big + Instagram versions)
- File renaming based on selected title
- JSON and text metadata output
- Interactive CLI with rich formatting
- Processing from new-paintings folder

### Core Modules
- **main.py**: CLI entry point
- **src/image_analyzer.py**: Claude vision API integration
- **src/file_manager.py**: File operations and renaming
- **src/metadata_manager.py**: Metadata file generation
- **src/cli_interface.py**: Interactive terminal UI
- **config/settings.py**: Configuration management
