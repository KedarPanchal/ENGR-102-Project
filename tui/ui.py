import pytermgui as ptg
import asyncio
import signal


class UI:
    """Manages the terminal user interface for the Flip Seven game.

    Provides a pytermgui-based terminal interface with multiple windows
    for displaying game information, player hands, and accepting user input.
    Handles asynchronous initialization and cleanup of the UI manager.

    Attributes:
        _manager: The pytermgui WindowManager instance.
        _layout: The layout manager for arranging windows.
        _input_field: The input field for user commands.
        _input_window: The window containing the input field.
        _manager_process: The asyncio task running the UI manager.
        _shutdown_event: Event used to signal UI shutdown.
    """

    def __init__(self):
        """Initialize the UI with windows and layout configuration.

        Creates a WindowManager with three slots:
        - main: Displays game information
        - hand: Shows the current player's hand (30% width)
        - input: Accepts user commands (height of 5)
        """
        # Initialize class variables
        self._manager = ptg.WindowManager()
        self._layout = self._manager.layout

        # Initialize layout
        self._layout.add_slot("main")
        self._layout.add_slot("hand", width=0.3)
        self._layout.add_break()
        self._layout.add_slot("input", height=5)

        # Initialize windows
        main_window = ptg.Window(title="[210 bold]Game Info")
        hand_window = ptg.Window(title="[210 bold] Current Player's Hand")
        self._input_field = ptg.InputField(prompt="> ")
        self._input_window = ptg.Window(self._input_field)

        # Add windows
        self._manager.add(main_window, assign="main")
        self._manager.add(hand_window, assign="hand")
        self._manager.add(self._input_window, assign="input")

        # Asynchronous class variables
        self._manager_process = None
        self._shutdown_event = asyncio.Event()

    async def run(self):
        """Start the UI manager and wait for shutdown signal.

        Initializes the UI manager in a background thread and waits for
        the shutdown event to be triggered. Once triggered, performs
        cleanup by stopping the manager and cancelling the background task.

        Note:
            This method blocks until stop() is called or a KeyboardInterrupt
            is received.
        """
        if self._manager_process:
            return

        self._manager.focus(self._input_window)
        self._input_field.select()
        self._manager_process = asyncio.create_task(asyncio.to_thread(self._manager.run))
        
        try:
            await self._shutdown_event.wait()
        except KeyboardInterrupt:
            pass
        
        self._manager.stop()
        self._manager_process.cancel()
        try:
            await self._manager_process
        except asyncio.CancelledError:
            pass
        self._manager_process = None

    def stop(self):
        """Signal the UI to shut down.

        Sets the shutdown event, which triggers the cleanup process in run().
        This method can be called from signal handlers or other contexts
        to gracefully terminate the UI.
        """
        self._shutdown_event.set()


# Test code goes here
if __name__ == "__main__":
    ui = UI()

    async def main():
        loop = asyncio.get_running_loop()
        # Needed for pytermgui to handle Ctrl+C properly
        loop.add_signal_handler(signal.SIGINT, ui.stop)
        try:
            await ui.run()
        finally:
            loop.remove_signal_handler(signal.SIGINT)

    asyncio.run(main())
