#!/usr/bin/env python3
"""
Test script to verify taiwan-invoice CLI installation works for all platforms.

Usage:
    python test-install.py              # Test all platforms
    python test-install.py claude       # Test specific platform
    python test-install.py --offline    # Test with offline mode
"""

import subprocess
import sys
import os
import json
import tempfile
from pathlib import Path

# All supported platforms
PLATFORMS = [
    'claude',
    'cursor',
    'windsurf',
    'copilot',
    'antigravity',
    'kiro',
    'codex',
    'qoder',
    'roocode',
    'gemini',
    'trae',
    'opencode',
    'continue',
    'codebuddy',
]

# Expected files after installation
EXPECTED_FILES = [
    'SKILL.md',
    'EXAMPLES.md',
    'references/ECPAY_API_REFERENCE.md',
    'references/SMILEPAY_API_REFERENCE.md',
    'references/AMEGO_API_REFERENCE.md',
    'scripts/generate-invoice-service.py',
    'scripts/test-invoice-amounts.py',
]


def load_platform_config(platform: str, templates_dir: Path) -> dict:
    """Load platform configuration from JSON file."""
    config_path = templates_dir / 'platforms' / f'{platform}.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_install_path(platform: str, base_dir: str, templates_dir: Path) -> str:
    """Get the expected installation path for a platform from JSON config."""
    config = load_platform_config(platform, templates_dir)

    if config and 'folderStructure' in config:
        root = config['folderStructure'].get('root', '')
        skill_path = config['folderStructure'].get('skillPath', '')
        return os.path.join(base_dir, root, skill_path)

    # Fallback to default pattern
    return os.path.join(base_dir, f'.{platform}', 'skills', 'taiwan-invoice')


def test_platform(platform: str, cli_path: str, templates_dir: Path, offline: bool = False) -> tuple[bool, str]:
    """Test installation for a single platform."""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Build command
            cmd = ['node', cli_path, 'init', '--ai', platform, '--force']
            if offline:
                cmd.append('--offline')

            # Run installation with UTF-8 encoding
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode != 0:
                return False, f"CLI error: {result.stderr[:100]}"

            # Check expected files
            install_path = get_install_path(platform, temp_dir, templates_dir)

            if not os.path.exists(install_path):
                # Try to find what was actually created
                for root, dirs, files in os.walk(temp_dir):
                    if 'SKILL.md' in files:
                        install_path = root
                        break
                else:
                    return False, f"Install path not found: {install_path}"

            missing_files = []
            for expected_file in EXPECTED_FILES:
                file_path = os.path.join(install_path, expected_file)
                if not os.path.exists(file_path):
                    missing_files.append(expected_file)

            if missing_files:
                return False, f"Missing: {', '.join(missing_files[:3])}"

            # Check SKILL.md has content
            skill_path = os.path.join(install_path, 'SKILL.md')
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) < 1000:
                    return False, f"SKILL.md too small ({len(content)} bytes)"
                if 'taiwan-invoice' not in content.lower() and 'e-invoice' not in content.lower():
                    return False, "SKILL.md missing expected content"

            return True, "OK"

        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)[:50]


def main():
    # Parse arguments
    platforms_to_test = PLATFORMS
    offline = '--offline' in sys.argv

    # Check for specific platform
    for arg in sys.argv[1:]:
        if arg in PLATFORMS:
            platforms_to_test = [arg]
            break

    # Find CLI path and templates dir
    script_dir = Path(__file__).parent.parent
    cli_path = script_dir / 'dist' / 'index.js'
    templates_dir = script_dir / 'assets' / 'templates'

    if not cli_path.exists():
        print("[ERROR] CLI not built. Run 'npm run build' first.")
        sys.exit(1)

    print("=" * 60)
    print("Taiwan Invoice CLI Installation Test")
    print("=" * 60)
    print(f"CLI Path: {cli_path}")
    print(f"Offline Mode: {offline}")
    print(f"Platforms: {len(platforms_to_test)}")
    print("=" * 60)
    print()

    results = []

    for platform in platforms_to_test:
        print(f"Testing {platform}...", end=' ', flush=True)
        success, message = test_platform(platform, str(cli_path), templates_dir, offline)
        results.append((platform, success, message))

        if success:
            print("[OK]")
        else:
            print(f"[FAIL] {message}")

    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed

    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")

    if failed > 0:
        print()
        print("Failed platforms:")
        for platform, success, message in results:
            if not success:
                print(f"  - {platform}: {message}")
        sys.exit(1)
    else:
        print()
        print("[OK] All platforms passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
