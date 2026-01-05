// TERMINATOR Terminal Homepage - Interactive Terminal

class TerminalHomepage {
    constructor() {
        this.terminal = document.getElementById('terminal');
        this.input = document.getElementById('command-input');
        this.suggestions = document.getElementById('suggestions');

        this.history = JSON.parse(localStorage.getItem('terminalHistory')) || [];
        this.historyIndex = this.history.length;
        this.currentInput = '';

        this.bookmarks = JSON.parse(localStorage.getItem('terminalBookmarks')) || this.getDefaultBookmarks();

        this.commands = this.initializeCommands();
        this.init();
    }

    init() {
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.input.addEventListener('input', () => this.handleInput());
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);

        // Focus input on click anywhere
        document.addEventListener('click', () => this.input.focus());
    }

    // Sanitize user input to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
        const dateStr = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        document.getElementById('current-time').textContent = `${dateStr} ${timeStr}`;
    }

    handleKeyDown(e) {
        // Enter key
        if (e.key === 'Enter') {
            e.preventDefault();
            const command = this.input.value.trim();
            if (command) {
                this.executeCommand(command);
                this.history.push(command);
                localStorage.setItem('terminalHistory', JSON.stringify(this.history));
                this.historyIndex = this.history.length;
            }
            this.input.value = '';
            this.suggestions.classList.remove('active');
        }

        // Arrow up - previous command
        else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (this.historyIndex > 0) {
                if (this.historyIndex === this.history.length) {
                    this.currentInput = this.input.value;
                }
                this.historyIndex--;
                this.input.value = this.history[this.historyIndex];
            }
        }

        // Arrow down - next command
        else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (this.historyIndex < this.history.length) {
                this.historyIndex++;
                this.input.value = this.historyIndex === this.history.length
                    ? this.currentInput
                    : this.history[this.historyIndex];
            }
        }

        // Tab - autocomplete
        else if (e.key === 'Tab') {
            e.preventDefault();
            const suggestions = this.getSuggestions(this.input.value);
            if (suggestions.length > 0) {
                this.input.value = suggestions[0].command;
            }
        }

        // Escape - clear suggestions
        else if (e.key === 'Escape') {
            this.suggestions.classList.remove('active');
        }
    }

    handleInput() {
        const value = this.input.value;
        if (value.length > 0) {
            this.showSuggestions(value);
        } else {
            this.suggestions.classList.remove('active');
        }
    }

    getSuggestions(input) {
        const lower = input.toLowerCase();
        return Object.entries(this.commands)
            .filter(([cmd]) => cmd.startsWith(lower))
            .map(([cmd, data]) => ({ command: cmd, description: data.description }));
    }

    showSuggestions(input) {
        const suggestions = this.getSuggestions(input);

        if (suggestions.length > 0) {
            this.suggestions.innerHTML = '';
            suggestions.slice(0, 5).forEach((s, index) => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';

                const cmdSpan = document.createElement('span');
                cmdSpan.className = 'suggestion-command';
                cmdSpan.textContent = s.command;

                const descSpan = document.createElement('span');
                descSpan.className = 'suggestion-description';
                descSpan.textContent = s.description;

                item.appendChild(cmdSpan);
                item.appendChild(descSpan);

                item.addEventListener('click', () => {
                    this.input.value = s.command + ' ';
                    this.input.focus();
                    this.suggestions.classList.remove('active');
                });

                this.suggestions.appendChild(item);
            });

            this.suggestions.classList.add('active');
        } else {
            this.suggestions.classList.remove('active');
        }
    }

    executeCommand(input) {
        // Add command to terminal (sanitized)
        this.addOutputSafe('user-input', `$ ${input}`);

        const parts = input.split(' ');
        const cmd = parts[0].toLowerCase();
        const args = parts.slice(1);

        if (this.commands[cmd]) {
            this.commands[cmd].action(args);
        } else {
            // Try as search query
            if (input.includes(' ') || !cmd.startsWith('/')) {
                this.commands.search.action([input]);
            } else {
                this.addOutputSafe('error-text', `Command not found: ${cmd}`);
                this.addOutputSafe('dim-text', "Type 'help' for available commands");
            }
        }

        this.scrollToBottom();
    }

    // Safe method to add output with text content
    addOutputSafe(className, text) {
        const line = document.createElement('div');
        line.className = 'output-line';
        const span = document.createElement('span');
        span.className = className;
        span.textContent = text;
        line.appendChild(span);
        this.terminal.appendChild(line);
    }

    // Add structured HTML output (for trusted templates only)
    addOutputHTML(htmlContent) {
        const line = document.createElement('div');
        line.className = 'output-line command-output';
        line.innerHTML = htmlContent;
        this.terminal.appendChild(line);
    }

    scrollToBottom() {
        this.terminal.scrollTop = this.terminal.scrollHeight;
    }

    initializeCommands() {
        return {
            help: {
                description: 'Show all available commands',
                action: () => {
                    const helpHTML = `
                        <h3 class="success-text">Available Commands:</h3>
                        <br>
                        <table>
                            <tr><td class="success-text">help</td><td class="dim-text">Show this help message</td></tr>
                            <tr><td class="success-text">clear</td><td class="dim-text">Clear terminal screen</td></tr>
                            <tr><td class="success-text">search &lt;query&gt;</td><td class="dim-text">Search Google</td></tr>
                            <tr><td class="success-text">go &lt;url&gt;</td><td class="dim-text">Navigate to URL</td></tr>
                            <tr><td class="success-text">bookmark [add|list]</td><td class="dim-text">Manage bookmarks</td></tr>
                            <tr><td class="success-text">weather [city]</td><td class="dim-text">Check weather</td></tr>
                            <tr><td class="success-text">time</td><td class="dim-text">Show current time</td></tr>
                            <tr><td class="success-text">reddit [r/subreddit]</td><td class="dim-text">Open Reddit</td></tr>
                            <tr><td class="success-text">youtube [search]</td><td class="dim-text">Search YouTube</td></tr>
                            <tr><td class="success-text">github [user/repo]</td><td class="dim-text">Open GitHub</td></tr>
                            <tr><td class="success-text">translate &lt;text&gt;</td><td class="dim-text">Translate text</td></tr>
                            <tr><td class="success-text">news [category]</td><td class="dim-text">Latest news</td></tr>
                            <tr><td class="success-text">terminator &lt;cmd&gt;</td><td class="dim-text">Send to TERMINATOR CLI</td></tr>
                            <tr><td class="success-text">history</td><td class="dim-text">Show command history</td></tr>
                        </table>
                        <br>
                        <span class="dim-text">You can also type anything to search Google directly!</span>
                    `;
                    this.addOutputHTML(helpHTML);
                }
            },

            clear: {
                description: 'Clear the terminal',
                action: () => {
                    this.terminal.innerHTML = '';
                }
            },

            search: {
                description: 'Search Google',
                action: (args) => {
                    const query = args.join(' ');
                    this.addOutputSafe('success-text', `🔍 Searching Google for: ${query}`);
                    setTimeout(() => {
                        window.location.href = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
                    }, 500);
                }
            },

            go: {
                description: 'Navigate to a URL',
                action: (args) => {
                    let url = args.join('');
                    if (!url.startsWith('http')) {
                        url = 'https://' + url;
                    }
                    this.addOutputSafe('success-text', `→ Opening: ${url}`);
                    setTimeout(() => {
                        window.location.href = url;
                    }, 500);
                }
            },

            bookmark: {
                description: 'Manage bookmarks',
                action: (args) => {
                    if (args[0] === 'add' && args.length >= 3) {
                        const name = args[1];
                        const url = args[2];
                        this.bookmarks[name] = url;
                        localStorage.setItem('terminalBookmarks', JSON.stringify(this.bookmarks));
                        this.addOutputSafe('success-text', `✓ Bookmark added: ${name} → ${url}`);
                    } else if (args[0] === 'list' || args.length === 0) {
                        this.addOutputHTML('<h3 class="success-text">📚 Bookmarks:</h3>');
                        Object.entries(this.bookmarks).forEach(([name, url]) => {
                            const line = document.createElement('div');
                            line.className = 'output-line';

                            const nameSpan = document.createElement('span');
                            nameSpan.className = 'dim-text';
                            nameSpan.textContent = `  ${name} → `;

                            const link = document.createElement('a');
                            link.href = url;
                            link.target = '_blank';
                            link.textContent = url;

                            line.appendChild(nameSpan);
                            line.appendChild(link);
                            this.terminal.appendChild(line);
                        });
                    } else if (this.bookmarks[args[0]]) {
                        window.location.href = this.bookmarks[args[0]];
                    } else {
                        this.addOutputSafe('error-text', 'Usage: bookmark [add name url | list | bookmark-name]');
                    }
                }
            },

            weather: {
                description: 'Check weather',
                action: (args) => {
                    const city = args.join(' ') || 'current location';
                    this.addOutputSafe('success-text', `🌤️  Opening weather for: ${city}`);
                    setTimeout(() => {
                        window.location.href = `https://www.google.com/search?q=weather+${encodeURIComponent(args.join(' '))}`;
                    }, 500);
                }
            },

            time: {
                description: 'Show current time',
                action: () => {
                    const now = new Date();
                    this.addOutputSafe('success-text', `🕐 Current time: ${now.toLocaleString()}`);
                    this.addOutputSafe('dim-text', `   Unix timestamp: ${Math.floor(now.getTime() / 1000)}`);
                }
            },

            reddit: {
                description: 'Open Reddit',
                action: (args) => {
                    const subreddit = args[0] || '';
                    const url = subreddit
                        ? `https://reddit.com/${subreddit}`
                        : 'https://reddit.com';
                    this.addOutputSafe('success-text', `→ Opening Reddit${subreddit ? ': ' + subreddit : ''}`);
                    setTimeout(() => window.location.href = url, 500);
                }
            },

            youtube: {
                description: 'Search YouTube',
                action: (args) => {
                    if (args.length > 0) {
                        const query = args.join(' ');
                        this.addOutputSafe('success-text', `🎥 Searching YouTube: ${query}`);
                        setTimeout(() => {
                            window.location.href = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;
                        }, 500);
                    } else {
                        window.location.href = 'https://youtube.com';
                    }
                }
            },

            github: {
                description: 'Open GitHub',
                action: (args) => {
                    const repo = args.join('/');
                    const url = repo
                        ? `https://github.com/${repo}`
                        : 'https://github.com';
                    this.addOutputSafe('success-text', `→ Opening GitHub${repo ? ': ' + repo : ''}`);
                    setTimeout(() => window.location.href = url, 500);
                }
            },

            translate: {
                description: 'Translate text',
                action: (args) => {
                    const text = args.join(' ');
                    this.addOutputSafe('success-text', `🌐 Translating: ${text}`);
                    setTimeout(() => {
                        window.location.href = `https://translate.google.com/?text=${encodeURIComponent(text)}`;
                    }, 500);
                }
            },

            news: {
                description: 'Latest news',
                action: (args) => {
                    const category = args[0] || 'top';
                    this.addOutputSafe('success-text', `📰 Opening news: ${category}`);
                    setTimeout(() => {
                        window.location.href = 'https://news.google.com';
                    }, 500);
                }
            },

            terminator: {
                description: 'Send command to TERMINATOR',
                action: (args) => {
                    const command = args.join(' ');
                    this.addOutputSafe('success-text', `⚡ Sending to TERMINATOR: ${command}`);
                    this.addOutputSafe('warning-text', 'Note: This requires TERMINATOR backend running');
                    // In production, this would make an API call to TERMINATOR
                    // fetch('http://localhost:8000/api/command', { method: 'POST', body: JSON.stringify({ command }) })
                }
            },

            history: {
                description: 'Show command history',
                action: () => {
                    this.addOutputHTML('<h3 class="success-text">Command History:</h3>');
                    if (this.history.length > 0) {
                        this.history.slice(-20).forEach((cmd, i) => {
                            this.addOutputSafe('dim-text', `  ${i + 1}. ${cmd}`);
                        });
                    } else {
                        this.addOutputSafe('dim-text', 'No history yet');
                    }
                }
            }
        };
    }

    getDefaultBookmarks() {
        return {
            gh: 'https://github.com',
            gmail: 'https://mail.google.com',
            drive: 'https://drive.google.com',
            yt: 'https://youtube.com',
            reddit: 'https://reddit.com',
            twitter: 'https://twitter.com',
            linkedin: 'https://linkedin.com',
            netflix: 'https://netflix.com',
            terminator: 'http://localhost:8000'
        };
    }
}

// Initialize terminal when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TerminalHomepage();
});
