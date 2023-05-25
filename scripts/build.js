const fs = require('fs-extra');
const path = require('path');
const chokidar = require('chokidar');

const srcDir = path.join(__dirname, '..', 'src');
const distDirFirefox = path.join(__dirname, '..', 'dist.firefox');
const distDirChrome = path.join(__dirname, '..', 'dist.chrome');

// srcディレクトリの内容をdistディレクトリにコピーする関数
async function copyFiles(srcDir, distDir) {
  try {
    await fs.emptyDir(distDir);
    await fs.copy(path.join(srcDir, 'icons/icon128.png'), path.join(distDir, 'icons/icon128.png'));
    console.log(`Files copied to ${distDir}`);
  } catch (err) {
    console.error('Error copying files:', err);
  }
}

const { exec } = require('child_process');

// Browserifyを実行する関数
function runBrowserify() {
  exec('npm run browserify', (error, stdout, stderr) => {
    if (error) {
      console.error('Error running Browserify:', error);
    } else {
      console.log('Browserify completed');
    }
  });
}

// ファイルの変更を監視して自動的に再ビルドする関数
// memo: ubuntu ` sudo sysctl fs.inotify.max_user_watches=102400 `
function watchFiles() {
  const watcher = chokidar.watch(srcDir, { persistent: true });
  watcher.on('all', (event, filePath) => {
    console.log(`File ${event}: ${filePath}`);
    build();
  });
}

// Firefox向けのビルド
async function buildFirefox() {
  await copyFiles(srcDir, distDirFirefox);
  // Firefox向けの特定の処理を行う場合は、ここに追加の処理を記述する
  await fs.copy(path.join(srcDir, 'manifest.firefox.json'), path.join(distDirFirefox, 'manifest.json'));
  console.log('Firefox build completed');
}

// Chrome向けのビルド
async function buildChrome() {
  await copyFiles(srcDir, distDirChrome);
  // Chrome向けの特定の処理を行う場合は、ここに追加の処理を記述する
  await fs.copy(path.join(srcDir, 'manifest.chrome.json'), path.join(distDirChrome, 'manifest.json'));
  await fs.copy(path.join(srcDir, 'background.js'), path.join(distDirChrome, 'background.js'));
  runBrowserify();
  console.log('Chrome build completed');
}

// メインのビルド関数
async function build() {
  try {
    // Firefox向けのビルドを実行
    await buildFirefox();
    // Chrome向けのビルドを実行
    await buildChrome();
  } catch (err) {
    console.error('Error building extensions:', err);
  }
}

// ビルドを実行
build();

if (process.argv.length > 2){
  if('--watch' !== process.argv[2]) {
    console.error(`Usage: node build.js --watch`);
    process.exit(1);
  }
  // ファイルの変更を監視して自動的に再ビルド
  watchFiles();
}
