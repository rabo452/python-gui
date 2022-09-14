from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

import re
from transcript import *
from phrase_find import *
from compare import *


# pages and their methods
# 1 page
class DownloadTranscriptPage(Screen):
    youtubeLinkTextInput = ObjectProperty()
    errorBlock = ObjectProperty()
    successBlock = ObjectProperty()

    def GetTranscript(self):
        YoutubeLink = self.youtubeLinkTextInput.text.replace(' ', '')
        ErrorBlock = self.errorBlock
        SuccessBlock = self.successBlock

        ErrorBlock.text = ''
        SuccessBlock.text = ''

        try:
            transcript_class = YoutubeVideoTranscript()
            video_transcript = transcript_class.get_transcript(YoutubeLink)
            video_title = transcript_class.get_video_title(YoutubeLink)
            video_id = transcript_class.get_video_id(YoutubeLink)

            if os.path.exists('./transcript') == False: os.makedirs('./transcript')
            transcript_class.save_transcript_into_file('./transcript/{}.txt'.format(video_title), video_id,
                                                       video_transcript)

            SuccessBlock.text = 'Video transcript successfully saved into your computer'
        except:
            ErrorBlock.text = "You indicated wrong youtube link or this video doesn't have the transcripts, please check the field"


# 2 page
class DownloadChannelTranscriptPage(Screen):
    youtubeChannelTextInput = ObjectProperty()
    errorBlock = ObjectProperty()
    successBlock = ObjectProperty()

    def GetChannelTranscript(self):
        ChannelId = self.youtubeChannelTextInput.text.replace(' ', '')
        ErrorBlock = self.errorBlock
        SuccessBlock = self.successBlock

        SuccessBlock.text = ''
        ErrorBlock.text = ''

        try:
            videos = YoutubeChannelTranscript().get_all_videos_channel(ChannelId)
            if not videos: raise Exception()

            channel_name = videos[0]['channel_name']
            if os.path.exists(f'./transcript/{channel_name}') == False: os.makedirs(f'./transcript/{channel_name}')

            transcript_class = YoutubeVideoTranscript()
            for video in videos:
                try:
                    video_title = transcript_class.delete_phohibed_symbols(video['title']).replace(' ', '_')
                    video_id = video['id']
                    transcripts = transcript_class.get_transcript(f'https://www.youtube.com/watch?v={video_id}')
                    transcript_class.save_transcript_into_file(f'./transcript/{channel_name}/{video_title}.txt',
                                                               video_id, transcripts)
                except:
                    continue

            SuccessBlock.text = f'Video Transcripts from {channel_name} successfully saved into your computer'
        except:
            ErrorBlock.text = "You indicated wrong youtube channel id, please check the field"


# 3 page
class CompareFilesPage(Screen):
    choosedFileBlock = ObjectProperty()
    errorBlock = ObjectProperty()
    successBlock = ObjectProperty()

    def GetSelectedFile(self, SelectedFile):
        self.choosedFileBlock.text = ''
        self.successBlock.text = ''
        self.errorBlock.text = ''

        if len(SelectedFile) == 0:
            self.errorBlock.text = "You didn't choose the file"
        else:
            self.choosedFileBlock.text = 'You chose the file: {}'.format(SelectedFile[0])
            self.SelectedFile = SelectedFile[0]

    def GetTheSameFiles(self):
        self.choosedFileBlock.text = ''
        self.successBlock.text = ''
        self.errorBlock.text = ''

        try:
            f = open(self.SelectedFile, 'r+', encoding='utf-8')
            phrases = []
            for line in f.readlines(): phrases.append(line)
            f.close()

            founded_files = []
            for phrase in phrases:
                if phrase != '' and phrase != ' ':
                    [founded_files.append(result) for result in PhraseFinder().find_phrase_in_the_files(phrase.lower())]

            result_file = open('./sameFiles.txt', 'w+', encoding='utf-8')
            result_string = ''
            for file_info in founded_files: result_string += f'{file_info} \n'
            result_file.write(result_string)
            result_file.close()
            self.successBlock.text = 'Founded files have written in sameFiles.txt'
        except:
            self.errorBlock.text = "You didn't choose the file"


