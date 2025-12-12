```markdown
# stay-with-me
Small utility to keep the screen from turning off on Linux desktops.

## Features
- Uses `gdbus` to call `org.freedesktop.ScreenSaver.Inhibit` when available.
- Falls back to `xdg-screensaver reset` or `xset s reset` if `gdbus` is not present.
- Simple CLI: `start`, `stop`, `status`, `run`.

## Usage
1. Make the script executable:

```bash
chmod +x stay_with_me.py
```

2. Start in background:

```bash
./stay_with_me.py start
```

3. Stop:

```bash
./stay_with_me.py stop
```

4. Run in foreground (useful for testing or systemd services):

```bash
./stay_with_me.py run
```

5. Check status:

```bash
./stay_with_me.py status
```

## Notes
- `gdbus` is preferred (works on many Wayland/X11 desktops). If missing, the script will try `xdg-screensaver` or `xset`.
- For system integration, run `./stay_with_me.py run` in a systemd user service.

```bash
[Unit]
Description=Stay With Me - prevent screen sleep

[Service]
ExecStart=/usr/bin/python3 /path/to/stay_with_me.py run

[Install]
WantedBy=default.target
```

Replace `/path/to/` with the repository path.

```
For macOS, the script uses `caffeinate` when available. Example `launchd` user plist:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
		<key>Label</key>
		<string>com.example.staywithme</string>
		<key>ProgramArguments</key>
		<array>
			<string>/usr/bin/python3</string>
			<string>/path/to/stay_with_me.py</string>
			<string>run</string>
		</array>
		<key>RunAtLoad</key>
		<true/>
		<key>KeepAlive</key>
		<true/>
		<key>StandardOutPath</key>
		<string>/tmp/stay_with_me.log</string>
		<key>StandardErrorPath</key>
		<string>/tmp/stay_with_me.err</string>
	</dict>
</plist>
```

Replace `/path/to/` with the repository path. Load with `launchctl load ~/Library/LaunchAgents/com.example.staywithme.plist`.

# stay-with-me
Small app that prevent screen off
