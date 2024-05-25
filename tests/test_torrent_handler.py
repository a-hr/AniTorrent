import asyncio
from WebAPI import Nyaa
from TorrentHandler import TorrentHandler, Torrent


def search(term: str, fansub: str = "subsplease", language: str = "english"):
    search_engine = Nyaa()
    loop = asyncio.get_event_loop()

    torrents = loop.run_until_complete(search_engine.search(term, fansub, language))

    for ii, torrent in enumerate(torrents):
        print(f"Torrent {ii+1}:")
        print(torrent)
        print("------------------")
        if ii > 5:
            break
    return torrents


def download(torrent: Torrent):
    config = {
        "download_path": "/Users/varo/Downloads/series",
        "user": "admin",
        "password": "adminadmin",
        "host": "http://localhost:8080/",
        "qbittorrent_path": "/Applications/qBittorrent.app",
    }
    handler = TorrentHandler(config=config)
    handler.add_torrent(torrent)
    print(f"Added {torrent.raw_title} to download queue")
    return handler


if __name__ == "__main__":
    term = input("Search serie: ")
    torrents = search(term=term)

    selection = int(input("Select torrent: "))
    handler = download(torrents[selection - 1])

    while True:
        action = input("Enter action (update torrents, get status, exit): ")

        if action == "update torrents":
            downloading, to_process = handler.update()
            if not to_process:
                print("No torrents to process...")
                print(f"Downloading {len(downloading)} torrents:")
                for torrent in downloading:
                    print(torrent)
                    print("------------------")

        elif action == "exit":
            torrents = handler.get_progress()
            for torrent in torrents:
                handler.manual_remove(torrent)
                print(f"Removed {torrent.raw_title} from download queue")

            break

    print("Exiting...")
