# AniTorrent

![](https://img.shields.io/badge/Python%20-3.6%2B-blue)
![](https://img.shields.io/badge/Status-working-brightgreen)
![](https://img.shields.io/badge/fansubs-2-yellowgreen)

Browse and download anime at max speed effortlessly, without any ads and at the quality you wish. No need of programming knowledge: everything is managed through a desktop minimalist app. 

## Features

- Anime all-in-one downloader based on [qBittorrent API](https://github.com/rmartin16/qbittorrent-api).
- The downloading speed has no cap apart from your own internet.
- Ad-free.
- Full-featured: search by show title, quality, batch and fansub group, and download multiple episodes at the same time.
- Real time progress and ETA tracking on the app.
- Keep your shows automatically ordered on folders.
- Get rid of complex names: automatic parsing and renaming of episodes.
- Upload schedule for all of the fansubs, covering most of the airing shows.
- More to come: fav list, themes, MAL account linking...

## Changelog

- Updated search engine: now the user is able to search on multiple sources simultaneously.
- Improved parser.
- Added plugin system (easier to add new sources)
- General bugfixes:
  - Internal type checking improved.
  - Improved error handling.
 
## Supported Systems

- Windows
- Mac OS
- Linux

## Supported Sites

- [Erai Raws](https://www.erai-raws.info/): subtitles in many languages (Eng, Sp, Ger, Ita, Pt...), includes older series than SubsPlease.
- [SubsPlease](https://subsplease.org/): currently covers roughly all of the airing animes.
- Judas: some airing shows and NSFW uncensored stuff.
- HorribleSubs: not updating anymore, but still a big resource for old series. 
- More to come (feel free to ask through pull requests)

## Installation

1. Clone the repository or download the files and locate them wherever you like. 

2. Open a command line on the intallation folder and install the dependencies on `req.txt`.
```
pip install -r req.txt
```
* **Windows users might simply execute the setup.bat file**

3. Download and install the [qBittorrent desktop app](https://www.qbittorrent.org/download.php), and enable WebUI on your settings (custom user, pass and port might be set on AniTorrent settings aswell). Letting qBittorrent launch on startup is recommended.

**Note**:  

Aditionally, compiled binaries (`.exe`) can be downloaded for Windows through Releases:

- Just download the `.zip` and extract it on your PC.
- To launch the app, double click on `Anitorrent.exe`. It is recommended to create a shortcut on your desktop.

### Dependencies

This package is built upon:
- qBittorrent-api
- Requests
- BeautifulSoup
- Cloudscraper

## Usage

Just launch the app (`main.py`) and enjoy!

##  To-do

- [ ] Support for episode streaming without downloading (`VLC`)
- [x] 2 new fansubs: HorribleSubs (huge amount of old series) and Judas
- [ ] Favorite list
- [ ] MAL account linking
- [ ] New themes
- [ ] Add download history