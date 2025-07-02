"""Tests for file management and encounter listing features."""

import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.core.models import Encounter, Combatant
from dnd_encounter_tracker.core.exceptions import FileFormatError, ValidationError


class TestFileManagement:
    """Test file management operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)
        self.encounter_service = EncounterService(self.data_manager)
        
        # Create test encounter
        self.test_encounter = Encounter("Test Encounter")
        self.test_encounter.add_combatant(Combatant(
            name="Test Hero",
            max_hp=50,
            current_hp=35,
            initiative=15,
            combatant_type="player"
        ))
        self.test_encounter.add_combatant(Combatant(
            name="Test Monster",
            max_hp=25,
            current_hp=25,
            initiative=12,
            combatant_type="monster"
        ))
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_encounter_metadata_valid_file(self):
        """Test getting metadata for a valid encounter file."""
        # Save test encounter
        self.data_manager.save_to_file(self.test_encounter, "test_encounter")
        
        # Get metadata
        metadata = self.data_manager.get_encounter_metadata("test_encounter")
        
        assert metadata["filename"] == "test_encounter"
        assert "created" in metadata
        assert "last_modified" in metadata
        assert "size_bytes" in metadata
        assert metadata["size_bytes"] > 0
        assert metadata["version"] == "1.0"
        
        # Check that dates are valid ISO format
        datetime.fromisoformat(metadata["created"])
        datetime.fromisoformat(metadata["last_modified"])
    
    def test_get_encounter_metadata_nonexistent_file(self):
        """Test getting metadata for a file that doesn't exist."""
        with pytest.raises(FileFormatError) as exc_info:
            self.data_manager.get_encounter_metadata("nonexistent")
        
        assert "File not found" in str(exc_info.value)
    
    def test_get_encounter_metadata_empty_filename(self):
        """Test getting metadata with empty filename."""
        with pytest.raises(ValidationError) as exc_info:
            self.data_manager.get_encounter_metadata("")
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_list_encounters_with_metadata_empty_directory(self):
        """Test listing encounters when directory is empty."""
        encounters = self.data_manager.list_encounters_with_metadata()
        assert encounters == []
    
    def test_list_encounters_with_metadata_with_files(self):
        """Test listing encounters with metadata."""
        # Create multiple test encounters with different timestamps
        encounters_data = [
            ("encounter1", "First Encounter"),
            ("encounter2", "Second Encounter"),
            ("encounter3", "Third Encounter")
        ]
        
        for filename, name in encounters_data:
            encounter = Encounter(name)
            encounter.add_combatant(Combatant(
                name="Test Combatant",
                max_hp=20,
                current_hp=20,
                initiative=10
            ))
            self.data_manager.save_to_file(encounter, filename)
        
        # Get encounters with metadata
        encounters = self.data_manager.list_encounters_with_metadata()
        
        assert len(encounters) == 3
        
        # Check structure of returned data
        for encounter_info in encounters:
            assert "filename" in encounter_info
            assert "encounter_name" in encounter_info
            assert "metadata" in encounter_info
            
            metadata = encounter_info["metadata"]
            assert "created" in metadata
            assert "last_modified" in metadata
            assert "size_bytes" in metadata
            assert metadata["size_bytes"] > 0
        
        # Check that encounters are sorted by last modified (most recent first)
        timestamps = [e["metadata"]["last_modified"] for e in encounters]
        assert timestamps == sorted(timestamps, reverse=True)
    
    def test_backup_encounter_success(self):
        """Test successful backup creation."""
        # Save test encounter
        self.data_manager.save_to_file(self.test_encounter, "test_encounter")
        
        # Create backup
        backup_path = self.data_manager.backup_encounter("test_encounter")
        
        assert os.path.exists(backup_path)
        assert "test_encounter" in backup_path
        assert backup_path.endswith(".backup")
        
        # Verify backup contains same data
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert backup_data["name"] == "Test Encounter"
        assert len(backup_data["combatants"]) == 2
    
    def test_backup_encounter_nonexistent_file(self):
        """Test backup creation for nonexistent file."""
        with pytest.raises(FileFormatError) as exc_info:
            self.data_manager.backup_encounter("nonexistent")
        
        assert "File not found" in str(exc_info.value)
    
    def test_backup_encounter_empty_filename(self):
        """Test backup creation with empty filename."""
        with pytest.raises(ValidationError) as exc_info:
            self.data_manager.backup_encounter("")
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_cleanup_old_backups_no_backups(self):
        """Test cleanup when no backup files exist."""
        deleted_files = self.data_manager.cleanup_old_backups()
        assert deleted_files == []
    
    def test_cleanup_old_backups_with_files(self):
        """Test cleanup of old backup files."""
        # Create test encounter
        self.data_manager.save_to_file(self.test_encounter, "test_encounter")
        
        # Create multiple backup files manually
        backup_files = []
        for i in range(8):  # Create more than max_backups (5)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:02d}"
            backup_filename = f"test_encounter_{timestamp}.backup"
            backup_path = Path(self.temp_dir) / backup_filename
            
            # Create backup file with test data
            with open(backup_path, 'w') as f:
                json.dump({"name": f"Backup {i}", "combatants": []}, f)
            
            backup_files.append(str(backup_path))
        
        # Run cleanup (keep 3 backups)
        deleted_files = self.data_manager.cleanup_old_backups(max_backups=3)
        
        # Should delete 5 files (8 - 3 = 5)
        assert len(deleted_files) == 5
        
        # Check that files were actually deleted
        for deleted_file in deleted_files:
            assert not os.path.exists(deleted_file)
        
        # Check that 3 files remain
        remaining_backups = list(Path(self.temp_dir).glob("*.backup"))
        assert len(remaining_backups) == 3
    
    def test_save_with_metadata_preservation(self):
        """Test that metadata is properly preserved during save operations."""
        # Save encounter first time
        self.data_manager.save_to_file(self.test_encounter, "test_encounter")
        
        # Load encounter
        loaded_encounter = self.data_manager.load_from_file("test_encounter")
        
        # Modify encounter
        loaded_encounter.add_combatant(Combatant(
            name="New Combatant",
            max_hp=30,
            current_hp=30,
            initiative=8
        ))
        
        # Save again
        self.data_manager.save_to_file(loaded_encounter, "test_encounter")
        
        # Check metadata
        metadata = self.data_manager.get_encounter_metadata("test_encounter")
        
        # Created date should be preserved, last_modified should be updated
        assert "created" in metadata
        assert "last_modified" in metadata
        
        # Both should be valid dates
        created = datetime.fromisoformat(metadata["created"])
        modified = datetime.fromisoformat(metadata["last_modified"])
        
        # Modified should be same or later than created
        assert modified >= created
    
    def test_automatic_backup_on_overwrite(self):
        """Test that backup is automatically created when overwriting files."""
        # Save initial encounter
        self.data_manager.save_to_file(self.test_encounter, "test_encounter")
        
        # Modify and save again (should create backup)
        self.test_encounter.add_combatant(Combatant(
            name="Another Combatant",
            max_hp=15,
            current_hp=15,
            initiative=5
        ))
        
        self.data_manager.save_to_file(self.test_encounter, "test_encounter")
        
        # Check that backup was created
        backup_files = list(Path(self.temp_dir).glob("test_encounter.json.backup"))
        assert len(backup_files) == 1
        
        # Verify backup contains original data (2 combatants)
        with open(backup_files[0], 'r') as f:
            backup_data = json.load(f)
        
        assert len(backup_data["combatants"]) == 2  # Original data
        
        # Verify current file contains new data (3 combatants)
        current_encounter = self.data_manager.load_from_file("test_encounter")
        assert len(current_encounter.combatants) == 3  # Updated data


