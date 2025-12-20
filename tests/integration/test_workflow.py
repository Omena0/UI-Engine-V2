"""Integration tests for the UI engine."""

import sys
import os
import time
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pygame
import engine as ui


def ensure_pygame_ready():
    """Ensure pygame and font module are properly initialized."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()


def test_basic_ui_workflow():
    """Test a basic UI workflow with multiple components."""
    # Initialize pygame without display for testing
    ensure_pygame_ready()
    
    try:
        # Create window
        window = ui.Window((800, 600))
        
        # Create a frame
        frame = ui.Frame(window, (10, 10), (300, 200))
        
        # Create components in the frame
        label = ui.Label(frame, (10, 10), "Test Application", (None, 16))
        button = ui.Button(frame, (10, 40), "Click Me", (100, 30))
        field = ui.Field(frame, (10, 80), (None, 14), "Type here...", size=(200, 25))
        
        # Test that components are properly nested
        assert len(window.children) == 1
        assert window.children[0] == frame
        assert len(frame.children) == 3
        
        # Test rendering doesn't crash
        try:
            window.render()
            window.draw()
            # If we get here, rendering succeeded
            assert True
        except Exception as e:
            raise AssertionError(f"Rendering failed: {e}")
    finally:
        # Clean up pygame but don't quit completely to avoid invalidating fonts for other tests
        if pygame.get_init():
            pygame.display.quit()


def test_performance_benchmark():
    """Basic performance test to ensure we're not regressing."""
    ensure_pygame_ready()
    
    try:
        window = ui.Window((800, 600))
        
        # Create multiple components
        for i in range(10):
            frame = ui.Frame(window, (i * 70, i * 50), (60, 40))
            ui.Button(frame, (5, 5), f"Btn{i}", (50, 30))
        
        # Time a series of render calls
        start_time = time.time()
        for _ in range(100):
            window.render()
            window.draw()
        end_time = time.time()
        
        # Should complete 100 renders in less than 1 second (very generous)
        duration = end_time - start_time
        assert duration < 1.0, f"100 renders took {duration:.3f}s, too slow"
    finally:
        # Clean up pygame but don't quit completely to avoid invalidating fonts for other tests
        if pygame.get_init():
            pygame.display.quit()
