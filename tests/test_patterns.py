import re

if __name__ == "__main__":
    # add here sample filenames of the fansub you want to parse
    filenames = [
        "[SubsPlease] Kimetsu no Yaiba - Katanakaji no Sato-hen - 03 (1080p) [78D6EBBA].mkv",
        "[SubsPlease] Kimi wa Houkago Insomnia - 03 (480p) [2A42B8FE].mkv",
        "[SubsPlease] The IDOLM@STER Cinderella Girls - U149 - 04 (720p) [A75ED191].mkv",
    ]

    # add the regex pattern to test
    pattern = r"^\[.+?\]\s*(?P<series>.+?)\s*-\s*(?P<episode>\d+)\s*\((?P<quality>\d+p)\)\s*\[.+\]\.mkv$"

    # it should print the series name, episode number and video quality for each filename
    for filename in filenames:
        match = re.match(pattern, filename)

        if match:
            series_name = match.group("series")
            episode_number = match.group("episode")
            video_quality = match.group("quality")
            print("Series Name: " + series_name)
            print("Episode Number: " + episode_number)
            print("Video Quality: " + video_quality)
            print()
        else:
            print("No match found for " + filename)
            print()
