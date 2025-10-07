"""
Keyboard interrupt handler for graceful termination
"""
import signal
import sys

class GracefulInterrupter:
    """
    Handle keyboard interrupts gracefully
    """
    def __init__(self):
        self.interrupted = False
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle interrupt signal"""
        print("\nKeyboard interrupt detected. Closing browser and exiting gracefully...")
        self.interrupted = True
        sys.exit(0)
    
    def is_interrupted(self):
        """Check if interrupted"""
        return self.interrupted