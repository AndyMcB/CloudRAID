import os, sqlite3
from datetime import date
from driver import DriverController
from raid.RAID5 import *
from raid.RAIDFile import RAIDFile
from subprocess import call


class Main:
    cur_milli_time = lambda: int(round(time.time() * 1000))
    conn = sqlite3.connect('file_cache.db', timeout=10)
    driver = DriverController.CloudRAID()
    raid = RAID5(driver)
    down_storage = driver.check_connection() #Contains details about any downed providers


    def __init__(self):
        RAIDFile.db_remove_file(self.conn, 'test.txt') # testing


    def upload(self, file_name):
        if len(self.down_storage) > 1:
            logging.error("Write abilitied disabled. Insufficient storage providers.\n Check your provider is up and try again")
            return

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
                            conn=self.conn)  ##ToDo - trigger data rebuild from parity if file not found occurs
            if repr(file) != "''":
                logging.warning("File successfully RAIDED")
            else:
                raise Exception('File could not be raided')
                return

            logging.warning("Writing file to storage")
            self.raid.write_file(file, file.file_name)


    def download(self, file_name):
        if len(self.down_storage) > 2:
            logging.error(
                "Read abilitied disabled. Insufficient storage providers.\n Check your providers are up and try again")
            return

        logging.warning('Downloading file data')
        f_name, ext = os.path.splitext(os.path.basename(file_name))

        data = self.driver.download_blocks(f_name)

        if data is not None:
            logging.warning("Reconstructing file data")
            if ext == '.jpg':
                self.raid.rebuild_img_file(data, f_name)
            elif ext == '.txt':
                self.raid.rebuild_txt_file(data, f_name)
            else:
                raise Exception('File Type not Supported')

            logging.warning('File Reconstructed!')
        else:
            logging.error("No Data to rebuild from")
            pass  # ToDo - implement task queue


    def remove_file(self):
        RAIDFile.db_remove_file(self.conn, 'test.txt')
        # ToDo add removal from storage units

    def check_connections(self):
        status = self.driver.check_connection()
        for status in status:
            logging.critical("Provider Down: {}".format(status[2]))

    def print_uploaded_files(self):
        pass # todo add query to sqlite db

    def get_metadata(self):
        pass


    def open_upload_folder(self):
        call(["explorer", ".\\uploads\\"])


    def exit(self):
        logging.warning("Exiting System")
        sys.exit(1)


if __name__ == "__main__":
    main = Main()


    while True:
        print("\nPlease enter a number: (1)upload (2)download (3)metadata (4)exit (5)uploads (6)downloads /")
        choice = int(input())

        if choice == 1:
            print("\nPlease input a file name from uploads folder")
            choice = input()
            main.upload("uploads/{}".format(choice))

        elif choice == 2:
            print("\nPlease input a file name to download")
            choice = input()
            main.download("{}".format(choice))

        elif choice == 3:
            print("\nPrinting metadata")
            print(main.get_metadata())

        elif choice == 4:
            main.exit()

        elif choice == 5:
            print("\nOpening up uploads folder")
            main.open_upload_folder()

        elif choice == 6:
            print("\nOpening Download Folder")
                  #todo implement
        else:
            print("Invalid input, please try agian")


##ToDo - build thread that will check connection status every minute or so