const { app, BrowserWindow, Menu, shell, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow;
let backendProcess;

// --- Backend management ---

function startBackend() {
  if (app.isPackaged) {
    const backendPath = path.join(process.resourcesPath, "backend", "devin-backend.exe");
    console.log("Starting packaged backend:", backendPath);
    backendProcess = spawn(backendPath, [], { 
      shell: false,
      env: { ...process.env, PYTHONUNBUFFERED: "1" }
    });
  } else {
    const backendDir = path.join(__dirname, "../../backend");
    const uvicornCmd = process.platform === "win32" ? "uvicorn" : "uvicorn";

    console.log("Starting dev backend from:", backendDir);
    backendProcess = spawn(uvicornCmd, ["app.main:app", "--host", "127.0.0.1", "--port", "8000"], {
      cwd: backendDir,
      shell: true,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
    });
  }

  backendProcess.stdout?.on("data", (data) => {
    console.log(`[Backend] ${data}`);
  });

  backendProcess.stderr?.on("data", (data) => {
    console.error(`[Backend] ${data}`);
  });

  backendProcess.on("error", (err) => {
    console.error("Failed to start backend:", err.message);
    dialog.showErrorBox(
      "Backend Error",
      `Could not start the AI backend:\n${err.message}\n\nMake sure Python and uvicorn are installed.`
    );
  });

  backendProcess.on("close", (code) => {
    console.log(`Backend exited with code ${code}`);
    backendProcess = null;
  });
}

function stopBackend() {
  if (backendProcess) {
    if (process.platform === "win32") {
      spawn("taskkill", ["/pid", backendProcess.pid.toString(), "/f", "/t"], { shell: true });
    } else {
      backendProcess.kill("SIGTERM");
    }
    backendProcess = null;
  }
}

// --- Window creation ---

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 900,
    minHeight: 650,
    title: "Devin AI Assistant",
    icon: path.join(__dirname, "../public/icon.png"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
    backgroundColor: "#030712",
    show: false,
    autoHideMenuBar: false,
  });

  // Show when ready to prevent white flash
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  // Load the app
  if (app.isPackaged) {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  } else {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  }

  // Open links in external browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// --- Menu ---

const menuTemplate = [
  {
    label: "Devin AI",
    submenu: [
      { label: "About Devin AI", role: "about" },
      { type: "separator" },
      {
        label: "Reset AI Memory",
        click: () => {
          const choice = dialog.showMessageBoxSync(mainWindow, {
            type: "warning",
            buttons: ["Cancel", "Reset"],
            title: "Reset AI Memory",
            message: "This will erase ALL learned knowledge. The AI will start from scratch.",
          });
          if (choice === 1) {
            mainWindow.webContents.executeJavaScript(
              `fetch("http://127.0.0.1:8000/api/memory/reset", { method: "POST" }).then(() => location.reload())`
            );
          }
        },
      },
      { type: "separator" },
      { label: "Quit", accelerator: "CmdOrCtrl+Q", click: () => app.quit() },
    ],
  },
  {
    label: "Edit",
    submenu: [
      { role: "undo" },
      { role: "redo" },
      { type: "separator" },
      { role: "cut" },
      { role: "copy" },
      { role: "paste" },
      { role: "selectAll" },
    ],
  },
  {
    label: "View",
    submenu: [
      { role: "reload" },
      { role: "forceReload" },
      { role: "toggleDevTools" },
      { type: "separator" },
      { role: "resetZoom" },
      { role: "zoomIn" },
      { role: "zoomOut" },
      { type: "separator" },
      { role: "togglefullscreen" },
    ],
  },
  {
    label: "Window",
    submenu: [{ role: "minimize" }, { role: "zoom" }, { role: "close" }],
  },
];

// --- App lifecycle ---

app.whenReady().then(() => {
  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  startBackend();

  // Wait a moment for backend to start, then create window
  setTimeout(createWindow, 1500);
});

app.on("window-all-closed", () => {
  stopBackend();
  app.quit();
});

app.on("before-quit", () => {
  stopBackend();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
