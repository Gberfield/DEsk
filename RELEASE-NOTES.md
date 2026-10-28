**English** | [日本語](RELEASE-NOTES.ja.md)

# DEsk v0.1.4 (BETA)

## What changed since v0.1.3

- **Fixed: after the screen turned off, it never came back** on some
  monitors (GitHub #18). Many HDMI and DisplayPort monitors say they have
  been unplugged when they go to sleep, and DEsk ended the whole session when
  its last screen went away: nothing could wake it, and every program in it
  was closed. DEsk now keeps the session and waits for the screen. A screen
  that comes back while the desk is dark stays dark until you press a key or
  move the mouse, so a sleeping monitor is left asleep. If your monitor stays
  asleep this way, press its power button (turning off its deep-sleep or
  power-saving setting avoids it). Thanks to JamesStallings on GitHub for the
  report and the `desk-report` that showed what happened.
- **Fixed: on a laptop whose firmware screen stayed beside its graphics
  card, the desk was drawn in 2D on a screen nobody sees.** Some drivers
  (NVIDIA's, unless `nvidia_drm.fbdev=1` is set) leave the screen the
  firmware started with (simpledrm) beside the real card, and DEsk took that
  one as its main screen: drawn on the processor, in 2D Fallback, with the
  laptop's own panel showing only the wood. DEsk now leaves the firmware's
  screen out when a graphics card with screens of its own is there, and says
  so in its log ("screens: ... left out"). If you set `WLR_DRM_DEVICES`
  yourself, it is left as you set it. Thanks to Darkhawk on Discord for the
  report and the `desk-report`.
- **Arabic and more in Shell Settings' "Second layout".** Arabic, Persian,
  Hebrew, Greek, Ukrainian, Hindi and Thai can now be chosen there (any
  layout xkb knows could already be written into `shell.conf`). And DEsk's
  own shortcuts, such as Super+A for ALL APPS and Super+L to lock, now work
  while a second layout like Arabic or Russian is on; before, they did
  nothing until you changed back. Thanks to YZ10 on Discord for asking.
- **GTK 4 programs on paper too.** DEsk's GTK theme now has a GTK 4 part, so
  GTK 4 programs that follow the theme (pavucontrol, for one) get the same
  paper, ink and brass as GTK 3 ones in a DEsk session. Programs made with
  libadwaita (most of GNOME's) do not follow themes; the README has the one
  line that puts them on paper too, if you want it in every desktop. Thanks
  to VKOWinHecker201 on GitHub, who made the GTK 4 stylesheet (#17).
- **Fixed: on a screen put together on the GPU, a sheet's turned-up corner
  showed the bare desk** instead of the sheet beneath it. It now shows what
  is underneath, as on the processor. (Known issue since v0.1.)
- **Fixed: after changing Graphics, the Control Panel and the post box were
  drawn wrong until you logged in again** (GitHub #12). The Control Panel
  lost its needles, lamps and labels, and the post box its letters: the
  traced picture under them was made again on top of them. Thanks to
  Myttenzzz on GitHub for the report.
- **Fixed: an unfolded (maximized) browser came back small after a
  full-screen video.** Chrome, Brave and other Chromium browsers ask to be
  maximized again when they leave full screen, and DEsk took any such request
  as "the other way round". It now does what the window asks for. Thanks to
  what on Discord for the report.
- **Fixed: on a slower processor, the front door (the lock screen) stood
  still for a second or more**, sometimes for several, so that typing the
  password and going in were late. The door is drawn on the processor even
  with a GPU. Its fine picture is now drawn behind everything else and
  given up as soon as it is no longer needed, and the moving picture gets
  coarser at once when the machine cannot keep up. On a machine like
  2010's, going in after typing the password takes as long as on a fast
  one.
- **Fixed: "DEsk" in the bookcase did nothing inside DEsk.** That entry opens
  DEsk in a window from another desktop; it is now left out inside DEsk.
- **Fixed: an old X program folded into a blank sheet.** A window whose
  title is in Latin-1 rather than UTF-8 left its folded sheet without its
  letter and name; it now gets a "?" for its letter, and its name. Program
  names that are not proper UTF-8 (a desktop file in another encoding, or a
  long name cut off inside a letter) are cleaned up as they are read.
- **`desk-report`** now lists each graphics device with its driver and the
  screens plugged into it, NVIDIA's `fbdev` setting, and the kernel options
  that choose them. A laptop whose firmware screen sat beside its NVIDIA
  card (only the desk's wood showing) is then plain from its first lines.
- **Docs: where `shell.conf` is.** Your own `~/.config/desk/shell.conf` is
  written the first time you change a setting in Shell Settings; until then
  the machine's `/etc/xdg/desk/shell.conf` and the defaults hold (README,
  docs/CONFIGURATION.md).

## What changed in v0.1.3

- **New: games on the whole screen, with the mouse caught.** `Super+F` puts
  the window in front on the whole screen (and back). A game can now catch
  the pointer to look around, and gets the mouse's movement as it should.
  `Alt+Tab` (and `Super+Tab`, `Alt+F1`) moves to the next window, putting a
  game on the whole screen back on its sheet first. `Super+M` folds the
  window in front. The bookcase, the Control Panel, the post box and the
  drawer still come up in front of a game, and the mouse is yours while they
  are up. Alt+Tab takes a game alone on the whole screen back to the desk.
  In a virtual machine, or with a tablet, a game now gets the movement too.
  This is the community's work: thanks to barenakedchicken
  (dentarthurdent on Discord), who wrote it, and to Array, who tried it with
  Overwatch.
- **Fixed: a folded Python program was called "py"** (Linux Mint's Software
  Manager, for one). Its sheet now has the program's own name and icon.
  Thanks to barenakedchicken (dentarthurdent on Discord), who found it and
  sent a fix.
- **Fixed: the clock went on counting from the last track** when Spotify
  moved to the next one. A new track now starts at 0 on the clock's MEDIA
  page. Thanks to Array on Discord for the report and the video.
- **Fixed: a picture-in-picture video went behind other windows**
  (Firefox, Chromium). It now stays in front. Thanks to Yusuf0Zain for
  the report on GitHub.
- **Fixed: apps whose icon is only an SVG got a printed letter** on the
  bookcase. The installers now bring `rsvg-convert`, a small tool that
  draws SVG; ImageMagick still works when it is there instead.
- **New: `scripts/uninstall.sh`** takes DEsk off the machine again: its
  programs and files, "DEsk" on the login screen, its settings for the whole
  machine, and the wlroots the installer built. Your own settings and the
  packages from your distribution are left. See "Uninstall" in the README.
- **Fixed: Arabic (and Hebrew, Thai, Devanagari...) came out as boxes** on
  the bookcase, in ALL APPS and in window titles. They are now set in a
  typeface that has them. The letters are not yet joined up or set right to
  left. Thanks to robot5477 on Discord for the report.
- **Fixed: on 4K screens, ALL APPS, the memo pad and the calendar were
  slow and soft.** Writing in the book, turning its pages and taking up the
  memo pad no longer stall (it was about a third of a second a letter, and
  over a second for the memo's first); the same went for any screen at Low,
  Medium and 2D. The grain of the paper was shrunk through cairo's finest
  filter at every pixel; it is now shrunk once. And at Ultra, the book, the
  papers, the calendar and the clock's figures are now drawn at the screen's
  own resolution (up to a 4K screen's worth of pixels) instead of 2048
  pixels wide and enlarged. That takes up to about 500 MB more on a 4K
  screen, and turning a page costs about two and a half times as much; High
  and below draw them as before. Thanks to Fendergluid on Discord for the
  report.
- **Sharper at Low, Medium and 2D.** The book, the papers, the calendar, the
  clock and its buttons, and the console's lamps and needles are now drawn at
  the screen's own resolution (up to 2048 pixels wide) at every level, rather
  than at the room's -- a third of it at 2D on a 1920 screen, which left the
  clock's buttons unreadable. The room, the door and the weather at it stay
  as they were. On an old machine the book costs the most: writing in it and
  turning its pages can take a few tenths of a second at 2D, and the desk
  takes 50 to 130 MB more.
- **New: a letter on the desk can be carried.** Take hold of it and move
  it wherever you like; it stays there. A click without moving still puts it
  away.
- **New: screen sharing asks which screen** (with two or more), in a
  small window, instead of always sharing the first. Sharing a single window
  is not possible yet. Thanks to Nightshade on Discord for the report.
- **`desk-report`** now also takes what the system's journal says of DEsk and
  the login screen since this boot, for when the login goes straight back to
  the login screen; and it says whether the screen was put together on the
  processor, and which screen-sharing portal (xdg-desktop-portal-wlr) is
  installed.
- **Fixed: "Clock skew detected"** when building from the ZIP west of Japan.
  The files in the release now carry a time in the past everywhere.

## What changed in v0.1.2

- **Fedora**: an installer for Fedora 43 and 44 (and what is built on them,
  such as Nobara), `sudo sh scripts/install_fedora.sh`. Everything comes from
  Fedora's own repositories, wlroots 0.18 included (`wlroots0.18`); it is
  built from its release only on a Fedora that has none. Packages that are
  only recommended are left out, as on Debian and Ubuntu. Not in Fedora, so
  done without: the memo pad's Klee One (Noto Serif CJK instead), Mugshot,
  and the letters for a low battery and for updates.
  `install_session.sh` recognises Fedora, and Shell Settings names Fedora's
  packages when a row has nothing to open.
- **Fixed: the Arch installer stopped while building wlroots** (on an Arch
  without `wlroots0.18` from the AUR), with "mkdir: cannot create directory".
  Thanks to Axenity on Discord, who found the cause and the fix.
- **Fixed: a black screen in the next desktop** (Plasma, for one) after
  logging out of DEsk. DEsk's session now takes back what it told the
  user's systemd, and stops the portals it started, once it is over.
- **Fixed: a letter taken out of the post box could not be thrown away.**
  Click it on the desk.
- **New: `desk-report`**, which gathers what a bug report needs into one
  file (`~/desk-report.txt`), with personal things taken out. Run it in a
  terminal and attach the file.
- **Fixed: a blank sheet waited about 45 seconds** for programs that run in
  a terminal (btop) or call their window by another name (KDE's System
  Settings). The window now finds its sheet by the program it came from, and
  a program that quits without a window has its sheet cleared in seconds.

## What changed in v0.1.1

- **Fixed: opening the calendar or the memo pad stopped the desk** on
  screens drawn by the GPU. On a GPU screen the desk read the size of a
  picture it had already handed over, and laid it for the whole screen.
- **Simpler install**: one line per system, `sudo sh scripts/install_debian.sh`
  (or `install_ubuntu.sh`, `install_arch.sh`), at the top of the README. Each
  installer now checks the copy against `SHA256SUMS` itself.

To update, unpack the new release and run the same line again; your
settings are kept.

## About DEsk

DEsk is a Wayland desktop for Linux in realistic
skeuomorphism -- the kind iOS 6 had -- in which the desktop is a desk:
windows are sheets of paper, the dock is a drawer, programs are filed in
binders on a bookcase, notifications arrive in a post box, and one desk lamp
lights a ray-traced room.

## What is in it

- **A whole desktop**, not only a window manager: a Wayland compositor
  (wlroots 0.18) with its own notification daemon, system tray, media
  controls, screen lock, idle and screen-off handling, display arrangement
  memory, and a session that starts the polkit agent, keyring, input method
  and network applet for you.
- **Windows on paper**, folded away, opened out to the desk, crumpled and
  thrown when closed. Folded windows lie on the desk under the others, or go
  into the drawer.
- **The drawer** (the dock), **the bookcase** with eight binders and an ALL
  APPS book you can search, **the Control Panel** (meters, Wi-Fi and
  Bluetooth levers, volume, brightness, the tray), **the post box**, a
  **desk calendar** with sticky notes, a **memo pad** and a **clock** with a
  media player page.
- **The front door** as the screen lock, in the real time of day and,
  optionally, the real weather.
- **Shell Settings**, which also opens the free programs DEsk borrows for the
  rest of the machine, each row naming the program it uses.
- **Seven languages**: English, Japanese, Chinese (simplified), Korean,
  Spanish, French and German, with calendars printed the way each country
  prints them and Chinese and Korean set in their own cut of the CJK fonts.
- **More than one screen**: the desk on one, a plain desk to put windows on
  on the others.
- **Five quality levels**, from Ultra down to a 2D Fallback that DEsk picks by
  itself when the screen is drawn on the CPU (no GPU, or a virtual machine
  without 3D).
- **Installers** for Debian 13, Ubuntu 24.04 and 26.04, Arch Linux and
  Fedora 43 and 44 (and their derivatives), which install DEsk, what it
  needs and a classic set of GTK programs, and check the copy against
  `SHA256SUMS` first.

## Installing

Unpack the release (`DEsk-v0.1.4-BETA.zip` or `.tar.gz`), go into its folder
and run the line for your system:

```sh
sudo sh scripts/install_debian.sh    # Debian 13
sudo sh scripts/install_ubuntu.sh    # Ubuntu 24.04 / 26.04, Linux Mint, Pop!_OS
sudo sh scripts/install_arch.sh      # Arch Linux, EndeavourOS, Manjaro
sudo sh scripts/install_fedora.sh    # Fedora 43 / 44, Nobara
```

Then log out and choose **DEsk** on the login screen. The README has the
details, the options (`--yes`, `--no-apps`, `--bare`, `--prefix`) and how to
build it yourself. To update later, run the same line from the new copy;
your settings and the traced room are kept.

The first start at a screen size traces the room: a few seconds on a GPU,
and longer on the processor (a letter on the desk says so). It is kept on
disk afterwards.

## Known limitations

- **Not yet supported protocols**: layer-shell (panels such as waybar, and
  slurp for picking an area), session-lock (external screen lockers),
  gamma-control (night light), input-method-v2 (on-screen keyboards),
  fractional-scale.
- **High-density screens**: DEsk sizes its own things in points, but does
  not yet tell programs a scale, so their windows come out small on a HiDPI
  screen.
- **More than one screen**: screens other than the desk's show a plain desk
  for windows; the bookcase, Control Panel and post box are on the desk's
  screen only.
- **X11 programs** run through Xwayland. Ones that keep the screen awake
  through `org.freedesktop.ScreenSaver` (some video players and games) are
  not yet heard.
- **Suspend and hibernate** have no button yet (log out, restart and power
  off do).
- **Screen sharing** shares whole screens, not single windows, and does not
  start when the screen is put together on the processor (wlroots' software
  renderer, as on a machine without a GPU driver): the screen-sharing portal
  (xdg-desktop-portal-wlr) needs GPU buffers from a wlroots as old as the
  0.18 DEsk is built on. `desk-report` says which it is.
- **Right-to-left scripts** (Arabic, Hebrew) show their letters, but not
  joined up or in right-to-left order, in what DEsk draws itself.
- **Translations** other than English and Japanese have not yet been
  reviewed by native speakers.
- **No plugin API**: changing DEsk means changing its source
  ([docs/MODDING.md](docs/MODDING.md)).
- Real hardware tested so far: VMware virtual machines (SVGA3D) and an ASUS
  ZenBook Duo (two GPUs, two screens). Reports from other machines are very
  welcome.
- **Fedora** was tried in a clean Fedora 44 container: the installer from
  scratch and again as an update, the wlroots build for a Fedora without it,
  and the installed desk run headless. Logging in to it on a Fedora machine
  (GDM, SDDM) has not been tried yet.

## How it was checked

Built with no warnings in four configurations (minimal, `-Werror`,
`_FORTIFY_SOURCE=3`, AddressSanitizer + UndefinedBehaviorSanitizer), with a
strict warning set and GCC's static analyzer over every file; run under
ThreadSanitizer, AddressSanitizer and UndefinedBehaviorSanitizer, including
with deliberately malformed settings, data and `.desktop` files; every view
rendered in all seven languages; the translation tables checked by
`meson test`. Details in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Checking your copy

The folder carries `SHA256SUMS`, which the installer checks before it builds.
The archive comes with `DEsk-v0.1.4-BETA.tar.gz.sha256`:

```sh
sha256sum -c DEsk-v0.1.4-BETA.tar.gz.sha256
```

## License

MIT. See [LICENSE](LICENSE).
