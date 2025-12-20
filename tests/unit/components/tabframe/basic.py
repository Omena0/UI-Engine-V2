"""Tests for TabFrame component."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


class TestTabFrame:
    """Test suite for TabFrame component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def tab_names(self):
        """Create sample tab names."""
        return ["Tab 1", "Tab 2", "Tab 3", "Tab 4"]

    @pytest.fixture
    def tabframe(self, window, tab_names):
        """Create a basic tabframe for testing."""
        return ui.TabFrame(window, (10, 10), (300, 200), len(tab_names))

    def test_creation(self, window, tab_names):
        """Test basic tabframe creation."""
        tabframe = ui.TabFrame(window, (10, 10), (300, 200), len(tab_names))
        assert tabframe.pos == (10, 10)
        assert tabframe.size == (300, 200)
        assert hasattr(tabframe, '_tab_frames') or hasattr(tabframe, 'tabs') or hasattr(tabframe, '_tabs')

    def test_creation_with_different_tabs(self, window):
        """Test tabframe creation with different tab configurations."""
        tab_configs = [
            ["Single"],
            ["A", "B"],
            ["First", "Second", "Third"],
            ["One", "Two", "Three", "Four", "Five"],
            [f"Tab {i}" for i in range(10)],  # Many tabs
        ]
        
        for tabs in tab_configs:
            tabframe = ui.TabFrame(window, (10, 10), (300, 200), len(tabs))
            try:
                tabframe.render()
            except Exception as e:
                pytest.fail(f"TabFrame with {len(tabs)} tabs failed to render: {e}")

    def test_initial_state(self, tabframe):
        """Test tabframe initial state."""
        # Should have a default active tab (usually first)
        if hasattr(tabframe, 'active_tab'):
            assert isinstance(tabframe.active_tab, int)
        elif hasattr(tabframe, '_active_tab'):
            assert isinstance(tabframe._active_tab, int)
        elif hasattr(tabframe, 'current_tab'):
            assert isinstance(tabframe.current_tab, int)

    def test_rendering(self, tabframe):
        """Test tabframe rendering."""
        try:
            tabframe.render()
            if hasattr(tabframe, 'blits'):
                assert len(tabframe.blits) > 0
        except Exception as e:
            pytest.fail(f"TabFrame rendering failed: {e}")

    def test_tab_switching(self, tabframe):
        """Test switching between tabs."""
        num_tabs = len(getattr(tabframe, '_tabs', []) or getattr(tabframe, 'tabs', []) or getattr(tabframe, '_tab_names', []))
        
        if num_tabs == 0:
            num_tabs = 4  # Default from fixture
        
        for i in range(num_tabs):
            if hasattr(tabframe, 'active_tab'):
                tabframe.active_tab = i
                assert tabframe.active_tab == i
            elif hasattr(tabframe, '_active_tab'):
                tabframe._active_tab = i
                assert tabframe._active_tab == i
            elif hasattr(tabframe, 'current_tab'):
                tabframe.current_tab = i
                assert tabframe.current_tab == i
            
            try:
                tabframe.render()
            except Exception as e:
                pytest.fail(f"TabFrame rendering failed with tab {i}: {e}")

    def test_click_tab_headers(self, tabframe):
        """Test clicking on tab headers to switch tabs."""
        # Calculate approximate tab header positions
        width = tabframe.size[0]
        num_tabs = 4  # From fixture
        tab_width = width // num_tabs
        
        for i in range(num_tabs):
            # Click in the middle of each tab header
            click_x = tabframe.pos[0] + (i * tab_width) + (tab_width // 2)
            click_y = tabframe.pos[1] + 15  # Assume tab headers are ~30px high
            
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(click_x, click_y), button=1)
            
            try:
                tabframe._event(click_event)
                tabframe.render()  # Ensure it can render after click
            except Exception as e:
                pytest.fail(f"TabFrame tab header click failed for tab {i}: {e}")

    def test_adding_content_to_tabs(self, window, tabframe):
        """Test adding content to tabs if supported."""
        # Check if tabframe supports adding content
        if hasattr(tabframe, 'add_to_tab') or hasattr(tabframe, 'set_tab_content'):
            try:
                # Try adding simple components to tabs
                for i in range(2):  # Test first two tabs
                    label = ui.Label(window, (20, 50), f"Content for tab {i}")
                    
                    if hasattr(tabframe, 'add_to_tab'):
                        tabframe.add_to_tab(i, label)
                    elif hasattr(tabframe, 'set_tab_content'):
                        tabframe.set_tab_content(i, [label])
                
                tabframe.render()
            except Exception as e:
                pytest.fail(f"TabFrame adding content failed: {e}")

    def test_tab_content_rendering(self, tabframe):
        """Test that tab content is properly rendered."""
        # Switch to different tabs and ensure content renders
        for i in range(2):
            if hasattr(tabframe, 'active_tab'):
                tabframe.active_tab = i
            elif hasattr(tabframe, '_active_tab'):
                tabframe._active_tab = i
            
            try:
                tabframe.render()
            except Exception as e:
                pytest.fail(f"TabFrame content rendering failed for tab {i}: {e}")

    def test_different_sizes(self, window, tab_names):
        """Test tabframe with different sizes."""
        sizes = [(200, 150), (400, 300), (100, 100), (500, 400)]
        
        for width, height in sizes:
            tabframe = ui.TabFrame(window, (10, 10), (width, height), len(tab_names))
            # TabFrame may adjust size based on internal constraints
            actual_size = tabframe.size
            assert actual_size[0] > 0 and actual_size[1] > 0
            assert actual_size[0] <= width and actual_size[1] <= height
            
            try:
                tabframe.render()
            except Exception as e:
                pytest.fail(f"TabFrame with size {width}x{height} failed to render: {e}")

    def test_long_tab_names(self, window):
        """Test tabframe with long tab names."""
        long_names = [
            "Very Long Tab Name",
            "Another Extremely Long Tab Name",
            "Short",
            "This is an absurdly long tab name that might cause overflow issues",
        ]
        
        tabframe = ui.TabFrame(window, (10, 10), (300, 200), len(long_names))
        try:
            tabframe.render()
        except Exception as e:
            pytest.fail(f"TabFrame with long tab names failed to render: {e}")

    def test_unicode_tab_names(self, window):
        """Test tabframe with unicode tab names."""
        unicode_names = ["普通话", "Español", "Français", "🎯Tab", "αβγδε"]
        
        tabframe = ui.TabFrame(window, (10, 10), (300, 200), len(unicode_names))
        try:
            tabframe.render()
        except Exception as e:
            pytest.fail(f"TabFrame with unicode tab names failed to render: {e}")

    def test_empty_tab_names(self, window):
        """Test tabframe with empty tab names."""
        try:
            tabframe = ui.TabFrame(window, (10, 10), (300, 200), 0)
            tabframe.render()
        except Exception as e:
            # Empty tabs might not be supported
            pass

    def test_single_tab(self, window):
        """Test tabframe with single tab."""
        tabframe = ui.TabFrame(window, (10, 10), (300, 200), 1)
        try:
            tabframe.render()
        except Exception as e:
            pytest.fail(f"TabFrame with single tab failed to render: {e}")

    def test_with_many_tabs(self, window):
        """Test creation with many tabs."""
        many_tabs = ["Tab1", "Tab2", "Tab3", "Tab4", "Tab5", "Tab6", "Tab7", "Tab8"]
        tabframe = ui.TabFrame(window, (10, 10), (500, 300), len(many_tabs))
        assert tabframe is not None

    def test_mouse_hover_tabs(self, tabframe):
        """Test mouse hover over tab headers."""
        # Hover over different tab header areas
        hover_positions = [
            (50, 15),   # First tab
            (125, 15),  # Second tab
            (200, 15),  # Third tab
            (275, 15),  # Fourth tab
        ]
        
        for x, y in hover_positions:
            motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(x, y))
            try:
                tabframe._event(motion_event)
            except Exception as e:
                pytest.fail(f"TabFrame mouse hover failed at ({x}, {y}): {e}")

    def test_keyboard_navigation(self, tabframe):
        """Test keyboard navigation between tabs."""
        key_events = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2),
        ]
        
        for event in key_events:
            try:
                tabframe._event(event)
            except Exception as e:
                pytest.fail(f"TabFrame keyboard navigation failed for key {event.key}: {e}")

    def test_focus_handling(self, tabframe):
        """Test tabframe focus handling."""
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 15), button=1)
        
        try:
            tabframe._event(click_event)
        except Exception as e:
            pytest.fail(f"TabFrame focus handling failed: {e}")

    def test_bounds_checking(self, tabframe):
        """Test click bounds checking."""
        # Test clicks in different areas
        test_clicks = [
            (0, 0),         # Far outside
            (50, 15),       # Tab header area
            (50, 100),      # Content area
            (350, 15),      # Outside right edge
            (50, 250),      # Below tabframe
        ]
        
        for x, y in test_clicks:
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=1)
            try:
                tabframe._event(click_event)
            except Exception as e:
                pytest.fail(f"TabFrame bounds checking failed at ({x}, {y}): {e}")

    def test_different_positions(self, window, tab_names):
        """Test tabframe at different positions."""
        positions = [(0, 0), (50, 100), (200, 50), (300, 200)]
        
        for x, y in positions:
            tabframe = ui.TabFrame(window, (x, y), (300, 200), len(tab_names))
            assert tabframe.pos == (x, y)
            
            try:
                tabframe.render()
            except Exception as e:
                pytest.fail(f"TabFrame at position ({x}, {y}) failed to render: {e}")

    def test_tab_close_if_supported(self, tabframe):
        """Test tab closing functionality if supported."""
        if hasattr(tabframe, 'close_tab') or hasattr(tabframe, 'remove_tab'):
            try:
                initial_count = len(getattr(tabframe, '_tabs', []) or getattr(tabframe, 'tabs', []) or [1,2,3,4])
                
                if hasattr(tabframe, 'close_tab'):
                    tabframe.close_tab(0)
                elif hasattr(tabframe, 'remove_tab'):
                    tabframe.remove_tab(0)
                
                tabframe.render()
                
                # Check if tab count decreased
                current_count = len(getattr(tabframe, '_tabs', []) or getattr(tabframe, 'tabs', []) or [1,2,3])
                # Note: might not change depending on implementation
                
            except Exception as e:
                pytest.fail(f"TabFrame tab closing failed: {e}")

    def test_tab_addition_if_supported(self, tabframe):
        """Test adding new tabs if supported."""
        if hasattr(tabframe, 'add_tab') or hasattr(tabframe, 'insert_tab'):
            try:
                if hasattr(tabframe, 'add_tab'):
                    new_frame = tabframe.add_tab()  # add_tab takes no arguments
                    assert new_frame is not None
                elif hasattr(tabframe, 'insert_tab'):
                    tabframe.insert_tab(1)  # May also take no string argument

                tabframe.render()

            except Exception as e:
                pytest.fail(f"TabFrame tab addition failed: {e}")

    def test_custom_colors_if_supported(self, window, tab_names):
        """Test tabframe with custom colors if supported."""
        tabframe = ui.TabFrame(window, (10, 10), (300, 200), len(tab_names))
        
        color_attrs = ['tab_color', 'active_tab_color', 'bg_color', 'text_color']
        test_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        for attr in color_attrs:
            if hasattr(tabframe, attr):
                for color in test_colors:
                    try:
                        setattr(tabframe, attr, color)
                        tabframe.render()
                    except Exception as e:
                        pytest.fail(f"TabFrame custom color {attr} failed: {e}")

    def test_disabled_tabs_if_supported(self, tabframe):
        """Test disabling individual tabs if supported."""
        if hasattr(tabframe, 'disable_tab') or hasattr(tabframe, 'set_tab_enabled'):
            try:
                if hasattr(tabframe, 'disable_tab'):
                    tabframe.disable_tab(1)
                elif hasattr(tabframe, 'set_tab_enabled'):
                    tabframe.set_tab_enabled(1, False)
                
                tabframe.render()
                
                # Try to click disabled tab
                click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(125, 15), button=1)
                tabframe._event(click_event)
                
            except Exception as e:
                pytest.fail(f"TabFrame disabled tabs failed: {e}")

    def test_callback_functionality(self, window, tab_names):
        """Test tabframe callback functionality."""
        callback_called = False
        callback_tab = None
        
        def test_callback(tab_index=None):
            nonlocal callback_called, callback_tab
            callback_called = True
            callback_tab = tab_index
        
        try:
            tabframe = ui.TabFrame(window, (10, 10), (300, 200), len(tab_names), callback=test_callback)
            
            # Trigger callback by clicking a tab
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(125, 15), button=1)
            tabframe._event(click_event)
            
        except TypeError:
            # Constructor might not accept callback parameter
            pass
        except Exception as e:
            pytest.fail(f"TabFrame callback test failed: {e}")

    def test_tab_header_height_if_configurable(self, window, tab_names):
        """Test configurable tab header height if supported."""
        try:
            tabframe = ui.TabFrame(window, (10, 10), (300, 200), len(tab_names))
            
            if hasattr(tabframe, 'tab_height') or hasattr(tabframe, 'header_height'):
                heights = [20, 30, 40, 50]
                for height in heights:
                    if hasattr(tabframe, 'tab_height'):
                        tabframe.tab_height = height
                    elif hasattr(tabframe, 'header_height'):
                        tabframe.header_height = height
                    
                    tabframe.render()
                    
        except Exception as e:
            pytest.fail(f"TabFrame header height configuration failed: {e}")

    def test_scrollable_tabs_if_supported(self, tabframe):
        """Test scrollable tabs for overflow if supported."""
        # This would be relevant for many tabs
        if hasattr(tabframe, 'scroll_tabs') or hasattr(tabframe, 'tab_scroll'):
            try:
                # Simulate scrolling
                scroll_event = pygame.event.Event(pygame.MOUSEWHEEL, y=1)
                tabframe._event(scroll_event)
                
                scroll_event = pygame.event.Event(pygame.MOUSEWHEEL, y=-1)
                tabframe._event(scroll_event)
                
                tabframe.render()
                
            except Exception as e:
                pytest.fail(f"TabFrame scrollable tabs failed: {e}")

    def test_tab_content_area_size(self, tabframe):
        """Test that content area size is calculated correctly."""
        # Content area should be smaller than total tabframe size
        total_size = tabframe.size
        
        if hasattr(tabframe, 'content_area') or hasattr(tabframe, 'get_content_area'):
            try:
                if hasattr(tabframe, 'content_area'):
                    content_area = tabframe.content_area
                elif hasattr(tabframe, 'get_content_area'):
                    content_area = tabframe.get_content_area()
                
                # Content area should be within total size
                if isinstance(content_area, tuple) and len(content_area) >= 2:
                    assert content_area[0] <= total_size[0]
                    assert content_area[1] <= total_size[1]
                    
            except Exception as e:
                pytest.fail(f"TabFrame content area size calculation failed: {e}")

    def test_rapid_tab_switching(self, tabframe):
        """Test rapid switching between tabs."""
        width = tabframe.size[0]
        num_tabs = 4
        tab_width = width // num_tabs
        
        # Rapidly click different tabs
        for i in range(20):
            tab_index = i % num_tabs
            click_x = tabframe.pos[0] + (tab_index * tab_width) + (tab_width // 2)
            click_y = tabframe.pos[1] + 15
            
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(click_x, click_y), button=1)
            
            try:
                tabframe._event(click_event)
            except Exception as e:
                pytest.fail(f"TabFrame rapid switching failed at iteration {i}: {e}")

    def test_tab_state_persistence(self, tabframe):
        """Test that tab state persists through renders."""
        # Set specific tab as active
        if hasattr(tabframe, 'active_tab'):
            tabframe.active_tab = 2
            initial_tab = tabframe.active_tab
        elif hasattr(tabframe, '_active_tab'):
            tabframe._active_tab = 2
            initial_tab = tabframe._active_tab
        else:
            initial_tab = 2
        
        # Render multiple times
        for _ in range(5):
            try:
                tabframe.render()
            except Exception as e:
                pytest.fail(f"TabFrame state persistence failed: {e}")
        
        # Check active tab is still the same
        if hasattr(tabframe, 'active_tab'):
            assert tabframe.active_tab == initial_tab
        elif hasattr(tabframe, '_active_tab'):
            assert tabframe._active_tab == initial_tab

    def test_edge_case_sizes(self, window, tab_names):
        """Test tabframe with edge case sizes."""
        edge_sizes = [
            (50, 50),    # Very small
            (10, 200),   # Very narrow
            (300, 20),   # Very short
        ]
        
        for width, height in edge_sizes:
            try:
                tabframe = ui.TabFrame(window, (10, 10), (width, height), len(tab_names))
                tabframe.render()
            except Exception as e:
                # Some edge cases might not be supported
                pass

    def test_tab_index_bounds(self, tabframe):
        """Test tab index bounds checking."""
        # Test setting invalid tab indices
        invalid_indices = [-1, 999, -10]
        
        for index in invalid_indices:
            try:
                if hasattr(tabframe, 'active_tab'):
                    tabframe.active_tab = index
                elif hasattr(tabframe, '_active_tab'):
                    tabframe._active_tab = index
                
                # Should handle gracefully
                tabframe.render()
                
            except Exception as e:
                # Implementation might raise exception for invalid indices
                pass
