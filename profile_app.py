import cProfile
import pstats
import io
import sys
import os
import time
import threading

# Add the engine to the path
sys.path.insert(0, os.path.dirname(__file__))

def profile_main():
    """Run the actual main.py application for profiling"""
    import main
    # This will run main.py which calls window.mainloop()
    # The mainloop will run indefinitely, so we need a way to stop it

def run_main_with_timeout():
    """Run main.py and stop it after a timeout"""
    # Import and let main.py set up everything
    import main
    import pygame
    import engine.util as util
    
    # Start a timer to quit after 3 seconds
    import time
    start_time = time.time()
    
    def quit_after_timeout():
        while time.time() - start_time < 3.0:
            time.sleep(0.1)
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    timer = threading.Thread(target=quit_after_timeout, daemon=True)
    timer.start()
    
    # This will run the main loop for ~3 seconds then quit
    # main.py ends with window.mainloop() which will run until QUIT event
    
    # Return the actual average FPS from the engine
    return util.get_average_fps()

if __name__ == "__main__":
    print("Profiling the actual main.py application...")
    
    # Create a profiler
    profiler = cProfile.Profile()
    
    # Run the profiling
    avg_fps = profiler.runcall(run_main_with_timeout)
    
    # Create a StringIO buffer to capture the output
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    
    # Sort by cumulative time and print top 30 functions
    ps.sort_stats('cumulative')
    ps.print_stats(30)
    
    # Get the profiling results
    profile_output = s.getvalue()
    
    print(f"\nActual Average FPS: {avg_fps:.1f}")
    print("\nTop 30 functions by cumulative time:")
    print("=" * 60)
    print(profile_output)
    
    # Also sort by total time
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats('tottime')
    ps.print_stats(20)
    
    profile_output = s.getvalue()
    print("\nTop 20 functions by total time:")
    print("=" * 60)
    print(profile_output)
