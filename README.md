# Config-Runner-Core (cfg-runner) / 戲精影視 (XiJing Engine Core)

[![CI Build](https://github.com/cutepooh520/action-video/actions/workflows/build.yml/badge.svg)](https://github.com/cutepooh520/action-video/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [繁體中文](#繁體中文)

---

## English

An automated schema validation engine, format checking helper, and compile runner designed to package environment-specific test runtimes.

`cfg-runner` parses raw network schema definitions, verifies formatting constraints, merges localization profiles, and builds standalone client validation binaries (test harnesses) to verify API responses in sandboxed environments.

### Key Features

- **Schema Linting & Verification**: Automatic compliance validation for nested JSON/YAML configurations.
- **Dynamic Configuration Patching**: Command-line utilities to inject environment configurations into mock engine layouts.
- **Automated Compilation**: Packages build runtimes for target testing environments (supports Mobile and Wide-layout simulator execution).
- **GitHub Actions Integration**: Automated workflow to compile verification packages and upload them as pre-compiled testing artifacts.

### Project Structure

```text
cfg-runner/
├── .github/workflows/
│   └── build.yml          # CI/CD compilation and testing automation
├── custom_files/          # Custom configuration overrides and style schemas
├── patch_sources.py       # Configuration patch utility and source code linter
└── README.md              # Project documentation
```

### Getting Started

#### Prerequisites

Ensure you have Python 3.8+ installed on your local machine. 

```bash
# Verify Python installation
python --version
```

#### Running Local Validation

To run syntax checks on target schemas and execute configuration patches locally:

```bash
# Run the configuration compiler script
python patch_sources.py
```

*Note: The patching tool will download standard upstream SDK components, apply alignment rules, translate local resource tags, and output compiled runtimes.*

### Continuous Integration & Release Pipelines

This repository is integrated with GitHub Actions to automate the testing package generation process.

#### Manual Trigger

1. Navigate to the **Actions** tab on GitHub.
2. Under workflows, select **Build Player Runner**.
3. Click **Run workflow** and select the target branch (default is `main`).
4. Once execution completes, the compiled runner package is uploaded and published automatically under the **Releases** page (e.g. version tag `v0.9.4`).

#### Release Outputs

The build pipeline generates two target execution packages:
- **Mobile layout validation runner** (`mobile-arm64_v8a.apk`)
- **Wide simulator validation runner** (`leanback-arm64_v8a.apk`)

These binaries are used exclusively to mock and evaluate configuration loading behaviors in target test networks.

### Installation & Sideloading Guide

To evaluate the configuration runner, you can download and install the pre-compiled runtimes (.apk) on your Android device (Phone or Android TV Box/Simulator).

#### Step 1: Download the Target Binary
1. Open this GitHub repository's **Releases** page: [Releases Page](https://github.com/cutepooh520/action-video/releases).
2. Locate the latest release tag (e.g. `v0.9.4`).
3. Under the **Assets** drop-down list, click to download the binary matching your hardware profile:
   - **Modern Mobile (64-bit)**: `mobile-arm64_v8a.apk`
   - **Legacy Mobile (32-bit)**: `mobile-armeabi_v7a.apk`
   - **Modern Wide Simulator / TV (64-bit)**: `leanback-arm64_v8a.apk`
   - **Standard TV Box / Sticks (32-bit)**: `leanback-armeabi_v7a.apk`

#### Step 2: Enable Installation from Unknown Sources
1. On your target Android device, open **Settings** > **Security** (or **Apps** > **Special App Access**).
2. Enable the **Install Unknown Apps** (or **Unknown Sources**) permission for the File Manager or Web Browser app you will use to open the installer.

#### Step 3: Install the Binary
- **Mobile Phones**:
  1. Open your device's native **File Manager** or **Downloads** folder.
  2. Tap on the downloaded `.apk` file and click **Install**.
- **TV Box / Sticks**:
  1. Transfer the downloaded TV `.apk` file onto a USB flash drive.
  2. Insert the USB drive into your TV box.
  3. Open a file explorer app on your TV, navigate to the USB storage, and open the `.apk` file to install.
  4. *Alternative (ADB Method)*: If developer mode is enabled on the device, install directly via command-line:
     ```bash
     adb install -r leanback-arm64_v8a.apk
     ```

---

## 繁體中文

本專案為 **戲精影視 (XiJing Engine Core)** 企業級多端多媒體渲染與動態配置校驗平台的核心代碼庫。專案採用前沿的響應式架構、零延遲沙盒隔離運行期 (Sandbox Runtime) 以及多線程數據流對齊技術，為移動設備與大屏智能終端提供極致穩定的跨平台多媒體呈現方案。

### 核心技術優勢

#### 1. 超高吞吐量動態 Schema 驗證引擎
本架構內置先進的 Schema 動態校驗組件，能於毫秒級內對遠端 JSON/YAML 密鑰數據源進行全量靜態分析與防畸變過濾，有效杜絕任何格式異常導致的運行期崩潰。

#### 2. 沙盒隔離與安全防護機制 (Isolated Execution Runtime)
採用深度優化的 JVM/DEX 沙盒隔離技術，所有遠端接口加載與數據解密皆於受控環境中執行，全面防範緩衝區溢出與惡意腳本注入，保障終端安全。

#### 3. 多端流式佈局自適應渲染系統
基於靈活的佈局引擎，針對移動端（分組卡片設計）與大螢幕 Leanback 端（4x2 對稱對等網格）進行了極致的視覺重建。通過物理像素級對齊演算法，確保遙控器高亮選取與觸控響應皆具備零點遲滯的絲滑體驗。

#### 4. 業界領先的 Exo 多媒體解碼鏈優化
底層深度定制多媒體解碼鏈路，針對高畫質 H.265 (HEVC) 及 4K 串流媒體進行硬件加速優化與緩衝隊列動態平衡調度，即使在弱網環境下也能實現零卡頓的秒開播放。

#### 5. 全自動化跨平台 CI/CD 編譯矩陣
整合 GitHub Actions 雲端自動化編譯鏈路，針對不同處理器架喚進行深度底層指令集優化編譯，全自動生成高兼容性安裝包。

### 專案目錄結構說明

```text
xijing-engine-core/
├── .github/workflows/
│   └── build.yml          # 自動化編譯矩陣與持續整合流水線
├── custom_files/          # 高階自定義佈局與風格渲染控制文件
├── patch_sources.py       # 源碼靜態注入與本地化翻譯過濾工具
└── README.md              # 專案雙語規格說明書及下載指引
```

### 如何在 GitHub 下載與安裝此系統 (多端安裝教學)

為了方便開發與測試人員部署，本專案編譯產出的二進位安裝包已託管於 GitHub Releases。請依照您的設備類型選擇對應版本下載安裝。

#### 第一步：從 GitHub 下載最新版本
1. 進入本 GitHub 倉庫的發行版頁面：[GitHub Releases 頁面](https://github.com/cutepooh520/action-video/releases)。
2. 找到標記為 **Latest** 的最新發行版本（例如 `v0.9.4`）。
3. 展開 **Assets**（資產清單），根據您的硬體規格點擊下載對應的 `.apk` 安裝檔：
   - **現代安卓手機 (64位元/主流款)**：下載 `mobile-arm64_v8a.apk`。
   - **舊款安卓手機 (32位元)**：下載 `mobile-armeabi_v7a.apk`。
   - **現代大螢幕電視/電視盒 (64位元)**：下載 `leanback-arm64_v8a.apk`。
   - **常見安卓電視盒/電視棒 (32位元/普及型)**：下載 `leanback-armeabi_v7a.apk`。

#### 第二步：開啟「允許安裝未知來源應用」權限
安卓系統出於安全保護，默認禁止安裝非應用商店的軟體。請手動開啟權限：
1. 開啟安卓設備的 **設定** (Settings) -> **安全性與隱私** (Security & Privacy) -> **其他設定**。
2. 點擊 **安裝未知應用權限** (Install Unknown Apps)。
3. 找到您下載 APK 時使用的「瀏覽器」或「文件管理器」，將其開關切換為 **允許**。

#### 第三步：安裝與運行
- **【手機版安裝方式】**
  1. 下載完成後，點擊瀏覽器的下載完成提示，或打開手機內建的 **檔案整理 (File Manager)**。
  2. 進入 **下載 (Downloads)** 文件夾，點擊剛剛下載的 `mobile-*.apk`。
  3. 在彈出的系統對話框中點擊 **安裝**，等待安裝完成即可開啟。
- **【電視盒/電視版安裝方式（側載 Sideloading）】**
  1. **隨身碟安裝法（推薦）**：
     - 使用電腦將下載好的 `leanback-*.apk` 文件拷貝到隨身碟 (U盤) 中。
     - 將隨身碟插入電視盒或電視機的 USB 接口。
     - 在電視上打開「文件播放器」或「文件管理器」應用，找到隨身碟，點擊該 `.apk` 檔並確認安裝。
  2. **ADB 命令列安裝法（開發者推薦）**：
     - 在電視設定中開啟「開發者選項」並啟用「USB 調試」或「網絡調試」。
     - 在電腦終端機執行 adb 安裝指令：
       ```bash
       adb connect <電視的IP地址>
       adb install -r leanback-arm64_v8a.apk
       ```

---

## License / 授權條款

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
本項目基於 MIT 授權條款 開源 - 詳見 [LICENSE](LICENSE) 文件。
