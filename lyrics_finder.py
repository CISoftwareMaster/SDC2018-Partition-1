import sys
import urllib.request
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QApplication, QLabel, QPushButton


class lyrics_finder(QWidget):
    # app class
    def __init__(self):
        # initialise widgets
        super().__init__()

        self.song_title = QLineEdit()
        self.artist_name = QLineEdit()
        self.song_lyrics = QTextEdit()

        self.init_widgets()

    def get_lyrics(self):
        # update user interface
        self.song_lyrics.setText("Loading...")

        # formulate URL for the lyric-finder website
        a = self.song_title.text().replace(" ", "+")
        b = self.artist_name.text().replace(" ", "+")

        url = "https://search.azlyrics.com/search.php?q={}+{}".format(a, b)

        # try loading the lyrics-finder website
        try:
            with urllib.request.urlopen(url) as document:
                # parse using Beautiful Soup
                document = BeautifulSoup(document, "html.parser")

                # try to find a link
                search_options = {"class": "text-left visitedlyr"}
                match = document.find("td", search_options).find("a")

                # try following the link
                try:
                    with urllib.request.urlopen(match.get("href")) as lyric_document:
                        lyric_document = BeautifulSoup(lyric_document, "html.parser")

                        # find the main container
                        search_options = {"class": "col-xs-12 col-lg-8 text-center"}
                        main_container = lyric_document.find("div", search_options)

                        # try to find the lyric body
                        for container in main_container.findAll("div"):
                            # if the text node is long enough, make it the lyric body
                            if len(container.get_text()) > len(self.song_title.text()) + 30:
                                lyric_body = container.get_text()
                                break

                        # update our user interface
                        if lyric_body:
                            self.song_lyrics.setText(lyric_body)
                except:
                    self.song_lyrics.setText("Error loading lyric document!")
        except:
            self.song_lyrics.setText("Error loading document!")

    def init_widgets(self):
        # create labels
        st_label = QLabel("Song Title")
        an_label = QLabel("Artist Name")

        # set input / output placeholders
        self.song_title.setPlaceholderText("\"A Song\"")
        self.artist_name.setPlaceholderText("\"An Artist\" (optional)")
        self.song_lyrics.setPlaceholderText("Lyrics will appear here...")

        # initialise button and connections
        fetch_btn = QPushButton("Get Lyrics")
        fetch_btn.clicked.connect(self.get_lyrics)

        # set widget geometry
        self.setMinimumSize(380, 500)

        # layout
        layout = QVBoxLayout()

        def _add_input_row(a, b):
            # initialise a new widget and layout object
            row_view = QWidget()
            row = QHBoxLayout()

            # layout
            row.addWidget(a)
            row.addWidget(b)
            row_view.setLayout(row)

            # insert to parent
            layout.addWidget(row_view)

        # insert input views
        _add_input_row(st_label, self.song_title)
        _add_input_row(an_label, self.artist_name)

        # insert output views
        layout.addWidget(fetch_btn)
        layout.addWidget(self.song_lyrics)
        self.setLayout(layout)


# application initialisation
if __name__ == "__main__":
    # initialise QT app
    app = QApplication(sys.argv)

    # create window
    window = lyrics_finder()
    window.show()

    # enter main loop
    sys.exit(app.exec_())
