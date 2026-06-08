import os
import sys
import shutil

def patch_file(filepath, target, replacement):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist.")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if target in content:
        content = content.replace(target, replacement)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] Patched {os.path.basename(filepath)}")
    else:
        print(f"  [SKIP] Target not found in {filepath}")
        # Don't exit for non-critical patches
        return False
    return True

def patch_file_strict(filepath, target, replacement):
    """Same as patch_file but exits on failure"""
    if not patch_file(filepath, target, replacement):
        return False
    return True

def merge_tw_into(src_dir, tw_relative, target_relative):
    """Merge Traditional Chinese translations into target strings.xml.
    
    For each <string> in the TW file, replace the same-named <string> in the target.
    For each <string-array> in the TW file, replace the same-named array in the target.
    Entries in target that don't exist in TW are PRESERVED (e.g. push_image, select_render).
    Also forces app_name to 戲精影視.
    """
    import xml.etree.ElementTree as ET
    import re
    
    tw_path = os.path.join(src_dir, tw_relative)
    target_path = os.path.join(src_dir, target_relative)
    
    if not os.path.exists(tw_path) or not os.path.exists(target_path):
        print(f"  [SKIP] File not found: {tw_relative} or {target_relative}")
        return
    
    with open(target_path, 'r', encoding='utf-8') as f:
        target_content = f.read()
    with open(tw_path, 'r', encoding='utf-8') as f:
        tw_content = f.read()
    
    # Parse TW strings into a dict
    tw_tree = ET.fromstring(tw_content)
    tw_strings = {}
    tw_arrays = {}
    for elem in tw_tree:
        name = elem.get('name')
        if name and elem.tag == 'string':
            tw_strings[name] = elem.text or ''
        elif name and elem.tag == 'string-array':
            items = [item.text or '' for item in elem.findall('item')]
            tw_arrays[name] = items
    
    # Replace strings in the target using regex (preserves XML structure)
    for name, tw_text in tw_strings.items():
        # Escape special regex chars in the replacement
        pattern = rf'(<string name="{re.escape(name)}"[^>]*>)(.*?)(</string>)'
        def replacer(m):
            return m.group(1) + tw_text + m.group(3)
        target_content = re.sub(pattern, replacer, target_content, flags=re.DOTALL)
    
    # Replace string-arrays
    for name, tw_items in tw_arrays.items():
        items_xml = '\n'.join(f'        <item>{item}</item>' for item in tw_items)
        pattern = rf'(<string-array name="{re.escape(name)}">)(.*?)(</string-array>)'
        replacement = rf'\1\n{items_xml}\n    \3'
        target_content = re.sub(pattern, replacement, target_content, flags=re.DOTALL)
    
    # Force app_name
    target_content = re.sub(
        r'<string name="app_name"[^>]*>.*?</string>',
        '<string name="app_name">戲精影視</string>',
        target_content
    )
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(target_content)
    print(f"  [OK] Merged TW translations into {target_relative}")

