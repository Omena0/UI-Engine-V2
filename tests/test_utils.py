"""Testing utilities for efficient test execution."""

import pytest
import pygame
import engine as ui

# Global window instance to be shared across tests
_GLOBAL_WINDOW = None

def get_global_window(size=(800, 600)):
    """Get or create a global window instance."""
    global _GLOBAL_WINDOW
    if _GLOBAL_WINDOW is None:
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        _GLOBAL_WINDOW = ui.Window(size)
    return _GLOBAL_WINDOW

@pytest.fixture(scope="session")
def global_window():
    """Session-level window fixture - single window for all tests."""
    return get_global_window()

@pytest.fixture(scope="session")
def small_window():
    """Session-level small window fixture."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    return ui.Window((400, 300))

# Common component fixtures

@pytest.fixture(scope="session")
def sample_text():
    """Sample text for text-based tests."""
    return "Sample testing text"

@pytest.fixture(scope="session")
def component_options():
    """Sample options for components like dropdown, segmented, etc."""
    return ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"]
