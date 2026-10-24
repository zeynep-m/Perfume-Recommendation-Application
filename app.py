"""Application composition and lifecycle."""


class PerfumeApplication:
    """Compose the recommendation window and own the application lifecycle."""

    def __init__(self):
        from application_window import create_window

        self.window = create_window()

    def run(self):
        """Start the Tk event loop."""
        self.window.mainloop()


def main():
    PerfumeApplication().run()
