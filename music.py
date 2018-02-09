import sys
import urllib.request
from bs4 import BeautifulSoup
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


class MP_Lyric_Fetch_Thread(QThread):
    finished_fetching = pyqtSignal(str)
    task_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # fetched lyrics
        self.lyrics = None
        self.title = None
        self.artist = None

    def fetch(self, title, artist):
        self.title = title
        self.artist = artist

        # start the thread
        if not self.isRunning():
            self.start(QThread.NormalPriority)

    def prepare_str(self, s):
        s = s.replace(" ", "+")
        s = s.replace("&", "%26")
        return s

    def run(self):
        # prepare parameters
        self.title = self.prepare_str(self.title)
        self.artist = self.prepare_str(self.artist)

        # formulate URL for the lyric search website
        url = "https://search.azlyrics.com/search.php?q=%s+%s" % (self.title, self.artist)

        try:
            with urllib.request.urlopen(url) as document:
                # parse the document using Beautiful Soup
                document = BeautifulSoup(document, "html.parser")

                # update task
                self.task_changed.emit("Fetching lyrics...")

                # find the first link then follow it
                link = document.find("td", {"class", "text-left visitedlyr"}).find("a")

                with urllib.request.urlopen(link.get("href")) as l_document:
                    l_document = BeautifulSoup(l_document, "html.parser")

                    # find the main content divider
                    self.task_changed.emit("Finding lyric body...")
                    container = l_document.find("div", {"class": "col-xs-12 col-lg-8 text-center"})

                    # find the longest text node
                    for item in container.findAll("div"):
                        if len(item.text) > len(self.title) + 40:
                            self.finished_fetching.emit(item.text)
                            break

        # something happened
        except:
            self.finished_fetching.emit(None)

        # stop this thread
        self.quit()


class MP_Button(QPushButton):
    def __init__(self, title):
        super().__init__(title)
        self.setMouseTracking(True)

        # cursor position
        self.cursor_x = 0
        self.cursor_y = 0

    def _update_cposition(self, e):
        if e.buttons() == Qt.LeftButton:
            # update cursor position
            self.cursor_x = e.x()
            self.cursor_y = e.y()

            # update widget
            self.repaint()

    def mousePressEvent(self, e):
        # handle default behaviour
        super().mousePressEvent(e)

        # update cursor position
        self._update_cposition(e)

    def mouseMoveEvent(self, e):
        self._update_cposition(e)

    def paintEvent(self, e):
        # get the size of this element
        width = self.width()
        height = self.height()

        painter = QPainter(self)

        # draw background
        painter.setRenderHint(QPainter.Antialiasing)

        if self.isDown():
            fill = QLinearGradient(width/2, 0, width/2, height)
            fill.setColorAt(0, QColor(140, 180, 250))
            fill.setColorAt(1, QColor(80, 120, 190))

            # update pen color
            pen = painter.pen()
            pen.setColor(QColor(255, 255, 255))
            painter.setPen(pen)

            painter.fillRect(QRect(0, 0, width, height), fill)
        else:
            painter.fillRect(QRect(0, 0, width, height), QColor(230, 230, 230))

        # draw text
        pen = painter.pen()
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawText(QRectF(0, 0, width, height), self.text(), QTextOption(Qt.AlignCenter))

        # draw click effect
        if self.isDown():
            # update pen
            painter.setPen(QPen(Qt.NoPen))

            painter.setBrush(QBrush(QColor(255, 255, 255, 80)))
            painter.drawEllipse(self.cursor_x-32, self.cursor_y-32, 64, 64)


