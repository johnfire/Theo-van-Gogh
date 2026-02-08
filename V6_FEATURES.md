# v6 Feature Summary - File Organization & Upload Tracking

## What's New

### 1. User Can Provide Own Title
- At start: "Do you have a name for this painting? [y/N]"
- If YES: User enters title directly
- If NO: AI generates 5 options to choose from

### 2. Automatic File Organization
After processing completes, paintings are automatically moved:

**Process:**
1. Reads collection from metadata (e.g., "Oil Paintings")
2. Sanitizes to folder name: lowercase + spaces→dashes ("oil-paintings")
3. Creates folder if needed: `/my-paintings-big/oil-paintings/`
4. Moves file from `/new-paintings/` to collection folder
5. Updates metadata with new file path
6. Repeats for Instagram version

**Example:**
```
Before:
/my-paintings-big/new-paintings/bavarian_twilight.jpg
Collection in metadata: "Oil Paintings"

After:
/my-paintings-big/oil-paintings/bavarian_twilight.jpg
/my-paintings-instagram/oil-paintings/bavarian_twilight.jpg
```

### 3. Upload Status Tracking
Creates `upload_status.json` tracking:
- Which paintings have been processed
- Which platforms they've been uploaded to
- Pending uploads per platform

**Structure:**
```json
{
  "paintings": {
    "bavarian_twilight": {
      "metadata_path": "...",
      "processed_date": "2025-02-07...",
      "uploads": {
        "FASO": false,
        "Instagram": false,
        "Mastodon": false
      }
    }
  },
  "platforms": ["FASO", "Instagram", "Mastodon", ...],
  "last_updated": "..."
}
```

### 4. Social Media Platform Management
In Admin Mode (option 5):
- View current platforms
- Add new platforms (Instagram, TikTok, Mastodon, etc.)
- Platforms are automatically added to all paintings with status: false

**Default platforms:** FASO
**Expandable:** User can add unlimited platforms

### 5. Post-Processing Summary
After processing paintings, shows:
- How many paintings organized
- Which collection folders they went to
- Upload status per platform
- Any errors during organization

## New Files

1. **src/upload_tracker.py** - Manages upload status tracking
2. **src/file_organizer.py** - Moves files to collection folders
3. **upload_status.json** - Created in project root (tracks uploads)

## Updated Files

1. **main.py** - Added organization step and upload tracking
2. **src/cli_interface.py** - Added ask_for_user_title() method
3. **src/admin_mode.py** - Added social media platform management

## Workflow Changes

### Complete Processing Flow:
1. User runs: `python main.py process`
2. For each painting:
   - Ask if user has title (YES→enter, NO→generate 5)
   - Enter all metadata
   - Generate description
   - Rename files
   - Save metadata
3. **NEW:** After all paintings processed:
   - Move to collection folders
   - Update metadata paths
   - Add to upload tracker
   - Show summary

### Future Phases
Upload tracker is ready for Phase 2:
- FASO upload module (mark as uploaded to FASO)
- Social media upload modules (mark per platform)
- Each module will call: `tracker.mark_uploaded(filename, "Instagram")`

## Usage

### Normal Processing:
```bash
python main.py process
# ... process paintings ...
# Automatically organizes and tracks
```

### Add Social Media Platform:
```bash
python main.py admin
# Select option 5: Manage Social Media Platforms
# Add: "Instagram", "TikTok", "Bluesky", etc.
```

### View Pending Uploads:
The upload tracker tracks everything. Phase 2 will add commands like:
```bash
python main.py uploads pending
python main.py upload-to-faso
python main.py post-to-instagram
```

## File Locations After Organization

```
Pictures/
├── my-paintings-big/
│   ├── new-paintings/          (empty after processing)
│   ├── oil-paintings/          (organized by collection)
│   ├── watercolor-paintings/
│   ├── abstracts/
│   └── ...
├── my-paintings-instagram/
│   ├── new-paintings/          (empty after processing)
│   ├── oil-paintings/
│   ├── watercolor-paintings/
│   └── ...
└── processed-metadata/
    ├── new-paintings/          (empty after processing)
    ├── oil-paintings/          (metadata organized too)
    ├── watercolor-paintings/
    └── ...
```

## Ready for Phase 2: FASO Upload

Everything is in place for uploading:
- Files organized by collection
- Metadata has all info needed
- Upload tracker knows what's pending
- Can mark items as uploaded

Next: Build FASO upload module that:
1. Gets pending FASO uploads from tracker
2. Uploads to FASO API
3. Marks as uploaded in tracker
