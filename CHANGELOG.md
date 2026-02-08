# Art Processor v3 - Changelog

## Changes from v2

### Manual Dimension Input with Individual Components
- **Changed**: Dimensions are now entered as separate width, height, and depth values
- **Configurable Units**: Set DIMENSION_UNIT in config/settings.py to "cm" or "in"
- **Workflow**:
  1. Enter width (e.g., 60)
  2. Enter height (e.g., 80)
  3. Enter depth (e.g., 2, or 0 for flat works)
- **Stored Format**: JSON contains both individual values and formatted string
  ```json
  "dimensions": {
    "width": 60.0,
    "height": 80.0,
    "depth": 2.0,
    "unit": "cm",
    "formatted": "60cm x 80cm x 2cm"
  }
  ```

### All Previous v2 Features Retained
- Single folder processing (new-paintings)
- Separate substrate and medium fields
- Subject, style, and collection metadata
- All extensible configuration lists

## Complete Workflow

1. Place paintings in `Pictures/my-paintings-big/new-paintings/`
2. Run: `python main.py process`
3. For each painting:
   - Generate & select title (5 options)
   - **Enter width** (number)
   - **Enter height** (number)
   - **Enter depth** (number, 0 for flat)
   - Select substrate (paper, board, canvas, linen)
   - Select medium (acrylic, oil, watercolor, pen and ink, pencil)
   - Select subject
   - Select style
   - Select collection
   - Enter price (EUR)
   - Confirm/edit creation date
4. System generates description, renames files, saves metadata

## Changing Units

Edit `config/settings.py`:
```python
# Set to "cm" for centimeters or "in" for inches
DIMENSION_UNIT = "cm"  # Change to "in" for inches
```

The unit is saved with each painting's metadata, so you can mix units across different paintings if needed.

## Output Example

```json
{
  "title": {
    "selected": "Bavarian Twilight"
  },
  "dimensions": {
    "width": 60.0,
    "height": 80.0,
    "depth": 2.0,
    "unit": "cm",
    "formatted": "60cm x 80cm x 2cm"
  },
  "substrate": "canvas",
  "medium": "oil",
  "subject": "landscape",
  "style": "impressionism",
  "collection": "oils"
}
```

## Usage

```bash
# Process all paintings in new-paintings folder
python main.py process

# Verify configuration
python main.py verify-config
```
