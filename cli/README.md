# taiwan-invoice-skill

CLI to install Taiwan E-Invoice skill for AI coding assistants.

## Installation

```bash
npm install -g taiwan-invoice-skill
```

## Usage

```bash
# Install for specific AI assistant
taiwan-invoice init --ai claude        # Claude Code
taiwan-invoice init --ai cursor        # Cursor
taiwan-invoice init --ai windsurf      # Windsurf
taiwan-invoice init --ai antigravity   # Antigravity
taiwan-invoice init --ai copilot       # GitHub Copilot
taiwan-invoice init --ai kiro          # Kiro
taiwan-invoice init --ai codex         # Codex CLI
taiwan-invoice init --ai roocode       # Roo Code
taiwan-invoice init --ai qoder         # Qoder
taiwan-invoice init --ai gemini        # Gemini CLI
taiwan-invoice init --ai trae          # Trae
taiwan-invoice init --ai opencode      # OpenCode
taiwan-invoice init --ai continue      # Continue
taiwan-invoice init --ai codebuddy     # CodeBuddy
taiwan-invoice init --ai all           # All assistants

# Options
taiwan-invoice init --offline          # Skip GitHub download, use bundled assets only
taiwan-invoice init --force            # Overwrite existing files
taiwan-invoice init --global           # Install to global directory

# Other commands
taiwan-invoice list                    # List supported platforms
taiwan-invoice info                    # Show skill information
taiwan-invoice versions                # List available versions
taiwan-invoice update                  # Check for updates
```

## How It Works

By default, `taiwan-invoice init` tries to download the latest release from GitHub to ensure you get the most up-to-date version. If the download fails (network error, rate limit), it automatically falls back to the bundled assets included in the CLI package.

Use `--offline` to skip the GitHub download and use bundled assets directly.

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run locally
node dist/index.js --help
```

## License

MIT
