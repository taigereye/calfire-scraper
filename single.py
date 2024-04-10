import utils.constants as C
import utils.classes as I


scraper_runner = I.ScraperRunner(
    run_type=C.SINGLE,
    description="Run CalFire web scraper for a single year"
)
scraper_runner.initialize_args()
scraper_runner.run_one()
