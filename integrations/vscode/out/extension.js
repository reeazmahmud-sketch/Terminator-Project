"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const TERMINATOR_PATH = path.join(os.homedir(), 'Desktop', 'Terminator-Project');
const CLI_PATH = path.join(TERMINATOR_PATH, 'terminator_universal_cli.py');
function activate(context) {
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
        if (!editor)
            return;
        const selection = editor.document.getText(editor.selection);
        const language = editor.document.languageId;
        await askTerminator(`Explain this ${language} code in detail:\n\n${selection}`);
    });
    // Review selected code
    const reviewCodeCmd = vscode.commands.registerCommand('terminator.reviewCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor)
            return;
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
    context.subscriptions.push(launchCmd, askSelectedCmd, askInputCmd, explainCodeCmd, reviewCodeCmd, agentsCmd, healthCmd);
}
async function askTerminator(query) {
    const terminal = vscode.window.createTerminal({
        name: 'TERMINATOR Query',
        cwd: TERMINATOR_PATH
    });
    // Escape the query for shell
    const escapedQuery = query.replace(/'/g, "'\"'\"'");
    terminal.sendText(`echo '${escapedQuery}' | python3 terminator_universal_cli.py`);
    terminal.show();
}
async function runTerminatorCommand(command) {
    const terminal = vscode.window.createTerminal({
        name: 'TERMINATOR',
        cwd: TERMINATOR_PATH
    });
    terminal.sendText(`echo '${command}' | python3 terminator_universal_cli.py`);
    terminal.show();
}
function deactivate() {
    console.log('TERMINATOR AI extension deactivated');
}
//# sourceMappingURL=extension.js.map