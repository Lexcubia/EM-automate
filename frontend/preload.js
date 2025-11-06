/**
 * Electron 预加载脚本
 * 安全地暴露Node.js API给渲染进程
 */
const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
    // 应用信息
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),

    // 后端配置
    getBackendConfig: () => ipcRenderer.invoke('get-backend-config'),

    // 文件对话框
    showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
    showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),

    // 错误对话框
    showErrorBox: (title, content) => ipcRenderer.invoke('show-error-box', title, content),

    // 平台信息
    platform: process.platform,

    // 开发模式检测
    isDev: process.env.NODE_ENV === 'development'
});

// 在控制台暴露一些调试信息（仅在开发模式）
if (process.env.NODE_ENV === 'development') {
    contextBridge.exposeInMainWorld('debugAPI', {
        log: (...args) => console.log('[Renderer]', ...args),
        error: (...args) => console.error('[Renderer]', ...args),
        warn: (...args) => console.warn('[Renderer]', ...args)
    });
}