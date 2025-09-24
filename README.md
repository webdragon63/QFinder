# QFinder (The Query Finder)

QFinder is a simple Python GUI tool for crawling websites and extracting URLs with query parameters and forms. It helps penetration testers and bug bounty hunters quickly enumerate interesting endpoints for further analysis.

## Features

- **Website Crawler**: Recursively finds URLs and forms on a given website (up to depth 2).
- **Query Detection**: Highlights URLs containing query parameters.
- **Form Extraction**: Shows detected forms and their input fields.
- **Copy to Clipboard**: Double-click a found query to copy it.
- **Adjustable Crawl Speed**: Choose Fast, Normal, or Slow.
- **Modern Dark UI**: Fast, minimal interface using PyQt5.

## Usage


2. **Run QFinder**:

   ```bash
   source qfinder.sh
   ```

3. **Enter a website URL** (e.g., `https://example.com`) and click **Start**.
4. **Double-click a found query** to copy it to your clipboard.

## Screenshot



## Notes

- **Depth**: Only crawls up to 2 levels deep for speed and safety.
- **Speed**: Adjust crawl speed via the dropdown for slower sites or stealth.

---
**Author:** [WebDragon63](https://github.com/webdragon63)\
**YouTube Channel** [INDIAN CYBER ARMY](https://youtube.com/@webdragon63)