class MP_SeekSlider(QSlider):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.dragged = False

        # cursor position
        self.cursor_x = 0
        self.cursor_y = 0

    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        # update drag
        self.dragged = True

        # update cursor position
        self.cursor_x = e.x()
        self.cursor_y = e.y()

        # update slider value
        if e.buttons() == Qt.LeftButton:
            # determine where the user clicked
            s = self.maximum() * (e.x() / self.width())
            self.setValue(s)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        # release drag
        self.dragged = False
        self.repaint()

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)

        # update cursor position
        self.cursor_x = e.x()
        self.cursor_y = e.y()

        # update slider value
        if e.buttons() == Qt.LeftButton:
            # determine where the user clicked
            s = self.maximum() * (e.x() / self.width())
            self.setValue(s)

    def setMaximum(self, maximum):
        super().setMaximum(maximum)

        # update target
        self.ts = maximum/1000
        self.tm = self.ts / 60

    def paintEvent(self, e):
        width = self.width()
        height = self.height()

        # set up QPainter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # draw slider track
        painter.setPen(QPen(Qt.NoPen))
        track = QLinearGradient(width/2, 0, width/2, height)
        track.setColorAt(0, QColor(150, 150, 150))
        track.setColorAt(1, QColor(80, 80, 80))
        painter.fillRect(QRect(0, 1, width, height-2), track)

        if self.value() != self.maximum():
            # determine slider position
            p = (self.value() / self.maximum())

            # determine the seek's time position
            s = self.value()/1000
            m = s/60

            # draw slider trail
            fill = QLinearGradient(width/2, 0, width/2, height)
            fill.setColorAt(0, QColor(140, 180, 250))
            fill.setColorAt(1, QColor(80, 120, 190))
            painter.fillRect(QRect(0, 1, width * p, height-2), fill)

            # draw slider head
            painter.fillRect(QRect((width * p)-2, 0, 2, height), QColor(110, 150, 230))

            # draw slider text
            text_pen = QPen(Qt.SolidLine)
            text_pen.setColor(QColor(255, 255, 255))
            painter.setPen(text_pen)

            painter.drawText(QRectF(0, 0, width, height), "%im, %is / %im, %is (%.1f%s)" %
                             (m, s % 60, self.tm, self.ts % 60, p*100, "%"),
                             QTextOption(Qt.AlignCenter))
        else:
            text_pen = QPen(Qt.SolidLine)
            text_pen.setColor(QColor(255, 255, 255))
            painter.setPen(text_pen)

            painter.drawText(QRectF(0, 0, width, height), "Done", QTextOption(Qt.AlignCenter))

        if self.dragged:
            # draw drag cursor
            painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
            painter.drawEllipse(self.cursor_x-16, (height/2)-16, 32, 32)


class MP_VolumeSlider(MP_SeekSlider):
    def __init__(self):
        super().__init__()

    def paintEvent(self, e):
        width = self.width()
        height = self.height()

        # set up QPainter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # draw slider track
        painter.setPen(QPen(Qt.NoPen))
        track = QLinearGradient(width/2, 0, width/2, height)
        track.setColorAt(0, QColor(150, 150, 150))
        track.setColorAt(1, QColor(80, 80, 80))
        painter.fillRect(QRect(0, 1, width, height-2), track)

        # determine volume slider position
        p = (self.value() / self.maximum())

        # colour-blending factor
        f = (self.value() / self.maximum())

        # colour values for the volume slider
        r = 255 + (-255 * f)
        g = 100 + (155 * f)
        t = 255 + (-255 * f)

        # draw slider trail
        painter.fillRect(QRect(0, 1, width * p, height-2), QColor(r, g, 0))

        # draw slider head
        painter.fillRect(QRect((width * p)-2, 0, 2, height), QColor(r, g, 0))

        # draw slider text
        text_pen = QPen(Qt.SolidLine)
        text_pen.setColor(QColor(t, t, t))
        painter.setPen(text_pen)

        if self.value() != self.maximum():
            painter.drawText(QRectF(0, 0, width, height), "%i%s" %
                             (p * 100, "%"), QTextOption(Qt.AlignCenter))
        else:
            painter.drawText(QRectF(0, 0, width, height), "Max", QTextOption(Qt.AlignCenter))

        if self.dragged:
            # draw drag cursor
            painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
            painter.drawEllipse(self.cursor_x-16, (height/2)-16, 32, 32)


