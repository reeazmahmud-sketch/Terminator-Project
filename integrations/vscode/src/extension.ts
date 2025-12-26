import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';
import * as os from 'os';

const TERMINATOR_PATH = path.join(os.homedir(), 'Desktop', 'Terminator-Project');
const CLI_PATH = path.join(TERMINATOR_PATH, 'terminator_universal_cli.py');

export function activate(context: vscode.ExtensionContext) {
    console.log('TERMINATOR AI extension activated');

    // Launch TERMINATOR in integrated terminal
    const launchCmd = vscode.commands.registerCommand('terminator.launch', () => {
        const terminal = vscode.window.createTerminal({
            name: 'TERMINATOR',
            cwd: TERMINATOR_PATH
        });
        terminal.sendText('python3 terminator_universal_cli.py');
        terminal.show();
    });

    // Ask about selected text
    const askSelectedCmd = vscode.commands.registerCommand('terminator.askSelected', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No text selected');
            return;
        }

        const selection = editor.document.getText(editor.selection);
        if (!selection) {
            vscode.window.showWarningMessage('No text selected');
            return;
        }

        await askTerminator(`Explain this code:\n\n${selection}`);
    });

    // Ask with input box
    const askInputCmd = vscode.commands.registerCommand('terminator.askInput', async () => {
        const query = await vscode.window.showInputBox({
            prompt: 'What would you like to ask TERMINATOR?',
            placeHolder: 'Enter your question...'
        });

        if (query) {
            await askTerminator(query);
        }
    });

    // Explain selected code
    const explainCodeCmd = vscode.commands.registerCommand('terminator.explainCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        const selection = editor.document.getText(editor.selection);
        const language = editor.document.languageId;

        await askTerminator(`Explain this ${language} code in detail:\n\n${selection}`);
    });

    // Review selected code
    const reviewCodeCmd = vscode.commands.registerCommand('terminator.reviewCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        const selection = editor.document.getText(editor.selection);
        const language = editor.document.languageId;

        await askTerminator(`Review this ${language} code for bugs, security issues, and improvements:\n\n${selection}`);
    });

    // List agents
    const agentsCmd = vscode.commands.registerCommand('terminator.agents', async () => {
        await runTerminatorCommand('/agents');
    });

    // Health check
    const healthCmd = vscode.commands.registerCommand('terminator.health', async () => {
        await runTerminatorCommand('/healthCheck');
    });

    context.subscriptions.push(
        launchCmd,
        askSelectedCmd,
        askInputCmd,
        explainCodeCmd,
        reviewCodeCmd,
        agentsCmd,
        healthCmd
    );
}

async function askTerminator(query: string): Promise<void> {
    const terminal = vscode.window.createTerminal({
        name: 'TERMINATOR Query',
        cwd: TERMINATOR_PATH
    });

    // Escape the query for shell
    const escapedQuery = query.replace(/'/g, "'\"'\"'");

    terminal.sendText(`echo '${escapedQuery}' | python3 terminator_universal_cli.py`);
    terminal.show();
}

async function runTerminatorCommand(command: string): Promise<void> {
    const terminal = vscode.window.createTerminal({
        name: 'TERMINATOR',
        cwd: TERMINATOR_PATH
    });

    terminal.sendText(`echo '${command}' | python3 terminator_universal_cli.py`);
    terminal.show();
}

export function deactivate() {
    console.log('TERMINATOR AI extension deactivated');
}
