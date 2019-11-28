import cv2
import os
import system
import sys


# read frames from txt
def read_annotation(tracker_id, video_id):
    file_adress = 'tracker/{}/result/{}.txt'.format(tracker_id, video_id)
    txt = open(file_adress)
    result = txt.readlines()
    print(len(result))
    video = []
    frame = []
    frame_id = 0
    for line in result:
        person = line.split(',')
        if not len(person) == 0:
            if int(person[0]) == frame_id:
                frame.append(person)
            else:
                frame_id += 1
                video.append(frame)
                frame = []
                frame.append(person)
    print(frame_id)
    return video, frame_id


# draw rectangle
def draw_rectangle(frame, img):
    lineThickness = 2
    color_table = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255))
    color_num = 0
    for person in frame:
        color_num = (color_num + 1) % 6
        color = color_table[color_num]
        x = int(person[2])
        w = int(person[3])
        y = int(person[4])
        h = int(person[5])
        dot1 = (x, y)
        dot2 = (x + w, y)
        dot3 = (x + w, y + h)
        dot4 = (x, y + h)
        cv2.line(img, dot1, dot2, color, lineThickness)
        cv2.line(img, dot2, dot3, color, lineThickness)
        cv2.line(img, dot3, dot4, color, lineThickness)
        cv2.line(img, dot4, dot1, color, lineThickness)
    return img


# save the composed videos and frames
def save_tracker_info(challenge_id, tracker_id):
    tracker_adress = "home/data/tracker/{}/".format(challenge_id)
    # build challenge dir
    os.mkdir(tracker_adress + "video")
    os.mkdir(tracker_adress + "frame")


if __name__ == '__main__':
    tracker_id = sys.argv[1]
    # if not os.path.exists('./tracker'):
    #     os.mkdir('./tracker')
    # if not os.path.exists('./tracker/{}'.format(tracker_id)):
    #     os.mkdir('./tracker/{}'.format(tracker_id))

    result_path = './tracker/{}/result'.format(tracker_id)
    video_path = './tracker/{}/video'.format(tracker_id)
    frame_path = './tracker/{}/frame'.format(tracker_id)
    
    if not os.path.exists(video_path):
        os.mkdir(video_path)
    if not os.path.exists(frame_path):
        os.mkdir(frame_path)

    for filename in os.listdir(result_path):
        print(filename)
        video_id = filename.split('.')[0]
        video, frame_num = read_annotation(tracker_id, video_id)
        print("total frame num is {}".format(frame_num))

        # generate annotated graphs
        for frame_id in range(frame_num):
            print("processing frame {}".format(frame_id))
            imgname = str(frame_id).zfill(6) + '.jpg'
            origin_img = './frame/test/{}/{}'.format(video_id, imgname)
            print("origin_img: {}".format(origin_img))
            img = cv2.imread(origin_img)
            frame = video[frame_id]
            img1 = draw_rectangle(frame, img)
            if not os.path.exists('./tracker/{}/frame/{}'.format(tracker_id, video_id)):
                os.mkdir('./tracker/{}/frame/{}'.format(tracker_id, video_id))
            cv2.imwrite('./tracker/{}/frame/{}/{}'.format(tracker_id, video_id, imgname), img1)

        # generate annotated videos
        video_address = './tracker/{}/video/{}.mp4'.format(tracker_id, video_id)
        frame_address = './tracker/{}/frame/{}/%6d.jpg'.format(tracker_id, video_id)
        system.call("ffmpeg -framerate 24 -i {} {}".format(frame_address, video_address))