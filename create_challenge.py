import pymysql
import os


def build_challenge_table(cursor):
    try:
        build_sql = "CREATE TABLE challenge " \
                    "(id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50), varity VARCHAR(50), video_num INT, train_num INT, test_num INT, " \
                    "start_time VARCHAR(50), description VARCHAR(50), status TINYINT, metrics VARCHAR(50)) AUTO_INCREMENT=1;"
        print(build_sql)
        cursor.execute(build_sql)
    except:
        print('Build table challenge fail')


def create_challenge(cursor, challenge_info):
    """ insert the basic information of a challenge

    params
    cursor: database cursor
    challenge_info: basic info of the challenge (must be a tuple)
        (name, varity, video_num, train_num, test_num, start_time, description, status)
    """
    try:
        insert_sql = "INSERT INTO CHALLENGE " \
                     "(name, varity, video_num, train_num, test_num, start_time, description, status, metrics) " \
                     "VALUES " \
                     "{};".format(str(challenge_info))
        print(insert_sql)
        cursor.execute(insert_sql)
    except:
        print('Insert new challenge fail')


def build_video_table(cursor, challenge_id, param_list):
    """ add the basic information of each video

    params
    cursor: database cursor
    challenge_id
    param_list: params of a video (fps...)
    """
    try:
        param_sql = "id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50), type VARCHAR(50)"
        for metrics in param_list:
            param_sql += ", "
            param_sql += str(metrics)
            param_sql += " DECIMAL(8,4)"
        param_sql += ", status TINYINT"
        build_sql = "CREATE TABLE video_{} ({}) AUTO_INCREMENT=1;".format(challenge_id, param_sql)
        print(build_sql)
        cursor.execute(build_sql)
    except:
        print('Build table video fail')


def add_video(cursor, challenge_id, name, type, param_list, param_value):
    """

    param
    cursor
    challenge_id
    param_list: list of video params (must tuple)
    param_value: value of above params (must tuple)
    """
    try:
        param_sql = ', '.join(('name', 'type') + param_list + ('status',))
        value_sql = str((name, type) + param_value + (1,))
        insert_sql = "INSERT INTO video_{} ({}) VALUES {};".format(challenge_id, param_sql, value_sql)
        print(insert_sql)
        cursor.execute(insert_sql)
    except:
        print('Insert new video fail')


def build_tracker_table(cursor, challenge_id, metrics_list):
    """ add the basic information of each video

    params
    cursor: database cursor
    challenge_id
    metrics_list: metrics to evaluate tracker performance
    params_from_web: the basic information user fill in the web while creating the tracker
    """
    try:
        metrics_sql = "id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50), short_name VARCHAR(50), description VARCHAR(50), " \
                      "hardware VARCHAR(50), runtime VARCHAR(50), create_time INT, "
        for metrics in metrics_list:
            metrics_sql += str(metrics)
            metrics_sql += " DECIMAL(8,4), "
        metrics_sql += "user_id INT, status TINYINT"
        build_sql = "CREATE TABLE tracker_{} ({}) AUTO_INCREMENT=1;".format(challenge_id, metrics_sql)
        print(build_sql)
        cursor.execute(build_sql)
    except:
        print('Build table tracker_video fail')


def build_tracker_video_table(cursor, challenge_id, metrics_list):
    """ build the tracker_video table

    param
    cursor:
    challenge_id:
    video_num:
    """
    try:
        metrics_sql = "id INT PRIMARY KEY AUTO_INCREMENT, tracker_id INT, video_id INT"
        for metrics in metrics_list:
            metrics_sql += ", "
            metrics_sql += str(metrics)
            metrics_sql += " DECIMAL(8,4)"

        build_sql = "CREATE TABLE tracker_video_{} ({}) AUTO_INCREMENT=1;".format(challenge_id, metrics_sql)
        print(build_sql)
        cursor.execute(build_sql)
    except:
        print('Build table tracker_video fail')


def create_challenge_dir(challenge_id):
    try:
        challenge_adress = "home/data/challenge/{}/".format(challenge_id)
        tracker_adress = "home/data/tracker/{}/".format(challenge_id)
        # build challenge dir
        os.mkdir(challenge_adress + "video")
        os.mkdir(challenge_adress + "frame")
        os.mkdir(challenge_adress + "groundtruth")
    except:
        print('create challenge directory fail')

if __name__ == '__main__':
    # ------------------------------------------------------------------------------------------ #
    # parameters you need to pass:
    challenge_id = 1

    # parameters of one challenge   !!!warning: you should not modify this list
    challenge_param_list = ('challenge_name', 'challenge_catagory', 'video_num', 'train_num', 'test_num', 'date', 'description', 'status', 'metrics')
    
    # basic information of a challenge !!!please make one-to-one correspondence with challenge_param_list
    challenge_info = ('mot2018', 'mot', 2, 1, 1, '2018/11/16', 'good', 1, 'MOTA, MOTP')
    metrics_list = ('MOTA', 'MOTP')
    
    # parameters of one video   !!!warning: you should not modify this list
    video_param_list = ('fps', 'resolution', 'tracks', 'boxes', 'density')

    # basic information of videos !!!please make one-to-one correspondence with video_param_list
    video_list = ([
                    {
                        'name': 'Shanghai station',
                        'type': 'train',
                        'param_value': ('21', '1080x768', '9', '3380', '9.8')
                    }
                ])

    # ------------------------------------------------------------------------------------------ #
    # create challenge process
    conn = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='abcd.1234',
        db='challenge',
        charset='utf8'
    )
    cursor = conn.cursor()

    build_challenge_table(cursor)

    # create challenge
    create_challenge(cursor, challenge_info)

    # build video table
    build_video_table(cursor, challenge_id, video_param_list)

    # add videos
    for video in video_list:
        name = video['name']
        type = video['type']
        param_value = video['param_value']
        add_video(cursor, challenge_id, name, type, video_param_list, param_value)

    # build tracker table
    build_tracker_table(cursor, challenge_id, metrics_list)

    # build tacker_video table
    build_tracker_video_table(cursor, challenge_id, metrics_list)

    print('Create success!')