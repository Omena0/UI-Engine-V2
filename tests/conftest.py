"""Shared test configuration and fixtures."""

import pytest
import pygame
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame once for the test session."""
    pygame.init()
    # Ensure font module is properly initialized
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def clean_pygame():
    """Ensure clean pygame state for each test."""
    # Don't quit/reinit pygame as it causes font module issues
    # Just ensure pygame is initialized
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield
    # Don't clean up pygame between tests to avoid font issues


@pytest.fixture(scope="class")
def sample_window():
    """Create a sample window for testing - shared across test class."""
    import engine as ui
    # Ensure pygame is ready
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    return ui.Window((800, 600))


@pytest.fixture(scope="class") 
def small_window():
    """Create a small window for testing - shared across test class."""
    import engine as ui
    # Ensure pygame is ready
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    return ui.Window((400, 300))


@pytest.fixture
def sample_surface():
    """Create a sample surface for testing."""
    return pygame.Surface((100, 100))


@pytest.fixture
def red_surface():
    """Create a red surface for testing."""
    surface = pygame.Surface((50, 50))
    surface.fill((255, 0, 0))
    return surface


@pytest.fixture
def sample_colors():
    """Provide common colors for testing."""
    return {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'gray': (128, 128, 128),
    }


@pytest.fixture
def sample_positions():
    """Provide common positions for testing."""
    return [
        (0, 0),
        (10, 10),
        (50, 50),
        (100, 100),
        (200, 150),
    ]


@pytest.fixture
def sample_sizes():
    """Provide common sizes for testing."""
    return [
        (50, 50),
        (100, 30),
        (200, 150),
        (300, 200),
    ]


# Test helpers
def assert_no_exception(func, *args, **kwargs):
    """Assert that a function call doesn't raise an exception."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def create_mock_event(event_type, **kwargs):
    """Create a mock pygame event."""
    return pygame.event.Event(event_type, **kwargs)


# Common test data
SAMPLE_TEXTS = [
    "",
    "Hello",
    "Hello World",
    "This is a longer text string for testing",
    "Unicode: αβγδε ñáéíóú 中文 🚀",
    "Special: !@#$%^&*()_+-=[]{}|;':\",./<>?",
    "Numbers: 1234567890",
    "Mixed: Test123!@#",
]

FONT_SIZES = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32]

COMMON_COLORS = [
    (0, 0, 0),        # Black
    (255, 255, 255),  # White
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
    (128, 128, 128),  # Gray
]
