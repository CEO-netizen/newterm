# Maintainer: Gage Singleton <zeroday0x00@disroot.org>
pkgname=newterm
pkgver=0.1.0
pkgrel=1
pkgdesc="A custom terminal emulator for Wayland with GPU acceleration and customizable themes"
arch=('x86_64')
url="https://github.com/CEO-netizen/newterm"
license=('MIT')
depends=('python' 'python-gobject' 'vte3')
makedepends=('python-setuptools' 'python-wheel' 'python-installer' 'python-pip')
source=("newterm-0.1.0.tar.gz")
sha256sums=(SKIP)

build() {
    python -m pip wheel . --no-deps --wheel-dir dist
}

package() {
    python -m installer --destdir="$pkgdir" dist/*.whl
}
