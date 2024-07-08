import csv


def generate_csvs(tracks: list):
    with open('api.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["LAT", "LON", "SOG", "COG", "HEADING", "ROT", "NAV_STT", "TIMESTAMP", "MMSI"])
        for track in tracks:
            writer.writerow(track)
