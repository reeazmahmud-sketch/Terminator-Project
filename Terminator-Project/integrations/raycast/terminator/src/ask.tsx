import { closeMainWindow, showHUD } from "@raycast/api";
import { execFile } from "child_process";

interface Arguments {
  query: string;
}

export default async function Command(props: { arguments: Arguments }) {
  const { query } = props.arguments;
  await closeMainWindow();

  // Escape single quotes for AppleScript string
  const safeQuery = query.replace(/'/g, "'\"'\"'");

  const script = `tell application "Terminal"
    activate
    do script "echo '${safeQuery}' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
  end tell`;

  execFile("/usr/bin/osascript", ["-e", script], (error) => {
    if (error) console.error("Ask error:", error);
  });

  await showHUD("Asked TERMINATOR");
}
