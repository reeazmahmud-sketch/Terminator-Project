import { closeMainWindow, showHUD } from "@raycast/api";
import { execFile } from "child_process";

export default async function Command() {
  await closeMainWindow();

  const script = `tell application "Terminal"
    activate
    do script "echo /agents | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
  end tell`;

  execFile("/usr/bin/osascript", ["-e", script], (error) => {
    if (error) console.error("Agents error:", error);
  });

  await showHUD("Listing Agents");
}