# 4 page
class CompareAndDownloadVideosPage(Screen):
    sourceLinksBlock = ObjectProperty()
    mainVideoBlock = ObjectProperty()
    errorBlock = ObjectProperty()
    successBlock = ObjectProperty()

    def CompareVideos(self):
        self.successBlock.text = ''
        self.errorBlock.text = ''

        try:
            main_id = YoutubeVideoTranscript().get_video_id(self.mainVideoBlock.text.replace(' ', ''))
            link = f'https://youtu.be/{main_id}'
            YoutubeVideoTranscript().get_transcript(link)

            SourceYoutubeVideos = []
            for block in self.sourceLinksBlock.children:
                if block.text.replace(' ', '') == '': continue
                try:
                    id = YoutubeVideoTranscript().get_video_id(block.text.replace(' ', ''))
                    link = f'https://youtu.be/{id}'
                    YoutubeVideoTranscript().get_transcript(link)
                    SourceYoutubeVideos.append(id)
                except:
                    continue

            if not SourceYoutubeVideos: raise Exception()
            Compare_video_class().main([[main_id, SourceYoutubeVideos]])
            self.successBlock.text = "The same parts of videos have been written in transcripts directory"
        except:
            self.errorBlock.text = "Please make sure that you wrote the right youtube links"


# search the same transcripts in files and download video by these transcripts,
# 5 page
class SearchAndDownloadVideos(Screen):
    choosedFileBlock = ObjectProperty()
    errorBlock = ObjectProperty()
    successBlock = ObjectProperty()

    def GetSelectedFile(self, SelectedFile):
        self.choosedFileBlock.text = ''
        self.successBlock.text = ''
        self.errorBlock.text = ''

        if len(SelectedFile) == 0:
            self.errorBlock.text = "You didn't choose the file"
        else:
            self.choosedFileBlock.text = 'You chose the file: {}'.format(SelectedFile[0])
            self.SelectedFile = SelectedFile[0]

    def CompareAndDownloadTranscriptFiles(self):
        try:
            result = TheSameFilesTranscripts().get_the_same_video_ids(self.SelectedFile)
            if not result:
                self.errorBlock.text = "Program didn't find the same transcripts as you downloaded"
                return

            main_video_id, source_video_ids = result['main_video_id'], result['source_video_ids']
            Compare_video_class().main([[main_video_id, source_video_ids]])
            self.successBlock.text = "The same parts of videos have been written in files directory"
        except:
            self.errorBlock.text = "You didn't choose the file, here isn't the .txt files or id of video incorrect"


# 6 page, the same as 4 functionality but user can add links in text input
class CompareAndDownloadVideosTextInputPage(Screen):
    sourceLinksBlock = ObjectProperty()
    mainVideoBlock = ObjectProperty()
    errorBlock = ObjectProperty()
    successBlock = ObjectProperty()

    def CompareVideos(self):
        self.successBlock.text = ''
        self.errorBlock.text = ''

        try:
            main_id = YoutubeVideoTranscript().get_video_id(self.mainVideoBlock.text.replace(' ', ''))
            link = f'https://youtu.be/{main_id}'
            YoutubeVideoTranscript().get_transcript(link)

            text = self.sourceLinksBlock.text
            links = re.findall(r'(https?://[\d\w\-\_\.\/]+)\b', text)
            SourceYoutubeVideos = []
            for href in links:
                try:
                    id = YoutubeVideoTranscript().get_video_id(href)
                    link = f'https://youtu.be/{id}'
                    YoutubeVideoTranscript().get_transcript(link)
                    SourceYoutubeVideos.append(id)
                except:
                    continue

            if not SourceYoutubeVideos: raise Exception()
            Compare_video_class().main([[main_id, SourceYoutubeVideos]])
            self.successBlock.text = "The same parts of videos have been written in transcripts directory"
        except:
            self.errorBlock.text = "Please make sure that you wrote the right youtube links"


class ProgramApp(App):
    def build(self):
        Window.size = (980, 640)
        sm = ScreenManager()
        sm.add_widget(DownloadTranscriptPage(name='firstPage'))
        sm.add_widget(DownloadChannelTranscriptPage(name='secondPage'))
        sm.add_widget(CompareFilesPage(name='thirdPage'))
        sm.add_widget(CompareAndDownloadVideosPage(name='fourthPage'))
        sm.add_widget(SearchAndDownloadVideos(name='fifthPage'))
        sm.add_widget(CompareAndDownloadVideosTextInputPage(name='sixthPage'))

        return sm


if __name__ == '__main__':
    ProgramApp().run()
