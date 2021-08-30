# get transcript from youtube video, youtube channel

import requests
from youtube_transcript_api import YouTubeTranscriptApi
import pytube
from phrase_find import *
api_key = ''


class YoutubeVideoTranscript:
    def get_transcript(self, youtube_link):
        video_id = pytube.extract.video_id(youtube_link)
        transcripts = YouTubeTranscriptApi.get_transcript(video_id)
        return transcripts

    def get_video_id(self, youtube_link):
        return pytube.extract.video_id(youtube_link)

    def get_video_title(self, youtube_link):
        return self.delete_phohibed_symbols(pytube.YouTube(youtube_link).title).replace(' ', '_')

    def delete_phohibed_symbols(self, string):
        replacements = ['?', '/', '\\', '*', '>', '<', '"', ':', '|', "'"]
        for i in replacements:
            string = string.replace(i, '')
        return string

    def save_transcript_into_file(self, file_path, video_id, transcript):
        file_text = video_id + '\n'

        for obj in transcript:
            file_text += '{} {} \n'.format(obj['text'], self.change_time_format(obj['start']))

        f = open(file_path, 'w+', encoding='utf-8')
        f.write(file_text)
        f.close()

    #secs format to mins:secs format
    def change_time_format(self,secs):
        minutes, secs = str(round(secs / 60, 2)).split('.') #time in minutes
        secs = str(round(int(secs) / 10 * 6)) #from milisecs to secs
        if int(minutes) <= 9: minutes = '0' + minutes
        if int(secs) <= 9: secs = '0' + secs

        if int(minutes) >= 60: # if it has hours
            hours = round(int(minutes) / 60)
            minutes = str(round(int(minutes) % 60))
            if int(minutes) <= 9: minutes = '0' + minutes

            return "{}:{}:{}".format(hours, minutes, secs)
        return "{}:{}".format(minutes,secs)

class YoutubeChannelTranscript:
    api_key = api_key
    #return arr with ids of youtube links
    def get_all_videos_channel(self, channel_id):
        base_url = 'https://www.googleapis.com/youtube/v3/search?'
        videos = []

        first_url = base_url + 'key={}&channelId={}&part=snippet,id&order=date&maxResults=700'.format(self.api_key, channel_id)
        url = first_url
        while True:
            try:
                res = requests.get(url).json()
                for item in res['items']:
                    try: videos.append({'title': item['snippet']['title'], 'id': item['id']['videoId'], 'channel_name': item['snippet']['channelTitle']})
                    except: continue

                url = first_url + '&pageToken={0}'.format(res['nextPageToken'])
            except: break
        return videos




#this class do comparing the text to understand if texts has similiar phrases (3)
#class for section 5 in program
class Compare_text:
    #if it has >5 simliar phrases then return true, else false
    def compare_text(self, text1,text2):
        simliar_phrases = 0
        text1_words = [word for line in text1.replace('!', '').replace('?', '').replace('.','').replace(',','').lower().split('\n') for word in line.split(' ') if word != '']
        text2_words = [word for line in text2.replace('!', '').replace('?', '').replace('.','').replace(',','').lower().split('\n') for word in line.split(' ') if word != '']

        text1_index = -1
        while text1_index < (len(text1_words) - 1):
            text1_index += 1
            text1_word = text1_words[text1_index]

            text2_index = -1
            while text2_index < (len(text2_words) - 1):
                text2_index += 1
                text2_word = text2_words[text2_index]

                if text1_word == text2_word:
                    #check the next 10 words
                    is_simliar_phrase = True
                    for i in range(5):
                        if (text1_index + i) >= (len(text1_words) - 1) or (text2_index + i) >= (len(text2_words) - 1):
                            is_simliar_phrase = False
                            break

                        text1_word = text1_words[text1_index + i]
                        text2_word = text2_words[text2_index + i]
                        if text1_word != text2_word:
                            is_simliar_phrase = False
                            break
                    if is_simliar_phrase:
                        simliar_phrases += 1

        if simliar_phrases >= 20: return True
        return False



# this class finds the same phrases in transcript files,
class TheSameFilesTranscripts:
    def get_the_same_video_ids(self,file_path):
        result = {}

        f = open(file_path, 'r+', encoding='utf-8')
        main_video_transcript = f.read()
        f.close()

        main_video_id = main_video_transcript.split('\n')[0].replace(' ', '') #first string in file is video id

        txt_files = PhraseFinder().get_txt_files()
        if not txt_files: raise Exception()

        sources_id = []
        for txt_path in txt_files:
            f = open(txt_path, 'r+', encoding='utf-8')
            file_data = f.read()
            f.close()

            source_video_id = file_data.split('\n')[0].replace(' ', '')
            if source_video_id == main_video_id: continue

            try: YouTubeTranscriptApi.get_transcript(source_video_id)
            except: continue

            if Compare_text().compare_text(main_video_transcript, file_data): sources_id.append(source_video_id)

        if len(sources_id) != 0:
            result['source_video_ids'] = sources_id
            result['main_video_id'] = main_video_id
        return result
