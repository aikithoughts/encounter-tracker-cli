"""Data persistence layer for the D&D Encounter Tracker."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

from ..core.models import Encounter, Combatant
from ..core.exceptions import FileFormatError, ValidationError


class DataManager:
    """Manages data persistence for encounters using JSON files."""
    
    def __init__(self, data_directory: str = "encounters"):
        """Initialize the DataManager.
        
        Args:
            data_directory: Directory to store encounter files
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
    
    def save_to_file(self, encounter: Encounter, filename: str) -> None:
        """Save an encounter to a JSON file.
        
        Args:
            encounter: Encounter to save
            filename: Name of the file to save to
            
        Raises:
            FileFormatError: If file operations fail
            ValidationError: If encounter data is invalid
        """
        if not filename:
            raise ValidationError(
                field="filename",
                value=filename,
                reason="cannot be empty"
            )
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.data_directory / filename
        
        try:
            # Create backup if file exists
            if filepath.exists():
                backup_path = filepath.with_suffix('.json.backup')
                shutil.copy2(filepath, backup_path)
            
            # Convert encounter to dictionary
            encounter_data = self._encounter_to_dict(encounter)
            
            # Write to temporary file first, then rename for atomic operation
            temp_filepath = filepath.with_suffix('.json.tmp')
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(encounter_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_filepath.replace(filepath)
            
        except (OSError, IOError) as e:
            raise FileFormatError(
                filename=filename,
                operation="save",
                reason=f"File system error: {e}"
            )
        except Exception as e:
            raise FileFormatError(
                filename=filename,
                operation="save",
                reason=f"Unexpected error: {e}"
            )
    
    def load_from_file(self, filename: str) -> Encounter:
        """Load an encounter from a JSON file.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded encounter
            
        Raises:
            FileFormatError: If file doesn't exist or is corrupted
            ValidationError: If encounter data is invalid
        """
        if not filename:
            raise ValidationError(
                field="filename",
                value=filename,
                reason="cannot be empty"
            )
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.data_directory / filename
        
        if not filepath.exists():
            raise FileFormatError(
                filename=filename,
                operation="load",
                reason="File not found"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate file format
            self._validate_file_format(data, filename)
            
            # Convert dictionary to encounter
            encounter = self._dict_to_encounter(data)
            
            return encounter
            
        except json.JSONDecodeError as e:
            raise FileFormatError(
                filename=filename,
                operation="load",
                reason=f"Invalid JSON format: {e}"
            )
        except (OSError, IOError) as e:
            raise FileFormatError(
                filename=filename,
                operation="load",
                reason=f"File system error: {e}"
            )
        except Exception as e:
            if isinstance(e, (FileFormatError, ValidationError)):
                raise
            raise FileFormatError(
                filename=filename,
                operation="load",
                reason=f"Unexpected error: {e}"
            )
    
    def validate_file_format(self, filename: str) -> bool:
        """Validate that a file has the correct encounter format.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            True if file format is valid
            
        Raises:
            FileFormatError: If file format is invalid
        """
        try:
            self.load_from_file(filename)
            return True
        except (FileFormatError, ValidationError):
            return False
    
    def get_available_encounters(self) -> List[str]:
        """Get list of available encounter files.
        
        Returns:
            List of encounter filenames (without .json extension)
        """
        try:
            json_files = list(self.data_directory.glob("*.json"))
            # Filter out backup and temporary files
            encounter_files = [
                f.stem for f in json_files 
                if not f.name.endswith(('.backup', '.tmp'))
            ]
            return sorted(encounter_files)
        except Exception:
            return []
    
    def get_encounter_metadata(self, filename: str) -> Dict[str, Any]:
        """Get metadata for an encounter file.
        
        Args:
            filename: Name of the file to get metadata for
            
        Returns:
            Dictionary with file metadata including creation date, last modified, size
            
        Raises:
            FileFormatError: If file doesn't exist or can't be read
        """
        if not filename:
            raise ValidationError(
                field="filename",
                value=filename,
                reason="cannot be empty"
            )
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.data_directory / filename
        
        if not filepath.exists():
            raise FileFormatError(
                filename=filename,
                operation="get metadata",
                reason="File not found"
            )
        
        try:
            stat = filepath.stat()
            
            # Try to get metadata from file content
            file_metadata = {}
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_metadata = data.get("metadata", {})
            except (json.JSONDecodeError, KeyError):
                # If we can't read the metadata from file, that's okay
                pass
            
            return {
                "filename": filepath.stem,
                "full_path": str(filepath),
                "size_bytes": stat.st_size,
                "created": file_metadata.get("created", datetime.fromtimestamp(stat.st_ctime).isoformat()),
                "last_modified": file_metadata.get("last_modified", datetime.fromtimestamp(stat.st_mtime).isoformat()),
                "version": file_metadata.get("version", "unknown"),
                "file_system_created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "file_system_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except (OSError, IOError) as e:
            raise FileFormatError(
                filename=filename,
                operation="get metadata",
                reason=f"File system error: {e}"
            )
    
    def list_encounters_with_metadata(self) -> List[Dict[str, Any]]:
        """Get list of available encounters with their metadata.
        
        Returns:
            List of dictionaries containing encounter info and metadata
        """
        encounters = []
        
        for filename in self.get_available_encounters():
            try:
                metadata = self.get_encounter_metadata(filename)
                
                # Try to get encounter name from file content
                encounter_name = filename  # Default to filename
                try:
                    encounter = self.load_from_file(filename)
                    encounter_name = encounter.name
                except Exception:
                    # If we can't load the encounter, use filename
                    pass
                
                encounters.append({
                    "filename": filename,
                    "encounter_name": encounter_name,
                    "metadata": metadata
                })
                
            except Exception:
                # If we can't get metadata for a file, skip it
                continue
        
        # Sort by last modified date (most recent first)
        encounters.sort(key=lambda x: x["metadata"]["last_modified"], reverse=True)
        
        return encounters
    
    def backup_encounter(self, filename: str) -> str:
        """Create a backup of an encounter file.
        
        Args:
            filename: Name of the file to backup
            
        Returns:
            Path to the backup file
            
        Raises:
            FileFormatError: If file doesn't exist or backup fails
        """
        if not filename:
            raise ValidationError(
                field="filename",
                value=filename,
                reason="cannot be empty"
            )
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.data_directory / filename
        
        if not filepath.exists():
            raise FileFormatError(
                filename=filename,
                operation="backup",
                reason="File not found"
            )
        
        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{filepath.stem}_{timestamp}.backup"
            backup_path = self.data_directory / backup_filename
            
            shutil.copy2(filepath, backup_path)
            
            return str(backup_path)
            
        except (OSError, IOError) as e:
            raise FileFormatError(
                filename=filename,
                operation="backup",
                reason=f"File system error: {e}"
            )
    
    def cleanup_old_backups(self, max_backups: int = 5) -> List[str]:
        """Clean up old backup files, keeping only the most recent ones.
        
        Args:
            max_backups: Maximum number of backup files to keep per encounter
            
        Returns:
            List of deleted backup file paths
        """
        deleted_files = []
        
        try:
            # Group backup files by their base encounter name
            backup_files = list(self.data_directory.glob("*.backup"))
            backup_groups = {}
            
            for backup_file in backup_files:
                # Extract base name (everything before the timestamp)
                name_parts = backup_file.stem.split('_')
                if len(name_parts) >= 3:  # name_timestamp.backup
                    base_name = '_'.join(name_parts[:-2])  # Remove timestamp parts
                    if base_name not in backup_groups:
                        backup_groups[base_name] = []
                    backup_groups[base_name].append(backup_file)
            
            # For each group, keep only the most recent backups
            for base_name, backups in backup_groups.items():
                if len(backups) > max_backups:
                    # Sort by modification time (newest first)
                    backups.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    
                    # Delete old backups
                    for old_backup in backups[max_backups:]:
                        try:
                            old_backup.unlink()
                            deleted_files.append(str(old_backup))
                        except (OSError, IOError):
                            # If we can't delete a file, continue with others
                            continue
            
            return deleted_files
            
        except Exception:
            # If cleanup fails, return empty list (non-critical operation)
            return []
    
    def delete_encounter(self, filename: str) -> None:
        """Delete an encounter file.
        
        Args:
            filename: Name of the file to delete
            
        Raises:
            FileFormatError: If file doesn't exist or deletion fails
        """
        if not filename:
            raise ValidationError(
                field="filename",
                value=filename,
                reason="cannot be empty"
            )
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.data_directory / filename
        
        if not filepath.exists():
            raise FileFormatError(
                filename=filename,
                operation="delete",
                reason="File not found"
            )
        
        try:
            filepath.unlink()
        except (OSError, IOError) as e:
            raise FileFormatError(
                filename=filename,
                operation="delete",
                reason=f"File system error: {e}"
            )
    
    def encounter_exists(self, filename: str) -> bool:
        """Check if an encounter file exists.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if file exists
        """
        if not filename:
            return False
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.data_directory / filename
        return filepath.exists()
    
    def _encounter_to_dict(self, encounter: Encounter) -> Dict[str, Any]:
        """Convert an Encounter object to a dictionary.
        
        Args:
            encounter: Encounter to convert
            
        Returns:
            Dictionary representation of the encounter
        """
        now = datetime.now().isoformat()
        
        # Check if encounter has existing metadata (for updates)
        created_date = now
        if hasattr(encounter, '_metadata') and encounter._metadata:
            created_date = encounter._metadata.get("created", now)
        
        return {
            "name": encounter.name,
            "combatants": [
                {
                    "name": c.name,
                    "max_hp": c.max_hp,
                    "current_hp": c.current_hp,
                    "initiative": c.initiative,
                    "notes": c.notes.copy(),
                    "combatant_type": c.combatant_type,
                    "tie_breaker": c._tie_breaker
                }
                for c in encounter.combatants
            ],
            "current_turn": encounter.current_turn,
            "round_number": encounter.round_number,
            "metadata": {
                "created": created_date,
                "last_modified": now,
                "version": "1.0"
            }
        }
    
    def _dict_to_encounter(self, data: Dict[str, Any]) -> Encounter:
        """Convert a dictionary to an Encounter object.
        
        Args:
            data: Dictionary representation of encounter
            
        Returns:
            Encounter object
            
        Raises:
            ValidationError: If data is invalid
        """
        try:
            # Create combatants
            combatants = []
            for c_data in data.get("combatants", []):
                combatant = Combatant(
                    name=c_data["name"],
                    max_hp=c_data["max_hp"],
                    current_hp=c_data["current_hp"],
                    initiative=c_data["initiative"],
                    notes=c_data.get("notes", []).copy(),
                    combatant_type=c_data.get("combatant_type", "unknown")
                )
                # Restore tie breaker if present
                if "tie_breaker" in c_data:
                    combatant._tie_breaker = c_data["tie_breaker"]
                
                combatants.append(combatant)
            
            # Create encounter
            encounter = Encounter(
                name=data["name"],
                combatants=combatants,
                current_turn=data.get("current_turn", 0),
                round_number=data.get("round_number", 1)
            )
            
            # Preserve metadata if present
            if "metadata" in data:
                encounter._metadata = data["metadata"]
            
            return encounter
            
        except KeyError as e:
            raise ValidationError(
                field="encounter data",
                value=str(e),
                reason=f"Missing required field: {e}"
            )
        except (TypeError, ValueError) as e:
            raise ValidationError(
                field="encounter data",
                value=str(e),
                reason=f"Invalid data type: {e}"
            )
    
    def _validate_file_format(self, data: Dict[str, Any], filename: str) -> None:
        """Validate the structure of encounter data.
        
        Args:
            data: Dictionary to validate
            filename: Filename for error messages
            
        Raises:
            FileFormatError: If format is invalid
        """
        if not isinstance(data, dict):
            raise FileFormatError(
                filename=filename,
                operation="validate",
                reason="File does not contain a valid JSON object"
            )
        
        # Check required top-level fields
        required_fields = ["name", "combatants"]
        for field in required_fields:
            if field not in data:
                raise FileFormatError(
                    filename=filename,
                    operation="validate",
                    reason=f"Missing required field: {field}"
                )
        
        # Validate encounter name
        if not isinstance(data["name"], str) or not data["name"].strip():
            raise FileFormatError(
                filename=filename,
                operation="validate",
                reason="Invalid encounter name"
            )
        
        # Validate combatants
        if not isinstance(data["combatants"], list):
            raise FileFormatError(
                filename=filename,
                operation="validate",
                reason="Combatants field must be a list"
            )
        
        for i, combatant_data in enumerate(data["combatants"]):
            if not isinstance(combatant_data, dict):
                raise FileFormatError(
                    filename=filename,
                    operation="validate",
                    reason=f"Combatant {i} is not a valid object"
                )
            
            # Check required combatant fields
            required_combatant_fields = ["name", "max_hp", "current_hp", "initiative"]
            for field in required_combatant_fields:
                if field not in combatant_data:
                    raise FileFormatError(
                        filename=filename,
                        operation="validate",
                        reason=f"Combatant {i} missing field: {field}"
                    )
            
            # Validate combatant field types
            if not isinstance(combatant_data["name"], str) or not combatant_data["name"].strip():
                raise FileFormatError(
                    filename=filename,
                    operation="validate",
                    reason=f"Combatant {i} has invalid name"
                )
            
            for field in ["max_hp", "current_hp", "initiative"]:
                if not isinstance(combatant_data[field], int):
                    raise FileFormatError(
                        filename=filename,
                        operation="validate",
                        reason=f"Combatant {i} field '{field}' must be an integer"
                    )
            
            # Validate optional fields
            if "notes" in combatant_data and not isinstance(combatant_data["notes"], list):
                raise FileFormatError(
                    filename=filename,
                    operation="validate",
                    reason=f"Combatant {i} notes must be a list"
                )
            
            if "combatant_type" in combatant_data and not isinstance(combatant_data["combatant_type"], str):
                raise FileFormatError(
                    filename=filename,
                    operation="validate",
                    reason=f"Combatant {i} combatant_type must be a string"
                )
        
        # Validate optional top-level fields
        if "current_turn" in data and not isinstance(data["current_turn"], int):
            raise FileFormatError(
                filename=filename,
                operation="validate",
                reason="Current_turn must be an integer"
            )
        
        if "round_number" in data and not isinstance(data["round_number"], int):
            raise FileFormatError(
                filename=filename,
                operation="validate",
                reason="Round_number must be an integer"
            )