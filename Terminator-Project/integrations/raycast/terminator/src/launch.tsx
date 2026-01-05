import { closeMainWindow, showHUD } from "@raycast/api";
import { execFile } from "child_process";

export default async function Command() {
  await closeMainWindow();

  // Using execFile with osascript is safe - no shell injection possible
  const script = `tell application "Terminal"
    activate
    do script "cd ~/Desktop/Terminator-Project && python3 terminator_universal_cli.py"
  end tell`;

  execFile("/usr/bin/osascript", ["-e", script], (error) => {
    if (error) console.error("Launch error:", error);
  });

  await showHUD("TERMINATOR Launched");
}
