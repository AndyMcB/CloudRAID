import os, sqlite3
from datetime import date
from driver import DriverController
from raid.RAID5 import *
from raid.RAIDFile import RAIDFile

logging.warning(' Started')
cur_milli_time = lambda: int(round(time.time() * 1000))

start_time = cur_milli_time()
try:
    file_name = sys.argv[1]
except:
    file_name = 'testFiles/test.txt'

conn = sqlite3.connect('file_cache.db', timeout=10)
driver = DriverController.CloudRAID()
raid = RAID5(driver)

with open(file_name, 'rb') as file:
    logging.warning("File: " + file_name)
    f_name, ext = os.path.splitext(os.path.basename(file.name))

    file_metadata = {
        'name': f_name,
        'file_type': ext,
        'full_name': f_name + ext,
        'size': os.path.getsize(file_name),
        'date_added': date.today()
    }

    file = RAIDFile(1, file_metadata, file.read(),
                    conn=conn)  ##ToDo - trigger data rebuild from parity if file not found occurs

    if repr(file) != "''":
        logging.warning("File successfully RAIDED")
        logging.warning("Writing file to storage")
        raid.write_file(file, file.file_name)

    logging.warning('Downloading file data')
    data = driver.download_blocks(f_name)

    if data is not None:
        logging.warning("Reconstructing file data")
        ret = raid.reconstruct_txt_from_parity(data, f_name, '_1')
        logging.warning('File Reconstructed!')
    else:
        logging.error("No Data to rebuild from")
        pass  # ToDo - implement task queue

conn.close()
end_time = cur_milli_time()
total_time = end_time - start_time
logging.warning("Program completed in approximatly " + str(total_time/1000) + ' seconds')