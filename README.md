<img src="https://raw.githubusercontent.com/akashpoudelnp/sshme/main/logo.png">

### SSHMe

SSHMe is a simple tool to manage your SSH keys. It allows you to add, list, remove, and connect to your SSH keys. It
also allows you to connect to your SSH keys with a single command.

### Installation

Before you begin installation install the dependencies:

```bash
sudo apt install python3-pyperclip python3-pystray python3-pyqt5
```

Then download the executable and logo and place it in same directory.

For this example we will place the files in `~/.local/share/sshme` directory.

```bash
mkdir ~/.local/share/sshme
cd ~/.local/share/sshme
```

Then we download the executable and logo inside the directory.

```bash
wget https://raw.githubusercontent.com/akashpoudelnp/sshme/main/sshme
wget https://raw.githubusercontent.com/akashpoudelnp/sshme/main/logo.png
```

We make the executable file executable.

```bash
chmod +x sshme
```

Then we create a desktop entry for the application.

```bash
echo "[Desktop Entry]
Name=SSHMe
Exec=$HOME/.local/share/sshme/sshme
Icon=$HOME/.local/share/sshme/logo.png
Type=Application
Categories=Utility;" > ~/.local/share/applications/sshme.desktop
```

### Usage

Search for SSHMe in your application menu and click on it to open the SSHMe application.

You can also add SSHMe to startup applications to run it on startup.

### Support

The current build of **sshme** was tested and ran on following systems:

- Linux Mint 22.04
- KDE Neon 6
- Ubuntu 22.04