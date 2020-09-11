
fetch() {
    git clone https://github.com/tremor-rs/tremor-mkdocs-lexer
}

install() {
    cd tremor-mkdocs-lexer
    python3 ./setup.py install
}
fetch
install
