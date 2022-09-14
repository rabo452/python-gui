import requests
import pytube
import os
from bs4 import BeautifulSoup as bs
from moviepy.video.io.VideoFileClip import VideoFileClip
from youtube_transcript_api import YouTubeTranscriptApi
this_module = __import__(__name__)

#compare two or more different videos to find the same parts and download it
#for 1 main video can be more than 1 source video make sure of it!
class Compare_video_class:
    # this function do all work for compare videos, return nothing
    # videos - id of youtube videos
    #youtube videos with transcripts
    def main(self,videos = []):
        if not videos: return
        #here will be stored all files
        if os.path.exists('./files') == False:
            os.makedirs('./files')
        if os.path.exists('./files/videos') == False:
            os.makedirs('./files/videos')
        if os.path.exists('./files/transcripts') == False:
            os.makedirs('./files/transcripts')

        main_videos_ids = []
        sources_videos_ids = []

        transcript_compare_main_videos = [] # save transcript into this arr for compare function
        transcript_compare_sources_videos = [] # save transcript into this arr for compare function

        #get main and sources videos
        for main_video, sources_videos in videos:
            main_videos_ids.append(main_video)
            sources_videos_ids.append(sources_videos)



        #loop that takes the transcript text from main and sources videos
        for i in range(len(main_videos_ids)):
            if not main_videos_ids[i] or not sources_videos_ids[i]:
                continue
            transcript_compare_sources_videos.append([]) #need to save arr of transcripts of source videos
            transcript_compare_main_videos.append([])

            video_title = self.delete_need_symbols(self.get_youtube_video_title(main_videos_ids[i]))

            transcript_text_string_time = "{} \n".format(main_videos_ids[i])
            transcript_text_string_without_time = "{} \n".format(main_videos_ids[i])
            for phrase_obj in YouTubeTranscriptApi.get_transcript(main_videos_ids[i]):
                transcript_text_string_time += '{}     {} \n'.format(phrase_obj['text'].replace('\n', ''), self.secs_to_time(int(phrase_obj['start'])))
                transcript_text_string_without_time += '{} \n'.format(phrase_obj['text'].replace('\n', ''))
                for word in [word for word in phrase_obj['text'].lower().replace('!', '').replace('?', '').replace('\n', '').replace('.', '').replace(',', '').split(' ') if word != '']:
                    transcript_compare_main_videos[i].append(word) # for main only save words the timing doesn't matter

            self.save_transcript_text(video_title, transcript_text_string_time)
            self.save_transcript_text(video_title + '_', transcript_text_string_without_time)

            for source_video_id in sources_videos_ids[i]:
                video_title = self.delete_need_symbols(self.get_youtube_video_title(source_video_id))

                transcript_text_string_time = "{} \n".format(source_video_id)
                transcript_text_string_without_time = "{} \n".format(source_video_id)
                transcript_source_video = []
                for phrase_obj in YouTubeTranscriptApi.get_transcript(source_video_id):
                    transcript_text_string_time += '{}     {} \n'.format(phrase_obj['text'].replace('\n', ''), self.secs_to_time(int(phrase_obj['start'])))
                    transcript_text_string_without_time += '{} \n'.format(phrase_obj['text'].replace('\n', ''))
                    for arr_word in [[word, int(phrase_obj['start'])] for word in phrase_obj['text'].lower().replace('!', '').replace('?', '').replace('\n', '').replace('.', '').replace(',', '').split(' ') if word != '']:
                        transcript_source_video.append(arr_word) #append the each word with timing of phrase

                transcript_compare_sources_videos[i].append(transcript_source_video)
                self.save_transcript_text(video_title, transcript_text_string_time)
                self.save_transcript_text(video_title + '_', transcript_text_string_without_time)




        #compare the transcript and get the timing there is transcript words the same for each main and source video
        for i in range(len(transcript_compare_main_videos)):
            transcript_main = transcript_compare_main_videos[i]
            transcripts_sources = transcript_compare_sources_videos[i]
            try:
                self.cut_and_download_youtube_video(sources_videos_ids[i], self.compare_video_transcripts(transcript_main,transcripts_sources))
            except: continue 



    def cut_and_download_youtube_video(self, sources_videos_ids, cut_moments):
        if not cut_moments: return
        for i in range(len(sources_videos_ids)):
            source_video_id = sources_videos_ids[i]
            video_cut_moments = cut_moments[i] #cut timestamp for this source video

            video_title = self.delete_need_symbols(self.get_youtube_video_title(source_video_id))
            download_path = './files/videos/{}/'.format(video_title)
            if os.path.exists(download_path) == False:
                os.makedirs(download_path)

            youtube = pytube.YouTube('https://youtu.be/' + source_video_id)
            video = youtube.streams.get_highest_resolution()
            video.download(download_path, filename = video_title)

            f = open(download_path + 'cut points video.txt', 'w+', encoding='utf-8')
            cut_point_string = ''
            count_of_video = 1 #how many videos already cutted need for name of file of cut video
            transcripts = YouTubeTranscriptApi.get_transcript(source_video_id)
            for cut_start_point, cut_end_point in video_cut_moments: # single_cut_moment[0] - start point, single_cut_moment[1] - end point
                video_path = os.path.join(download_path, 'video {}/'.format(count_of_video))
                if os.path.exists(video_path) == False: os.makedirs(video_path)


                self.write_cutted_transcript(cut_start_point,cut_end_point, source_video_id, count_of_video, video_title, video_path, transcripts)
                cut_point_string += " start point: {}, end point: {}, for {} video \n".format(self.secs_to_time(cut_start_point),self.secs_to_time(cut_end_point),count_of_video)
                clip = VideoFileClip(download_path + video_title + '.mp4').subclip(cut_start_point, cut_end_point + 2)
                clip.write_videofile(video_path + video_title + str(count_of_video) + '.mp4')
                clip.close()
                count_of_video += 1

            f.write(cut_point_string)
            f.close()


    def write_cutted_transcript(self, start_point, end_point, video_id, count_of_video, video_title, path, transcripts):
        f = open(os.path.join(path,f'transcript for video {count_of_video}.txt'), 'w+',encoding='utf-8')
        cutted_transcript = ''
        for phrase_obj in transcripts:
            phrase_obj['start'] = int(phrase_obj['start'])
            if phrase_obj['start'] > start_point and phrase_obj['start'] < end_point:
                cutted_transcript += phrase_obj['text'] + '   {} \n'.format(self.secs_to_time(phrase_obj['start']))
        f.write(cutted_transcript)
        f.close()



    #this function compare main transcript and sources transcripts videos
    #return arr with timing that the same for main video and source video
    def compare_video_transcripts(self, main_transcript_words, sources_transcripts):
        result = []
        for i in range(len(sources_transcripts)):
            source_transcript_video = sources_transcripts[i]
            result.append([])

            source_index = -1
            while source_index < len(source_transcript_video) - 1:
                source_index += 1
                source_word, souce_timing = source_transcript_video[source_index]

                main_index = -1
                while main_index < len(main_transcript_words) - 1:
                    main_index += 1
                    main_word = main_transcript_words[main_index]
                    if source_word == main_word:
                        #test the next 10 words for the same
                        part_of_video = True
                        for y in range(11):
                            if (main_index + y) >= len(main_transcript_words) - 1 or source_index + y >= (len(source_transcript_video) - 1):
                                part_of_video = False
                                break

                            main_word = main_transcript_words[main_index + y]
                            source_word, souce_timing = source_transcript_video[source_index + y]
                            if source_word != main_word:
                                part_of_video = False
                                break

                        if not part_of_video: continue
                        start_point = source_transcript_video[source_index][1]
                        source_index += 10
                        main_index += 10

                        while True:
                            if (main_index) >= (len(main_transcript_words) - 1) or (source_index) >= (len(source_transcript_video) - 1):
                                end_point = source_transcript_video[source_index][1]
                                result[i].append([start_point, end_point])
                                break

                            main_word = main_transcript_words[main_index]
                            source_word, souce_timing = source_transcript_video[source_index]
                            if main_word != source_word:
                                #check if the next 30 words the same maybe 1 word doesn't exit
                                the_same_part = False
                                for y in range(30):
                                    if (main_index + y) >= len(main_transcript_words) - 1 or (source_index + y) >= (len(source_transcript_video) - 1):
                                        the_same_part = False
                                        break
                                    main_word = main_transcript_words[main_index + y]
                                    source_word, souce_timing = source_transcript_video[source_index + y]
                                    if source_word == main_word:
                                        the_same_part = True
                                        main_index += y
                                        source_index += y
                                        break

                                if not the_same_part:
                                    end_point = source_transcript_video[source_index][1]
                                    result[i].append([start_point, end_point])
                                    break
                            main_index += 1
                            source_index += 1
        return result

    #support functions
    def delete_need_symbols(self,string):
        replacements = ['?', '/', '\\', '*', '>', '<', '"', ':', '|', '\'']
        for i in replacements:
            string = string.replace(i, '')
        return string

    def secs_to_time(self,secs):
        minutes, secs = str(round(secs / 60, 2)).split('.') #time in minutes
        secs = str(round(float(secs) / 10 * 6)) #from milisecs to secs
        if int(minutes) <= 9:
            minutes = '0' + minutes
        if int(secs) <= 9:
            secs = '0' + secs
        return "{}:{}".format(minutes,secs)

    #save transcript text into file
    def save_transcript_text(self, file_name, text):
        if os.path.exists('./files/transcripts/{}'.format(file_name)) == False:
            os.makedirs('./files/transcripts/{}'.format(file_name))
        f = open("./files/transcripts/{}/{}.txt".format(file_name, file_name), 'w+', encoding='utf-8')
        f.write(text)
        f.close()

    def get_youtube_video_title(self, id):
        r = requests.get(f'https://www.youtube.com/watch?v={id}')
        return bs(r.text,'lxml').select('title')[0].text.replace(' - YouTube', '')


if __name__ == '__main__':
    Compare_video_class().main([['qj49b929tgk', ['BmYv8XGl-YU', '7f97tMnV_TU']]])
