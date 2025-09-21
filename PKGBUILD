# Maintainer: Gage Singleton <zeroday0x00@disroot.org>
pkgname=newterm
pkgver=0.1.4
pkgrel=1
pkgdesc="A custom terminal emulator for Wayland with GPU acceleration and customizable themes"
arch=('x86_64')
url="https://github.com/CEO-netizen/newterm"
license=('GPL3')
depends=('python' 'python-gobject' 'vte3')
makedepends=('python-setuptools' 'python-wheel' 'python-installer' 'python-pip')

build() {
    cd "$srcdir"
    python -m build --wheel --outdir ../dist
}

package() {
    python -m installer --destdir="$pkgdir" "$srcdir/../dist/"*.whl
}
