import os, sqlite3
from tkinter import Tk
from datetime import date
from tkinter.filedialog import askopenfilename

from driver import DriverController
from raid.RAID5 import *
from raid.RAIDFile import RAIDFile
from subprocess import call


class Main:
    cur_milli_time = lambda: int(round(time.time() * 1000))
    conn = sqlite3.connect('file_cache.db', timeout=10)
    driver = DriverController.CloudRAID()
    raid = RAID5(driver)
    down_storage = driver.check_connection()  # Contains details about any downed providers


    def __init__(self):
        RAIDFile.db_remove_file(self.conn, 'test.txt')  # testing


    def upload(self, file_name):
        if len(self.down_storage) > 1:
            logging.error(
                "Write abilitied disabled. Insufficient storage providers.\n Check your provider is up and try again")
            return
        try:
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
        except FileNotFoundError:
            logging.error("File not found.")



    def download(self, file_name):
        if len(self.down_storage) > 2:
            logging.error(
                "Read abilitied disabled. Insufficient storage providers.\n Check your providers are up and try again")
            return

        logging.warning('Downloading file data')
        f_name, ext = os.path.splitext(os.path.basename(file_name))

        data = self.driver.download_blocks(f_name)
        data[2] = ('Google', '_p') #todo remove unnecessary falses from tuples

        unavailable = []
        for d in data:
            if isinstance(d, tuple):
                 unavailable.append(d)

        data = [d for d in data if type(d) != tuple]

        if len(unavailable) > 1:
            logging.critical('{} unavailable. File cannot be rebuilt.'.format(unavailable))
            return False
        elif len(unavailable) == 1:
            logging.error('{} could not find data'.format(unavailable))

        #todo remove tuples frrm data and send to relevent funations
            if data != []:
                logging.warning("Reconstructing file data")
                if ext == '.jpg':
                    self.raid.rebuild_img_file(data, f_name)
                elif ext == '.txt':
                    self.raid.rebuild_txt_file(data, f_name)
                else:
                    logging.error("File type not supported!")

                logging.warning('File Reconstructed!')
            else:
                logging.error(
                    "No Data to rebuild from. \n\tIf it was uploaded recently it may need to be indexed by your storage providers")
                pass  # ToDo - implement task queue


    def remove_file(self, file_name):
        RAIDFile.db_remove_file(self.conn, file_name)
        self.driver.delete(file_name)


    def check_connections(self):
        status = self.driver.check_connection()
        if len(status) != 0:
            for status in status:
                logging.critical("Provider Down: {}".format(status[2]))
        else:
            logging.warning("All providers up")


    def print_uploaded_files(self):
        pass  # todo add query to sqlite db


    def get_metadata(self):
        pass


    def open_upload_folder(self):
        call(["explorer", ".\\uploads\\"])


    def open_download_folder(self):
        call(["explorer", ".\\downloads\\"])


    def exit(self):
        logging.warning("Exiting System")
        sys.exit(1)


if __name__ == "__main__":
    main = Main()

    while True:
        time.sleep(2)
        print(
            "\nPlease enter a number: (1)upload (2)download (3)metadata "
            "(4)exit (5)uploads \n\t\t\t\t\t   (6)downloads (7) Delete")

        try:
            choice = int(input())
        except:
            choice = 100

        if choice == 1:
            print("\nPlease input a file name from uploads folder")
            Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
            file = askopenfilename(initialdir='uploads/')  # show an "Open" dialog box and return the path to the selected file
            file_name = os.path.basename(file)
            main.upload("uploads/{}".format(file_name))

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
            main.open_download_folder()
        elif choice == 7:
            print("\nPlease input a file name to delete")
            choice = input()
            main.remove_file(choice)
        else:
            print("Invalid input, please try agian")

            ##ToDo improve conections[T,T,T] dialog
            ##todo error when downloading  name with case mismatch
            ##ToDo thread a task that checks the internet status
            ##ToDo - build thread that will check connection status every minute or so
