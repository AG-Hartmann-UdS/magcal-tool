import tkinter as tk
from tkinter import messagebox, filedialog
from os import path
import serial.tools.list_ports as stl
from serial import SerialException
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import json
from serial_port import SerialPort
import numpy as np
from fit_ellipsoid import fit_ellipsoid
from utilities import matrix_string, generate_ellispoid


class CalibrationTool(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Magnetic Calibration tool")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Start building the window
        # Defaults
        self.__def_dir_path = path.dirname(path.realpath(__file__))
        self.__def_baudrate = 115200
        self.__def_filename = 'trial.txt'
        self.__def_com = 'COM10'
        self.__def_delim = ","
        self.__def_field = 50.0

        # Form entry for serial port
        self.__com_label__ = tk.Label(self, text="Serial port:")
        self.__com_label__.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.__com_port_v__ = tk.StringVar()
        self.__com_menu__ = tk.OptionMenu(self, self.__com_port_v__, self.__def_com)
        self.__com_menu__.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Serial port refresh button
        self.__refresh_button__ = tk.Button(self, text="Refresh", width=10, command=self.__sweep_port__)
        self.__refresh_button__.grid(row=0, column=2, sticky='w')

        # Form entry for Baud rate
        self.__baud_label__ = tk.Label(self, text="Baud Rate:")
        self.__baud_label__.grid(row=0, column=3, sticky='e')
        # menu with 1200, 2400, 4800, 19200, 38400, 57600, and 115200
        self.__baud_menu_v__ = tk.StringVar()
        self.__baud_menu__ = tk.OptionMenu(self, self.__baud_menu_v__,
                                           "1200", "2400", "4800", "19200", "38400", "57600", "115200")
        self.__baud_menu__.grid(row=0, column=4, sticky='w')

        # Button to run the data acquisition
        self.__start_button__ = tk.Button(self, text="Open port", width=10, command=self.__start_serial_logging__)
        self.__start_button__.grid(row=1, column=1, sticky='w')

        # Button to stop data acquisition
        self.__stop_button__ = tk.Button(self, text="Close port", width=10, command=self.__stop_serial_logging__)
        self.__stop_button__.grid(row=1, column=2, sticky='w')

        # Delimiter field
        self.__delim_label__ = tk.Label(self, text="Delimiter:")
        self.__delim_label__.grid(row=1, column=3, padx=5, pady=5, sticky='e')
        self.__delim_entry_v__ = tk.StringVar()
        self.__delim_entry__ = tk.Entry(self, textvariable=self.__delim_entry_v__, width=1)
        self.__delim_entry__.grid(row=1, column=4, padx=5, pady=5, sticky='w')

        # Form entry for filename
        self.__filen_label__ = tk.Label(self, text="Filename:")
        self.__filen_label__.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.__filen_entry_v__ = tk.StringVar()
        self.__filen_entry__ = tk.Entry(self, textvariable=self.__filen_entry_v__, width=10)
        self.__filen_entry__.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='w')

        # Form entry for directory
        self.__folder_label__ = tk.Label(self, text="Select Folder:")
        self.__folder_label__.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.__folder_entry_v__ = tk.StringVar()
        self.__folder_entry__ = tk.Entry(self, textvariable=self.__folder_entry_v__)
        self.__folder_entry__.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='ew')

        # Button for folder dialog
        self.__folder_button__ = tk.Button(self, text="...", command=self.__set_folder__)
        self.__folder_button__.grid(row=3, column=4, padx=5, pady=5, sticky='w')

        # # Entry for the earth's magnetic field strength
        self.__geomag_label__ = tk.Label(self, text="|B|=")
        self.__geomag_label__.grid(row=3, column=5, padx=5, pady=5, sticky='e')
        #
        self.__geomag_entry_v__ = tk.StringVar()
        self.__geomag_entry__ = tk.Entry(self, textvariable=self.__geomag_entry_v__, width=7)
        self.__geomag_entry__.grid(row=3, column=6, padx=5, pady=5, sticky='w')

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_box_aspect((1, 1, 1))

        self.__plot_canvas__ = FigureCanvasTkAgg(self.fig, master=self)
        self.__plot_canvas__.draw()
        self.__plot_canvas__.get_tk_widget().grid(row=4, column=0, columnspan=5, rowspan=5)

        # A basic status bar
        self.__status_bar__ = tk.Label(self, text="Ready...", relief=tk.SUNKEN, anchor=tk.W)
        self.__status_bar__.grid(row=9, column=0, columnspan=5, padx=5, pady=(20, 5), sticky='nsew')

        # Results
        self.__compute_button__ = tk.Button(self, text="Calibrate", command=self.__compute_coefficients__)
        self.__compute_button__.grid(row=4, column=5, columnspan=2, padx=5, pady=5, sticky='nsew')

        self.U = np.zeros([3, 3])
        self.c = np.zeros(3)

        self.__label_U__ = tk.Label(self, text="Soft-iron \ncalibration matrix:", justify='left')
        self.__label_U__.grid(row=5, column=5, columnspan=2, padx=5, pady=5, sticky='sw')
        self.__results_U__ = tk.Label(self, text=matrix_string(self.U))
        self.__results_U__.grid(row=6, column=5, columnspan=2, padx=5, pady=5, sticky='nw')
        self.__label_c__ = tk.Label(self, text="Hard-iron \noffset vector:", justify='left')
        self.__label_c__.grid(row=7, column=5, columnspan=2, padx=5, pady=5, sticky='sw')
        self.__results_c__ = tk.Label(self, text=matrix_string(self.c))
        self.__results_c__.grid(row=8, column=5, columnspan=2, padx=5, pady=5, sticky='nw')

        # Save the calibration parameters
        self__results_button__ = tk.Button(self, text="Save", command=self.__save_coefficients__)
        self__results_button__.grid(row=9, column=5, columnspan=2, padx=5, pady=5, sticky='nsew')

        # Resize the columns
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)
        self.grid_columnconfigure(4, weight=0)
        self.grid_columnconfigure(5, weight=1)

        # Resize the rows
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=0)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=0)

        self.ser = None
        self.file = None

        # File number and line counts
        # Defaults. These are changed if a cache is found
        self.com_port = self.__def_com
        self.baudrate = self.__def_baudrate
        self.filename = self.__def_filename
        self.folder = self.__def_dir_path
        self.delimiter = self.__def_delim
        self.field = self.__def_field

        self.start_logging = False

        self.__cache_file__ = path.join(self.__def_dir_path, 'defaults').replace('\\', '/')
        self.__set_fields__()
        self.__sweep_port__()

    def __start_serial_logging__(self):
        self.folder = self.__folder_entry_v__.get()

        # Set path to save files
        if not path.isdir(self.folder):
            messagebox.showerror("Error!", message="No such Directory. Please check if directory exists")
            self.start_logging = False
            return

        # Serial port parameters
        self.com_port = self.__com_port_v__.get()
        self.baudrate = self.__baud_menu_v__.get()

        # Filename
        self.filename = self.__filen_entry_v__.get()

        self.delimiter = self.__delim_entry_v__.get()
        self.field = self.__geomag_entry_v__.get()

        try:
            self.ser = SerialPort(self.com_port, self.folder, baudrate=self.baudrate, delimiter=self.delimiter)
            self.ser.open_port()
        except SerialException:
            messagebox.showerror("Error!",
                                 message="COM Port cannot be opened. Check if device connected or already in use!")
            self.start_logging = False
            return

        self.file = open(path.join(self.folder, self.filename), 'a')

        self.start_logging = True
        self.__status_bar__.config(text='Logging...')

    def __stop_serial_logging__(self):
        self.start_logging = False
        self.__status_bar__.config(text='Ready...')

        if self.file is not None:
            self.file.close()
            self.file = None
        if self.ser.isOpen():
            self.ser.close()

    def __compute_coefficients__(self):
        # Check if port has been closed
        if self.ser is not None:
            if self.ser.isOpen():
                messagebox.showerror("Error!",
                                     message="Please close serial port before performing computation!")
                return
        try:
            self.delimiter = self.__delim_entry_v__.get()
            data = np.loadtxt(path.join(self.folder, self.filename), delimiter=self.delimiter)
        except FileNotFoundError:
            messagebox.showerror("Error!", message="No datafile found at location! Try collecting again")
            return
        params = fit_ellipsoid(data)
        if params is not None:
            self.field = float(self.__geomag_entry_v__.get())
            self.U, self.c = params
            self.U *= self.field
            self.__results_U__.config(text=matrix_string(self.U))
            self.__results_c__.config(text=matrix_string(self.c))

            # Results are also plotting
            x1, y1, z1, x2, y2, z2 = generate_ellispoid(self.U, self.c, self.field)
            if self.ser is None:
                self.ax.scatter3D(data[:, 0], data[:, 1], data[:, 2], c='r', alpha=0.6)
            self.ax.plot_surface(x1, y1, z1, color='xkcd:sky blue', alpha=0.5, antialiased=True)
            self.ax.plot_surface(x2, y2, z2, color='r', alpha=0.5, antialiased=True)
        else:
            messagebox.showerror("Error!",
                                 message="Not enough data to perform calibration!")

    def __save_coefficients__(self):
        data_dict = {"U": np.array2string(self.U, separator=",", formatter={'float_kind': lambda x: "%.4f" % x}),
                     "c": np.array2string(self.c, separator=",", formatter={'float_kind': lambda x: "%.4f" % x}),
                     "B": str(self.field)}
        dict_str = json.dumps(data_dict, indent=4)
        with open("parameters.json", "w") as f:
            f.write(dict_str)
            f.close()

    def __set_fields__(self):
        # Load the cached values
        if path.isfile(self.__cache_file__):
            with open(self.__cache_file__) as f:
                dict_str = f.read()
                f.close()
            var_dict = json.loads(dict_str)
            self.__filen_entry_v__.set(var_dict['filename'])
            self.__com_port_v__.set(var_dict['com_port'])
            self.__baud_menu_v__.set(str(var_dict['baudrate']))
            self.__folder_entry_v__.set(var_dict['folder'])
            self.__delim_entry_v__.set(var_dict['delimiter'])
            self.__geomag_entry_v__.set(str(var_dict['field']))
        else:
            self.__filen_entry_v__.set(self.__def_filename)
            self.__com_port_v__.set(self.__def_com)
            self.__baud_menu_v__.set(str(self.__def_baudrate))
            self.__folder_entry_v__.set(self.__def_dir_path)
            self.__delim_entry_v__.set(self.__def_delim)
            self.__geomag_entry_v__.set(str(self.__def_field))

    def __sweep_port__(self):

        port_list = stl.comports()
        self.__com_menu__['menu'].delete(0, 'end')
        for port in port_list:
            self.__com_menu__['menu'].add_command(label=port.description,
                                                  command=tk._setit(self.__com_port_v__, port.device))

    def __set_folder__(self):

        fname = filedialog.askdirectory(initialdir=self.folder)
        if len(fname) != 0:
            self.__folder_entry_v__.set(fname)

    def __dump_cache__(self):

        var_dict = {
            'folder': self.__folder_entry_v__.get(),
            'baudrate': int(self.__baud_menu_v__.get()),
            'com_port': self.__com_port_v__.get(),
            'filename': self.__filen_entry_v__.get(),
            'delimiter': self.__delim_entry_v__.get(),
            'field': self.__geomag_entry_v__.get()
        }
        dict_str = json.dumps(var_dict, indent=4)
        with open(self.__cache_file__, 'w') as f:
            f.write(dict_str)
            f.close()

    def close(self):
        yn = tk.messagebox.askyesno(title="Quit", message="Do you want to quit?")
        if yn:
            if self.ser is not None:
                self.ser.close()
            if self.file is not None:
                self.file.close()
            self.__dump_cache__()
            self.quit()
            self.destroy()

    def run(self):
        while 1:
            if self.start_logging:
                self.ser.fill_buffer()
                self.ax.scatter(self.ser.data_buffer[:, 0], self.ser.data_buffer[:, 1],
                                self.ser.data_buffer[:, 2], c='r')
                self.__plot_canvas__.draw()
                np.savetxt(self.file, self.ser.data_buffer, delimiter=self.delimiter)
            try:
                self.update()
            except tk.TclError:
                break
