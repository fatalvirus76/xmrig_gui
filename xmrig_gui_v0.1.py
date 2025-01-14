import tkinter as tk
from tkinter import ttk, messagebox
import json
import subprocess


class XMRigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XMRig GUI")
        self.settings = {}
        self.network_entries = {}
        self.cpu_entries = {}
        self.api_entries = {}
        self.tls_entries = {}
        self.logging_entries = {}
        self.misc_entries = {}
        self.process = None

        # Notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # Add tabs
        self.add_tab(notebook, "Network", self.network_entries, self.network_options())
        self.add_tab(notebook, "CPU Backend", self.cpu_entries, self.cpu_options())
        self.add_tab(notebook, "API", self.api_entries, self.api_options())
        self.add_tab(notebook, "TLS", self.tls_entries, self.tls_options())
        self.add_tab(notebook, "Logging", self.logging_entries, self.logging_options())
        self.add_tab(notebook, "Misc", self.misc_entries, self.misc_options())

        # Control buttons
        buttons_frame = tk.Frame(root)
        buttons_frame.pack(fill="x", pady=10)

        tk.Button(buttons_frame, text="Save", command=self.save_settings).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Load", command=self.load_settings).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Run XMRig", command=self.run_xmrig).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Stop XMRig", command=self.stop_xmrig).pack(side="left", padx=5)

    def add_tab(self, notebook, tab_name, entries, options):
        """Add a tab with options."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=tab_name)
        self.add_options(tab, entries, options)

    def add_options(self, tab, entries, options):
        """Add options to a given tab."""
        for row, (label_text, param, key, *widget_type) in enumerate(options):
            tk.Label(tab, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            if widget_type and widget_type[0] == "checkbox":
                var = tk.IntVar(value=0)  # Ensure all checkboxes are unchecked initially
                checkbox = tk.Checkbutton(tab, variable=var)
                checkbox.grid(row=row, column=1, sticky="w", padx=5, pady=2)
                entries[key] = var
            elif widget_type and widget_type[0] == "dropdown":
                choices = widget_type[1]
                combobox = ttk.Combobox(tab, values=choices, state="readonly", width=37)
                combobox.set(choices[0])  # Default to the first choice
                combobox.grid(row=row, column=1, padx=5, pady=2)
                entries[key] = combobox
            else:
                entry = tk.Entry(tab, width=40)
                default_value = widget_type[0] if widget_type else ""  # Set default value if provided
                entry.insert(0, default_value)
                entry.grid(row=row, column=1, padx=5, pady=2)
                entries[key] = entry

    def update_ui_with_settings(self):
        """Update the UI with loaded settings."""
        for tab_entries in [self.network_entries, self.cpu_entries, self.api_entries, self.tls_entries, self.logging_entries, self.misc_entries]:
            for key, widget in tab_entries.items():
                value = self.settings.get(key, "")
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, value)
                elif isinstance(widget, tk.IntVar):
                    # Ensure we handle checkbox values properly
                    widget.set(int(value) if value else 0)  # Default to 0 if empty
                elif isinstance(widget, ttk.Combobox):
                    widget.set(value if value else widget.get())  # Set to the current value if empty

    def save_settings(self):
        """Save settings to a file, but only include parameters used in this program."""
        self.settings = {}
        for key, entry in {**self.network_entries, **self.cpu_entries, **self.api_entries, **self.tls_entries, **self.logging_entries, **self.misc_entries}.items():
            value = entry.get() if isinstance(entry, (tk.Entry, ttk.Combobox)) else entry.get()
            
            # Handle the case where the value is empty
            if isinstance(value, str) and value.strip() == "":
                continue  # Skip empty string values
            
            # Save the value to settings
            self.settings[key] = value
        
        with open("xmrig_parameters.json", "w") as f:
            json.dump(self.settings, f, indent=4)

    def load_settings(self):
        """Load settings from a file."""
        try:
            with open("xmrig_parameters.json", "r") as f:
                self.settings = json.load(f)
            self.update_ui_with_settings()
        except FileNotFoundError:
            messagebox.showerror("Error", "No parameter file found.")

    def run_xmrig(self):
        """Run XMRig with current settings in mate-terminal, without using the -c flag."""
        if self.process and self.process.poll() is None:  # If XMRig is already running
            messagebox.showwarning("Warning", "XMRig is already running.")
            return

        command = ["./xmrig"]

        # Collect settings and add to command
        for key, widget in {**self.network_entries, **self.cpu_entries, **self.api_entries, **self.tls_entries, **self.logging_entries, **self.misc_entries}.items():
            value = widget.get() if isinstance(widget, tk.Entry) else widget.get()

            if isinstance(widget, tk.IntVar) and value:  # For checkboxes only if checked
                command.append(f"--{key}")
            elif value:  # For other widget types
                command.append(f"--{key}={value}")

        # Start xmrig in mate-terminal
        try:
            self.process = subprocess.Popen([
                "mate-terminal", "--", "bash", "-c", " ".join(command) + "; exec bash"
            ])
        except FileNotFoundError:
            messagebox.showerror("Error", "mate-terminal is not installed or not found.")

    def stop_xmrig(self):
        """Stop the running XMRig process."""
        if self.process:
            self.process.terminate()  # Terminate the process gracefully
            self.process = None
            messagebox.showinfo("Info", "XMRig stopped.")
        else:
            messagebox.showwarning("Warning", "XMRig is not running.")

    @staticmethod
    def network_options():
        return [
            ("URL", "-o", "url", "stratum+tcp://randomxmonero.auto.nicehash.com:9200"),
            ("Coin", "--coin", "coin"),
            ("Username", "-u", "user", "38bj4uu8uDsnC5NjoeGb8TMviBCEtMiaet"),
            ("Password", "-p", "pass"),
            ("Userpass", "-O", "userpass"),
            ("Proxy", "-x", "proxy"),
            ("Keepalive", "-k", "keepalive", "checkbox"),
            ("Nicehash", "--nicehash", "nicehash", "checkbox"),
            ("Rig ID", "--rig-id", "rig-id"),
            ("Algorithm", "-a", "algo", "dropdown", [
                "gr", "rx/graft", "cn/upx2", "argon2/chukwav2", "cn/ccx", "kawpow", "rx/keva", 
                "cn-pico/tlo", "rx/sfx", "rx/arq", "rx/0", "argon2/chukwa", "argon2/ninja", "rx/wow", 
                "cn/fast", "cn/rwz", "cn/zls", "cn/double", "cn/r", "cn-pico", "cn/half", "cn/2", 
                "cn/xao", "cn/rto", "cn-heavy/tube", "cn-heavy/xhv", "cn-heavy/0", "cn/1", 
                "cn-lite/1", "cn-lite/0", "cn/0"
            ]),
        ]

    @staticmethod
    def cpu_options():
        return [
            ("Disable CPU", "--no-cpu", "no-cpu", "checkbox"),
            ("Threads", "-t", "threads"),
            ("CPU Affinity", "--cpu-affinity", "cpu-affinity"),
            ("Algorithm Variation", "-v", "av"),
            ("CPU Priority", "--cpu-priority", "cpu-priority"),
            ("Max Threads Hint", "--cpu-max-threads-hint", "cpu-max-threads-hint"),
            ("CPU Memory Pool", "--cpu-memory-pool", "cpu-memory-pool"),
            ("CPU No Yield", "--cpu-no-yield", "cpu-no-yield", "checkbox"),
            ("No Huge Pages", "--no-huge-pages", "no-huge-pages", "checkbox"),
            ("Huge Page Size", "--hugepage-size", "hugepage-size"),
            ("Huge Pages JIT", "--huge-pages-jit", "huge-pages-jit", "checkbox"),
            ("ASM Optimizations", "--asm", "asm", "dropdown", ["auto", "none", "intel", "ryzen", "bulldozer"]),
            ("Argon2 Implementation", "--argon2-impl", "argon2-impl", "dropdown", ["x86_64", "SSE2", "SSSE3", "XOP", "AVX2", "AVX-512F"]),
            ("RandomX Init", "--randomx-init", "randomx-init"),
            ("RandomX No NUMA", "--randomx-no-numa", "randomx-no-numa", "checkbox"),
            ("RandomX Mode", "--randomx-mode", "randomx-mode", "dropdown", ["auto", "fast", "light"]),
            ("RandomX 1GB Pages", "--randomx-1gb-pages", "randomx-1gb-pages", "checkbox"),
            ("RandomX MSR", "--randomx-wrmsr", "randomx-wrmsr"),
            ("RandomX No RDMSR", "--randomx-no-rdmsr", "randomx-no-rdmsr", "checkbox"),
            ("RandomX Cache QoS", "--randomx-cache-qos", "randomx-cache-qos", "checkbox"),
        ]

    @staticmethod
    def api_options():
        return [
            ("Worker ID", "--api-worker-id", "api-worker-id"),
            ("Instance ID", "--api-id", "api-id"),
            ("Host", "--http-host", "http-host", "127.0.0.1"),
            ("Port", "--http-port", "http-port"),
            ("Access Token", "--http-access-token", "http-access-token"),
            ("No Restricted", "--http-no-restricted", "http-no-restricted", "checkbox"),
        ]

    @staticmethod
    def tls_options():
        return [
            ("TLS Gen", "--tls-gen", "tls-gen"),
        ]

    @staticmethod
    def logging_options():
        return [
            ("Syslog", "-S", "syslog", "checkbox"),
        ]

    @staticmethod
    def misc_options():
        return []  # Removed the config file option


if __name__ == "__main__":
    root = tk.Tk()
    app = XMRigGUI(root)
    root.mainloop()
