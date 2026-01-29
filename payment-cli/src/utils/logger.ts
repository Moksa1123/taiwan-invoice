import chalk from 'chalk';

export const logger = {
  title(text: string): void {
    console.log();
    console.log(chalk.bold.cyan(`  ${text}`));
    console.log();
  },

  info(text: string): void {
    console.log(chalk.blue('  ℹ'), text);
  },

  success(text: string): void {
    console.log(chalk.green('  ✓'), text);
  },

  warn(text: string): void {
    console.log(chalk.yellow('  ⚠'), text);
  },

  error(text: string): void {
    console.log(chalk.red('  ✖'), text);
  },
};