class TestEncounterServiceFileManagement:
    """Test file management operations through EncounterService."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)
        self.encounter_service = EncounterService(self.data_manager)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_encounter_metadata_through_service(self):
        """Test getting encounter metadata through service layer."""
        # Create and save encounter
        encounter = self.encounter_service.create_encounter("Service Test")
        self.encounter_service.add_combatant("Hero", 40, 16, "player")
        self.encounter_service.save_encounter("service_test")
        
        # Get metadata through service
        metadata = self.encounter_service.get_encounter_metadata("service_test")
        
        assert metadata["filename"] == "service_test"
        assert "created" in metadata
        assert "last_modified" in metadata
        assert metadata["size_bytes"] > 0
    
    def test_list_encounters_with_metadata_through_service(self):
        """Test listing encounters with metadata through service layer."""
        # Create multiple encounters
        for i in range(3):
            encounter = self.encounter_service.create_encounter(f"Test Encounter {i+1}")
            self.encounter_service.add_combatant(f"Hero {i+1}", 30, 15, "player")
            self.encounter_service.save_encounter(f"test_{i+1}")
        
        # Get encounters with metadata
        encounters = self.encounter_service.list_encounters_with_metadata()
        
        assert len(encounters) == 3
        
        for encounter_info in encounters:
            assert encounter_info["filename"].startswith("test_")
            assert encounter_info["encounter_name"].startswith("Test Encounter")
            assert "metadata" in encounter_info
    
    def test_backup_encounter_through_service(self):
        """Test backup creation through service layer."""
        # Create and save encounter
        encounter = self.encounter_service.create_encounter("Backup Test")
        self.encounter_service.add_combatant("Hero", 40, 16, "player")
        self.encounter_service.save_encounter("backup_test")
        
        # Create backup through service
        backup_path = self.encounter_service.backup_encounter("backup_test")
        
        assert os.path.exists(backup_path)
        assert "backup_test" in backup_path
        assert backup_path.endswith(".backup")
    
    def test_cleanup_old_backups_through_service(self):
        """Test backup cleanup through service layer."""
        # Create encounter and multiple backups
        encounter = self.encounter_service.create_encounter("Cleanup Test")
        self.encounter_service.add_combatant("Hero", 40, 16, "player")
        self.encounter_service.save_encounter("cleanup_test")
        
        # Create multiple backup files manually
        for i in range(7):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:02d}"
            backup_filename = f"cleanup_test_{timestamp}.backup"
            backup_path = Path(self.temp_dir) / backup_filename
            
            with open(backup_path, 'w') as f:
                json.dump({"name": f"Backup {i}", "combatants": []}, f)
        
        # Cleanup through service (keep 3)
        deleted_files = self.encounter_service.cleanup_old_backups(max_backups=3)
        
        assert len(deleted_files) == 4  # 7 - 3 = 4
        
        # Check remaining files
        remaining_backups = list(Path(self.temp_dir).glob("*.backup"))
        assert len(remaining_backups) == 3


class TestFileManagementEdgeCases:
    """Test edge cases and error conditions for file management."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_metadata_corrupted_json(self):
        """Test getting metadata from a file with corrupted JSON."""
        # Create file with invalid JSON
        corrupted_file = Path(self.temp_dir) / "corrupted.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Should still return file system metadata
        metadata = self.data_manager.get_encounter_metadata("corrupted")
        
        assert metadata["filename"] == "corrupted"
        assert "file_system_created" in metadata
        assert "file_system_modified" in metadata
        assert metadata["size_bytes"] > 0
    
    def test_list_encounters_with_mixed_file_types(self):
        """Test listing encounters when directory contains non-encounter files."""
        # Create valid encounter
        encounter = Encounter("Valid Encounter")
        self.data_manager.save_to_file(encounter, "valid")
        
        # Create non-JSON file
        non_json_file = Path(self.temp_dir) / "not_json.txt"
        with open(non_json_file, 'w') as f:
            f.write("This is not JSON")
        
        # Create backup file (should be filtered out)
        backup_file = Path(self.temp_dir) / "valid.json.backup"
        with open(backup_file, 'w') as f:
            f.write("{}")
        
        # Create temporary file (should be filtered out)
        temp_file = Path(self.temp_dir) / "temp.json.tmp"
        with open(temp_file, 'w') as f:
            f.write("{}")
        
        # List encounters
        encounters = self.data_manager.list_encounters_with_metadata()
        
        # Should only return the valid encounter
        assert len(encounters) == 1
        assert encounters[0]["filename"] == "valid"
    
    @patch('os.path.exists')
    def test_backup_with_permission_error(self, mock_exists):
        """Test backup creation when file system operations fail."""
        mock_exists.return_value = True
        
        # Create test file
        test_file = Path(self.temp_dir) / "test.json"
        with open(test_file, 'w') as f:
            json.dump({"name": "Test", "combatants": []}, f)
        
        # Mock shutil.copy2 to raise permission error
        with patch('shutil.copy2', side_effect=PermissionError("Access denied")):
            with pytest.raises(FileFormatError) as exc_info:
                self.data_manager.backup_encounter("test")
            
            assert "File system error" in str(exc_info.value)
    
    def test_cleanup_with_permission_errors(self):
        """Test cleanup when some files can't be deleted."""
        # Create backup files
        backup_files = []
        for i in range(5):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:02d}"
            backup_filename = f"test_{timestamp}.backup"
            backup_path = Path(self.temp_dir) / backup_filename
            
            with open(backup_path, 'w') as f:
                json.dump({"name": f"Backup {i}", "combatants": []}, f)
            
            backup_files.append(backup_path)
        
        # Make one file read-only (simulate permission error)
        backup_files[0].chmod(0o444)
        
        try:
            # Run cleanup - should handle permission errors gracefully
            deleted_files = self.data_manager.cleanup_old_backups(max_backups=2)
            
            # Should delete what it can, skip what it can't
            assert len(deleted_files) <= 3  # May not be able to delete all
            
        finally:
            # Restore permissions for cleanup
            try:
                backup_files[0].chmod(0o644)
            except:
                pass