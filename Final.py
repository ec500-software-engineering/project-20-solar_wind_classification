import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel,  QGridLayout, QTextEdit, QRadioButton,\
    QFileDialog,QLineEdit
import audio_v3
import time
import os
import AudioToTest
import ibm_cloud_sdk_core
import translation
import textRankVersion0
from queue import Queue


class CCMS(QWidget):
    def __init__(self):
        super(CCMS, self).__init__()
        self.setWindowTitle('Conference Call Minute Summary')

        self.re = audio_v3.Recorder()
        self.T = translation.translation()

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.setLayout(self.grid)
        self.resize(800, 300)

        self.at = QLabel('Audio Text')
        self.grid.addWidget(self.at, 0, 0)

        self.namelabel = QLabel("File Name")
        self.grid.addWidget(self.namelabel,1,6)

        self.filename = QLineEdit("")
        self.grid.addWidget(self.filename,2,6)

        self.lt = QLabel("Language Transfer")
        self.grid.addWidget(self.lt,0,3)

        self.rb = QPushButton("Recording")
        self.rb.setCheckable(True)
        self.rb.clicked.connect(self.recording_button_clicked)
        self.grid.addWidget(self.rb,4,0,1,1)

        self.ftb = QPushButton("File Transfer")
        self.ftb.clicked.connect(self.audio_trans)
        self.grid.addWidget(self.ftb,4,1,1,1)

        self.afb = QPushButton("Add Audio File")
        self.afb.clicked.connect(self.audio_text)
        self.grid.addWidget(self.afb,4,2,1,1)

        self.textrank = QRadioButton("Text Rank")
        self.textrank.clicked.connect(self.text_rank)
        self.grid.addWidget(self.textrank,0,6)

        self.audiotext = QTextEdit()
        self.grid.addWidget(self.audiotext, 1, 0, 3,3)

        self.texttran = QTextEdit()
        self.grid.addWidget(self.texttran,1,3,3,3)

        self.chinese = QRadioButton("Chinese")
        self.chinese.clicked.connect(self.to_chinese)
        self.grid.addWidget(self.chinese,0,4)

        self.english = QRadioButton("English")
        self.english.clicked.connect(self.to_english)
        self.grid.addWidget(self.english, 0, 5)

        self.export = QPushButton("Export Text")
        self.export.clicked.connect(self.export_text)
        self.grid.addWidget(self.export,4,3)

        self.time = ""

    def recording_button_clicked(self):
        if self.rb.isChecked():
            self.rb.setText("Stop Recording")
            self.re.start()
        else:
            self.re.stop()
            self.re.save(time.strftime("%m-%d_%H-%M", time.localtime()))
            self.rb.setText("Start Recording")

    def audio_trans(self):
        absolute_path = QFileDialog.getOpenFileName(self, 'Open file','.',"all files(*);;"
                                                    "wav files (*.wav);;"
                                                    "mp3 files(*.mp3);;flac files(*.flac)")
        if absolute_path[0]:
            if self.filename.text():
                os.system("ffmpeg -y -i " + absolute_path[0] +" "+ self.filename.text()+".wav")
            else:
                os.system("ffmpeg -y -i " + absolute_path[0] + " out.wav")
        else:
            pass


    def audio_text(self):
        try:
            absolute_path = QFileDialog.getOpenFileName(self, 'Open file',
                                                        '.', "wav files (*.wav)")
            if absolute_path[0]:
                A = AudioToTest.AudioToTest()

                A.recognize(absolute_path[0])
                print(absolute_path[0].split("/")[-1].split(".")[0]+".json")
                text = self.A.audiojson(absolute_path[0].split("/")[-1].split(".")[0]+".json")
                self.audiotext.setText(text)

        except ibm_cloud_sdk_core.api_exception.ApiException:
            print("need api property")
            sys.exit(1)

    def to_chinese(self):
        text = self.audiotext.toPlainText()
        self.texttran.setText(self.T.translate(text,"zh-CN")['translatedText'])

    def to_english(self):
        text = self.audiotext.toPlainText()
        self.texttran.setText(self.T.translate(text, "en")['translatedText'])

    def export_text(self):
        text = self.texttran.toPlainText()
        if self.filename.text() != "":
            filename = self.filename.text()+".txt"
        else:
            filename = "out.txt"
        with open("./"+filename,'w') as F:
            F.write(text)

    def text_rank(self):
        TR = textRankVersion0.TextRank(self.audiotext.toPlainText())
        TR.get_word_confidence()
        TR.get_matrix()
        TR.calculate_converge_list()
        out = ""
        for i in TR.get_combine_word():
            i = i.split(":")[-1]
            out = out+i+"\n"
        self.texttran.setText(out)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CCMS()
    ex.show()
    sys.exit(app.exec_())
