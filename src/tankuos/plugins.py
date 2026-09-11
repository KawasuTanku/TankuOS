"""TankuOS plugin widgets."""

from textual.widgets import Static, Input
from textual.containers import Vertical

from tankuos.theme import theme


class ShellPane(Vertical):
    """Simple interactive shell plugin — Input + history display."""
    
    CSS = """
    ShellPane {
        height: 1fr;
        padding: 0;
    }
    
    .shell-output {
        height: 1fr;
        overflow-y: auto;
        padding: 0 1;
    }
    
    .shell-input {
        height: 1;
        border: none;
        background: $bg_inset;
    }
    """
    
    def compose(self):
        yield Static("", classes="shell-output", id="output")
        yield Input(placeholder="$ ", classes="shell-input", id="input")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        output = self.query_one("#output", Static)
        
        if cmd == "exit":
            self.remove()
            return
        
        if cmd == "help":
            content = "Commands: help, exit, ls, pwd, date, whoami, echo\n"
        elif cmd == "ls":
            content = "MailVault  monster  pane.py  palettes.py  Retirement  shell.py  tests  theme.py\n"
        elif cmd == "pwd":
            content = "/home/hermes\n"
        elif cmd == "date":
            import datetime
            content = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n")
        elif cmd == "whoami":
            content = "hermes\n"
        elif cmd.startswith("echo "):
            content = cmd[5:] + "\n"
        elif cmd == "":
            content = ""
        else:
            content = f"{cmd}: command not found. Try 'help'\n"
        
        # Use renderable content (cast to str)
        current = str(output.render())
        if current == "None" or not current:
            current = ""
        output.update(current + f"$ {cmd}\n{content}")
        event.input.value = ""