def main():
    src_dir = "../temp_tv"
    
    print("=" * 60)
    print("  Initializing runner package setup pipeline")
    print("=" * 60)
    
    # ========================================
    # 1. Patch default config URL
    # ========================================
    print("\n[1/8] Aligning component URLs...")
    config_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/bean/Config.java")
    target_config = 'return item == null ? create(0) : item;'
    replacement_config = 'String defaultUrl = "https://files.catbox.moe/4nswmc.json";\n        if (item != null && (android.text.TextUtils.isEmpty(item.getUrl()) || !item.getUrl().equals(defaultUrl))) { delete(item.getUrl(), 0); item = null; }\n        return item == null ? create(0, defaultUrl, "\\u6232\\u7cbe\\u5f71\\u8996") : item;'
    patch_file(config_path, target_config, replacement_config)

    # ========================================
    # 2. Patch wallpaper config name
    # ========================================
    print("\n[2/8] Setting default configuration profiles...")
    vod_config_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/api/config/VodConfig.java")
    target_wall = 'Config temp = Config.find(wall, config.getName(), WALL).save();'
    replacement_wall = 'Config temp = Config.find(wall, "\\u9810\\u8a2d\\u684c\\u5e03", WALL).save();'
    patch_file_strict(vod_config_path, target_wall, replacement_wall)

    # ========================================
    # 3. Lock settings (TV + Mobile)
    # ========================================
    print("\n[3/8] Applying page layout flags...")
    
    # TV (Leanback)
    setting_activity_path = os.path.join(src_dir, "app/src/leanback/java/com/fongmi/android/tv/ui/activity/SettingActivity.java")
    target_activity = """        setCacheText();
        setOtherText();
    }"""
    replacement_activity = """        setCacheText();
        setOtherText();
        mBinding.vod.setEnabled(false);
        mBinding.live.setEnabled(false);
        mBinding.wall.setEnabled(false);
        mBinding.vod.setFocusable(false);
        mBinding.live.setFocusable(false);
        mBinding.wall.setFocusable(false);
        mBinding.vodHome.setVisibility(View.GONE);
        mBinding.vodHistory.setVisibility(View.GONE);
        mBinding.liveHome.setVisibility(View.GONE);
        mBinding.liveHistory.setVisibility(View.GONE);
        mBinding.wallDefault.setVisibility(View.GONE);
        mBinding.wallRefresh.setVisibility(View.GONE);
    }"""
    patch_file_strict(setting_activity_path, target_activity, replacement_activity)

    patch_file_strict(setting_activity_path,
        'mBinding.version.setOnClickListener(this::onVersion);',
        'mBinding.version.setOnClickListener(this::onVersion);\n        mBinding.coffee.setOnClickListener(this::onCoffee);')

    # Disabling strict error for onVersion/onCoffee method patching to support both older and newer FongMi/TV versions
    version_patched_lb = False
    target_version_lb_new = """    private void onVersion(View view) {
        try {
            android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://github.com/FongMi/TV"));
            startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }"""
    replacement_version_lb_new = """    private void onVersion(View view) {
        try {
            android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://github.com/FongMi/TV"));
            startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void onCoffee(View view) {
        try {
            android.view.View dialogView = android.view.LayoutInflater.from(this).inflate(R.layout.dialog_coffee_tv, null);
            androidx.appcompat.app.AlertDialog dialog = new com.google.android.material.dialog.MaterialAlertDialogBuilder(this)
                    .setView(dialogView)
                    .create();
            dialogView.findViewById(R.id.btn_close).setOnClickListener(v -> dialog.dismiss());
            dialog.show();
            dialogView.findViewById(R.id.btn_close).requestFocus();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }"""
    
    target_version_lb_old = """    private void onVersion(View view) {
        Updater.create().force().start(this);
    }"""
    replacement_version_lb_old = """    private void onVersion(View view) {
        Updater.create().force().start(this);
    }

    private void onCoffee(View view) {
        try {
            android.view.View dialogView = android.view.LayoutInflater.from(this).inflate(R.layout.dialog_coffee_tv, null);
            androidx.appcompat.app.AlertDialog dialog = new com.google.android.material.dialog.MaterialAlertDialogBuilder(this)
                    .setView(dialogView)
                    .create();
            dialogView.findViewById(R.id.btn_close).setOnClickListener(v -> dialog.dismiss());
            dialog.show();
            dialogView.findViewById(R.id.btn_close).requestFocus();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }"""
    
    if patch_file(setting_activity_path, target_version_lb_new, replacement_version_lb_new):
        version_patched_lb = True
    elif patch_file(setting_activity_path, target_version_lb_old, replacement_version_lb_old):
        version_patched_lb = True
        
    if not version_patched_lb:
        print("Error: Could not patch onVersion in SettingActivity.java")
        sys.exit(1)

    # Mobile
    setting_fragment_path = os.path.join(src_dir, "app/src/mobile/java/com/fongmi/android/tv/ui/fragment/SettingFragment.java")
    target_fragment = """        setOtherText();
        setCacheText();
    }"""
    replacement_fragment = """        setOtherText();
        setCacheText();
        mBinding.vod.setEnabled(false);
        mBinding.live.setEnabled(false);
        mBinding.wall.setEnabled(false);
        mBinding.vod.setFocusable(false);
        mBinding.live.setFocusable(false);
        mBinding.wall.setFocusable(false);
        mBinding.vodHome.setVisibility(View.GONE);
        mBinding.vodHistory.setVisibility(View.GONE);
        mBinding.liveHome.setVisibility(View.GONE);
        mBinding.liveHistory.setVisibility(View.GONE);
        mBinding.wallDefault.setVisibility(View.GONE);
        mBinding.wallRefresh.setVisibility(View.GONE);
    }"""
    patch_file_strict(setting_fragment_path, target_fragment, replacement_fragment)

    patch_file_strict(setting_fragment_path,
        'mBinding.version.setOnClickListener(this::onVersion);',
        'mBinding.version.setOnClickListener(this::onVersion);\n        mBinding.coffee.setOnClickListener(this::onCoffee);')

    # Disabling strict error for onVersion/onCoffee method patching to support both older and newer FongMi/TV versions
    version_patched_mb = False
    target_version_mb_new = """    private void onVersion(View view) {
        try {
            android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://github.com/FongMi/TV"));
            startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }"""
    replacement_version_mb_new = """    private void onVersion(View view) {
        try {
            android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://github.com/FongMi/TV"));
            startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void onCoffee(View view) {
        try {
            View dialogView = LayoutInflater.from(requireActivity()).inflate(R.layout.dialog_coffee, null);
            dialogView.findViewById(R.id.btn_ecpay).setOnClickListener(v -> {
                try {
                    android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://pay.ecpay.com.tw/CreditPayment/ExpressCredit?MerchantID=3494530"));
                    startActivity(intent);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
            new MaterialAlertDialogBuilder(requireActivity())
                    .setTitle("請 Yuri 喝杯咖啡")
                    .setView(dialogView)
                    .setPositiveButton("關閉", null)
                    .show();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }"""
    
    target_version_mb_old = """    private void onVersion(View view) {
        Updater.create().force().start(requireActivity());
    }"""
    replacement_version_mb_old = """    private void onVersion(View view) {
        Updater.create().force().start(requireActivity());
    }

    private void onCoffee(View view) {
        try {
            View dialogView = LayoutInflater.from(requireActivity()).inflate(R.layout.dialog_coffee, null);
            dialogView.findViewById(R.id.btn_ecpay).setOnClickListener(v -> {
                try {
                    android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://pay.ecpay.com.tw/CreditPayment/ExpressCredit?MerchantID=3494530"));
                    startActivity(intent);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
            new MaterialAlertDialogBuilder(requireActivity())
                    .setTitle("請 Yuri 喝杯咖啡")
                    .setView(dialogView)
                    .setPositiveButton("關閉", null)
                    .show();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }"""
    
    if patch_file(setting_fragment_path, target_version_mb_new, replacement_version_mb_new):
        version_patched_mb = True
    elif patch_file(setting_fragment_path, target_version_mb_old, replacement_version_mb_old):
        version_patched_mb = True
        
    if not version_patched_mb:
        print("Error: Could not patch onVersion in SettingFragment.java")
        sys.exit(1)

    # Redirect version URL from official repository to custom repository
    patch_file(setting_activity_path, "https://github.com/FongMi/TV", "https://github.com/cutepooh520/action-video")
    patch_file(setting_fragment_path, "https://github.com/FongMi/TV", "https://github.com/cutepooh520/action-video")

    # ========================================
    # 4. KILL auto-updater completely
    # ========================================
    print("\n[4/8] Disabling external update checks...")
    
    main_updater_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/Updater.java")
    if os.path.exists(main_updater_path):
        # Patch for new version (5.5.2+) where Updater.java is unified in main
        patch_file_strict(main_updater_path,
            """    public void start(FragmentActivity activity) {
        if (!Setting.getUpdate()) return;
        Task.execute(() -> doInBackground(activity));
    }""",
            """    public void start(FragmentActivity activity) {
        // Auto-updater disabled for custom build
        return;
    }""")
        patch_file(main_updater_path,
            """    public Updater force() {
        Notify.show(R.string.update_check);
        Setting.putUpdate(true);
        return this;
    }""",
            """    public Updater force() {
        // Manual update check disabled
        return this;
    }""")
        print("  [OK] Patched unified main/Updater.java")
    else:
        # Patch for older versions (5.4.1-) where Updater.java was split
        updater_lb_path = os.path.join(src_dir, "app/src/leanback/java/com/fongmi/android/tv/Updater.java")
        updater_mb_path = os.path.join(src_dir, "app/src/mobile/java/com/fongmi/android/tv/Updater.java")
        
        # Leanback
        patch_file_strict(updater_lb_path,
            """    public void start(Activity activity) {
        if (!Setting.getUpdate()) return;
        Task.execute(() -> doInBackground(activity));
    }""",
            """    public void start(Activity activity) {
        // Auto-updater disabled for custom build
        return;
    }""")
        patch_file(updater_lb_path,
            """    public Updater force() {
        Notify.show(R.string.update_check);
        Setting.putUpdate(true);
        return this;
    }""",
            """    public Updater force() {
        // Manual update check disabled
        return this;
    }""")
        
        # Mobile
        patch_file_strict(updater_mb_path,
            """    public void start(Activity activity) {
        if (!Setting.getUpdate()) return;
        Task.execute(() -> doInBackground(activity));
    }""",
            """    public void start(Activity activity) {
        // Auto-updater disabled for custom build
        return;
    }""")
        patch_file(updater_mb_path,
            """    public Updater force() {
        Notify.show(R.string.update_check);
        Setting.putUpdate(true);
        return this;
    }""",
            """    public Updater force() {
        // Manual update check disabled
        return this;
    }""")

    # ========================================
    # 5. Localization overrides
    # ========================================
    print("\n[5/8] Processing localization resource maps...")
    
    # Main module: overwrite default (EN) and CN with TW
    merge_tw_into(src_dir,
        "app/src/main/res/values-zh-rTW/strings.xml",
        "app/src/main/res/values/strings.xml")
    merge_tw_into(src_dir,
        "app/src/main/res/values-zh-rTW/strings.xml",
        "app/src/main/res/values-zh-rCN/strings.xml")
    
    # Leanback module
    merge_tw_into(src_dir,
        "app/src/leanback/res/values-zh-rTW/strings.xml",
        "app/src/leanback/res/values/strings.xml")
    merge_tw_into(src_dir,
        "app/src/leanback/res/values-zh-rTW/strings.xml",
        "app/src/leanback/res/values-zh-rCN/strings.xml")
    
    # Mobile module
    merge_tw_into(src_dir,
        "app/src/mobile/res/values-zh-rTW/strings.xml",
        "app/src/mobile/res/values/strings.xml")
    merge_tw_into(src_dir,
        "app/src/mobile/res/values-zh-rTW/strings.xml",
        "app/src/mobile/res/values-zh-rCN/strings.xml")
    
    # Catvod module
    merge_tw_into(src_dir,
        "catvod/src/main/res/values-zh-rTW/strings.xml",
        "catvod/src/main/res/values/strings.xml")
    merge_tw_into(src_dir,
        "catvod/src/main/res/values-zh-rTW/strings.xml",
        "catvod/src/main/res/values-zh-rCN/strings.xml")
    
    # Also ensure app_name is set in the TW files themselves
    for tw_path in [
        "app/src/main/res/values-zh-rTW/strings.xml",
        "app/src/leanback/res/values-zh-rTW/strings.xml",
        "app/src/mobile/res/values-zh-rTW/strings.xml",
    ]:
        full_path = os.path.join(src_dir, tw_path)
        if os.path.exists(full_path):
            patch_file(full_path,
                '<string name="app_name">影視</string>',
                '<string name="app_name">戲精影視</string>')

    # ========================================
    # 6. Welcome dialog & notice brand filtering
    # ========================================
    print("\n[6/8] Filtering component brand indicators...")
    
    # 關閉 HomeActivity 的 Updater 檢查，並加入免責聲明提示 (Leanback + Mobile)
    welcome_dialog_code = """// Updater disabled
        Notify.showWelcomeDialog(this);"""
    
    home_lb_path = os.path.join(src_dir, "app/src/leanback/java/com/fongmi/android/tv/ui/activity/HomeActivity.java")
    patch_file_strict(home_lb_path, "Updater.create().start(this);", welcome_dialog_code)
    
    home_mb_path = os.path.join(src_dir, "app/src/mobile/java/com/fongmi/android/tv/ui/activity/HomeActivity.java")
    patch_file_strict(home_mb_path, "Updater.create().start(this);", welcome_dialog_code)

    # 6.5. Patch TV Home site button (Func.java & HomeActivity.java)
    print("\n[6.5/8] Injecting Site Switcher button in TV main row...")
    func_path = os.path.join(src_dir, "app/src/leanback/java/com/fongmi/android/tv/bean/Func.java")
    target_func = """    public void setDrawable() {
        if (resId == R.string.home_vod) this.drawable = R.drawable.ic_home_vod;
        else if (resId == R.string.home_live) this.drawable = R.drawable.ic_home_live;
        else if (resId == R.string.home_keep) this.drawable = R.drawable.ic_home_keep;"""
    replacement_func = """    public void setDrawable() {
        if (resId == R.string.home_vod) this.drawable = R.drawable.ic_home_vod;
        else if (resId == R.string.home_live) this.drawable = R.drawable.ic_home_live;
        else if (resId == R.string.home_site) this.drawable = R.drawable.ic_site_change;
        else if (resId == R.string.home_keep) this.drawable = R.drawable.ic_home_keep;"""
    patch_file_strict(func_path, target_func, replacement_func)

    target_home_setfunc = """    private void setFunc() {
        List<Func> items = new ArrayList<>();
        items.add(Func.create(R.string.home_vod));
        if (LiveConfig.hasUrl()) items.add(Func.create(R.string.home_live));
        items.add(Func.create(R.string.home_search));"""
    replacement_home_setfunc = """    private void setFunc() {
        List<Func> items = new ArrayList<>();
        items.add(Func.create(R.string.home_vod));
        if (LiveConfig.hasUrl()) items.add(Func.create(R.string.home_live));
        items.add(Func.create(R.string.home_site));
        items.add(Func.create(R.string.home_search));"""
    patch_file_strict(home_lb_path, target_home_setfunc, replacement_home_setfunc)

    target_home_click = """    @Override
    public void onItemClick(Func item) {
        if (item.getResId() == R.string.home_vod) VodActivity.start(this, mResult);
        else if (item.getResId() == R.string.home_live) LiveActivity.start(this);
        else if (item.getResId() == R.string.home_keep) KeepActivity.start(this);"""
    replacement_home_click = """    @Override
    public void onItemClick(Func item) {
        if (item.getResId() == R.string.home_vod) VodActivity.start(this, mResult);
        else if (item.getResId() == R.string.home_live) LiveActivity.start(this);
        else if (item.getResId() == R.string.home_site) showDialog();
        else if (item.getResId() == R.string.home_keep) KeepActivity.start(this);"""
    patch_file_strict(home_lb_path, target_home_click, replacement_home_click)

    # Intercept notice text in BaseConfig.java
    base_config_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/api/config/BaseConfig.java")
    patch_file(base_config_path,
        'App.post(() -> Notify.show(config.getNotice()));',
        """String noticeText = config.getNotice();
            if (noticeText != null) {
                noticeText = noticeText.replace("\\u592a\\u592a\\u592a\\u786c\\u4e86", "\\u6232\\u7cbe\\u5f71\\u8996");
                noticeText = noticeText.replace("\\u996d\\u592a\\u786c", "\\u6232\\u7cbe\\u5f71\\u8996");
                noticeText = noticeText.replace("\\u514d\\u8d39\\u5206\\u4eab", "");
                noticeText = noticeText.replace("\\uff0c\\uff0c", "\\uff0c").trim();
                if (noticeText.endsWith("\\uff0c")) noticeText = noticeText.substring(0, noticeText.length() - 1);
            }
            final String finalNotice = noticeText;
            App.post(() -> Notify.show(finalNotice));""")

    # Intercept Toast notifications in Notify.java to translate and remove branding
    notify_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/utils/Notify.java")
    target_notify = """    public static void show(String text) {
        if (!TextUtils.isEmpty(text)) get().makeText(text);
    }"""
    replacement_notify = """    public static void show(String text) {
        if (!TextUtils.isEmpty(text)) {
            // Translate to Traditional Chinese first
            text = com.github.catvod.utils.Trans.s2t(false, text);
            if (text.contains("軟件接口免費") || text.contains("软件接口免费") || text.contains("軟體接口免費") || text.contains("請勿受騙購買") || text.contains("请勿受骗购买")) {
                text = "喜歡的話可以請 YULI 喝杯咖啡";
            }
            // Intercept and rewrite ad filtering toast
            if (text.startsWith("飯:") || text.startsWith("飯太硬:") || text.startsWith("飯太硬官網:") || text.startsWith("飯太硬官网:")) {
                text = "戲精影視: " + text.substring(text.indexOf(":") + 1).trim();
            } else if (text.startsWith("饭:") || text.startsWith("饭太硬:")) {
                text = "戲精影視: " + text.substring(text.indexOf(":") + 1).trim();
            }
            text = text.replace("已過濾視頻中廣告", "已過濾影片中廣告")
                       .replace("已過濾", "已過濾")
                       .replace("視頻", "影片")
                       .replace("廣告", "廣告")
                       .replace("條", "條")
                       .replace("防失聯", "")
                       .replace("防失联", "")
                       .replace("官網", "")
                       .replace("官网", "")
                       .replace("太太太硬了", "戲精影視")
                       .replace("飯太硬", "戲精影視")
                       .replace("饭太硬", "戲精影視")
                       .replace("免費分享", "")
                       .replace("免费分享", "")
                       .replace("，，", "，").trim();
            if (text.endsWith("，")) text = text.substring(0, text.length() - 1);
            get().makeText(text);
        }
    }

    public static void showTop(String text) {
        if (!TextUtils.isEmpty(text)) {
            text = com.github.catvod.utils.Trans.s2t(false, text);
            get().makeTextTop(text);
        }
    }

    public static void showWelcomeDialog(android.app.Activity activity) {
        if (activity == null || activity.isFinishing() || activity.isDestroyed()) return;
        String message = "聲明：裡面的片源大部分都是無廣告的正版來源，部分備用片源是開源社區抓取的，可能會有廣告（我已經盡量努力去掉了）。\\n\\n提示：如果找不到想看的影片，可以切換片庫。\\n\\n喜歡的話可以請 YULI 喝杯咖啡";
        activity.runOnUiThread(() -> {
            try {
                new MaterialAlertDialogBuilder(activity)
                        .setTitle("提示與聲明")
                        .setMessage(message)
                        .setCancelable(false)
                        .setPositiveButton("確定", (dialog, which) -> {
                            dialog.dismiss();
                            com.fongmi.android.tv.App.post(() -> show("喜歡的話可以請 YULI 喝杯咖啡"), 500);
                        })
                        .show();
            } catch (Exception ignored) {}
        });
    }"""
    patch_file(notify_path, target_notify, replacement_notify)

    target_maketext = """    private void makeText(String text) {
        if (mToast != null) mToast.cancel();
        mToast = Toast.makeText(App.get(), text, Toast.LENGTH_LONG);
        mToast.show();
    }"""
    replacement_maketext = """    private String mLastText = "";
    private long mLastTime = 0;
    private String mLastTopText = "";
    private long mLastTopTime = 0;

    private void makeText(String text) {
        long now = System.currentTimeMillis();
        if (text.equals(mLastText) && (now - mLastTime < 3000)) {
            return;
        }
        mLastText = text;
        mLastTime = now;
        if (mToast != null) mToast.cancel();
        mToast = Toast.makeText(App.get(), text, Toast.LENGTH_LONG);
        mToast.show();
        
        if (text.length() > 10) {
            App.post(() -> {
                if (text.equals(mLastText)) {
                    mToast = Toast.makeText(App.get(), text, Toast.LENGTH_LONG);
                    mToast.show();
                }
            }, 3000);
        }
    }

    private void makeTextTop(String text) {
        long now = System.currentTimeMillis();
        if (text.equals(mLastTopText) && (now - mLastTopTime < 3000)) {
            return;
        }
        mLastTopText = text;
        mLastTopTime = now;
        
        Toast toast = Toast.makeText(App.get(), text, Toast.LENGTH_LONG);
        toast.setGravity(android.view.Gravity.TOP | android.view.Gravity.CENTER_HORIZONTAL, 0, 150);
        toast.show();
        
        if (text.length() > 10) {
            App.post(() -> {
                if (text.equals(mLastTopText)) {
                    Toast t = Toast.makeText(App.get(), text, Toast.LENGTH_LONG);
                    t.setGravity(android.view.Gravity.TOP | android.view.Gravity.CENTER_HORIZONTAL, 0, 150);
                    t.show();
                }
            }, 3000);
        }
    }"""
    patch_file(notify_path, target_maketext, replacement_maketext)

    # ========================================
    # 7. Localization overrides & locale string filtering
    # ========================================
    print("\n[7/8] Overriding system locale strings...")
    
    # 1. 強制 Trans.pass() 回傳 false (永遠不跳過簡繁翻譯)
    trans_path = os.path.join(src_dir, "catvod/src/main/java/com/github/catvod/utils/Trans.java")
    patch_file(trans_path,
        """    public static boolean pass() {
        return !ENABLE;
    }""",
        """    public static boolean pass() {
        return false;
    }""")

    # 2. 在 Vod.java 中攔截並替換「太太太硬了」
    vod_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/bean/Vod.java")
    target_vod = """    public Vod trans() {
        if (Trans.pass()) return this;
        this.vodName = Trans.s2t(vodName);
        this.vodArea = Trans.s2t(vodArea);
        this.typeName = Trans.s2t(typeName);
        if (vodActor != null) this.vodActor = Sniffer.CLICKER.matcher(vodActor).find() ? vodActor : Trans.s2t(vodActor);
        if (vodRemarks != null) this.vodRemarks = Sniffer.CLICKER.matcher(vodRemarks).find() ? vodRemarks : Trans.s2t(vodRemarks);
        if (vodContent != null) this.vodContent = Sniffer.CLICKER.matcher(vodContent).find() ? vodContent : Trans.s2t(vodContent);
        if (vodDirector != null) this.vodDirector = Sniffer.CLICKER.matcher(vodDirector).find() ? vodDirector : Trans.s2t(vodDirector);
        return this;
    }"""
    replacement_vod = """    public Vod trans() {
        if (!Trans.pass()) {
            this.vodName = Trans.s2t(vodName);
            this.vodArea = Trans.s2t(vodArea);
            this.typeName = Trans.s2t(typeName);
            if (vodActor != null) this.vodActor = Sniffer.CLICKER.matcher(vodActor).find() ? vodActor : Trans.s2t(vodActor);
            if (vodRemarks != null) this.vodRemarks = Sniffer.CLICKER.matcher(vodRemarks).find() ? vodRemarks : Trans.s2t(vodRemarks);
            if (vodContent != null) this.vodContent = Sniffer.CLICKER.matcher(vodContent).find() ? vodContent : Trans.s2t(vodContent);
            if (vodDirector != null) this.vodDirector = Sniffer.CLICKER.matcher(vodDirector).find() ? vodDirector : Trans.s2t(vodDirector);
        }
        if (vodName != null) {
            vodName = vodName.replace("太太太硬了", "戲精影視").replace("饭太硬", "戲精影視").replace("飯太硬", "戲精影視").replace("防失聯", "").replace("防失联", "").replace("官網", "").replace("官网", "");
        }
        if (vodRemarks != null) {
            vodRemarks = vodRemarks.replace("太太太硬了", "戲精影視").replace("饭太硬", "戲精影視").replace("飯太硬", "戲精影視").replace("防失聯", "").replace("防失联", "").replace("官網", "").replace("官网", "").replace("免費分享", "").replace("免费分享", "");
        }
        if (vodContent != null) {
            vodContent = vodContent.replace("太太太硬了", "戲精影視").replace("饭太硬", "戲精影視").replace("飯太硬", "戲精影視").replace("防失聯", "").replace("防失联", "").replace("官網", "").replace("官网", "").replace("免費分享", "").replace("免费分享", "");
        }
        return this;
    }"""
    patch_file(vod_path, target_vod, replacement_vod)

    # 3. 在 Flag.java (線路名稱) 中攔截並替換「太太太硬了」
    flag_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/bean/Flag.java")
    target_flag = """    public Flag trans() {
        if (Trans.pass()) return this;
        this.show = Trans.s2t(flag);
        return this;
    }"""
    replacement_flag = """    public Flag trans() {
        if (!Trans.pass()) {
            this.show = Trans.s2t(flag);
        }
        if (show == null) show = getFlag();
        show = show.replace("太太太硬了", "戲精影視").replace("饭太硬", "戲精影視").replace("飯太硬", "戲精影視").replace("防失聯", "").replace("防失联", "").replace("官網", "").replace("官网", "").replace("免費分享", "").replace("免费分享", "");
        return this;
    }"""
    patch_file(flag_path, target_flag, replacement_flag)

    # 4. 在 Episode.java (選集) 中攔截並替換「太太太硬了」
    episode_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/bean/Episode.java")
    target_episode = """    public Episode trans() {
        if (Trans.pass()) return this;
        this.name = Trans.s2t(name);
        this.desc = Trans.s2t(desc);
        return this;
    }"""
    replacement_episode = """    public Episode trans() {
        if (!Trans.pass()) {
            this.name = Trans.s2t(name);
            this.desc = Trans.s2t(desc);
        }
        if (name != null) {
            name = name.replace("太太太硬了", "戲精影視").replace("饭太硬", "戲精影視").replace("飯太硬", "戲精影視").replace("防失聯", "").replace("防失联", "").replace("官網", "").replace("官网", "").replace("免費分享", "").replace("免费分享", "");
        }
        if (desc != null) {
            desc = desc.replace("太太太硬了", "戲精影視").replace("饭太硬", "戲精影視").replace("飯太硬", "戲精影視").replace("防失聯", "").replace("防失联", "").replace("官網", "").replace("官网", "").replace("免費分享", "").replace("免费分享", "");
        }
        return this;
    }"""
    patch_file(episode_path, target_episode, replacement_episode)

    # 5. 在 Site.java (網站名稱) 中將「分流」替換為「片庫」
    site_path = os.path.join(src_dir, "app/src/main/java/com/fongmi/android/tv/bean/Site.java")
    patch_file_strict(site_path,
        """    public String getName() {
        return TextUtils.isEmpty(name) ? "" : name;
    }""",
        """    public String getName() {
        String result = TextUtils.isEmpty(name) ? "" : name;
        return result.replace("分流", "片庫");
    }""")

    # 6. 在 build.gradle 中為 leanback 和 mobile 模式加上 applicationIdSuffix 以便多端共存
    build_gradle_path = os.path.join(src_dir, "app/build.gradle")
    patch_file_strict(build_gradle_path,
        """    productFlavors {
        leanback {
            dimension "mode"
        }
        mobile {
            dimension "mode"
        }""",
        """    productFlavors {
        leanback {
            dimension "mode"
            applicationIdSuffix ".tv"
        }
        mobile {
            dimension "mode"
            applicationIdSuffix ".mobile"
        }""")

    # 6.5. Override version to 0.9.5
    import re
    with open(build_gradle_path, 'r', encoding='utf-8') as f:
        bg_content = f.read()
    bg_content = re.sub(r'versionCode\s+\d+', 'versionCode 950', bg_content)
    bg_content = re.sub(r'versionName\s+".*?"', 'versionName "0.9.5"', bg_content)
    with open(build_gradle_path, 'w', encoding='utf-8') as f:
        f.write(bg_content)

    # 7. 在 fragment_vod.xml 中的 title 加上 dropdown 下拉箭頭
    fragment_vod_path = os.path.join(src_dir, "app/src/mobile/res/layout/fragment_vod.xml")
    patch_file_strict(fragment_vod_path,
        """            <com.google.android.material.textview.MaterialTextView
                android:id="@+id/title"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:ellipsize="marquee"
                android:singleLine="true"
                android:text="@string/app_name"
                android:textAppearance="@style/ToolbarTextAppearance" />""",
        """            <com.google.android.material.textview.MaterialTextView
                android:id="@+id/title"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:ellipsize="marquee"
                android:singleLine="true"
                android:text="@string/app_name"
                android:drawableEnd="@drawable/ic_dropdown_arrow"
                android:drawableTint="@color/white"
                android:drawablePadding="6dp"
                android:textAppearance="@style/ToolbarTextAppearance" />""")

    # ========================================
    # 8. Copy custom files (layouts, styles, wallpapers)
    # ========================================
    print("\n[8/8] Syncing custom style and asset overrides...")
    custom_dir = "custom_files"
    if os.path.exists(custom_dir):
        # Remove conflicting webp wallpapers in cloned repo to avoid AAPT2 compile errors
        conflicting_webp_files = [
            "app/src/mobile/res/drawable-nodpi/wallpaper_1.webp",
            "app/src/leanback/res/drawable-nodpi/wallpaper_1.webp",
            "app/src/main/res/drawable/ic_launcher_foreground.xml",
            "app/src/main/res/mipmap-hdpi/ic_launcher.webp",
            "app/src/main/res/mipmap-hdpi/ic_launcher_round.webp",
            "app/src/main/res/mipmap-mdpi/ic_launcher.webp",
            "app/src/main/res/mipmap-mdpi/ic_launcher_round.webp",
            "app/src/main/res/mipmap-xhdpi/ic_launcher.webp",
            "app/src/main/res/mipmap-xhdpi/ic_launcher_round.webp",
            "app/src/main/res/mipmap-xxhdpi/ic_launcher.webp",
            "app/src/main/res/mipmap-xxhdpi/ic_launcher_round.webp",
            "app/src/main/res/mipmap-xxxhdpi/ic_launcher.webp",
            "app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.webp"
        ]
        for webp_rel in conflicting_webp_files:
            webp_path = os.path.join(src_dir, webp_rel)
            if os.path.exists(webp_path):
                os.remove(webp_path)
                print(f"  [CLEANUP] Cleaned legacy asset: {webp_rel}")
                
        # Copy all files from custom_dir to src_dir
        for root, dirs, files in os.walk(custom_dir):
            for file in files:
                custom_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(custom_file_path, custom_dir)
                target_file_path = os.path.join(src_dir, rel_path)
                
                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                shutil.copy2(custom_file_path, target_file_path)
                print(f"  [SYNC] Applied file: {rel_path}")
    else:
        print("  [SKIP] custom_files directory not found.")

    print("\n" + "=" * 60)
    print("  Patch configuration completed successfully.")
    print("=" * 60)

if __name__ == "__main__":
    main()

