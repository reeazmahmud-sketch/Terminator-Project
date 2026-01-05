from modules.core.module_loader import TerminatorModule, ModuleContext

class HelloWorldModule(TerminatorModule):
    def on_load(self):
        self.context.log("Hello World Module Loaded!")
        self.context.register_command("hello", self.cmd_hello)

    def on_enable(self):
        self.context.log("Hello World Module Enabled")

    def on_disable(self):
        self.context.log("Hello World Module Disabled")

    def cmd_hello(self, args):
        self.context.log("Hello from the external module! 👋")
        if args:
            self.context.log(f"You said: {' '.join(args)}")

