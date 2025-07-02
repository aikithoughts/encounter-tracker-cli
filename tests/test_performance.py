"""Performance tests for large encounters and operations."""

import pytest
import time
import tempfile
import os
import statistics
from typing import List, Callable

from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.cli.display import DisplayManager
from tests.fixtures.data_generators import DataGenerator


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
    
    def __str__(self):
        return f"{self.operation_name}: {self.duration:.4f}s"


class TestLargeEncounterPerformance:
    """Test performance with large encounters."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
        self.display_manager = DisplayManager()
        self.generator = DataGenerator()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def time_operation(self, operation: Callable, operation_name: str) -> float:
        """Time a single operation and return duration in seconds."""
        with PerformanceTimer(operation_name) as timer:
            operation()
        return timer.duration
    
    def time_multiple_operations(self, operation: Callable, operation_name: str, iterations: int = 5) -> dict:
        """Time an operation multiple times and return statistics."""
        durations = []
        for _ in range(iterations):
            duration = self.time_operation(operation, operation_name)
            durations.append(duration)
        
        return {
            'operation': operation_name,
            'iterations': iterations,
            'min': min(durations),
            'max': max(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'stdev': statistics.stdev(durations) if len(durations) > 1 else 0,
            'durations': durations
        }
    
    @pytest.mark.parametrize("size", [50, 100, 200, 500])
    def test_large_encounter_creation_performance(self, size):
        """Test performance of creating large encounters."""
        def create_large_encounter():
            encounter = self.generator.create_large_encounter(size)
            self.encounter_service.current_encounter = encounter
        
        stats = self.time_multiple_operations(
            create_large_encounter,
            f"Create encounter with {size} combatants"
        )
        
        print(f"\n{stats['operation']}:")
        print(f"  Mean: {stats['mean']:.4f}s")
        print(f"  Range: {stats['min']:.4f}s - {stats['max']:.4f}s")
        
        # Performance assertions (adjust thresholds as needed)
        if size <= 100:
            assert stats['mean'] < 1.0, f"Creating {size} combatants took too long: {stats['mean']:.4f}s"
        elif size <= 200:
            assert stats['mean'] < 2.0, f"Creating {size} combatants took too long: {stats['mean']:.4f}s"
        else:
            assert stats['mean'] < 5.0, f"Creating {size} combatants took too long: {stats['mean']:.4f}s"
    
    @pytest.mark.parametrize("size", [50, 100, 200])
    def test_initiative_sorting_performance(self, size):
        """Test performance of initiative sorting with large encounters."""
        # Create large encounter
        encounter = self.generator.create_large_encounter(size)
        self.encounter_service.current_encounter = encounter
        
        def sort_by_initiative():
            encounter.sort_by_initiative()
        
        stats = self.time_multiple_operations(
            sort_by_initiative,
            f"Sort {size} combatants by initiative"
        )
        
        print(f"\n{stats['operation']}:")
        print(f"  Mean: {stats['mean']:.4f}s")
        
        # Initiative sorting should be very fast
        assert stats['mean'] < 0.1, f"Sorting {size} combatants took too long: {stats['mean']:.4f}s"
    
    @pytest.mark.parametrize("size", [50, 100, 200])
    def test_save_load_performance(self, size):
        """Test performance of saving and loading large encounters."""
        # Create large encounter
        encounter = self.generator.create_large_encounter(size)
        self.encounter_service.current_encounter = encounter
        
        filename = f"large_encounter_{size}"
        
        # Test save performance
        def save_encounter():
            self.encounter_service.save_encounter(filename)
        
        save_stats = self.time_multiple_operations(
            save_encounter,
            f"Save encounter with {size} combatants"
        )
        
        # Test load performance
        def load_encounter():
            self.encounter_service.load_encounter(filename)
        
        load_stats = self.time_multiple_operations(
            load_encounter,
            f"Load encounter with {size} combatants"
        )
        
        print(f"\nSave/Load performance for {size} combatants:")
        print(f"  Save mean: {save_stats['mean']:.4f}s")
        print(f"  Load mean: {load_stats['mean']:.4f}s")
        
        # File I/O should be reasonable
        assert save_stats['mean'] < 1.0, f"Saving {size} combatants took too long: {save_stats['mean']:.4f}s"
        assert load_stats['mean'] < 1.0, f"Loading {size} combatants took too long: {load_stats['mean']:.4f}s"
    
    @pytest.mark.parametrize("size", [50, 100])
    def test_display_performance(self, size):
        """Test performance of displaying large encounters."""
        # Create large encounter
        encounter = self.generator.create_large_encounter(size)
        self.encounter_service.current_encounter = encounter
        
        def display_encounter():
            # Capture output to avoid printing during tests
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                self.display_manager.show_encounter_summary(encounter)
            finally:
                sys.stdout = old_stdout
        
        stats = self.time_multiple_operations(
            display_encounter,
            f"Display encounter with {size} combatants"
        )
        
        print(f"\n{stats['operation']}:")
        print(f"  Mean: {stats['mean']:.4f}s")
        
        # Display should be fast
        assert stats['mean'] < 0.5, f"Displaying {size} combatants took too long: {stats['mean']:.4f}s"
    
    def test_bulk_hp_updates_performance(self):
        """Test performance of bulk HP updates."""
        size = 100
        encounter = self.generator.create_large_encounter(size)
        self.encounter_service.current_encounter = encounter
        
        def bulk_hp_updates():
            for combatant in encounter.combatants:
                self.encounter_service.update_hp(combatant.name, "-5")
        
        stats = self.time_multiple_operations(
            bulk_hp_updates,
            f"Update HP for {size} combatants"
        )
        
        print(f"\n{stats['operation']}:")
        print(f"  Mean: {stats['mean']:.4f}s")
        
        # Bulk updates should be reasonable
        assert stats['mean'] < 1.0, f"Bulk HP updates took too long: {stats['mean']:.4f}s"
    
    def test_bulk_note_operations_performance(self):
        """Test performance of bulk note operations."""
        size = 50  # Smaller size for note operations
        encounter = self.generator.create_large_encounter(size)
        self.encounter_service.current_encounter = encounter
        
        def bulk_add_notes():
            for i, combatant in enumerate(encounter.combatants):
                self.encounter_service.add_note(combatant.name, f"Performance test note {i}")
        
        stats = self.time_multiple_operations(
            bulk_add_notes,
            f"Add notes to {size} combatants"
        )
        
        print(f"\n{stats['operation']}:")
        print(f"  Mean: {stats['mean']:.4f}s")
        
        # Note operations should be reasonable
        assert stats['mean'] < 0.5, f"Bulk note operations took too long: {stats['mean']:.4f}s"
    
    def test_turn_advancement_performance(self):
        """Test performance of turn advancement in large encounters."""
        size = 100
        encounter = self.generator.create_large_encounter(size)
        self.encounter_service.current_encounter = encounter
        
        def advance_full_round():
            # Advance through all combatants once
            for _ in range(len(encounter.combatants)):
                self.encounter_service.next_turn()
        
        stats = self.time_multiple_operations(
            advance_full_round,
            f"Advance through full round with {size} combatants"
        )
        
        print(f"\n{stats['operation']}:")
        print(f"  Mean: {stats['mean']:.4f}s")
        
        # Turn advancement should be very fast
        assert stats['mean'] < 0.1, f"Turn advancement took too long: {stats['mean']:.4f}s"


class TestMemoryUsage:
    """Test memory usage with large encounters."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
        self.generator = DataGenerator()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    @pytest.mark.skipif(
        not pytest.importorskip("psutil", reason="psutil not available"),
        reason="Memory tests require psutil"
    )
    def test_memory_usage_scaling(self):
        """Test that memory usage scales reasonably with encounter size."""
        sizes = [10, 50, 100, 200]
        memory_usage = []
        
        for size in sizes:
            # Create encounter
            encounter = self.generator.create_large_encounter(size)
            self.encounter_service.current_encounter = encounter
            
            # Measure memory
            memory_mb = self.get_memory_usage()
            memory_usage.append((size, memory_mb))
            
            print(f"Encounter with {size} combatants: {memory_mb:.2f} MB")
        
        # Memory usage should not grow exponentially
        # This is a basic sanity check
        largest_size, largest_memory = memory_usage[-1]
        smallest_size, smallest_memory = memory_usage[0]
        
        memory_ratio = largest_memory / smallest_memory
        size_ratio = largest_size / smallest_size
        
        # Memory growth should be roughly linear with size
        # Allow some overhead for Python object management
        assert memory_ratio < size_ratio * 2, f"Memory usage grew too quickly: {memory_ratio:.2f}x for {size_ratio}x size increase"
    
    def test_memory_cleanup_after_operations(self):
        """Test that memory is properly cleaned up after operations."""
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available for memory testing")
        
        initial_memory = self.get_memory_usage()
        
        # Perform memory-intensive operations
        for i in range(10):
            encounter = self.generator.create_large_encounter(100)
            self.encounter_service.current_encounter = encounter
            
            # Perform various operations
            for combatant in encounter.combatants[:10]:  # Limit to avoid excessive time
                self.encounter_service.update_hp(combatant.name, "-5")
                self.encounter_service.add_note(combatant.name, f"Test note {i}")
            
            # Save and load
            filename = f"memory_test_{i}"
            self.encounter_service.save_encounter(filename)
            self.encounter_service.load_encounter(filename)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.2f} MB -> {final_memory:.2f} MB (+{memory_increase:.2f} MB)")
        
        # Memory increase should be reasonable (allow for some Python overhead)
        assert memory_increase < 50, f"Memory increased too much: {memory_increase:.2f} MB"


