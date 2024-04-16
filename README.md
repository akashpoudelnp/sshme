<img src="https://raw.githubusercontent.com/akashpoudelnp/sshme/main/sshme-logo.png">

### SSHMe

SSHMe is a simple tool to manage your SSH keys. It allows you to add, list, remove, and connect to your SSH keys. It
also allows you to connect to your SSH keys with a single command.

### Installation

Run the following command to install SSHMe.

```bash
 sudo mkdir /usr/share/applications/sshme && sudo wget https://raw.githubusercontent.com/akashpoudelnp/sshme/main/sshme -O /usr/share/applications/sshme/sshme && sudo wget https://raw.githubusercontent.com/akashpoudelnp/sshme/main/sshme-logo.png -O /usr/share/applications/sshme/sshme-logo.png && sudo chmod +x /usr/share/applications/sshme/sshme && echo "[Desktop Entry] Name=SSHMe Comment=Manage your SSH keys Exec=/usr/share/applications/sshme/sshme Icon=/usr/share/applications/sshme/sshme-logo.png Terminal=false Type=Application Categories=Utility;Development;" | sudo tee /usr/share/applications/sshme.desktop
```

### Usage

Search for SSHMe in your application menu and click on it to open the SSHMe application.

### Support

The current build of **sshme** was tested and ran on following systems:

- Linux Mint 22.04
- KDE Neon 6


