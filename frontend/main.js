/**
 * Electron 主进程
 * EM-Automate 桌面应用
 */
const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// 全局变量
let mainWindow;
let backendProcess;
const isDev = process.env.NODE_ENV === 'development';
const isWin = process.platform === 'win32';

// 后端服务器配置
const BACKEND_CONFIG = {
    host: '127.0.0.1',
    port: 8000,
    script: isDev
        ? path.join(__dirname, '..', 'backend', 'api_server.py')
        : path.join(__dirname, 'backend', 'api_server.py')
};

function createWindow() {
    // 创建浏览器窗口
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 1000,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        show: false,
        titleBarStyle: 'default'
    });

    // 加载应用
    if (isDev) {
        // 开发模式加载本地服务器
        mainWindow.loadURL('http://localhost:5173');
        // 打开开发者工具
        mainWindow.webContents.openDevTools();
    } else {
        // 生产模式加载打包后的文件
        mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
    }

    // 窗口准备好后显示
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        mainWindow.focus();
    });

    // 处理窗口关闭
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // 处理外部链接
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

function startBackend() {
    return new Promise((resolve, reject) => {
        console.log('启动后端服务器...');

        // 检查Python环境
        const pythonCmd = isWin ? 'python' : 'python3';

        // 启动后端进程
        backendProcess = spawn(pythonCmd, [BACKEND_CONFIG.script], {
            stdio: ['pipe', 'pipe', 'pipe'],
            cwd: path.dirname(BACKEND_CONFIG.script)
        });

        let output = '';
        let errorOutput = '';

        backendProcess.stdout.on('data', (data) => {
            output += data.toString();
            console.log('Backend:', data.toString().trim());

            // 检查是否成功启动
            if (output.includes('Uvicorn running on')) {
                console.log('后端服务器启动成功');
                resolve();
            }
        });

        backendProcess.stderr.on('data', (data) => {
            errorOutput += data.toString();
            console.error('Backend Error:', data.toString().trim());
        });

        backendProcess.on('close', (code) => {
            if (code !== 0) {
                console.error(`后端服务器退出，代码: ${code}`);
                console.error('错误输出:', errorOutput);
                reject(new Error(`后端服务器启动失败: ${errorOutput}`));
            }
        });

        backendProcess.on('error', (error) => {
            console.error('后端进程错误:', error);
            reject(error);
        });

        // 超时处理
        setTimeout(() => {
            if (!output.includes('Uvicorn running on')) {
                backendProcess.kill();
                reject(new Error('后端服务器启动超时'));
            }
        }, 10000);
    });
}

async function initializeApp() {
    try {
        // 启动后端服务器
        await startBackend();

        // 创建主窗口
        createWindow();

        console.log('应用初始化完成');
    } catch (error) {
        console.error('应用初始化失败:', error);

        // 显示错误对话框
        dialog.showErrorBox(
            '启动失败',
            `无法启动后端服务器:\n${error.message}\n\n请确保Python环境已正确安装。`
        );

        // 退出应用
        app.quit();
    }
}

// 应用事件处理
app.whenReady().then(initializeApp);

app.on('window-all-closed', () => {
    // 在Windows和Linux上，当所有窗口关闭时退出应用
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    // 在macOS上，当点击dock图标且没有其他窗口打开时重新创建窗口
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('before-quit', () => {
    // 应用退出前关闭后端服务器
    if (backendProcess) {
        console.log('关闭后端服务器...');
        backendProcess.kill('SIGTERM');
    }
});

// IPC 处理程序
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});

ipcMain.handle('get-backend-config', () => {
    return BACKEND_CONFIG;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, options);
    return result;
});

ipcMain.handle('show-error-box', (event, title, content) => {
    dialog.showErrorBox(title, content);
});

// 处理未捕获的异常
process.on('uncaughtException', (error) => {
    console.error('未捕获的异常:', error);
    if (mainWindow) {
        dialog.showErrorBox('应用错误', `发生未预期的错误:\n${error.message}`);
    }
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('未处理的Promise拒绝:', reason);
});