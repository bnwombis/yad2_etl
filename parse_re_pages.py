import yad2_parser
import logging


logging.basicConfig(level=logging.INFO)

driver = yad2_parser.init_selenium()
yad2_parser.init_parser()
max_page = yad2_parser.get_max_page()
yad2_parser.get_all_pages(max_page)

driver.quit