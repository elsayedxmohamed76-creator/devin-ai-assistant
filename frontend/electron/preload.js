const { contextBridge, ipcRenderer } = require("electron");

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld("electronAPI", {
  platform: process.platform,
  isElectron: true,
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron,
  },
});
