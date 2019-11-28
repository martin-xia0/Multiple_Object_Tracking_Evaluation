import os
import numpy as np
from numpy.core.multiarray import ndarray
from scipy import optimize
import pymysql


def load_annotation(filename):
    """load data from input txt

    params
    filename: file name of loading txt
    ---------
    return
    video: nXm matrix, contain n frames, each frame contains m objects
    frame_num: frame number of input txt
    obj_num: object num of each frame in time series
    ---------
    """
    txt = open(filename)
    result = txt.readlines()
    all_joint_video = []
    for joint_id in range(1,15):
        joint_video = []
        frame = []
        obj_num = []
        frame_id = 0
        for line in result:
            person = line.split(',')
            if not len(person) == 0:
                if int(person[0]) == frame_id:
                    frame.append(person[2*joint_id : 2*joint_id+2])
                else:
                    frame_id += 1
                    obj_num.append(len(frame))
                    joint_video.append(frame)
                    frame = [person[2*joint_id : 2*joint_id+2]]
        frame_num = frame_id
        print(joint_video)
        all_joint_video.append(joint_video)
    print("Total frame of {} is {}".format(filename, frame_num))
    return all_joint_video, frame_num, obj_num


def distance_matrix_series(gt_video, hp_video, frame_num):
    """

    params
    gt_video: ground truth frame series
    hp_video: hypothesis frame series
    frame_num: frame number of the video
    ----------
    return
    distance_matrix_series: distance_matrix of each joint frame in time series
    """
    distance_matrix_series = []
    for frame_id in range(frame_num):
        matrix = distance_matrix(gt_video[frame_id], hp_video[frame_id])
        distance_matrix_series.append(matrix)
        if frame_id == 0:
            print(matrix)
    return distance_matrix_series


def distance_matrix(gt_frame, hp_frame):
    """

    params
    gt_frame: ground truth frame
    hp_frame: hypothesis frame
    distance list； 14 distances between two obj
    --------------
    return
    distance_matrix: distance list between one pair (oi, hj) (euclid distance), each row represent one ground truth obj
    """
    distance_matrix = []
    for gt_obj in gt_frame:
        distance_row = []
        for hp_obj in hp_frame:
            distance = joint_distance(gt_obj, hp_obj)
            distance_row.append(distance)
        distance_matrix.append(distance_row)
    return distance_matrix


def joint_distance(gt_obj, hp_obj):
    """

    params
    gt_obj: object in ground truth
    hp_obj: object in hypothesis
    ----------
    return
    distance: distances of two obj (14 joints)
    """
    gt_obj = np.array(gt_obj).astype(int)
    hp_obj = np.array(hp_obj).astype(int)
    dist_x = abs(gt_obj[0] - hp_obj[0])
    dist_y = abs(gt_obj[1] - hp_obj[1])
    dist = np.sqrt(dist_x * dist_x + dist_y * dist_y)
    print("joint distance of this obj is:{}".format(dist))
    return dist


def mapping_series(distance_matrix_series):
    """ the hp_gt mapping in time series

    params
    distance_matrix_series
    --------------
    return
    mapping_series: matching pairs for each joint in each frame in time series
    distance_series: minimum distance series for each joint in each frame in time series
    """
    mapping_series = []
    distance_series = []
    test = 1
    for frame in distance_matrix_series:
        mapping, distance = mapping_frame(frame)
        mapping_series.append(mapping)
        distance_series.append(distance)
        if test:
            print(mapping)
            test = 0
    return mapping_series, distance_series


def mapping_frame(distance_matrix):
    """using hungary algorithm to get the mapping pairs (oi, hj)
    thus minimize the total gt-hp distance error

    params
    distance_matrix: distance matrix of each joint in one frame
    threshold: max distance to form a gt-hp pair
    -----------
    return
    frame_mapping: the joint series distance in one frame
    joint_mapping: the mapping pairs for one joint in frame{'oi': 'hj', 'oh': 'hl' ...}
    distance_frame: the minimum sum of distance for one frame
    """
    frame_mapping = {}
    threshold = 100
    distance_frame = 0
    distance_array = np.array(distance_matrix)
    print("The shape of the distance array is {}".format(distance_array.shape))
    opt_gt_id, opt_hp_id = optimize.linear_sum_assignment(distance_array)
    print(opt_hp_id)

    assert len(opt_gt_id) == len(opt_hp_id)
    pre_pair_num = len(opt_gt_id)
    for i in range(pre_pair_num):
        gt_id = opt_gt_id[i]
        hp_id = opt_hp_id[i]
        distance_frame = distance_array[gt_id][hp_id]
        if distance_frame < threshold:
            frame_mapping[gt_id] = hp_id
    return frame_mapping, distance_frame


