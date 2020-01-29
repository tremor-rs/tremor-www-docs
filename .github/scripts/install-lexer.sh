
fetch() {
    # To replace with a clone once the repo is open source!
    cp -r .github/vendor/lexer tremor-mkdocs-lexer
}

install() {
    cd tremor-mkdocs-lexer
    python3 ./setup.py install
}
fetch
install