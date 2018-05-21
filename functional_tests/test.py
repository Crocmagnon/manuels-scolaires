from selenium import webdriver


def main():
    browser = webdriver.Firefox()
    browser.get('http://localhost:8000')

    assert 'Django' in browser.title


if __name__ == '__main__':
    main()
