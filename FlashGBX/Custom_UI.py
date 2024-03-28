from PySide6.QtWidgets import QMainWindow, QApplication
import datetime, shutil, platform, os, math, traceback, re, time, serial, zipfile, subprocess, threading, sys

from PySide6.QtCore import QFile

from . import Util
from .pyside import QtCore, QtWidgets, QtGui, QApplication
from PySide6.QtUiTools import QUiLoader
from .Util import APPNAME, VERSION, VERSION_PEP440, ANSI
from .RomFileDMG import RomFileDMG
from .RomFileAGB import RomFileAGB
from .PocketCamera import PocketCamera
from . import hw_GBxCartRW, hw_GBxCartRW_ofw
from .ui.main_window import MainWindow

hw_devices = [hw_GBxCartRW, hw_GBxCartRW_ofw]


class Custom_UI(QMainWindow):

    CONN = None
    SETTINGS = None
    DEVICE = None
    FLASHCARTS = {"DMG": {}, "AGB": {}}
    APP_PATH = ""
    CONFIG_PATH = ""
    TBPROG = None  # Windows 7+ Taskbar Progress Bar
    PROGRESS = None
    CAMWIN = None
    FWUPWIN = None
    STATUS = {}

    def __init__(self, args):
        super(Custom_UI, self).__init__()
        self.ui = MainWindow()
        self.ui.setupUi(self)

        Util.APP_PATH = args['app_path']
        Util.CONFIG_PATH = args['config_path']
        self.FLASHCARTS = args["flashcarts"]
        self.PROGRESS = Util.Progress(self.UpdateProgress)
        self.ARGS = args

        global prog_bar_part_char
        if platform.system() == "Windows":
            prog_bar_part_char = [" ", " ", " ", " ", "▌", "▌", "▌", "▌"]
        else:
            prog_bar_part_char = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"]

        #connect buttons
        self.ui.playButton.clicked.connect(self.openEmulator)
        self.ui.pushButton_5.clicked.connect(self.restartAsOriginalGUI)

    def restartAsOriginalGUI(self):
        os.execv(sys.executable, ['python'] + [sys.argv[0]])

    def openEmulator(self):
        args = self.ARGS["argparsed"]
        header = self.SetUpCart(args)
        self.BackupROM(args, header)
        self.BackupRestoreRAM(args, header, "backup-save", True)

        emu_path = "C:\\Users\\admin\\Documents\\bgb\\bgb.exe"
        #emu_path = "E:\\Emuladores\\Gameboy\\bgbw64\\bgb64.exe"
        roms_dir = sys.path[1]
        rom_path = Util.GenerateFileName(mode=self.CONN.GetMode(), header=self.CONN.INFO, settings=None)

        self.DisconnectDevice()
        t = self.popenWithCallback([emu_path,
                                    roms_dir + "\\" + rom_path],
                                   self.onEmulatorClosed)

    def onEmulatorClosed(self):
        print("Emulator closed")
        args = self.ARGS["argparsed"]
        header = self.SetUpCart(args)
        self.BackupRestoreRAM(args, header, "restore-save", True)
        self.DisconnectDevice()

    def BackupROM(self, args, header):
        mbc = 1
        rom_size = 0

        path = Util.GenerateFileName(mode=self.CONN.GetMode(), header=self.CONN.INFO, settings=None)
        if self.CONN.GetMode() == "DMG":
            if args.dmg_mbc == "auto":
                try:
                    mbc = header["mapper_raw"]
                    if mbc == 0: mbc = 0x19  # MBC5 default
                except:
                    print(
                        "{:s}Couldn’t determine MBC type, will try to use MBC5. It can also be manually set with the “--dmg-mbc” command line switch.{:s}".format(
                            ANSI.YELLOW, ANSI.RESET))
                    mbc = 0x19
            else:
                if args.dmg_mbc.startswith("0x"):
                    mbc = int(args.dmg_mbc[2:], 16)
                elif args.dmg_mbc.isnumeric():
                    mbc = int(args.dmg_mbc)
                    if mbc == 1:
                        mbc = 0x01
                    elif mbc == 2:
                        mbc = 0x06
                    elif mbc == 3:
                        mbc = 0x13
                    elif mbc == 5:
                        mbc = 0x19
                    elif mbc == 6:
                        mbc = 0x20
                    elif mbc == 7:
                        mbc = 0x22
                    else:
                        mbc = 0x19
                else:
                    mbc = 0x19

            if args.dmg_romsize == "auto":
                try:
                    rom_size = Util.DMG_Header_ROM_Sizes_Flasher_Map[header["rom_size_raw"]]
                except:
                    print(
                        "{:s}Couldn’t determine ROM size, will use 8 MiB. It can also be manually set with the “--dmg-romsize” command line switch.{:s}".format(
                            ANSI.YELLOW, ANSI.RESET))
                    rom_size = 8 * 1024 * 1024
            else:
                sizes = ["auto", "32kb", "64kb", "128kb", "256kb", "512kb", "1mb", "2mb", "4mb", "8mb", "16mb", "32mb"]
                rom_size = Util.DMG_Header_ROM_Sizes_Flasher_Map[sizes.index(args.dmg_romsize) - 1]

        elif self.CONN.GetMode() == "AGB":
            if args.agb_romsize == "auto":
                rom_size = header["rom_size"]
            else:
                sizes = ["auto", "64kb", "128kb", "256kb", "512kb", "1mb", "2mb", "4mb", "8mb", "16mb", "32mb", "64mb",
                         "128mb", "256mb", "512mb"]
                rom_size = Util.AGB_Header_ROM_Sizes_Map[sizes.index(args.agb_romsize) - 1]

        if args.path != "auto":
            if os.path.isdir(args.path):
                path = args.path + "/" + path
            else:
                path = args.path

        if (path == ""): return
        if not args.overwrite and os.path.exists(os.path.abspath(path)):
            #answer = input("The target file “{:s}” already exists.\nDo you want to overwrite it? [y/N]: ".format(
                #os.path.abspath(path))).strip().lower()
            #print("")
            #if answer != "y":
                #print("Canceled.")
                #return
            print("ROM already backed")
            return

        try:
            f = open(path, "ab+")
            f.close()
        except PermissionError:
            print("{:s}Couldn’t access file “{:s}”.{:s}".format(ANSI.RED, path, ANSI.RESET))
            return
        except FileNotFoundError:
            print("{:s}Couldn’t find file “{:s}”.{:s}".format(ANSI.RED, path, ANSI.RESET))
            return

        s_mbc = ""
        if self.CONN.GetMode() == "DMG":
            if mbc in Util.DMG_Header_Mapper:
                s_mbc = " using Mapper Type “{:s}”".format(Util.DMG_Header_Mapper[mbc])
            else:
                s_mbc = " using Mapper Type 0x{:X}".format(mbc)
        if self.CONN.GetMode() == "DMG":
            print("The ROM will now be read{:s} and saved to “{:s}”.".format(s_mbc, os.path.abspath(path)))
        else:
            print("The ROM will now be read and saved to “{:s}”.".format(os.path.abspath(path)))

        print("")

        cart_type = 0
        if args.flashcart_type != "autodetect":
            if self.CONN.GetMode() == "DMG":
                carts = self.CONN.GetSupportedCartridgesDMG()[1]
            elif self.CONN.GetMode() == "AGB":
                carts = self.CONN.GetSupportedCartridgesAGB()[1]
            cart_type = 0
            for i in range(0, len(carts)):
                if not "names" in carts[i]: continue
                if carts[i]["type"] != self.CONN.GetMode(): continue
                if args.flashcart_type in carts[i]["names"] and "flash_size" in carts[i]:
                    print("Selected cartridge type: {:s}\n".format(args.flashcart_type))
                    rom_size = carts[i]["flash_size"]
                    cart_type = i
                    break
            if cart_type == 0:
                print("ERROR: Couldn’t select the selected cartridge type.\n")
        else:
            if self.CONN.GetMode() == "AGB":
                cart_types = self.CONN.GetSupportedCartridgesAGB()
                if "flash_type" in header:
                    print("Selected cartridge type: {:s}\n".format(cart_types[0][header["flash_type"]]))
                    cart_type = header["flash_type"]
                elif header['logo_correct'] and header['3d_memory'] is True:
                    for i in range(0, len(cart_types[0])):
                        if "3d_memory" in cart_types[1][i]:
                            print("Selected cartridge type: {:s}\n".format(cart_types[0][i]))
                            cart_type = i
                            break
        self.CONN.TransferData(
            args={'mode': 1, 'path': path, 'mbc': mbc, 'rom_size': rom_size, 'agb_rom_size': rom_size, 'start_addr': 0,
                  'fast_read_mode': True, 'cart_type': cart_type}, signal=self.PROGRESS.SetProgress)

    def BackupRestoreRAM(self, args, header, action, overwrite=False):
        add_date_time = args.save_filename_add_datetime is True
        rtc = args.store_rtc is True

        path_datetime = ""
        if add_date_time:
            path_datetime = "_{:s}".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

        path = Util.GenerateFileName(mode=self.CONN.GetMode(), header=self.CONN.INFO, settings=None)
        path = os.path.splitext(path)[0]
        path += "{:s}.sav".format(path_datetime)

        if self.CONN.GetMode() == "DMG":
            if args.dmg_mbc == "auto":
                try:
                    mbc = header["mapper_raw"]
                    if mbc == 0: mbc = 0x19  # MBC5 default
                except:
                    print(
                        "{:s}Couldn’t determine MBC type, will try to use MBC5. It can also be manually set with the “--dmg-mbc” command line switch.{:s}".format(
                            ANSI.YELLOW, ANSI.RESET))
                    mbc = 0x19
            else:
                if args.dmg_mbc.startswith("0x"):
                    mbc = int(args.dmg_mbc[2:], 16)
                elif args.dmg_mbc.isnumeric():
                    mbc = int(args.dmg_mbc)
                    if mbc == 1:
                        mbc = 0x01
                    elif mbc == 2:
                        mbc = 0x06
                    elif mbc == 3:
                        mbc = 0x13
                    elif mbc == 5:
                        mbc = 0x19
                    elif mbc == 6:
                        mbc = 0x20
                    elif mbc == 7:
                        mbc = 0x22
                    else:
                        mbc = 0x19
                else:
                    mbc = 0x19

            if args.dmg_savesize == "auto":
                try:
                    if header['mapper_raw'] == 0x06:  # MBC2
                        save_type = 1
                    elif header['mapper_raw'] == 0x22 and header["game_title"] in (
                    "KORO2 KIRBYKKKJ", "KIRBY TNT_KTNE"):  # MBC7 Kirby
                        save_type = 0x101
                    elif header['mapper_raw'] == 0x22 and header["game_title"] in (
                    "CMASTER_KCEJ"):  # MBC7 Command Master
                        save_type = 0x102
                    elif header['mapper_raw'] == 0xFD:  # TAMA5
                        save_type = 0x103
                    elif header['mapper_raw'] == 0x20:  # TAMA5
                        save_type = 0x104
                    else:
                        save_type = header['ram_size_raw']
                except:
                    save_type = 0x20000
            else:
                sizes = ["auto", "4k", "16k", "64k", "256k", "512k", "1m", "eeprom2k", "eeprom4k", "tama5", "4m"]
                save_type = args.dmg_savesize

            if save_type == 0:
                print(
                    "{:s}Unable to auto-detect the save size. Please use the “--dmg-savesize” command line switch to manually select it.{:s}".format(
                        ANSI.RED, ANSI.RESET))
                return

        elif self.CONN.GetMode() == "AGB":
            if args.agb_savetype == "auto":
                save_type = header["save_type"]
            else:
                sizes = ["auto", "eeprom4k", "eeprom64k", "sram256k", "flash512k", "flash1m", "dacs8m", "sram512k",
                         "sram1m"]
                save_type = sizes.index(args.agb_savetype)

            mbc = 0
            if save_type == 0 or save_type == None:
                print(
                    "{:s}Unable to auto-detect the save type. Please use the “--agb-savetype” command line switch to manually select it.{:s}".format(
                        ANSI.RED, ANSI.RESET))
                return

        else:
            return

        if args.path != "auto":
            if os.path.isdir(args.path):
                path = args.path + "/" + path
            else:
                path = args.path

        if (path == ""): return

        s_mbc = ""
        if self.CONN.GetMode() == "DMG":
            if mbc in Util.DMG_Header_Mapper:
                s_mbc = " using Mapper Type “{:s}”".format(Util.DMG_Header_Mapper[mbc])
            else:
                s_mbc = " using Mapper Type 0x{:X}".format(mbc)
        if action == "backup-save":
            if not overwrite and os.path.exists(os.path.abspath(path)):
                answer = input("The target file “{:s}” already exists.\nDo you want to overwrite it? [y/N]: ".format(
                    os.path.abspath(path))).strip().lower()
                print("")
                if answer != "y":
                    print("Canceled.")
                    return
                print("Save file will be rewritten")
            print("The cartridge save data will now be read{:s} and saved to the following file:\n{:s}".format(s_mbc,
                                                                                                               os.path.abspath(
                                                                                                                   path)))
        elif action == "restore-save":
            if not overwrite:
                answer = input(
                    "Restoring save data to the cartridge will erase the existing save.\nDo you want to overwrite it? [y/N]: ").strip().lower()
                if answer != "y":
                    print("Canceled.")
                    return
            print("The following save data file will now be written to the cartridge{:s}:\n{:s}".format(s_mbc,
                                                                                                        os.path.abspath(
                                                                                                            path)))
        elif action == "erase-save":
            if not overwrite:
                answer = input("Do you really want to erase the save data from the cartridge? [y/N]: ").strip().lower()
                if answer != "y":
                    print("Canceled.")
                    return
            print("The cartridge save data will now be erased from the cartridge{:s}.".format(s_mbc))
        elif action == "debug-test-save":
            print("The cartridge save data size will now be examined{:s}.\nNote: This is for debug use only.\n".format(
                s_mbc))

        if self.CONN.GetMode() == "AGB":
            if action == "restore-save" or action == "erase-save":
                buffer = None
                if self.CONN.GetMode() == "AGB" and "ereader" in self.CONN.INFO and self.CONN.INFO["ereader"] is True:
                    if self.CONN.GetFWBuildDate() == "":  # Legacy Mode
                        print("This cartridge is not supported in Legacy Mode.")
                        return
                    self.CONN.ReadInfo()
                    if "ereader_calibration" in self.CONN.INFO:
                        with open(path, "rb") as f:
                            buffer = bytearray(f.read())
                        if buffer[0xD000:0xF000] != self.CONN.INFO["ereader_calibration"]:
                            if not overwrite:
                                if action == "erase-save": action = "restore-save"
                                print("Note: Keeping existing e-Reader calibration data.")
                                buffer[0xD000:0xF000] = self.CONN.INFO["ereader_calibration"]
                            else:
                                print("Note: Overwriting existing e-Reader calibration data.")
                    else:
                        print("Note: No existing e-Reader calibration data found.")
            print("Using Save Type “{:s}”.".format(Util.AGB_Header_Save_Types[save_type]))
        elif self.CONN.GetMode() == "DMG":
            if rtc and header["mapper_raw"] in (0x10, 0x110, 0xFE):  # RTC of MBC3, MBC30, HuC-3
                print("Real Time Clock register values will also be written if applicable/possible.")

        try:
            if action == "backup-save":
                f = open(path, "ab+")
                f.close()
            elif action == "restore-save":
                f = open(path, "rb+")
                f.close()
        except PermissionError:
            print("{:s}Couldn’t access file “{:s}”.{:s}".format(ANSI.RED, path, ANSI.RESET))
            return
        except FileNotFoundError:
            print("{:s}Couldn’t find file “{:s}”.{:s}".format(ANSI.RED, path, ANSI.RESET))
            return

        print("")
        if action == "backup-save":
            self.CONN.TransferData(args={'mode': 2, 'path': path, 'mbc': mbc, 'save_type': save_type, 'rtc': rtc},
                                   signal=self.PROGRESS.SetProgress)
        elif action == "restore-save":
            verify_write = args.no_verify_write is False
            targs = {'mode': 3, 'path': path, 'mbc': mbc, 'save_type': save_type, 'erase': False, 'rtc': rtc,
                     'verify_write': verify_write}
            #if buffer is not None:
            #    targs["buffer"] = buffer
            #    targs["path"] = None
            self.CONN.TransferData(args=targs, signal=self.PROGRESS.SetProgress)
        elif action == "erase-save":
            self.CONN.TransferData(
                args={'mode': 3, 'path': path, 'mbc': mbc, 'save_type': save_type, 'erase': True, 'rtc': rtc},
                signal=self.PROGRESS.SetProgress)
        elif action == "debug-test-save":  # debug
            self.ARGS["debug"] = True

            print("Making a backup of the original save data.")
            ret = self.CONN.TransferData(
                args={'mode': 2, 'path': Util.CONFIG_PATH + "/test1.bin", 'mbc': mbc, 'save_type': save_type},
                signal=self.PROGRESS.SetProgress)
            if ret is False: return False
            time.sleep(0.1)
            print("Writing random data.")
            test2 = bytearray(os.urandom(os.path.getsize(Util.CONFIG_PATH + "/test1.bin")))
            with open(Util.CONFIG_PATH + "/test2.bin", "wb") as f:
                f.write(test2)
            self.CONN.TransferData(
                args={'mode': 3, 'path': Util.CONFIG_PATH + "/test2.bin", 'mbc': mbc, 'save_type': save_type,
                      'erase': False}, signal=self.PROGRESS.SetProgress)
            time.sleep(0.1)
            print("Reading back and comparing data.")
            self.CONN.TransferData(
                args={'mode': 2, 'path': Util.CONFIG_PATH + "/test3.bin", 'mbc': mbc, 'save_type': save_type},
                signal=self.PROGRESS.SetProgress)
            time.sleep(0.1)
            with open(Util.CONFIG_PATH + "/test3.bin", "rb") as f:
                test3 = bytearray(f.read())
            if self.CONN.CanPowerCycleCart():
                print("\nPower cycling.")
                for _ in range(0, 5):
                    self.CONN.CartPowerCycle(delay=0.1)
                    time.sleep(0.1)
                self.CONN.ReadInfo(checkRtc=False)
            time.sleep(0.2)
            print("\nReading back and comparing data again.")
            self.CONN.TransferData(
                args={'mode': 2, 'path': Util.CONFIG_PATH + "/test4.bin", 'mbc': mbc, 'save_type': save_type},
                signal=self.PROGRESS.SetProgress)
            time.sleep(0.1)
            with open(Util.CONFIG_PATH + "/test4.bin", "rb") as f:
                test4 = bytearray(f.read())
            print("Restoring original save data.")
            self.CONN.TransferData(
                args={'mode': 3, 'path': Util.CONFIG_PATH + "/test1.bin", 'mbc': mbc, 'save_type': save_type,
                      'erase': False}, signal=self.PROGRESS.SetProgress)
            time.sleep(0.1)

            if mbc == 6:
                for i in range(0, len(test2)):
                    test2[i] &= 0x0F
                    test3[i] &= 0x0F
                    test4[i] &= 0x0F

            if test2 != test4:
                diffcount = 0
                for i in range(0, len(test2)):
                    if test2[i] != test4[i]: diffcount += 1
                print("\n{:s}Differences found: {:d}{:s}".format(ANSI.RED, diffcount, ANSI.RESET))
            if test3 != test4:
                diffcount = 0
                for i in range(0, len(test3)):
                    if test3[i] != test4[i]: diffcount += 1
                print("\n{:s}Differences found between two consecutive readbacks: {:d}{:s}".format(ANSI.RED, diffcount,
                                                                                                   ANSI.RESET))
                input("")

            found_offset = test2.find(test3[0:512])
            if found_offset < 0:
                if self.CONN.GetMode() == "AGB":
                    print(
                        "\n{:s}It was not possible to save any data to the cartridge using save type “{:s}”.{:s}".format(
                            ANSI.RED, Util.AGB_Header_Save_Types[save_type], ANSI.RESET))
                else:
                    print(
                        "\n{:s}It was not possible to save any data to the cartridge.{:s}".format(ANSI.RED, ANSI.RESET))
            else:
                if found_offset == 0 and test2 != test3:  # Pokémon Crystal JPN
                    found_length = 0
                    for i in range(0, len(test2)):
                        if test2[i] != test3[i]: break
                        found_length += 1
                else:
                    found_length = len(test2) - found_offset

                if self.CONN.GetMode() == "DMG":
                    print("\n{:s}Done! The writable save data size is {:s} out of {:s} checked.{:s}".format(ANSI.GREEN,
                                                                                                            Util.formatFileSize(
                                                                                                                size=found_length),
                                                                                                            Util.formatFileSize(
                                                                                                                size=
                                                                                                                Util.DMG_Header_RAM_Sizes_Flasher_Map[
                                                                                                                    Util.DMG_Header_RAM_Sizes_Map.index(
                                                                                                                        save_type)]),
                                                                                                            ANSI.RESET))
                elif self.CONN.GetMode() == "AGB":
                    print(
                        "\n{:s}Done! The writable save data size using save type “{:s}” is {:s}.{:s}".format(ANSI.GREEN,
                                                                                                             Util.AGB_Header_Save_Types[
                                                                                                                 save_type],
                                                                                                             Util.formatFileSize(
                                                                                                                 size=found_length),
                                                                                                             ANSI.RESET))

            try:
                (_, _, cfi) = self.CONN.CheckFlashChip(limitVoltage=False)
                if len(cfi["raw"]) > 0:
                    with open(Util.CONFIG_PATH + "/cfi.bin", "wb") as f: f.write(cfi["raw"])
                    print("CFI data was extracted to “cfi.bin”.")
            except:
                pass

    def SetUpCart(self, args):
        # Connect to device
        if not self.FindDevices(port=None):
            print("No devices found.")
            return
        else:
            if not self.ConnectDevice():
                print("Couldn’t connect to the device.")
                return
            dev = self.DEVICE[1]
            builddate = dev.GetFWBuildDate()
            if builddate != "":
                print("\nConnected to {:s}".format(dev.GetFullNameExtended(more=True)))
            else:
                print("\nConnected to {:s}".format(dev.GetFullNameExtended()))

        # Choose gameboy mode by default
        print("Cartridge Mode: Game Boy or Game Boy Color")
        self.CONN.SetMode("DMG")
        time.sleep(0.2)

        # Read Header
        header = self.CONN.ReadInfo()
        (bad_read, s_header, header) = self.ReadCartridge(header)
        if s_header == "":
            print("\n{:s}Couldn’t read cartridge header. Please try again.{:s}\n".format(ANSI.RED, ANSI.RESET))
            self.DisconnectDevice()
            return
        if bad_read and not args.ignore_bad_header and (self.CONN.GetMode() == "AGB" or (
                self.CONN.GetMode() == "DMG" and "mapper_raw" in header and header["mapper_raw"] != 0x203)):
            print(
                "\n{:s}Invalid data was detected which usually means that the cartridge couldn’t be read correctly. Please make sure you selected the correct mode and that the cartridge contacts are clean. This check can be disabled with the command line switch “--ignore-bad-header”.{:s}\n".format(
                    ANSI.RED, ANSI.RESET))
            print("Cartridge Information:")
            print(s_header)
            self.DisconnectDevice()
            return

        print("\nCartridge Information:")
        print(s_header)

        return header

    def FindDevices(self, port=None):
        # pylint: disable=global-variable-not-assigned
        global hw_devices
        for hw_device in hw_devices:
            dev = hw_device.GbxDevice()
            ret = dev.Initialize(self.FLASHCARTS, port=port,
                                 max_baud=1000000 if self.ARGS["argparsed"].device_limit_baudrate else 1700000)
            if ret is False:
                self.CONN = None
            elif isinstance(ret, list):
                if len(ret) > 0: print("\n")
                for i in range(0, len(ret)):
                    status = ret[i][0]
                    msg = re.sub('<[^<]+?>', '', ret[i][1])
                    if status == 3:
                        print("{:s}{:s}{:s}".format(ANSI.RED, msg.replace("\n\n", "\n"), ANSI.RESET))
                        self.CONN = None

            if dev.IsConnected():
                self.DEVICE = (dev.GetFullNameExtended(), dev)
                dev.Close()
                break

        if self.DEVICE is None: return False
        return True

    def ConnectDevice(self):
        dev = self.DEVICE[1]
        port = dev.GetPort()
        ret = dev.Initialize(self.FLASHCARTS, port=port,
                             max_baud=1000000 if self.ARGS["argparsed"].device_limit_baudrate else 1700000)

        if ret is False:
            print("\n{:s}An error occured while trying to connect to the device.{:s}".format(ANSI.RED, ANSI.RESET))
            traceback.print_stack()
            self.CONN = None
            return False

        elif isinstance(ret, list):
            for i in range(0, len(ret)):
                status = ret[i][0]
                msg = re.sub('<[^<]+?>', '', ret[i][1])
                if status == 0:
                    print("\n" + msg)
                elif status == 1:
                    print("{:s}".format(msg))
                elif status == 2:
                    print("{:s}{:s}{:s}".format(ANSI.YELLOW, msg, ANSI.RESET))
                elif status == 3:
                    print("{:s}{:s}{:s}".format(ANSI.RED, msg, ANSI.RESET))
                    self.CONN = None
                    return False

        if dev.FW_UPDATE_REQ:
            print(
                "{:s}A firmware update for your {:s} device is required to fully use this software.\nPlease visit the official website at {:s} for updates.\n{:s}Current firmware version: {:s}{:s}".format(
                    ANSI.RED, dev.GetFullName(), dev.GetOfficialWebsite(), ANSI.YELLOW, dev.GetFirmwareVersion(),
                    ANSI.RESET))
            time.sleep(5)

        self.CONN = dev
        return True

    def DisconnectDevice(self):
        try:
            devname = self.CONN.GetFullNameExtended()
            self.CONN.Close(cartPowerOff=True)
            print("Disconnected from {:s}".format(devname))
        except:
            pass
        self.CONN = None

    def ReadCartridge(self, data):
        bad_read = False
        s = ""
        if self.CONN.GetMode() == "DMG":
            s += "Game Title:      {:s}\n".format(data["game_title"])
            if len(data['game_code']) > 0:
                s += "Game Code:       {:s}\n".format(data['game_code'])
            s += "Revision:        {:s}\n".format(str(data["version"]))
            s += "Super Game Boy:  "
            if data['sgb'] in Util.DMG_Header_SGB:
                s += "{:s}\n".format(Util.DMG_Header_SGB[data['sgb']])
            else:
                s += "Unknown (0x{:02X})\n".format(data['sgb'])
            s += "Game Boy Color:  "
            if data['cgb'] in Util.DMG_Header_CGB:
                s += "{:s}\n".format(Util.DMG_Header_CGB[data['cgb']])
            else:
                s += "Unknown (0x{:02X})\n".format(data['cgb'])

            s += "Real Time Clock: " + data["rtc_string"] + "\n"

            if data["logo_correct"]:
                s += "Nintendo Logo:   OK\n"
                if not os.path.exists(Util.CONFIG_PATH + "/bootlogo_dmg.bin"):
                    with open(Util.CONFIG_PATH + "/bootlogo_dmg.bin", "wb") as f:
                        f.write(data['raw'][0x104:0x134])
            else:
                s += "Nintendo Logo:   {:s}Invalid{:s}\n".format(ANSI.RED, ANSI.RESET)
                bad_read = True

            if data['header_checksum_correct']:
                s += "Header Checksum: Valid (0x{:02X})\n".format(data['header_checksum'])
            else:
                s += "Header Checksum: {:s}Invalid (0x{:02X}){:s}\n".format(ANSI.RED, data['header_checksum'],
                                                                            ANSI.RESET)
                bad_read = True
            s += "ROM Checksum:    0x{:04X}\n".format(data['rom_checksum'])
            try:
                s += "ROM Size:        {:s}\n".format(Util.DMG_Header_ROM_Sizes[data['rom_size_raw']])
            except:
                s += "ROM Size:        {:s}Not detected{:s}\n".format(ANSI.RED, ANSI.RESET)
                bad_read = True

            try:
                if data['mapper_raw'] == 0x06:  # MBC2
                    s += "Save Type:       {:s}\n".format(Util.DMG_Header_RAM_Sizes[1])
                elif data['mapper_raw'] == 0x22 and data["game_title"] in (
                        "KORO2 KIRBY", "KIRBY TNT"):  # MBC7 Kirby
                    s += "Save Type:       {:s}\n".format(
                        Util.DMG_Header_RAM_Sizes[Util.DMG_Header_RAM_Sizes_Map.index(0x101)])
                elif data['mapper_raw'] == 0x22 and data["game_title"] in ("CMASTER"):  # MBC7 Command Master
                    s += "Save Type:       {:s}\n".format(
                        Util.DMG_Header_RAM_Sizes[Util.DMG_Header_RAM_Sizes_Map.index(0x102)])
                elif data['mapper_raw'] == 0xFD:  # TAMA5
                    s += "Save Type:       {:s}\n".format(
                        Util.DMG_Header_RAM_Sizes[Util.DMG_Header_RAM_Sizes_Map.index(0x103)])
                elif data['mapper_raw'] == 0x20:  # MBC6
                    s += "Save Type:       {:s}\n".format(
                        Util.DMG_Header_RAM_Sizes[Util.DMG_Header_RAM_Sizes_Map.index(0x104)])
                else:
                    s += "Save Type:       {:s}\n".format(
                        Util.DMG_Header_RAM_Sizes[Util.DMG_Header_RAM_Sizes_Map.index(data['ram_size_raw'])])
            except:
                s += "Save Type:       Not detected\n"

            try:
                s += "Mapper Type:     {:s}\n".format(Util.DMG_Header_Mapper[data['mapper_raw']])
            except:
                s += "Mapper Type:     {:s}Not detected{:s}\n".format(ANSI.RED, ANSI.RESET)
                bad_read = True

            if data['logo_correct'] and not self.CONN.IsSupportedMbc(data["mapper_raw"]):
                print(
                    "{:s}\nWARNING: This cartridge uses a mapper that may not be completely supported by {:s} using the current firmware version of the {:s} device. Please check for firmware updates.{:s}".format(
                        ANSI.YELLOW, APPNAME, self.CONN.GetFullName(), ANSI.RESET))
            if data['logo_correct'] and data['game_title'] in ("NP M-MENU MENU", "DMG MULTI MENU ") and self.ARGS[
                "argparsed"].flashcart_type == "autodetect":
                cart_types = self.CONN.GetSupportedCartridgesDMG()
                for i in range(0, len(cart_types[0])):
                    if "DMG-MMSA-JPN" in cart_types[0][i]:
                        self.ARGS["argparsed"].flashcart_type = cart_types[0][i]

        elif self.CONN.GetMode() == "AGB":
            s += "Game Title:           {:s}\n".format(data["game_title"])
            s += "Game Code:            {:s}\n".format(data["game_code"])
            s += "Revision:             {:d}\n".format(data["version"])

            s += "Real Time Clock:      " + data["rtc_string"] + "\n"

            if data["logo_correct"]:
                s += "Nintendo Logo:        OK\n"
                if not os.path.exists(Util.CONFIG_PATH + "/bootlogo_agb.bin"):
                    with open(Util.CONFIG_PATH + "/bootlogo_agb.bin", "wb") as f:
                        f.write(data['raw'][0x04:0xA0])
            else:
                s += "Nintendo Logo:        {:s}Invalid{:s}\n".format(ANSI.RED, ANSI.RESET)
                bad_read = True
            if data["96h_correct"]:
                s += "Cartridge Identifier: OK\n"
            else:
                s += "Cartridge Identifier: {:s}Invalid{:s}\n".format(ANSI.RED, ANSI.RESET)
                bad_read = True

            if data['header_checksum_correct']:
                s += "Header Checksum:      Valid (0x{:02X})\n".format(data['header_checksum'])
            else:
                s += "Header Checksum:      {:s}Invalid (0x{:02X}){:s}\n".format(ANSI.RED, data['header_checksum'],
                                                                                 ANSI.RESET)
                bad_read = True

            s += "ROM Checksum:         "
            # Util.AGB_Global_CRC32 = 0
            db_agb_entry = data["db"]
            if db_agb_entry != None:
                if data["rom_size_calc"] < 0x400000:
                    s += "In database (0x{:06X})\n".format(db_agb_entry['rc'])
                # Util.AGB_Global_CRC32 = db_agb_entry['rc']
                s += "ROM Size:             {:d} MiB\n".format(int(db_agb_entry['rs'] / 1024 / 1024))
                data['rom_size'] = db_agb_entry['rs']
            elif data["rom_size"] != 0:
                s += "Not in database\n"
                if not data["rom_size"] in Util.AGB_Header_ROM_Sizes_Map:
                    data["rom_size"] = 0x2000000
                s += "ROM Size:             {:d} MiB\n".format(int(data["rom_size"] / 1024 / 1024))
            else:
                s += "Not in database\n"
                s += "ROM Size:             Not detected\n"
                bad_read = True

            stok = False
            if data["save_type"] == None:
                if db_agb_entry != None:
                    if db_agb_entry['st'] < len(Util.AGB_Header_Save_Types):
                        stok = True
                        s += "Save Type:            {:s}\n".format(Util.AGB_Header_Save_Types[db_agb_entry['st']])
                        data["save_type"] = db_agb_entry['st']
                if data["dacs_8m"] is True:
                    stok = True
                    s += "Save Type:            {:s}\n".format(Util.AGB_Header_Save_Types[6])
                    data["save_type"] = 6

            if stok is False:
                s += "Save Type:            Not detected\n"

            if data['logo_correct'] and isinstance(db_agb_entry, dict) and "rs" in db_agb_entry and db_agb_entry[
                'rs'] == 0x4000000 and not self.CONN.IsSupported3dMemory():
                print(
                    "{:s}\nWARNING: This cartridge uses a Memory Bank Controller that may not be completely supported yet. A future version of the {:s} device firmware may add support for it.{:s}".format(
                        ANSI.YELLOW, self.CONN.GetFullName(), ANSI.RESET))

            if "has_rtc" in data and data["has_rtc"] is not True and "no_rtc_reason" in data:
                if data["no_rtc_reason"] == 1:
                    print(
                        "{:s}NOTE: It seems that this cartridge’s Real Time Clock battery may no longer be functional and needs to be replaced.{:s}".format(
                            ANSI.YELLOW, ANSI.RESET))

        return (bad_read, s, data)

    def UpdateProgress(self, args):
        if args is None: return

        if "error" in args:
            print("{:s}{:s}{:s}".format(ANSI.RED, args["error"], ANSI.RESET))
            return

        pos = 0
        size = 0
        speed = 0
        elapsed = 0
        left = 0
        if "pos" in args: pos = args["pos"]
        if "size" in args: size = args["size"]
        if "speed" in args: speed = args["speed"]
        if "time_elapsed" in args: elapsed = args["time_elapsed"]
        if "time_left" in args: left = args["time_left"]

        if "action" in args:
            if args["action"] == "INITIALIZE":
                if args["method"] == "ROM_WRITE_VERIFY":
                    print("\n\nThe newly written ROM data will now be checked for errors.\n")
                elif args["method"] == "SAVE_WRITE_VERIFY":
                    print("\n\nThe newly written save data will now be checked for errors.\n")
            elif args["action"] == "ERASE":
                print("\033[KPlease wait while the flash chip is being erased... (Elapsed time: {:s})".format(
                    Util.formatProgressTime(elapsed)), end="\r")
            elif args["action"] == "UNLOCK":
                print("\033[KPlease wait while the flash chip is being unlocked... (Elapsed time: {:s})".format(
                    Util.formatProgressTime(elapsed)), end="\r")
            elif args["action"] == "SECTOR_ERASE":
                print("\033[KErasing flash sector at address 0x{:X}...".format(args["sector_pos"]), end="\r")
            elif args["action"] == "UPDATE_RTC":
                print("\nUpdating Real Time Clock...")
            elif args["action"] == "ERROR":
                print("{:s}{:s}{:s}{:s}".format(ANSI.CLEAR_LINE, ANSI.RED, args["text"], ANSI.RESET))
            elif args["action"] == "ABORTING":
                print("\nStopping...")
            elif args["action"] == "FINISHED":
                print("\n")
                self.FinishOperation()
            elif args["action"] == "ABORT":
                print("\nOperation stopped.\n")
                if "info_type" in args.keys() and "info_msg" in args.keys():
                    if args["info_type"] == "msgbox_critical":
                        print(ANSI.RED + args["info_msg"] + ANSI.RESET)
                    elif args["info_type"] == "msgbox_information":
                        print(args["info_msg"])
                    elif args["info_type"] == "label":
                        print(args["info_msg"])
                return
            elif args["action"] == "PROGRESS":
                # pv style progress status
                prog_str = "{:s}/{:s} {:s} [{:s}KiB/s] [{:s}] {:s}% ETA {:s} ".format(
                    Util.formatFileSize(size=pos).replace(" ", "").replace("Bytes", "B").replace("Byte", "B").rjust(8),
                    Util.formatFileSize(size=size).replace(" ", "").replace("Bytes", "B"),
                    Util.formatProgressTimeShort(elapsed), "{:.2f}".format(speed).rjust(6), "%PROG_BAR%",
                    "{:d}".format(int(pos / size * 100)).rjust(3), Util.formatProgressTimeShort(left))
                prog_width = shutil.get_terminal_size((80, 20))[0] - (len(prog_str) - 10)
                progress = min(1, max(0, pos / size))
                whole_width = math.floor(progress * prog_width)
                remainder_width = (progress * prog_width) % 1
                part_width = math.floor(remainder_width * 8)
                try:
                    part_char = prog_bar_part_char[part_width]
                    if (prog_width - whole_width - 1) < 0: part_char = ""
                    prog_bar = "█" * whole_width + part_char + " " * (prog_width - whole_width - 1)
                    print(prog_str.replace("%PROG_BAR%", prog_bar), end="\r")
                except UnicodeEncodeError:
                    prog_bar = "#" * whole_width + " " * (prog_width - whole_width)
                    print(prog_str.replace("%PROG_BAR%", prog_bar), end="\r", flush=True)
                except:
                    pass

    def FinishOperation(self):
        time_elapsed = None
        speed = None
        if "time_start" in self.PROGRESS.PROGRESS and self.PROGRESS.PROGRESS["time_start"] > 0:
            time_elapsed = time.time() - self.PROGRESS.PROGRESS["time_start"]
            speed = "{:.2f} KiB/s".format((self.CONN.INFO["transferred"] / 1024.0) / time_elapsed)
            self.PROGRESS.PROGRESS["time_start"] = 0

        if self.CONN.INFO["last_action"] == 4:  # Flash ROM
            self.CONN.INFO["last_action"] = 0
            if "verified" in self.PROGRESS.PROGRESS and self.PROGRESS.PROGRESS["verified"] == True:
                print("{:s}The ROM was written and verified successfully!{:s}".format(ANSI.GREEN, ANSI.RESET))
            else:
                print("ROM writing complete!")

        elif self.CONN.INFO["last_action"] == 1:  # Backup ROM
            self.CONN.INFO["last_action"] = 0
            dump_report = False
            dumpinfo_file = ""
            if self.ARGS["argparsed"].generate_dump_report is True:
                try:
                    dump_report = self.CONN.GetDumpReport()
                    if dump_report is not False:
                        if time_elapsed is not None and speed is not None:
                            dump_report = dump_report.replace("%TRANSFER_RATE%", speed)
                            dump_report = dump_report.replace("%TIME_ELAPSED%", Util.formatProgressTime(time_elapsed))
                        else:
                            dump_report = dump_report.replace("%TRANSFER_RATE%", "N/A")
                            dump_report = dump_report.replace("%TIME_ELAPSED%", "N/A")
                        dumpinfo_file = os.path.splitext(self.CONN.INFO["last_path"])[0] + ".txt"
                        with open(dumpinfo_file, "wb") as f:
                            f.write(bytearray([0xEF, 0xBB, 0xBF]))  # UTF-8 BOM
                            f.write(dump_report.encode("UTF-8"))
                except Exception as e:
                    print("ERROR: {:s}".format(str(e)))

            if self.CONN.GetMode() == "DMG":
                print("CRC32: {:08x}".format(self.CONN.INFO["file_crc32"]))
                print("SHA-1: {:s}\n".format(self.CONN.INFO["file_sha1"]))
                if self.CONN.INFO["rom_checksum"] == self.CONN.INFO["rom_checksum_calc"]:
                    print("{:s}The ROM backup is complete and the checksum was verified successfully!{:s}".format(
                        ANSI.GREEN, ANSI.RESET))
                elif ("DMG-MMSA-JPN" in self.ARGS["argparsed"].flashcart_type) or (
                        "mapper_raw" in self.CONN.INFO and self.CONN.INFO["mapper_raw"] in (0x105, 0x202)):
                    print("The ROM backup is complete!")
                else:
                    msg = "The ROM was dumped, but the checksum is not correct."
                    if self.CONN.INFO["loop_detected"] is not False:
                        msg += "\nA data loop was detected in the ROM backup at position 0x{:X} ({:s}). This may indicate a bad dump or overdump.".format(
                            self.CONN.INFO["loop_detected"],
                            Util.formatFileSize(size=self.CONN.INFO["loop_detected"], asInt=True))
                    else:
                        msg += "\nThis may indicate a bad dump, however this can be normal for some reproduction cartridges, unlicensed games, prototypes, patched games and intentional overdumps."
                    print("{:s}{:s}{:s}".format(ANSI.YELLOW, msg, ANSI.RESET))
            elif self.CONN.GetMode() == "AGB":
                print("CRC32: {:08x}".format(self.CONN.INFO["file_crc32"]))
                print("SHA-1: {:s}\n".format(self.CONN.INFO["file_sha1"]))
                if "db" in self.CONN.INFO and self.CONN.INFO["db"] is not None:
                    if self.CONN.INFO["db"]["rc"] == self.CONN.INFO["file_crc32"]:
                        print("{:s}The ROM backup is complete and the checksum was verified successfully!{:s}".format(
                            ANSI.GREEN, ANSI.RESET))
                    else:
                        msg = "The ROM backup is complete, but the checksum doesn’t match the known database entry."
                        if self.CONN.INFO["loop_detected"] is not False:
                            msg += "\nA data loop was detected in the ROM backup at position 0x{:X} ({:s}). This may indicate a bad dump or overdump.".format(
                                self.CONN.INFO["loop_detected"],
                                Util.formatFileSize(size=self.CONN.INFO["loop_detected"], asInt=True))
                        else:
                            msg += "\nThis may indicate a bad dump, however this can be normal for some reproduction cartridges, unlicensed games, prototypes, patched games and intentional overdumps."
                        print("{:s}{:s}{:s}".format(ANSI.YELLOW, msg, ANSI.RESET))
                else:
                    msg = "The ROM backup is complete! As there is no known checksum for this ROM in the database, verification was skipped."
                    if self.CONN.INFO["loop_detected"] is not False:
                        msg += "\nNOTE: A data loop was detected in the ROM backup at position 0x{:X} ({:s}). This may indicate a bad dump or overdump.".format(
                            self.CONN.INFO["loop_detected"],
                            Util.formatFileSize(size=self.CONN.INFO["loop_detected"], asInt=True))
                    print("{:s}{:s}{:s}".format(ANSI.YELLOW, msg, ANSI.RESET))

        elif self.CONN.INFO["last_action"] == 2:  # Backup RAM
            self.CONN.INFO["last_action"] = 0
            if not "debug" in self.ARGS and self.CONN.GetMode() == "DMG" and self.CONN.INFO["mapper_raw"] == 252 and \
                    self.CONN.INFO["transferred"] == 131072:  # Pocket Camera / 128 KiB: # 128 KiB
                answer = input("Would you like to extract Game Boy Camera pictures to “{:s}” now? [Y/n]: ".format(
                    Util.formatPathOS(os.path.abspath(os.path.splitext(self.CONN.INFO["last_path"])[0]),
                                      end_sep=True) + "IMG_PC**.{:s}".format(
                        self.ARGS["argparsed"].gbcamera_outfile_format))).strip().lower()
                if answer != "n":
                    pc = PocketCamera()
                    if pc.LoadFile(self.CONN.INFO["last_path"]) != False:
                        palettes = ["grayscale", "dmg", "sgb", "cgb1", "cgb2", "cgb3"]
                        pc.SetPalette(palettes.index(self.ARGS["argparsed"].gbcamera_palette))
                        file = os.path.splitext(self.CONN.INFO["last_path"])[0] + "/IMG_PC00.png"
                        if os.path.isfile(os.path.dirname(file)):
                            print("Can’t save pictures at location “{:s}”.".format(
                                os.path.abspath(os.path.dirname(file))))
                            return
                        if not os.path.isdir(os.path.dirname(file)):
                            os.makedirs(os.path.dirname(file))
                        for i in range(0, 32):
                            file = os.path.splitext(self.CONN.INFO["last_path"])[0] + "/IMG_PC{:02d}".format(i) + "." + \
                                   self.ARGS["argparsed"].gbcamera_outfile_format
                            pc.ExportPicture(i, file, scale=1)
                        print("The pictures were extracted.")
                print("")

            print("The save data backup is complete!")

        elif self.CONN.INFO["last_action"] == 3:  # Restore RAM
            self.CONN.INFO["last_action"] = 0
            if "save_erase" in self.CONN.INFO and self.CONN.INFO["save_erase"]:
                print("The save data was erased.")
                del (self.CONN.INFO["save_erase"])
            else:
                print("The save data was restored!")

        else:
            self.CONN.INFO["last_action"] = 0

    def popenWithCallback(self, args, on_exit):
        def runInThread(args, on_exit):
            p = subprocess.Popen(args)
            p.wait()
            on_exit()

        thread = threading.Thread(target=runInThread, args=(args, on_exit))
        thread.start()
        return thread

    def run(self):
        self.show()
        qt_app.exec()


qt_app = QApplication(sys.argv)
qt_app.setApplicationName(APPNAME)

'''if __name__ == '__main__':
    window = Custom_UI()
    window.run()
'''
