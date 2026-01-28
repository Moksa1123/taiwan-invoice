#!/usr/bin/env node

const { program } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const fs = require('fs');
const path = require('path');
const os = require('os');

const VERSION = '2.0.0';
const SKILL_NAME = 'taiwan-invoice';

// Supported AI platforms
const AI_TYPES = ['claude', 'cursor', 'antigravity', 'all'];

// Platform configurations
const PLATFORMS = {
  claude: {
    name: 'Claude Code',
    projectPath: '.claude/skills',
    globalPath: path.join(os.homedir(), '.claude', 'skills'),
    invocation: '/taiwan-invoice'
  },
  cursor: {
    name: 'Cursor',
    projectPath: '.cursor/skills',
    globalPath: path.join(os.homedir(), '.cursor', 'skills'),
    invocation: '/taiwan-invoice'
  },
  antigravity: {
    name: 'Google Antigravity',
    projectPath: '.agent/skills',
    globalPath: path.join(os.homedir(), '.gemini', 'antigravity', 'global_skills'),
    invocation: 'auto-activate'
  }
};

// Banner
function showBanner() {
  console.log('');
  console.log(chalk.cyan.bold('  Taiwan Invoice Skill'));
  console.log(chalk.dim('  Taiwan E-Invoice API integration for AI coding assistants'));
  console.log('');
}

// Copy directory recursively
function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return false;

  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    for (const file of fs.readdirSync(src)) {
      copyRecursive(path.join(src, file), path.join(dest, file));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
  return true;
}

// Install skill to a platform
async function installToPlatform(platform, options) {
  const config = PLATFORMS[platform];
  const targetBase = options.global ? config.globalPath : path.join(process.cwd(), config.projectPath);
  const targetPath = path.join(targetBase, SKILL_NAME);
  const assetsPath = path.join(__dirname, '..', 'assets', SKILL_NAME);

  const spinner = ora(`Installing to ${config.name}...`).start();

  // Check assets
  if (!fs.existsSync(assetsPath)) {
    spinner.fail(chalk.red(`Assets not found. Please reinstall: npm install -g taiwan-invoice-skill`));
    return false;
  }

  // Handle existing installation
  if (fs.existsSync(targetPath)) {
    if (!options.force) {
      spinner.warn(chalk.yellow(`${config.name} already installed. Use --force to overwrite.`));
      return false;
    }
    fs.rmSync(targetPath, { recursive: true, force: true });
  }

  // Create target directory
  if (!fs.existsSync(targetBase)) {
    fs.mkdirSync(targetBase, { recursive: true });
  }

  // Copy files
  if (copyRecursive(assetsPath, targetPath)) {
    spinner.succeed(chalk.green(`${config.name} installed successfully`));
    console.log(chalk.dim(`   ${targetPath}`));
    return true;
  } else {
    spinner.fail(chalk.red(`Failed to install ${config.name}`));
    return false;
  }
}

// Init command
async function initCommand(aiType, options) {
  showBanner();

  // Validate AI type
  if (!AI_TYPES.includes(aiType)) {
    console.log(chalk.red(`  Error: Invalid AI type "${aiType}"`));
    console.log(chalk.dim(`  Valid options: ${AI_TYPES.join(', ')}`));
    process.exit(1);
  }

  const platforms = aiType === 'all' ? Object.keys(PLATFORMS) : [aiType];
  let successCount = 0;

  for (const platform of platforms) {
    if (await installToPlatform(platform, options)) {
      successCount++;
    }
  }

  // Summary
  console.log('');
  if (successCount > 0) {
    console.log(chalk.green.bold('  Installation complete!'));
    console.log('');
    console.log(chalk.cyan('  Quick Start:'));

    for (const platform of platforms) {
      const config = PLATFORMS[platform];
      if (config.invocation === 'auto-activate') {
        console.log(chalk.dim(`    ${config.name}: Mention e-invoice topics (auto-activates)`));
      } else {
        console.log(chalk.dim(`    ${config.name}: Type ${config.invocation} or mention e-invoice topics`));
      }
    }

    console.log('');
    console.log(chalk.cyan('  Documentation:'));
    console.log(chalk.dim('    https://github.com/Moksa1123/taiwan-invoice'));
    console.log('');
  } else {
    console.log(chalk.yellow('  No installations were made.'));
    console.log('');
  }
}

// Setup CLI
program
  .name('taiwan-invoice')
  .description('Taiwan E-Invoice AI Skill installer')
  .version(VERSION, '-v, --version', 'Show version number');

program
  .command('init')
  .description('Install skill to your AI coding assistant')
  .requiredOption('-a, --ai <type>', `AI assistant type (${AI_TYPES.join(', ')})`)
  .option('-f, --force', 'Overwrite existing installation')
  .option('-g, --global', 'Install to global directory')
  .action((options) => {
    initCommand(options.ai, options);
  });

program
  .command('list')
  .description('List supported AI platforms')
  .action(() => {
    showBanner();
    console.log(chalk.cyan('  Supported Platforms:'));
    console.log('');
    for (const [key, config] of Object.entries(PLATFORMS)) {
      console.log(`    ${chalk.green(key.padEnd(15))} ${config.name}`);
      console.log(chalk.dim(`                    Project: ${config.projectPath}`));
      console.log(chalk.dim(`                    Global:  ${config.globalPath}`));
      console.log('');
    }
  });

program
  .command('info')
  .description('Show skill information')
  .action(() => {
    showBanner();
    console.log(chalk.cyan('  Skill Information:'));
    console.log('');
    console.log(`    ${chalk.dim('Name:')}        taiwan-invoice`);
    console.log(`    ${chalk.dim('Version:')}     ${VERSION}`);
    console.log(`    ${chalk.dim('Providers:')}   ECPay, SmilePay, Amego`);
    console.log(`    ${chalk.dim('Features:')}    Issue, Void, Allowance, Query, Print`);
    console.log(`    ${chalk.dim('License:')}     MIT`);
    console.log('');
    console.log(chalk.cyan('  Links:'));
    console.log(`    ${chalk.dim('GitHub:')}      https://github.com/Moksa1123/taiwan-invoice`);
    console.log(`    ${chalk.dim('npm:')}         https://www.npmjs.com/package/taiwan-invoice-skill`);
    console.log('');
  });

// Parse arguments
program.parse();

// Show help if no command
if (!process.argv.slice(2).length) {
  showBanner();
  program.outputHelp();
}
