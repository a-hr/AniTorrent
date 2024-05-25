# AniTorrent

![](https://img.shields.io/badge/Python%20-3.10%2B-blue)
![](https://img.shields.io/badge/Status-working-brightgreen)
![](https://img.shields.io/badge/fansubs-1-yellowgreen)

Browse and download anime at max speed effortlessly, without any ads and at the quality you wish. No need of programming knowledge: everything is managed through a desktop minimalist app. 

## Features

- Anime all-in-one downloader based on [qBittorrent API](https://github.com/rmartin16/qbittorrent-api).
- The downloading speed has no cap apart from your own internet.
- Ad-free.
- Full-featured: search by show title, quality, batch and fansub group, and download multiple episodes at the same time.
- Real time progress and ETA tracking on the app.
- Keep your shows automatically ordered in folders.
- Get rid of complex names: automatic parsing and renaming of episodes.

## Changelog

- Completely rewritten app, allowing for more features and better performance.
- Added support for multiple fansub groups.
- Added support for extension of available sources.
- New UI.
 
## Supported Systems

- Windows
- Mac OS
- Linux

## Supported Sites

- [SubsPlease](https://subsplease.org/): currently covers roughly all of the airing shows.

- *Coming soon*:
  - [Erai Raws](https://www.erai-raws.info/): subtitles in many languages (Eng, Sp, Ger, Ita, Pt...), includes older series than SubsPlease.


## Installation

1. Clone the repository or download the files and locate them wherever you like. 

2. Open a command line on the intallation folder and install the dependencies. In order to install the packages, create a new conda/mamba environment and clone `enviroment.yml`:

```bash
conda env create -n anitorrent -f environment.yml
```

3. Download and install the [qBittorrent desktop app](https://www.qbittorrent.org/download.php), and enable WebUI through the qBittorrent settings tab. AniTorrent will launch qBittorrent automatically if not running.

> Aditionally, compiled binaries (`.exe`) will be available soon.

## Usage

Just launch the app (`main.py`) and enjoy!

##  To-do

- [ ] Add binary releases for PC, Mac and Linux
- [ ] Add more sources (request them through issues or pull requests)
- [ ] Upload schedule of airing shows
- [ ] Download history