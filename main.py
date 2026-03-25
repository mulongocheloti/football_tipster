from config.settings import COMPETITIONS, SEASONS
from etl.sync_matches import sync_matches
from etl.sync_standings import sync_standings
from tipster.generate_tips import generate
from tipster.validate_tips import validate


def run():

    for season in SEASONS:

        print("Season:", season)

        for c in COMPETITIONS:

            print("Processing", c)

            sync_matches(c, season)

            sync_standings(c, season)

    generate()

    validate()


if __name__ == "__main__":

    run()