class MP_Window(QMainWindow):
    def __init__(self):
        # initialise QMainWindow
        super().__init__()

        # initialise media player
        self.player = QMediaPlayer(self, QMediaPlayer.StreamPlayback)
        self.player.setAudioRole(QAudio.MusicRole)

        # previous seek position
        self._px = 0

        # lyric-fetch thread
        self.thread = MP_Lyric_Fetch_Thread()

        # initialise user interface
        self.init_ui()

    def init_ui(self):
        # set window geometry
        self.setMinimumSize(380, 200)
        self.setMaximumWidth(540)

        # set window title
        self.setWindowTitle("Music Player")

        # initialise status bar
        self.statusBar()

        # set up menu bar
        self.menubar = self.menuBar()
        file_m = self.menubar.addMenu("&File")

        file_open = QAction("&Open File", self)
        file_open.setShortcut("Ctrl+O")
        file_open.setStatusTip("Open an mp3 file.")
        file_m.addAction(file_open)

        file_exit = QAction("&Quit", self)
        file_exit.setShortcut("Ctrl+Q")
        file_exit.setStatusTip("Quit Music Player.")
        file_m.addAction(file_exit)

        # playback menu
        playback_m = self.menubar.addMenu("&Playback")

        playback_playpause = QAction("&Play / Pause", self)
        playback_playpause.setStatusTip("Toggle audio playback.")
        playback_m.addAction(playback_playpause)

        playback_stop = QAction("&Stop", self)
        playback_stop.setShortcut("S")
        playback_stop.setStatusTip("Stop audio playback.")
        playback_m.addAction(playback_stop)

        # initialise view
        view = QWidget()
        layout = QVBoxLayout()

        # initialise file open dialog
        open_song_dialog = QFileDialog(self)
        open_song_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        open_song_dialog.setFileMode(QFileDialog.ExistingFiles)
        open_song_dialog.setNameFilter("MP3 Song Files (*.mp3)")

        # initialise controls
        lyric_view = QTextBrowser()
        control_bar = QWidget()
        control_bar_layout = QHBoxLayout()

        # hide lyric view by default
        lyric_view.hide()

        # update the text size for lyric view
        lfont = lyric_view.font()
        lfont.setPointSize(10)
        lyric_view.setFont(lfont)

        song_title = QLabel("Click open to start playing your songs...")

        control_playpause = MP_Button("Play")
        control_stop = MP_Button("Stop")
        control_open = MP_Button("Open")
        control_volume = MP_VolumeSlider()
        control_lyric_delay = QDial()

        control_playpause.repaint()
        control_stop.repaint()
        control_open.repaint()

        control_seek_slider = MP_SeekSlider()

        # set properties
        control_playpause.setShortcut("Space")
        control_bar.setLayout(control_bar_layout)

        control_lyric_delay.setValue(0)
        control_lyric_delay.setMinimum(-150)
        control_lyric_delay.setMaximum(150)
        control_lyric_delay.setNotchTarget(20)
        control_lyric_delay.setNotchesVisible(True)
        control_lyric_delay.setMaximumSize(32, 32)

        control_volume.setMaximumSize(50, 50)
        control_volume.setValue(self.player.volume())
        control_volume.setOrientation(Qt.Horizontal)
        control_volume.setMinimum(0)
        control_volume.setMaximum(100)

        control_seek_slider.setValue(0)
        control_seek_slider.setMinimum(0)
        control_seek_slider.setMaximum(self.player.duration())
        control_seek_slider.setOrientation(Qt.Horizontal)

        # layout elements
        control_bar_layout.addWidget(control_lyric_delay)
        control_bar_layout.addWidget(control_open)
        control_bar_layout.addWidget(control_stop)
        control_bar_layout.addWidget(control_playpause)
        control_bar_layout.addWidget(control_volume)

        layout.addWidget(lyric_view, 2)
        layout.addWidget(control_seek_slider)
        layout.addWidget(song_title, 1)
        layout.addWidget(control_bar)

        # dial animation timer
        da_timer = QTimer()
        da_timer.setSingleShot(False)
        da_timer.setInterval(50)
        self.da_progress = 0

        # temporary filename
        tfilename = ""

        # slots
        def _dial_animation_update():
            control_lyric_delay.setValue(control_lyric_delay.value() +
                                         (-control_lyric_delay.value() * self.da_progress))

            if self.da_progress < 1:
                self.da_progress += 0.1
            else:
                da_timer.stop()

        def _playpause_toggle():
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()
            else:
                self.player.play()

        def _seekbar_change(x):
            # update lyric view's scrollbar
            s = (control_seek_slider.value() / control_seek_slider.maximum())
            sb = lyric_view.verticalScrollBar()
            sb.setValue((s * sb.maximum()) + control_lyric_delay.value())

            if x != self._px:
                # update player seek position
                self.player.setPosition(x)

            # update previous seek position
            self._px = x

        def _media_position_changed(x):
            # update slider position
            self._px = x
            control_seek_slider.setValue(x)

        def _media_state_changed(x):
            # change the play-pause button label accordingly
            if x == QMediaPlayer.PlayingState:
                control_playpause.setText("Pause")
            else:
                control_playpause.setText("Play")

        @pyqtSlot(str)
        def _fetch_finished(result):
            if result:
                self.statusBar().showMessage("Lyric fetching successful!")

                # show lyrics
                lyric_view.setText(result)
                lyric_view.show()

                self.setMinimumSize(380, 460)
            else:
                # show error in status bar
                self.statusBar().showMessage("Lyric fetching error!")

        @pyqtSlot(str)
        def _fetch_update(update):
            self.statusBar().showMessage(update)

        def _handle_metadata(available):
            if available:
                # default values for the current file's metadata
                md_keys = self.player.availableMetaData()

                def get_metadata(keys, default=None):
                    for key in keys:
                        if key in md_keys:
                            return self.player.metaData(key)
                    return default

                # return the metadata if it is not empty, otherwise return the default value
                def md_value(md, default):
                    return md if md else default

                # get the essential metadata (if they're available)
                title = get_metadata(["Title"], tfilename.replace(".mp3", ""))
                artist = get_metadata(["AlbumArtist", "Artist", "ContributingArtist"])
                album = get_metadata(["AlbumTitle", "Album"])
                year = get_metadata(["Year"])

                # update our song name label
                song_title.setText("Title: %s\nArtist: %s%s%s" %
                                   (title, md_value(artist, "Unknown"),
                                    "\nAlbum: %s" % md_value(album, "Unknown"),
                                    "\nYear: %s" % md_value(year, "Unknown")))

                # run our lyric-fetch thread
                self.thread.fetch(title, md_value(artist, ""))

        def _file_opened(filename):
            # open file
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))

            # update song name
            song_name = filename.split("/")
            song_name = song_name[len(song_name)-1]

            # update the song title label
            song_title.setText("Loading...")
            tfilename = song_name

            # update seek bar
            control_seek_slider.setValue(0)

            # animate the lyric delay dial
            self.da_progress = 0
            da_timer.start()

            # hide the lyrics view, again
            lyric_view.hide()
            self.setMinimumSize(380, 200)

            # update status bar
            self.statusBar().showMessage("Loaded %s..." % filename)

        def _media_length_changed(x):
            control_seek_slider.setMaximum(x)

        def _about_to_close():
            self.player.stop()

            # stop the lyric fetch thread
            self.thread.quit()

        # set up connections
        qApp.aboutToQuit.connect(_about_to_close)
        self.thread.finished_fetching.connect(_fetch_finished)
        self.thread.task_changed.connect(_fetch_update)

        da_timer.timeout.connect(_dial_animation_update)

        self.player.durationChanged.connect(_media_length_changed)
        self.player.positionChanged.connect(_media_position_changed)
        self.player.stateChanged.connect(_media_state_changed)
        self.player.metaDataAvailableChanged.connect(_handle_metadata)

        file_open.triggered.connect(open_song_dialog.show)
        file_exit.triggered.connect(qApp.quit)
        playback_playpause.triggered.connect(_playpause_toggle)
        playback_stop.triggered.connect(self.player.stop)

        open_song_dialog.fileSelected.connect(_file_opened)

        control_open.clicked.connect(open_song_dialog.show)
        control_stop.clicked.connect(self.player.stop)
        control_playpause.clicked.connect(_playpause_toggle)

        control_volume.valueChanged.connect(self.player.setVolume)
        control_seek_slider.valueChanged.connect(_seekbar_change)

        # activate window
        view.setLayout(layout)
        self.setCentralWidget(view)
        self.show()


if __name__ == "__main__":
    # initialise Qt application
    app = QApplication(sys.argv)

    # initialise window
    window = MP_Window()

    # enter main loop
    sys.exit(app.exec_())
