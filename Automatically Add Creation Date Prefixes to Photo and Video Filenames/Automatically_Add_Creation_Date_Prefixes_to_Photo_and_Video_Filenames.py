#!/usr/bin/env python3
"""
Media File Date Renamer
Adds creation date to the beginning of media filenames in yyyy-mm-dd format
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import time

def get_file_creation_date(file_path):
    """
    Get the creation date of a file.
    Returns the earlier of creation time or modification time.
    """
    try:
        # Get file stats
        stat = os.stat(file_path)
        
        # Use creation time if available (Windows), otherwise use modification time
        if hasattr(stat, 'st_birthtime'):  # macOS
            creation_time = stat.st_birthtime
        elif hasattr(stat, 'st_ctime'):    # Windows creation time
            creation_time = stat.st_ctime
        else:
            creation_time = stat.st_mtime   # Fallback to modification time
        
        # Also get modification time
        modification_time = stat.st_mtime
        
        # Use the earlier of the two dates
        earliest_time = min(creation_time, modification_time)
        
        return datetime.fromtimestamp(earliest_time)
    
    except Exception as e:
        print(f"Error getting date for {file_path}: {e}")
        return None

def is_media_file(file_path):
    """
    Check if the file is a media file (photo or video).
    """
    media_extensions = {
        # Photo formats
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
        '.webp', '.svg', '.raw', '.cr2', '.nef', '.arw', '.dng',
        # Video formats
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', 
        '.m4v', '.3gp', '.mpg', '.mpeg', '.m2v', '.mts'
    }
    
    return Path(file_path).suffix.lower() in media_extensions

def already_has_date_prefix(filename):
    """
    Check if filename already starts with yyyy-mm-dd format.
    """
    import re
    date_prefix_pattern = r'^\d{4}-\d{2}-\d{2}\s+'
    return bool(re.match(date_prefix_pattern, filename))

def rename_media_files(directory_path, dry_run=True):
    """
    Rename media files by adding creation date prefix.
    
    Args:
        directory_path: Path to the directory containing files
        dry_run: If True, only show what would be renamed without actually renaming
    """
    
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        return
    
    # Get all files in directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    if not files:
        print("No files found in directory.")
        return
    
    # Filter for media files
    media_files = [f for f in files if is_media_file(f)]
    
    if not media_files:
        print("No media files found in directory.")
        return
    
    print(f"Found {len(media_files)} media files.")
    print(f"{'DRY RUN - ' if dry_run else ''}Processing files...\n")
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    for filename in media_files:
        file_path = os.path.join(directory_path, filename)
        
        # Skip if already has date prefix
        if already_has_date_prefix(filename):
            print(f"SKIP: {filename} (already has date prefix)")
            skipped_count += 1
            continue
        
        # Get creation date
        creation_date = get_file_creation_date(file_path)
        
        if creation_date is None:
            print(f"ERROR: Could not get date for {filename}")
            error_count += 1
            continue
        
        # Format date as yyyy-mm-dd
        date_str = creation_date.strftime('%Y-%m-%d')
        
        # Create new filename
        new_filename = f"{date_str} {filename}"
        new_file_path = os.path.join(directory_path, new_filename)
        
        # Check if new filename already exists
        if os.path.exists(new_file_path):
            print(f"ERROR: {new_filename} already exists, skipping {filename}")
            error_count += 1
            continue
        
        if dry_run:
            print(f"WOULD RENAME: {filename} → {new_filename}")
        else:
            try:
                os.rename(file_path, new_file_path)
                print(f"RENAMED: {filename} → {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"ERROR: Failed to rename {filename}: {e}")
                error_count += 1
    
    # Summary
    print(f"\n{'DRY RUN ' if dry_run else ''}SUMMARY:")
    print(f"Total media files: {len(media_files)}")
    if not dry_run:
        print(f"Successfully renamed: {renamed_count}")
    print(f"Skipped (already has date): {skipped_count}")
    print(f"Errors: {error_count}")

def main():
    """
    Main function to handle user interaction.
    """
    print("Media File Date Renamer")
    print("=" * 50)
    print("This tool adds creation dates to media filenames in yyyy-mm-dd format")
    print("Example: 'Clockwork.mp4' → '2023-03-15 Clockwork.mp4'\n")
    
    # Get directory from user
    while True:
        directory = input("Enter the directory path containing your media files: ").strip()
        
        # Remove quotes if user included them
        directory = directory.strip('"\'')
        
        if os.path.isdir(directory):
            break
        else:
            print(f"Directory '{directory}' does not exist. Please try again.\n")
    
    print(f"\nDirectory: {directory}")
    
    # First, do a dry run to show what would happen
    print("\n" + "="*50)
    print("PREVIEW (showing what would be renamed):")
    print("="*50)
    rename_media_files(directory, dry_run=True)
    
    # Ask user if they want to proceed
    print("\n" + "="*50)
    while True:
        proceed = input("Do you want to proceed with renaming? (yes/no): ").strip().lower()
        if proceed in ['yes', 'y']:
            print("\nProceeding with actual renaming...")
            rename_media_files(directory, dry_run=False)
            break
        elif proceed in ['no', 'n']:
            print("Operation cancelled.")
            break
        else:
            print("Please enter 'yes' or 'no'.")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
