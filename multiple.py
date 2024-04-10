import utils.constants as C
import utils.classes as I


scraper_runner = I.ScraperRunner(
    run_type=C.MULTIPLE,
    description="Run CalFire web scraper for a range of years"
)
scraper_runner.initialize_args()
scraper_runner.run_all()
