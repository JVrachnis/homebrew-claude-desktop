# Homebrew tap for Claude Desktop on Linux (proof of concept)

Unofficial. Installs the AppImage built by
[aaddrick/claude-desktop-debian](https://github.com/aaddrick/claude-desktop-debian),
for discussion in [#972](https://github.com/aaddrick/claude-desktop-debian/issues/972).

```bash
brew tap jvrachnis/claude-desktop <this-repo-url>
brew install claude-desktop-unofficial
```

## How it works

- Downloads the release AppImage (amd64 or arm64) pinned by SHA-256.
- Extracts it with `--appimage-extract` instead of running it, so FUSE is
  not needed. The project's `AppRun` supports an extracted run.
- Links `claude-desktop-unofficial` into Homebrew's `bin`, and installs a
  desktop entry, icon and AppStream metainfo under Homebrew's `share`.
- `livecheck` reads the latest release tag (`v<repo>+claude<app>`) and
  reports `<app>-<repo>`, matching the package version.

## What it doesn't do

- GTK, NSS, X11 and the other system libraries Electron needs come from the
  distribution, not Homebrew. Any desktop distro has them.
- The app appears in the launcher only if Homebrew's `share` is in
  `XDG_DATA_DIRS` (`brew shellenv` adds it).
- Cowork needs KVM, QEMU and OVMF firmware from the distribution;
  `claude-desktop-unofficial --doctor` checks them.
- No autostart or file-manager entries: the launcher writes those only for
  deb/rpm and mounted AppImages.