def MOTA_series(mapping_series, frame_num, gt_num, hp_num):
    """calculate the MOTA series of a video

    params
    mapping_series: mapping for the whole series
    frame_num: total number of frames
    gt_num: object num series of ground truth
    hp_num: object num series of hypothesis
    -----------
    return
    MOTA: MOTA for the whole series
    """
    MOTA_series = []
    for frame_id in range(frame_num):
        MOTA_series.append(MOTA_frame(mapping_series, frame_id, gt_num[frame_id], hp_num[frame_id])[0])
    return MOTA_series


def MOTA_frame(mapping_series, frame_id, gt_num, hp_num):
    """calculate MOTA of a frame

    params
    mapping_series: mapping for frame series
    frame_id: id of frame which is processing
    gt_num: object num of ground truth
    hp_num: object num of hypothesis
    -----------
    return
    MOTA: MOTA for a frame
    FN: false negative number of a frame (miss)
    FP: false positive number of a frame (false positive)
    """
    frame_MOTA = []
    if frame_id == 0:
        mismatch = 0
        false_positive = 0
        miss = 0
    else:
        mapping_prev = mapping_series[frame_id-1]
        mapping_now = mapping_series[frame_id]
        mismatch = 0
        for gt_obj_pre in mapping_prev:
            hp_obj_pre = mapping_prev[gt_obj_pre]
            if gt_obj_pre in mapping_now.keys():
                hp_obj_now = mapping_now[gt_obj_pre]
                if hp_obj_pre != hp_obj_now:
                    mismatch += 1
        false_positive = hp_num - len(mapping_now)
        miss = gt_num - len(mapping_now)
    print('Frame {}, mismatch:{}, false_positive:{}, miss:{}'.format(frame_id, mismatch, false_positive, miss))
    MOTA = 1 - (mismatch + false_positive + miss) / gt_num
    precision = 1 - false_positive / hp_num
    recall = 1 - miss / gt_num
    return MOTA, precision


def mAP_series(mapping_series, frame_num, gt_num, hp_num):
    """
    
    return:
    return mAP of one particular joint
    FP: false positive obj_num of one frame
    FN: false negative obj_num of one frame
    """
    mAP_series = []
    for frame_id in range(frame_num):
        mAP_series.append(MOTA_frame(mapping_series, frame_id, gt_num[frame_id], hp_num[frame_id])[1])
    return mAP_series


def evaluate_tracker(cursor, challenge_id, tracker_id, metrics_list, result_list):
    """fill in the evaluation result of a tracker.
    This tracker has already added in db when user create

    challenge_id
    tracker_id
    metrics_list: the metrics used to evaluate a tracker
    result_list: the evaluation result of the tracker

    return
    """
    result_sql = ""
    for i in range(len(metrics_list)):
        metrics = metrics_list[i]
        result = result_list[i]
        if i == len(metrics_list) - 1:
            result_sql += "{}={} ".format(metrics, result)
        else:
            result_sql += "{}={}, ".format(metrics, result)
    add_sql = "UPDATE TRACKER{} SET {} WHERE id={};".format(challenge_id, result_sql, tracker_id)
    print(add_sql)
    cursor.excute(add_sql)


if __name__ == '__main__':
    # conn = pymysql.Connect(
    #     host='localhost',
    #     port=3306,
    #     user='admin',
    #     passwd='abc.123',
    #     db='niewu',
    #     charset='utf8'
    # )
    # the tracker has already created, we now need to use the upload hypothesis files to get the evaluation results
    gt_video, gt_framenum, gt_objnum = load_annotation('posetrack_gt.txt')
    hp_video, hp_framenum, hp_objnum = load_annotation('posetrack_hp.txt')

    assert gt_framenum == hp_framenum
    frame_num = hp_framenum
    for joint_id in range(14):
        joint_distance_matrix_series = distance_matrix_series(gt_video[joint_id], hp_video[joint_id], frame_num)
        joint_mapping_series, distance_series = mapping_series(joint_distance_matrix_series)
        print(joint_mapping_series)
        joint_MOTA_series = MOTA_series(joint_mapping_series, frame_num, gt_objnum, hp_objnum)
        print(joint_MOTA_series)
        joint_mAP_series = mAP_series(joint_mapping_series, frame_num, gt_objnum, hp_objnum)
        print(joint_mAP_series)
        joint_MOTA = sum(joint_MOTA_series) / len(joint_MOTA_series)
        print(joint_MOTA)
