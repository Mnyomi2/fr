import os
import subprocess
import shutil

# --- User Configuration ---
CRD_SSH_Code = input("Enter your Google CRD command: ")
username = "user" #@param {type:"string"}
password = "root" #@param {type:"string"}
Pin = 123456 #@param {type: "integer"}
Autostart = True #@param {type: "boolean"}

# --- User and System Setup ---
print("Creating and configuring user...")
os.system(f"useradd -m -s /bin/bash {username}")
os.system(f"adduser {username} sudo")
os.system(f"echo '{username}:{password}' | sudo chpasswd")
# This sed command is often unnecessary on modern systems but doesn't hurt
os.system("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")
print(f"User '{username}' created successfully.")

class CRDSetup:
    def __init__(self, user):
        print("Starting system update...")
        os.system("apt-get update -y")
        print("System update finished.")
        
        self.installCRD()
        self.installDesktopEnvironment()
        self.changewall()
        self.installGoogleChrome()
        self.installQbit()
        self.finish(user)

    @staticmethod
    def installCRD():
        print("Installing Chrome Remote Desktop...")
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb'])
        subprocess.run(['dpkg', '--install', 'chrome-remote-desktop_current_amd64.deb'])
        subprocess.run(['apt-get', 'install', '--assume-yes', '--fix-broken'])
        print("Chrome Remote Desktop Installed!")

    @staticmethod
    def installDesktopEnvironment():
        print("Installing XFCE4 Desktop Environment...")
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        
        # --- FIX STARTS HERE: Pre-configure keyboard and locale ---
        print("Pre-configuring keyboard and locale to avoid interactive prompts...")
        
        # Install locales package first if not present
        os.system("apt-get install -y locales")
        
        # Set the selections for US English keyboard and locale
        os.system("echo 'keyboard-configuration keyboard-configuration/xkb-keymap select us' | debconf-set-selections")
        os.system("echo 'locales locales/locales_to_be_generated multiselect en_US.UTF-8 UTF-8' | debconf-set-selections")
        os.system("echo 'locales locales/default_environment_locale select en_US.UTF-8' | debconf-set-selections")
        
        # Apply the locale settings
        os.system("locale-gen en_US.UTF-8")
        os.system("dpkg-reconfigure --frontend noninteractive locales")
        
        # --- FIX ENDS HERE ---

        # Now install the desktop environment; it will use the pre-configured settings
        os.system("apt-get install --assume-yes xfce4 desktop-base xfce4-terminal sudo")
        os.system("bash -c 'echo \"exec /etc/X11/Xsession /usr/bin/xfce4-session\" > /etc/chrome-remote-desktop-session'")
        os.system("apt-get remove --assume-yes gnome-terminal")
        os.system("apt-get install --assume-yes xscreensaver")
        os.system("apt-get purge --assume-yes light-locker")
        os.system("apt-get install --reinstall --assume-yes xfce4-screensaver")
        os.system("systemctl disable lightdm.service")
        print("Installed XFCE4 Desktop Environment!")


    @staticmethod
    def installGoogleChrome():
        print("Installing Google Chrome...")
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"])
        subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"])
        subprocess.run(['apt-get', 'install', '--assume-yes', '--fix-broken'])
        print("Google Chrome Installed!")

    @staticmethod
    def changewall():
        print("Changing wallpaper...")
        try:
            subprocess.run(["curl", "-s", "-L", "-k", "-o", "xfce-verticals.png", "https://wallpaperaccess.com/download/ubuntu-2587485"], check=True)
            destination_path = '/usr/share/backgrounds/xfce/'
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
            shutil.copy("xfce-verticals.png", destination_path)
            print("Wallpaper Changed!")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Could not change wallpaper: {e}")

    @staticmethod
    def installQbit():
        print("Installing qBittorrent...")
        subprocess.run(["sudo", "apt-get", "install", "-y", "qbittorrent"])
        print("qBittorrent Installed!")

    @staticmethod
    def finish(user):
        print("Finalizing setup...")
        if Autostart:
            autostart_dir = f"/home/{user}/.config/autostart"
            os.makedirs(autostart_dir, exist_ok=True)
            
            link = "https://www.youtube.com/@The_Disala"
            colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {link}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true"""
            
            autostart_file_path = os.path.join(autostart_dir, "colab.desktop")
            with open(autostart_file_path, "w") as f:
                f.write(colab_autostart)
            
            os.system(f"chmod +x {autostart_file_path}")
            # Ensure correct ownership of the entire .config directory
            os.system(f"chown -R {user}:{user} /home/{user}/.config")
            print("Autostart script created.")
            
        # Add user to the CRD group and start the service
        os.system(f"adduser {user} chrome-remote-desktop")
        command = f"{CRD_SSH_Code} --pin={Pin}"
        
        print("Starting Chrome Remote Desktop service...")
        # Run the CRD command as the specified user
        subprocess.run(f"su - {user} -c '{command}'", shell=True)
        # Start the service as root
        os.system("service chrome-remote-desktop start")
        
        print("\n" + "."*58) 
        print(".....Brought By The Disala................................") 
        print("."*58) 
        print("......#####...######...####....####...##.......####.......") 
        print("......##..##....##....##......##..##..##......##..##......")  
        print("......##..##....##.....####...######..##......######......") 
        print("......##..##....##........##..##..##..##......##..##......") 
        print("......#####...######...####...##..##..######..##..##......") 
        print("."*58) 
        print("..Youtube Video Tutorial - https://youtu.be/xqpCQCJXKxU ..") 
        print("."*58) 
        print(f"Log in PIN : {Pin}") 
        print(f"User Name  : {username}") 
        print(f"User Pass  : {password}")
        print("\nSETUP COMPLETE! Your remote desktop should be accessible now.")
        print("The script will keep running to keep the session alive.")
        
        # Keep the script running to prevent the environment from shutting down
        while True:
            pass

# --- Main execution block ---
try:
    if not CRD_SSH_Code.strip():
        print("\nERROR: CRD Command cannot be empty.")
        print("Please get it from: https://remotedesktop.google.com/headless")
    elif len(str(Pin)) < 6:
        print("\nERROR: PIN must be at least 6 digits long.")
    else:
        CRDSetup(username)
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
