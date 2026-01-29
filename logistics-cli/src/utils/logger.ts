import chalk from 'chalk';

export const logger = {
  info: (msg: string) => console.log(chalk.blue('info'), msg),
  success: (msg: string) => console.log(chalk.green('success'), msg),
  warn: (msg: string) => console.log(chalk.yellow('warn'), msg),
  error: (msg: string) => console.log(chalk.red('error'), msg),

  title: (msg: string) => {
    console.log();
    console.log(chalk.bold.red('  ████████╗') + chalk.bold.yellow('  █████╗ ') + chalk.bold.green(' ██╗') + chalk.bold.cyan('  ██╗    ██╗') + chalk.bold.blue('  █████╗ ') + chalk.bold.magenta(' ███╗   ██╗'));
    console.log(chalk.bold.red('  ╚══██╔══╝') + chalk.bold.yellow(' ██╔══██╗') + chalk.bold.green(' ██║') + chalk.bold.cyan('  ██║    ██║') + chalk.bold.blue(' ██╔══██╗') + chalk.bold.magenta(' ████╗  ██║'));
    console.log(chalk.bold.red('     ██║   ') + chalk.bold.yellow(' ███████║') + chalk.bold.green(' ██║') + chalk.bold.cyan('  ██║ █╗ ██║') + chalk.bold.blue(' ███████║') + chalk.bold.magenta(' ██╔██╗ ██║'));
    console.log(chalk.bold.red('     ██║   ') + chalk.bold.yellow(' ██╔══██║') + chalk.bold.green(' ██║') + chalk.bold.cyan('  ██║███╗██║') + chalk.bold.blue(' ██╔══██║') + chalk.bold.magenta(' ██║╚██╗██║'));
    console.log(chalk.bold.red('     ██║   ') + chalk.bold.yellow(' ██║  ██║') + chalk.bold.green(' ██║') + chalk.bold.cyan('  ╚███╔███╔╝') + chalk.bold.blue(' ██║  ██║') + chalk.bold.magenta(' ██║ ╚████║'));
    console.log(chalk.bold.red('     ╚═╝   ') + chalk.bold.yellow(' ╚═╝  ╚═╝') + chalk.bold.green(' ╚═╝') + chalk.bold.cyan('   ╚══╝╚══╝ ') + chalk.bold.blue(' ╚═╝  ╚═╝') + chalk.bold.magenta(' ╚═╝  ╚═══╝'));
    console.log();
    console.log(chalk.bold.cyan('                    物流整合技能包'));
    console.log(chalk.bold.yellow(`                    ${msg}`));
    console.log();
  },

  box: (msg: string) => {
    // Calculate visual width (CJK characters count as 2)
    const getVisualWidth = (str: string) => {
      let width = 0;
      for (const char of str) {
        // CJK Unified Ideographs, Hiragana, Katakana, Hangul, CJK Punctuation
        const code = char.charCodeAt(0);
        if ((code >= 0x4E00 && code <= 0x9FFF) ||  // CJK Ideographs
            (code >= 0x3000 && code <= 0x303F) ||  // CJK Symbols and Punctuation
            (code >= 0x3040 && code <= 0x309F) ||  // Hiragana
            (code >= 0x30A0 && code <= 0x30FF) ||  // Katakana
            (code >= 0xAC00 && code <= 0xD7AF) ||  // Hangul
            (code >= 0xFF00 && code <= 0xFFEF)) {  // Fullwidth
          width += 2;
        } else {
          width += 1;
        }
      }
      return width;
    };

    const lines = msg.split('\n');
    // Remove all ANSI escape codes (more comprehensive pattern)
    const stripAnsi = (str: string) => str.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '');
    const maxWidth = Math.max(...lines.map(l => getVisualWidth(stripAnsi(l))));
    const boxWidth = maxWidth + 2; // +2 for the spaces inside │ content │

    console.log();
    console.log(chalk.green('╭' + '─'.repeat(boxWidth) + '╮'));
    const headerText = '  完成  ';
    const headerWidth = getVisualWidth(headerText);
    const headerPadding = boxWidth - headerWidth;
    console.log(chalk.green('│') + chalk.bold.green(headerText) + ' '.repeat(headerPadding) + chalk.green('│'));
    console.log(chalk.green('├' + '─'.repeat(boxWidth) + '┤'));

    lines.forEach(line => {
      const cleanLine = stripAnsi(line);
      const visualWidth = getVisualWidth(cleanLine);
      const padding = boxWidth - visualWidth - 2;
      console.log(chalk.green('│ ') + line + ' '.repeat(Math.max(0, padding)) + chalk.green(' │'));
    });

    console.log(chalk.green('╰' + '─'.repeat(boxWidth) + '╯'));
    console.log();
  },

  dim: (msg: string) => console.log(chalk.dim(msg)),
};
