APP_NAME = "AniTorrent_v2.0"

compile:
	@echo "Compiling the app for the current platform..."
	pyinstaller --onedir --noconsole --contents-directory src --name $(APP_NAME) main.py
	rm -rf build