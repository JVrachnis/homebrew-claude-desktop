class ClaudeDesktopUnofficial < Formula
  desc "Unofficial Linux packaging of Anthropic's Claude Desktop"
  homepage "https://github.com/aaddrick/claude-desktop-debian"
  version "6.28899.6-3.3.19"
  # The license covers this project's packaging. The bundled Claude Desktop
  # application is Anthropic's proprietary software.
  license any_of: ["MIT", "Apache-2.0"]

  if Hardware::CPU.arm?
    url "https://github.com/aaddrick/claude-desktop-debian/releases/download/v3.3.19%2Bclaude6.28899.6/claude-desktop-unofficial-6.28899.6-3.3.19-arm64.AppImage"
    sha256 "976c01c9ce678b6d2ae4d902fcefa89fe72e66fcc62ef8ee70e15829c2dff34c"
  else
    url "https://github.com/aaddrick/claude-desktop-debian/releases/download/v3.3.19%2Bclaude6.28899.6/claude-desktop-unofficial-6.28899.6-3.3.19-amd64.AppImage"
    sha256 "242068b7632982cedd2a582362366de81f6eb81517e74f205f3fc2a280dd13f0"
  end

  # Release tags look like v3.3.19+claude6.28899.6: the app version comes
  # after "+claude", the packaging version before it.
  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)\+claude(\d+(?:\.\d+)+)$/i)
    strategy :github_latest do |json, regex|
      match = json["tag_name"]&.match(regex)
      next if match.blank?

      "#{match[2]}-#{match[1]}"
    end
  end

  depends_on :linux

  def install
    appimage = Dir["*.AppImage"].first
    chmod 0755, appimage
    # Extract instead of running the AppImage directly, so FUSE is not
    # needed. AppRun handles an extracted run: APPIMAGE is unset, so the
    # AppImage-only autostart and file-manager heals no-op.
    system "./#{appimage}", "--appimage-extract"
    libexec.install Dir["squashfs-root/*"]

    # AppRun finds its tree with readlink -f "$0", so a symlink works.
    bin.install_symlink libexec/"AppRun" => "claude-desktop-unofficial"

    component = "io.github.aaddrick.claude-desktop-debian"
    (share/"icons/hicolor/256x256/apps").install_symlink \
      libexec/"usr/share/icons/hicolor/256x256/apps/#{component}.png"
    (share/"metainfo").install_symlink \
      libexec/"usr/share/metainfo/#{component}.appdata.xml"

    (share/"applications/#{component}.desktop").write <<~EOS
      [Desktop Entry]
      Name=Claude
      Comment=Claude Desktop for Linux
      Exec=#{opt_bin}/claude-desktop-unofficial %u
      Icon=#{component}
      Type=Application
      Terminal=false
      Categories=Network;Utility;
      MimeType=x-scheme-handler/claude;
      StartupWMClass=com.anthropic.Claude
    EOS
  end

  def caveats
    <<~EOS
      This is an unofficial package, not published by Anthropic.

      For the app to show in your desktop's launcher, #{HOMEBREW_PREFIX}/share
      must be in XDG_DATA_DIRS (`brew shellenv` adds it); log out and back
      in after installing.

      Cowork needs KVM, QEMU and virtiofsd from your distribution. Run
        claude-desktop-unofficial --doctor
      to check them.
    EOS
  end

  test do
    assert_match version.to_s.split("-").first,
                 shell_output("#{bin}/claude-desktop-unofficial --version")
  end
end
