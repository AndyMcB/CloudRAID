import os, sqlite3, pandas
from threading import Timer
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
        pass


    def upload(self, file_name):
        if len(self.down_storage) > 1:
            logging.error(
                "Write abilitied disabled. Insufficient storage providers.\n Check your provider is up and try again")
            return False
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
                    logging.error('File could not be raided')
                    return None

                logging.warning("Writing file to storage")

                try:
                    time = self.raid.write_file(file, file.file_name)
                    self.conn.execute('INSERT INTO upload_information (name, upload_time, date_uploaded) VALUES (?, ?, ?)',
                                 (file_metadata['full_name'], time, date.today()))
                    self.conn.commit()
                except Exception:
                    logging.error('File has no contents')

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

        unavailable = []
        for d in data:
            if isinstance(d, tuple):
                 unavailable.append(d)

        data = [d for d in data if type(d) != tuple] # Prune out actual data from

        if len(unavailable) > 1:
            logging.critical('{} unavailable. File cannot be rebuilt.'
                             '\n\tIf it was uploaded recently it may need to be indexed by your storage providers'.format(unavailable))
            return False

        elif len(unavailable) == 1:
            logging.error('Drive:{0}, {1} could not find data'.format(unavailable[0][1], unavailable[0][0]))
            missing_drive = [i[1] for i in unavailable]

            if len(missing_drive) > 0:
                missing_drive = missing_drive[0]
                if missing_drive == '_p':
                    logging.warning("Reconstructing file data")
                    if ext == '.jpg':
                        self.raid.rebuild_img_file(data, f_name)
                    elif ext == '.txt':
                        self.raid.rebuild_txt_file(data, f_name)
                    else:
                        logging.error("File type not supported!")

                    logging.warning('File Reconstructed!')

                else:
                    logging.warning("Reconstructing file data")
                    if ext == '.jpg':
                        self.raid.reconstruct_img_from_parity(data, f_name, missing_drive)
                    elif ext == '.txt':
                        self.raid.reconstruct_txt_from_parity(data, f_name, missing_drive)
                    else:
                        logging.error("File type not supported!")

                    logging.warning('File Reconstructed!')

        else:
            logging.warning("Reconstructing file data")
            if ext == '.jpg':
                self.raid.rebuild_img_file(data, f_name)
            elif ext == '.txt':
                self.raid.rebuild_txt_file(data, f_name)
            else:
                logging.error("File type not supported!")

            logging.warning('File Reconstructed!')
           # ToDo - implement task queue




    def remove_file(self, file_name):
        RAIDFile.db_remove_file(self.conn, file_name)
        self.driver.delete(file_name)


    def check_connections(self):
        status = self.driver.check_connection()
        if len(status) != 0:
            for status in status:
                logging.critical("Provider Down: {}".format(status[2]))



    def print_uploaded_files(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM files')
        info = cur.fetchall()
        headings = ['Full Name', 'Name', 'Extention', 'Size(B)', 'Date Uploaded']
        print(pandas.DataFrame(info, columns=headings))
        self.conn.commit()



    def get_metadata(self):
        remaining = self.driver.remaining_storage()
        print(remaining)

        cur = self.conn.cursor()
        cur.execute('Select * FROM upload_information')
        res = cur.fetchall()

        print('\nShowing last 10 uploads:')
        headings = ['File Name','Upload Time(ms)','Date Uploaded', '']
        print(pandas.DataFrame(res, columns=headings))

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
        options = [['Upload File (1)', 'Download File (2)'], ['Show Metadata (3)', 'Exit Session (4)'], ['Open uploads (5)',
                   'Open downloads (6)'], ['Delete File (7)', 'Show Available Files (8)']]
        print('____________________________________________________________________________\nEnter number from list below:')
        print(pandas.DataFrame(options, columns= ['','']))

        try:
            choice = int(input())
        except:
            choice = 100

        if choice == 1:
            print("\nPlease select a file")
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
            main.get_metadata()

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

        elif choice == 8:
            print("\nUploaded file data:\n")
            main.print_uploaded_files()
        else:
            print("Invalid input, please try agian")

        main.check_connections()

            ##todo error when downloading  name with case mismatch

# WARNING:root:File Payload is 3687.552 kilobytes
# WARNING:root:File uploaded to Dropbox
# WARNING:root:File Uploaded to Google
# WARNING:root:File Uploaded to Box
# WARNING:root:File uploaded in 4728.476 seconds
