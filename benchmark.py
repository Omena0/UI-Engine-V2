"""
Performance benchmark to identify bottlenecks in the UI engine
"""
import pygame
import time
import sys
import os

# Add engine to path
sys.path.insert(0, os.path.dirname(__file__))
import engine as ui

def benchmark_raw_pygame():
    """Benchmark raw pygame operations for baseline"""
    pygame.init()
    surface = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Create test surfaces
    test_surfaces = []
    for i in range(50):
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 0, 128))
        test_surfaces.append((surf, (i * 15 % 800, i * 10 % 600)))
    
    print("Benchmarking raw pygame...")
    
    frame_count = 0
    start_time = time.time()
    test_duration = 3.0
    
    while time.time() - start_time < test_duration:
        surface.fill((0, 0, 0))
        
        # Test regular blits
        for surf, pos in test_surfaces:
            surface.blit(surf, pos)
            
        pygame.display.flip()
        clock.tick()
        frame_count += 1
    
    fps = frame_count / test_duration
    print(f"Raw pygame blits: {fps:.1f} FPS")
    
    # Test fblits
    frame_count = 0
    start_time = time.time()
    
    while time.time() - start_time < test_duration:
        surface.fill((0, 0, 0))
        
        # Test fblits
        surface.fblits(test_surfaces)
            
        pygame.display.flip()
        clock.tick()
        frame_count += 1
    
    fps = frame_count / test_duration
    print(f"Raw pygame fblits: {fps:.1f} FPS")
    
    pygame.quit()

def benchmark_ui_engine():
    """Benchmark the UI engine"""
    # Initialize pygame first to avoid font issues
    pygame.init()
    print("Benchmarking UI engine...")
    
    window = ui.Window((800, 600))
    
    # Create test components
    frames = []
    for i in range(10):
        frame = ui.Frame(window, (i * 70, i * 50), (60, 40))
        frames.append(frame)
    
    frame_count = 0
    start_time = time.time()
    test_duration = 3.0
    
    while time.time() - start_time < test_duration:
        window.render()
        window.draw()
        frame_count += 1
        
        # Handle quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
    
    fps = frame_count / test_duration
    print(f"UI Engine: {fps:.1f} FPS")
    
    # Clean up display without quitting pygame to avoid font issues
    pygame.display.quit()

def benchmark_surface_creation():
    """Benchmark surface creation overhead"""
    print("Benchmarking surface creation...")
    
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)  # Hidden display for testing
    
    start_time = time.time()
    test_duration = 1.0
    surface_count = 0
    
    while time.time() - start_time < test_duration:
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf = surf.convert_alpha()
        surface_count += 1
    
    rate = surface_count / test_duration
    print(f"Surface creation rate: {rate:.1f} surfaces/sec")
    pygame.display.quit()

if __name__ == "__main__":
    print("UI Engine Performance Benchmark")
    print("=" * 40)
    
    benchmark_surface_creation()
    print()
    benchmark_raw_pygame()
    print()
    benchmark_ui_engine()