class TestScalabilityLimits:
    """Test the practical limits of the system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
        self.generator = DataGenerator()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.slow
    def test_maximum_practical_encounter_size(self):
        """Test the maximum practical encounter size."""
        # Test increasingly large encounters until we hit practical limits
        max_size = 1000
        
        try:
            encounter = self.generator.create_large_encounter(max_size)
            self.encounter_service.current_encounter = encounter
            
            # Test basic operations still work
            start_time = time.perf_counter()
            encounter.sort_by_initiative()
            sort_time = time.perf_counter() - start_time
            
            start_time = time.perf_counter()
            self.encounter_service.save_encounter("max_size_test")
            save_time = time.perf_counter() - start_time
            
            start_time = time.perf_counter()
            loaded = self.encounter_service.load_encounter("max_size_test")
            load_time = time.perf_counter() - start_time
            
            print(f"Maximum size test ({max_size} combatants):")
            print(f"  Sort time: {sort_time:.4f}s")
            print(f"  Save time: {save_time:.4f}s")
            print(f"  Load time: {load_time:.4f}s")
            
            # Verify data integrity
            assert len(loaded.combatants) == max_size
            assert loaded.name == encounter.name
            
            # Operations should still be reasonable even at max size
            assert sort_time < 1.0, f"Sorting {max_size} combatants took too long"
            assert save_time < 5.0, f"Saving {max_size} combatants took too long"
            assert load_time < 5.0, f"Loading {max_size} combatants took too long"
            
        except MemoryError:
            pytest.skip(f"System cannot handle {max_size} combatants due to memory constraints")
        except Exception as e:
            pytest.fail(f"Unexpected error with {max_size} combatants: {e}")
    
    def test_file_size_scaling(self):
        """Test how file sizes scale with encounter size."""
        sizes = [10, 50, 100, 200]
        file_sizes = []
        
        for size in sizes:
            encounter = self.generator.create_large_encounter(size)
            self.encounter_service.current_encounter = encounter
            
            filename = f"size_test_{size}"
            self.encounter_service.save_encounter(filename)
            
            file_size = os.path.getsize(f"{filename}.json")
            file_sizes.append((size, file_size))
            
            print(f"Encounter with {size} combatants: {file_size} bytes ({file_size/1024:.2f} KB)")
        
        # File size should scale roughly linearly
        largest_size, largest_file = file_sizes[-1]
        smallest_size, smallest_file = file_sizes[0]
        
        file_ratio = largest_file / smallest_file
        size_ratio = largest_size / smallest_size
        
        # Allow some overhead for JSON structure
        assert file_ratio < size_ratio * 1.5, f"File size grew too quickly: {file_ratio:.2f}x for {size_ratio}x size increase"
    
    def test_concurrent_operation_performance(self):
        """Test performance when multiple operations are performed rapidly."""
        size = 50
        encounter = self.generator.create_large_encounter(size)
        self.encounter_service.current_encounter = encounter
        
        start_time = time.perf_counter()
        
        # Perform many rapid operations
        for i in range(100):
            # Mix different types of operations
            combatant = encounter.combatants[i % len(encounter.combatants)]
            
            if i % 4 == 0:
                self.encounter_service.update_hp(combatant.name, "-1")
            elif i % 4 == 1:
                self.encounter_service.add_note(combatant.name, f"Rapid note {i}")
            elif i % 4 == 2:
                self.encounter_service.next_turn()
            else:
                # Re-sort initiative (expensive operation)
                encounter.sort_by_initiative()
        
        total_time = time.perf_counter() - start_time
        
        print(f"100 rapid operations on {size} combatants: {total_time:.4f}s")
        
        # Should handle rapid operations reasonably well
        assert total_time < 2.0, f"Rapid operations took too long: {total_time:.4f}s"