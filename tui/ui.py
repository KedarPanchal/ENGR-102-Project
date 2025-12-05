import pytermgui as ptg
import asyncio
import io
import keyboard
from typing import List, Optional


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
        self._main_window = ptg.Window(title="[210 bold]Game Info", overflow=ptg.Overflow.SCROLL)
        self._main_text = ptg.Label("")
        self._main_window += self._main_text
        self._hand_window = ptg.Window(title="[210 bold] Current Player's Hand and Score", overflow=ptg.Overflow.SCROLL)
        self._hand_text = ptg.Label("")
        self._hand_window += self._hand_text
        self._input_field = ptg.InputField(prompt="> ")
        self._input_window = ptg.Window(self._input_field)

        # Add windows
        self._manager.add(self._main_window, assign="main")
        self._manager.add(self._hand_window, assign="hand")
        self._manager.add(self._input_window, assign="input")

        # Input handling
        self._input_field.bind(ptg.keys.ENTER, self._handle_input)
        self._input_field.bind(ptg.keys.RETURN, self._handle_input)
        self._input_queue = None

        # Asynchronous class variables
        self._loop = None
        self._manager_process = None
        self._running = asyncio.Event()

    def _handle_input(self, widget: ptg.InputField, key):
        """Handle input field key events.

        If the Enter key is pressed, retrieves the input value,
        clears the input field, and processes the command.
        This function doesn't actually manage the keypresses, but is
        called by pytermgui when the appropriate key is detected.

        Args:
            widget: The input field widget.
            key: The key event.
        Returns:
            bool: True, since the input was handled.
        """
        command = widget.value.strip()
        widget.delete_back(len(widget.value))

        if not self._loop or not self._input_queue:
            return True

        if self._input_queue.full():
            return True

        self._loop.call_soon_threadsafe(self._input_queue.put_nowait, command)
        return True

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

        self._loop = asyncio.get_running_loop()
        self._input_queue = asyncio.Queue(maxsize=1)

        self._manager.focus(self._input_window)
        self._input_field.select()
        self._manager_process = asyncio.create_task(asyncio.to_thread(self._manager.run))
        self._running.set()

    async def wait_until_running(self):
        """Wait until the UI manager is fully running.

        This method can be used to ensure that the UI is ready before
        performing operations that depend on the UI being active.
        """
        await self._running.wait()

    async def stop(self):
        """Signal the UI to shut down.

        Sets the shutdown event, which triggers the cleanup process in run().
        This method can be called from signal handlers or other contexts
        to gracefully terminate the UI.
        """
        if not self._manager_process:
            return

        self._running.clear()
        self._manager.stop()
        self._manager_process.cancel()
        try:
            await self._manager_process
        except asyncio.CancelledError:
            pass

        self._manager_process = None
        keyboard.press_and_release("enter")  # Wake up input field if waiting

    async def input(self):
        """Asynchronously retrieve user input from the input field.

        Waits for the user to enter a command and press Enter, then
        returns the command as a string.

        Returns:
            str: The user-entered command.
        """
        if not self._input_queue:
            raise RuntimeError("UI is not running. Call run() before input().")

        command = await self._input_queue.get()
        return command

    async def println(self, *args: str, fmts: Optional[List[str]] = None, window: str = "main", sep: str = " ", end: str = "\n"):
        """Prints a line of text to a window asynchronously.
        Args:
            *args: The strings to print.
            fmts: Optional list of format strings for each argument.
                If not provided or empty, defaults to white text.
                If the number of formats is less than the number of arguments,
                the last format is applied to the remaining arguments.
            window: The window to print to ("main" or "hand").
                If not provided, defaults to "main".
            sep: The separator to use between arguments.
                If not provided, defaults to a single space.
            end: The string to append at the end of the line.
                If not provided, defaults to a newline.
        Raises:
            ValueError: If the number of formats exceeds the number of arguments
                or if an unknown window is specified.
        """

        # Default format is white text
        if fmts is None or len(fmts) == 0:
            fmts = ["#ffffff"] * len(args)

        # Extend formats to last applied format if not enough provided
        if len(fmts) < len(args):
            fmts += fmts[-1] * (len(args) - len(fmts))

        if len(fmts) > len(args):
            raise ValueError("Number of formats must be less than or equal to number of arguments")

        sstream = io.StringIO()

        # Write formatted arguments to string stream
        for fmt, arg in zip(fmts, args):
            print(f"[{fmt}]{str(arg)}[/]", end=sep, file=sstream)
        print(end, end="", file=sstream)

        # Prepare the label text
        label_text = sstream.getvalue().rstrip(sep)

        # Add widget to window in a thread-safe manner
        def _add_widget():
            match window:
                case "main":
                    self._main_text.value += label_text
                case "hand":
                    self._hand_text.value += label_text
                case _:
                    raise ValueError(f"Unknown window: {window}")

        # Run the widget addition in a thread to avoid blocking
        await asyncio.to_thread(_add_widget)

    async def clear(self, window: str = "main"):
        """Clears all content from the specified window asynchronously.
        Args:
            window: The window to clear ("main" or "hand").
                If not provided, defaults to "main".
        Raises:
            ValueError: If an unknown window is specified.
        """

        def _clear_window():
            match window:
                case "main":
                    # self._main_window.set_widgets([])
                    self._main_text.value = ""
                case "hand":
                    # self._hand_window.set_widgets([])
                    self._hand_text.value = ""
                case _:
                    raise ValueError(f"Unknown window: {window}")

        # Run the window clearing in a thread to avoid blocking
        await asyncio.to_thread(_clear_window)
        self._manager.compositor.redraw()


# Test code goes here
async def main():
    ui = UI()

    last_input = ""
    asyncio.create_task(ui.run())
    await ui.wait_until_running()
    while last_input.lower() != "exit":
        await ui.println("Enter 'exit' to quit.")
        last_input = await ui.input()
        await ui.println("You entered:", last_input)

    await ui.stop()

if __name__ == "__main__":
    asyncio.run(main())
